"""
Módulo para indexación en ChromaDB con normalización universal de metadatos
"""
import chromadb
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Tuple, Any
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
                metadata={"description": "Documentos legales indexados con metadatos universales"}
            )
            self.logger.info(f"Nueva colección creada: {CHROMA_COLLECTION_NAME}")
            return collection
    
    def _normalize_metadata_universal(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza TODOS los metadatos de forma universal y consistente.
        Ahora primero aplana todos los metadatos recursivamente y luego normaliza los valores.
        :param metadata: Metadatos a normalizar
        :return: Metadatos normalizados universalmente
        """
        # 1. Aplanar todos los metadatos recursivamente
        flat_metadata = self._extract_all_metadata_recursive(metadata)
        normalized = {}
        # 2. Normalizar nombres y valores
        for key, value in flat_metadata.items():
            if value is not None:
                normalized_key = self._normalize_field_name(key)
                normalized_value = self._normalize_value_by_type(value)
                normalized[normalized_key] = normalized_value
        # Añadir metadatos de indexación
        normalized['indexed_at'] = datetime.now().isoformat()
        normalized['indexing_version'] = 'universal_v2'
        return normalized
    
    def _normalize_field_name(self, field_name: str) -> str:
        """
        Normaliza el nombre de un campo para consistencia.
        Método privado que encapsula la lógica de normalización de nombres.
        
        :param field_name: Nombre del campo a normalizar
        :return: Nombre normalizado
        """
        import unicodedata
        import re
        # Eliminar tildes primero
        nfkd = unicodedata.normalize('NFKD', field_name)
        no_tildes = ''.join([c for c in nfkd if not unicodedata.combining(c)])
        # Insertar guiones bajos antes de mayúsculas (camelCase)
        snake = re.sub(r'([a-z])([A-Z])', r'\1_\2', no_tildes)
        # Convertir a minúsculas
        snake = snake.lower()
        # Reemplazar caracteres no alfanuméricos por guion bajo
        snake = ''.join(c if c.isalnum() else '_' for c in snake)
        # Remover múltiples guiones bajos
        snake = re.sub(r'_+', '_', snake)
        # Remover guiones bajos al inicio y final
        snake = snake.strip('_')
        return snake
    
    def _normalize_value_by_type(self, value: Any) -> Any:
        """
        Normaliza un valor según su tipo de datos.
        Método privado que encapsula la lógica de normalización de valores.
        
        :param value: Valor a normalizar
        :return: Valor normalizado
        """
        if isinstance(value, str):
            return self._normalize_string_value(value)
        elif isinstance(value, (int, float)):
            return value
        elif isinstance(value, bool):
            return value
        elif isinstance(value, (list, dict)):
            return str(value)  # Convertir estructuras complejas a string
        else:
            return str(value)
    
    def _normalize_string_value(self, value: str) -> str:
        """
        Normaliza un valor string específicamente.
        Método privado que encapsula la lógica de normalización de strings.
        
        :param value: String a normalizar
        :return: String normalizado
        """
        if not value:
            return ""
        
        # Normalizar texto (remover tildes, convertir a minúsculas)
        normalized = normalize_text(value)
        
        # Limpiar espacios extra
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _normalize_metadata(self, metadata: Dict) -> Dict:
        """
        Normalizar metadatos para búsqueda consistente (método legacy para compatibilidad).
        Método privado que encapsula la lógica de normalización específica.
        
        :param metadata: Metadatos a normalizar
        :return: Metadatos normalizados
        """
        normalized = {}
        
        # Filtrar valores None y convertir a strings válidos
        for key, value in metadata.items():
            if value is not None:
                if isinstance(value, (str, int, float, bool)):
                    normalized[key] = value
                else:
                    normalized[key] = str(value)
        
        # Normalizar nombres específicos
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
        """Preparar chunks para indexación en ChromaDB con normalización universal"""
        texts = []
        metadatas = []
        ids = []
        
        for chunk in chunks:
            # Texto del chunk
            texts.append(chunk.text)
            
            # Metadatos normalizados universalmente
            normalized_metadata = self._normalize_metadata_universal(chunk.metadata)
            metadatas.append(normalized_metadata)
            
            # ID único
            ids.append(chunk.id)
        
        return texts, metadatas, ids
    
    def index_document(self, document_id: str, text: str, metadata: Dict) -> Dict[str, any]:
        """
        Indexar un documento completo con normalización universal
        
        Args:
            document_id: ID único del documento
            text: Texto completo del documento
            metadata: Metadatos del documento
            
        Returns:
            Resultado de la indexación
        """
        self.logger.info(f"Iniciando indexación universal de documento: {document_id}")
        
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
            
            # Preparar datos para indexación con normalización universal
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
                "metadata_fields_indexed": len(metadatas[0]) if metadatas else 0,
                "indexed_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Documento indexado exitosamente: {document_id} ({len(chunks)} chunks)")
            return result
            
        except Exception as e:
            self.logger.error(f"Error indexando documento {document_id}: {e}")
            return {"success": False, "error": str(e), "document_id": document_id}
    
    def index_batch(self, documents: List[Dict]) -> Dict[str, any]:
        """
        Indexar un lote de documentos con normalización universal
        
        Args:
            documents: Lista de documentos con {'id', 'text', 'metadata'}
            
        Returns:
            Resultado del batch
        """
        self.logger.info(f"Iniciando indexación universal de lote: {len(documents)} documentos")
        
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
    
    def _repair_and_parse_json(self, json_str: str) -> Optional[Dict[str, Any]]:
        """
        Repara y parsea JSON mal formateado.
        Método privado que encapsula la lógica de reparación de JSON.
        
        :param json_str: String JSON a reparar
        :return: Diccionario parseado o None si falla
        """
        try:
            # Intentar parseo directo
            return json.loads(json_str)
        except json.JSONDecodeError:
            try:
                # Intentar reparar JSON básico
                repaired_json = self._basic_json_repair(json_str)
                return json.loads(repaired_json)
            except Exception as e:
                self.logger.warning(f"Error reparando JSON: {e}")
                return None
    
    def _basic_json_repair(self, json_str: str) -> str:
        """
        Reparación básica de JSON mal formateado.
        Método privado que encapsula la lógica de reparación básica.
        
        :param json_str: String JSON a reparar
        :return: String JSON reparado
        """
        # Reparaciones básicas comunes
        repaired = json_str.strip()
        
        # Remover caracteres de control
        repaired = ''.join(char for char in repaired if ord(char) >= 32 or char in '\n\r\t')
        
        # Corregir comillas mal escapadas
        repaired = repaired.replace('\\"', '"').replace('""', '"')
        
        # Corregir comas finales antes de llaves de cierre
        import re
        repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)
        
        # Corregir comas finales antes de llaves de apertura
        repaired = re.sub(r',(\s*[{[])', r'\1', repaired)
        
        return repaired
    
    def _extract_all_metadata_recursive(self, json_data: Any, prefix: str = "") -> Dict[str, Any]:
        """
        Extrae recursivamente TODOS los metadatos de cualquier estructura JSON.
        Método privado que encapsula la lógica de extracción recursiva.
        Sigue SRP - solo extrae metadatos.
        
        :param json_data: Datos JSON a procesar
        :param prefix: Prefijo para nombres de campos anidados
        :return: Diccionario con todos los metadatos extraídos
        """
        metadata = {}
        
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                normalized_key = self._normalize_field_name(key)
                if prefix:
                    normalized_key = f"{prefix}_{normalized_key}"
                
                if isinstance(value, (dict, list)):
                    # Recursión para estructuras anidadas
                    nested_metadata = self._extract_all_metadata_recursive(value, normalized_key)
                    metadata.update(nested_metadata)
                else:
                    metadata[normalized_key] = value
        elif isinstance(json_data, list):
            for i, item in enumerate(json_data):
                nested_metadata = self._extract_all_metadata_recursive(item, f"{prefix}_{i}")
                metadata.update(nested_metadata)
        
        return metadata
    
    def load_and_index_from_csv(self) -> Dict[str, any]:
        """
        Cargar documentos desde CSV e indexarlos con normalización universal y filtrado de campos relevantes
        """
        self.logger.info("Iniciando carga universal desde CSV (solo campos relevantes <70% vacíos)")

        # Lista de campos seleccionados para indexar (menos del 70% de vacíos)
        campos_para_indexar = [
            'id', 'document_id', 'json_path',
            'demandante_NombreEmpresaDemandante', 'demandante_numeroIdentificacionDelDemandante',
            'demandante_ciudadDelDemandante', 'demandados_0_nombreApellidosRazonSocial',
            'demandante_tipoIdentificacionDelDemandante', 'demandados_0_identificacion',
            'demandados_0_tipoIdentificacion', 'resolucionesRadicadosNumerosReferencias_0',
            'entidad_actualizacionCuentaDepositoJudicial', 'entidad_esEntidadJudicial',
            'entidad_TipoEntidadRemitente', 'entidad_ciudadEntidadRemitente',
            'entidad_entidadRemitente', 'elDemandadoMencionaPorcentaje',
            'elDemandadoTieneResponsabilidadSolidaria', 'elDemandadoTieneIncidenteDeDesacato',
            'elDemandadoTieneReiteraciones', 'elDemandadoTieneSanciones',
            'elDocumentoEnElTextoIncluyeLaPalabraCongelado', 'elDocumentoEnElTextoIncluyeLaPalabraDivorcio',
            'elDocumentoEnElTextoIncluyeLaPalabraSeparacion', 'elDocumentoEnElTextoIncluyeLaPalabraProcesoDeAlimentos',
            'elDocumentoEnElTextoIncluyeLaPalabraFamilia', 'esSolicitudDeInformacion',
            'existeCorreoElectronicoDeSolicitud', 'amountInWordsDiffersFromNumericValue',
            'existeNuevaCuantia', 'elDocumentoCumpleConLasReglasDeIdentificacionRemanente',
            'isDaviviendaThePayer', 'esMencionadoEnElDocumentoComoEmpleadoOTrabajador',
            'estaFirmadoElDocumento', 'firmaManuscrita', 'esJuzgadoElRemitente',
            'afectaAlgunCDT', 'afectarLaCuentaDeNominaDelDemandado', 'tipoMedidaCautelar',
            'elDocumentoEsUnCorreoElectronico', 'esActualizacionDeEmbargo',
            'elDocumentoIncluyeSolicitudProductoDeudores', 'elUnicoProductoFinancierEnElDocumentoEsDerechosEconomicos',
            'enElDocumentoSoloMencionaElProductoCanonArrendamiento', 'entidad_enElDocumentoSeMencionaAlgunaActualizacionEnElCorreo',
            'cuantosOficiosDiferentesHayEnElDocumento', 'firmaElectronica', 'destinatariosOficio_0',
            'EstructuraDocumento_header_rangoPaginas', 'entidad_correoElectronicoEntidadRemitente'
        ]

        try:
            # Cargar metadatos desde el nuevo CSV aplanado
            df = pd.read_csv(CSV_METADATA_PATH)
            self.logger.info(f"CSV cargado: {len(df)} documentos")

            documents_to_index = []

            for _, row in df.iterrows():
                document_id = row['document_id']
                document_path = row['json_path']
                metadata = {k: row[k] for k in df.columns if k in campos_para_indexar and pd.notna(row[k]) and row[k] != ''}
                # Asegurar que los campos clave estén presentes
                metadata['document_id'] = document_id
                metadata['document_path'] = document_path
                metadata['id'] = row['id']

                # Cargar contenido JSON
                json_path = os.path.join(JSON_DOCS_PATH, f"{document_id}.pdf", "output.json")
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        content = json.load(f)
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
            self.logger.info(f"Indexación universal completada: {result['successful']} exitosos, {result['failed']} fallidos")
            return result
        except Exception as e:
            self.logger.error(f"Error en indexación universal: {e}")
            return {"success": False, "error": str(e)}
    
    def search_similar(self, query: str, n_results: int = 10, where: Optional[Dict] = None) -> Dict[str, any]:
        """
        Buscar documentos similares con soporte para metadatos universales
        
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
                "total_results": len(results.get('ids', [[]])[0]) if results.get('ids') else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda: {e}")
            return {"error": str(e)}
    
    def get_collection_stats(self) -> Dict[str, any]:
        """
        Obtener estadísticas de la colección
        
        Returns:
            Estadísticas de la colección
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": CHROMA_COLLECTION_NAME,
                "total_chunks": count,
                "indexing_version": "universal_v2"
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)} 