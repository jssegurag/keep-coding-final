"""
Módulo para indexación en ChromaDB con normalización de metadatos
"""
import chromadb
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Tuple
import json
import os
from datetime import datetime
from config.settings import (
    CHROMA_PERSIST_DIRECTORY, 
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL,
    CSV_METADATA_PATH,
    JSON_DOCS_PATH
)
from src.chunking.document_chunker import DocumentChunker, Chunk
from src.utils.text_utils import normalize_text, clean_text_for_chunking
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/indexing.log")

class ChromaIndexer:
    def __init__(self, persist_directory: str = CHROMA_PERSIST_DIRECTORY):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.chunker = DocumentChunker()
        self.logger = logger
        
        # Crear o obtener colección
        self.collection = self._get_or_create_collection()
        
    def _get_or_create_collection(self):
        """Obtener colección existente o crear nueva"""
        try:
            # Intentar obtener colección existente
            collection = self.client.get_collection(CHROMA_COLLECTION_NAME)
            self.logger.info(f"Colección existente cargada: {CHROMA_COLLECTION_NAME}")
            return collection
        except:
            # Crear nueva colección
            collection = self.client.create_collection(
                name=CHROMA_COLLECTION_NAME,
                metadata={"description": "Documentos legales indexados"}
            )
            self.logger.info(f"Nueva colección creada: {CHROMA_COLLECTION_NAME}")
            return collection
    
    def _normalize_metadata(self, metadata: Dict) -> Dict:
        """Normalizar metadatos para búsqueda consistente"""
        normalized = {}
        
        # Filtrar valores None y convertir a strings válidos
        for key, value in metadata.items():
            if value is not None:
                if isinstance(value, (str, int, float, bool)):
                    normalized[key] = value
                else:
                    normalized[key] = str(value)
        
        # Normalizar nombres
        for key in ['demandante', 'demandado', 'entidad']:
            if key in normalized and normalized[key]:
                normalized[f"{key}_normalized"] = normalize_text(str(normalized[key]))
        
        # Normalizar fechas
        if 'fecha' in normalized and normalized['fecha']:
            try:
                # Intentar parsear fecha
                date_obj = pd.to_datetime(normalized['fecha'])
                normalized['fecha_normalized'] = date_obj.strftime('%Y-%m-%d')
            except:
                normalized['fecha_normalized'] = str(normalized['fecha'])
        
        # Normalizar cuantías
        if 'cuantia' in normalized and normalized['cuantia']:
            try:
                # Extraer solo números
                amount_str = str(normalized['cuantia'])
                amount_clean = ''.join(filter(str.isdigit, amount_str))
                normalized['cuantia_normalized'] = amount_clean
            except:
                normalized['cuantia_normalized'] = str(normalized['cuantia'])
        
        # Añadir timestamp de indexación
        normalized['indexed_at'] = datetime.now().isoformat()
        
        return normalized
    
    def _generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generar embeddings para una lista de textos"""
        try:
            embeddings = self.embedding_model.encode(texts)
            self.logger.info(f"Embeddings generados para {len(texts)} textos")
            return embeddings
        except Exception as e:
            self.logger.error(f"Error generando embeddings: {e}")
            raise
    
    def _prepare_chunks_for_indexing(self, chunks: List[Chunk]) -> Tuple[List[str], List[Dict], List[str]]:
        """Preparar chunks para indexación en ChromaDB"""
        texts = []
        metadatas = []
        ids = []
        
        for chunk in chunks:
            # Texto del chunk
            texts.append(chunk.text)
            
            # Metadatos normalizados
            normalized_metadata = self._normalize_metadata(chunk.metadata)
            metadatas.append(normalized_metadata)
            
            # ID único
            ids.append(chunk.id)
        
        return texts, metadatas, ids
    
    def index_document(self, document_id: str, text: str, metadata: Dict) -> Dict[str, any]:
        """
        Indexar un documento completo
        
        Args:
            document_id: ID único del documento
            text: Texto completo del documento
            metadata: Metadatos del documento
            
        Returns:
            Resultado de la indexación
        """
        self.logger.info(f"Iniciando indexación de documento: {document_id}")
        
        try:
            # Limpiar texto
            cleaned_text = clean_text_for_chunking(text)
            
            # Crear chunks
            chunks = self.chunker.chunk_document(cleaned_text, metadata)
            
            if not chunks:
                self.logger.warning(f"No se pudieron crear chunks para documento: {document_id}")
                return {"success": False, "error": "No chunks created"}
            
            # Validar chunks
            validation = self.chunker.validate_chunks(chunks)
            
            # Preparar datos para indexación
            texts, metadatas, ids = self._prepare_chunks_for_indexing(chunks)
            
            # Generar embeddings
            embeddings = self._generate_embeddings(texts)
            
            # Indexar en ChromaDB
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            result = {
                "success": True,
                "document_id": document_id,
                "chunks_indexed": len(chunks),
                "validation": validation,
                "indexed_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Documento indexado exitosamente: {document_id} ({len(chunks)} chunks)")
            return result
            
        except Exception as e:
            self.logger.error(f"Error indexando documento {document_id}: {e}")
            return {"success": False, "error": str(e), "document_id": document_id}
    
    def index_batch(self, documents: List[Dict]) -> Dict[str, any]:
        """
        Indexar un lote de documentos
        
        Args:
            documents: Lista de documentos con {'id', 'text', 'metadata'}
            
        Returns:
            Resultado del batch
        """
        self.logger.info(f"Iniciando indexación de lote: {len(documents)} documentos")
        
        results = []
        successful = 0
        failed = 0
        
        for doc in documents:
            result = self.index_document(
                document_id=doc['id'],
                text=doc['text'],
                metadata=doc['metadata']
            )
            
            results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
        
        batch_result = {
            "total_documents": len(documents),
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / len(documents)) * 100 if len(documents) > 0 else 0,
            "results": results
        }
        
        self.logger.info(f"Batch completado: {successful} exitosos, {failed} fallidos")
        return batch_result
    
    def load_and_index_from_csv(self) -> Dict[str, any]:
        """
        Cargar documentos desde CSV e indexarlos
        """
        self.logger.info("Iniciando carga desde CSV")
        
        try:
            # Cargar metadatos
            df = pd.read_csv(CSV_METADATA_PATH)
            self.logger.info(f"CSV cargado: {len(df)} documentos")
            
            documents_to_index = []
            
            for _, row in df.iterrows():
                # Extraer ID del documento desde la nueva estructura del CSV
                document_id = row['document_id']
                document_path = row['json_path']
                
                # Crear metadatos básicos
                metadata = {
                    'document_id': document_id,
                    'document_path': document_path,
                    'id': row['id']
                }
                
                # Parsear respuesta JSON si existe
                if 'metadata' in row and pd.notna(row['metadata']):
                    try:
                        response_data = json.loads(row['metadata'])
                        if isinstance(response_data, list):
                            # Si es una lista, tomar el primer elemento
                            response_data = response_data[0] if response_data else {}
                        
                        # Extraer información del demandante
                        if 'demandante' in response_data:
                            demandante = response_data['demandante']
                            if demandante:
                                # Nombres y apellidos
                                nombres = demandante.get('nombresPersonaDemandante', '')
                                apellidos = demandante.get('apellidosPersonaDemandante', '')
                                nombre_empresa = demandante.get('NombreEmpresaDemandante', '')
                                
                                if nombres and apellidos:
                                    metadata['demandante'] = f"{nombres} {apellidos}".strip()
                                elif nombre_empresa:
                                    metadata['demandante'] = nombre_empresa
                                else:
                                    metadata['demandante'] = 'No especificado'
                                
                                # Información adicional
                                metadata['tipo_identificacion'] = demandante.get('tipoIdentificacionDelDemandante', '')
                                metadata['numero_identificacion'] = demandante.get('numeroIdentificacionDelDemandante', '')
                                metadata['ciudad'] = demandante.get('ciudadDelDemandante', '')
                                metadata['departamento'] = demandante.get('DepartamentoDelDemandante', '')
                                metadata['correo'] = demandante.get('correoElectronicoDelDemandante', '')
                                metadata['direccion'] = demandante.get('direccionFisicaDelDemandante', '')
                                metadata['telefono'] = demandante.get('telefonoDelDemandante', '')
                        
                        # Extraer resoluciones si existen
                        if 'resolucionesRadicadosNumerosReferencias' in response_data:
                            metadata['resoluciones'] = response_data['resolucionesRadicadosNumerosReferencias']
                        
                        # Tipo de entidad
                        if 'TipoEntidadRemitente' in response_data:
                            metadata['tipo_entidad'] = response_data['TipoEntidadRemitente']
                            
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Error parseando JSON para documento {document_id}: {e}")
                
                # Cargar contenido JSON
                json_path = os.path.join(JSON_DOCS_PATH, f"{document_id}.pdf", "output.json")
                
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                        
                        # Extraer texto de todos los elementos del array 'texts'
                        texts_array = content.get('texts', [])
                        full_text = '\n'.join([t.get('text', '') for t in texts_array if t.get('text')])
                    
                    documents_to_index.append({
                        'id': document_id,
                        'text': full_text,
                        'metadata': metadata
                    })
                else:
                    self.logger.warning(f"Archivo JSON no encontrado: {json_path}")
            
            # Indexar documentos
            result = self.index_batch(documents_to_index)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error cargando desde CSV: {e}")
            return {"success": False, "error": str(e)}
    
    def get_collection_stats(self) -> Dict[str, any]:
        """Obtener estadísticas de la colección"""
        try:
            count = self.collection.count()
            
            # Obtener muestra de metadatos para análisis
            sample = self.collection.get(limit=10)
            
            stats = {
                "total_chunks": count,
                "collection_name": CHROMA_COLLECTION_NAME,
                "sample_metadata_keys": list(sample['metadatas'][0].keys()) if sample['metadatas'] else [],
                "last_updated": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}
    
    def search_similar(self, query: str, n_results: int = 10, where: Dict = None) -> Dict[str, any]:
        """
        Buscar chunks similares
        
        Args:
            query: Consulta de búsqueda
            n_results: Número de resultados
            where: Filtros de metadatos
            
        Returns:
            Resultados de búsqueda
        """
        try:
            # Generar embedding de la consulta
            query_embedding = self.embedding_model.encode([query])
            
            # Realizar búsqueda
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results,
                where=where
            )
            
            return {
                "query": query,
                "results": results,
                "total_found": len(results['ids'][0]) if results['ids'] else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda: {e}")
            return {"error": str(e), "query": query} 