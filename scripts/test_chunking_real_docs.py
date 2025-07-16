#!/usr/bin/env python3
"""
Script para analizar la efectividad del chunking con documentos reales
Busca recursivamente todos los output.json y extrae texto relevante para chunking
"""
import sys
import os
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chunking.document_chunker import DocumentChunker
from src.utils.text_utils import clean_text_for_chunking, LegalEntityExtractor, TextAnalyzer
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/chunking_real_docs.log")

class DocumentProcessor:
    """Clase para procesar documentos JSON de OCR"""
    
    def __init__(self):
        self.extractor = LegalEntityExtractor()
        self.analyzer = TextAnalyzer()
    
    def extract_text_from_json(self, json_path: str) -> Tuple[str, Dict]:
        """
        Extraer texto relevante de un archivo JSON de OCR
        
        Args:
            json_path: Ruta al archivo JSON
            
        Returns:
            Tuple con (texto_extraído, metadatos)
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extraer metadatos básicos
            metadata = {
                'document_id': Path(json_path).parent.name,
                'filename': data.get('name', 'unknown'),
                'schema_version': data.get('version', 'unknown'),
                'mimetype': data.get('origin', {}).get('mimetype', 'unknown')
            }
            
            # Extraer texto de todos los elementos de texto
            texts = []
            if 'texts' in data:
                for text_element in data['texts']:
                    if 'text' in text_element and text_element['text'].strip():
                        texts.append(text_element['text'].strip())
            
            # Combinar todos los textos
            full_text = '\n'.join(texts)
            
            return full_text, metadata
            
        except Exception as e:
            logger.error(f"Error procesando {json_path}: {e}")
            return "", {}
    
    def analyze_document_complexity(self, text: str) -> Dict:
        """Analizar complejidad del documento"""
        return self.analyzer.calculate_text_complexity(text)
    
    def extract_legal_entities(self, text: str) -> Dict:
        """Extraer entidades legales del texto"""
        return self.extractor.extract_legal_entities(text)

def find_all_json_files(target_dir: str) -> List[str]:
    """Encontrar todos los archivos output.json recursivamente"""
    json_files = []
    target_path = Path(target_dir)
    
    for json_file in target_path.rglob("output.json"):
        json_files.append(str(json_file))
    
    return json_files

def process_single_document(json_path: str, processor: DocumentProcessor, chunker: DocumentChunker) -> Dict:
    """Procesar un solo documento y generar métricas"""
    print(f"📄 Procesando: {Path(json_path).parent.name}")
    
    # Extraer texto y metadatos
    text, metadata = processor.extract_text_from_json(json_path)
    
    if not text.strip():
        return {
            'document_id': metadata.get('document_id', 'unknown'),
            'status': 'empty',
            'error': 'No se encontró texto en el documento'
        }
    
    # Limpiar texto
    cleaned_text = clean_text_for_chunking(text)
    
    # Analizar complejidad
    complexity = processor.analyze_document_complexity(cleaned_text)
    
    # Crear chunks
    chunks = chunker.chunk_document(cleaned_text, metadata)
    
    # Validar chunks
    validation = chunker.validate_chunks(chunks)
    
    # Extraer entidades
    entities = processor.extract_legal_entities(cleaned_text)
    
    # Calcular métricas de calidad
    total_tokens = sum(chunk.metadata['token_count'] for chunk in chunks)
    avg_tokens = total_tokens / len(chunks) if chunks else 0
    
    # Distribución de tamaños
    small_chunks = sum(1 for chunk in chunks if chunk.metadata['token_count'] < 50)
    medium_chunks = sum(1 for chunk in chunks if 50 <= chunk.metadata['token_count'] <= 200)
    large_chunks = sum(1 for chunk in chunks if chunk.metadata['token_count'] > 200)
    
    # Overlap
    chunks_with_overlap = sum(1 for chunk in chunks if chunk.overlap_start is not None)
    overlap_percentage = (chunks_with_overlap / len(chunks)) * 100 if chunks else 0
    
    return {
        'document_id': metadata.get('document_id', 'unknown'),
        'status': 'success',
        'text_length': len(text),
        'cleaned_length': len(cleaned_text),
        'total_chunks': len(chunks),
        'total_tokens': total_tokens,
        'avg_tokens_per_chunk': avg_tokens,
        'success_rate': validation['success_rate'],
        'chunks_within_size': validation['chunks_within_size'],
        'chunks_with_overlap': validation['chunks_with_overlap'],
        'errors': len(validation['errors']),
        'warnings': len(validation['warnings']),
        'small_chunks': small_chunks,
        'medium_chunks': medium_chunks,
        'large_chunks': large_chunks,
        'overlap_percentage': overlap_percentage,
        'complexity': complexity,
        'entities': entities,
        'sample_chunks': [
            {
                'id': chunk.id,
                'position': chunk.position,
                'token_count': chunk.metadata['token_count'],
                'text_preview': chunk.text[:150] + "..." if len(chunk.text) > 150 else chunk.text
            }
            for chunk in chunks[:3]  # Solo los primeros 3 chunks como muestra
        ]
    }

def generate_global_report(results: List[Dict]) -> Dict:
    """Generar reporte global de todos los documentos procesados"""
    
    successful_docs = [r for r in results if r['status'] == 'success']
    failed_docs = [r for r in results if r['status'] != 'success']
    
    if not successful_docs:
        return {
            'status': 'error',
            'message': 'No se procesaron documentos exitosamente'
        }
    
    # Métricas globales
    total_documents = len(results)
    successful_count = len(successful_docs)
    failed_count = len(failed_docs)
    
    # Promedios globales
    avg_success_rate = sum(d['success_rate'] for d in successful_docs) / successful_count
    avg_chunks_per_doc = sum(d['total_chunks'] for d in successful_docs) / successful_count
    avg_tokens_per_chunk = sum(d['avg_tokens_per_chunk'] for d in successful_docs) / successful_count
    
    # Distribución global de chunks
    total_small = sum(d['small_chunks'] for d in successful_docs)
    total_medium = sum(d['medium_chunks'] for d in successful_docs)
    total_large = sum(d['large_chunks'] for d in successful_docs)
    
    # Análisis de entidades
    all_entities = defaultdict(int)
    for doc in successful_docs:
        for entity_type, entities in doc['entities'].items():
            all_entities[entity_type] += len(entities)
    
    # Complejidad promedio
    avg_complexity = {
        'avg_sentence_length': sum(d['complexity']['avg_sentence_length'] for d in successful_docs) / successful_count,
        'avg_word_length': sum(d['complexity']['avg_word_length'] for d in successful_docs) / successful_count,
        'lexical_diversity': sum(d['complexity']['lexical_diversity'] for d in successful_docs) / successful_count,
        'total_words': sum(d['complexity']['total_words'] for d in successful_docs),
        'total_sentences': sum(d['complexity']['total_sentences'] for d in successful_docs)
    }
    
    return {
        'summary': {
            'total_documents': total_documents,
            'successful_documents': successful_count,
            'failed_documents': failed_count,
            'success_rate': (successful_count / total_documents) * 100
        },
        'chunking_metrics': {
            'avg_success_rate': avg_success_rate,
            'avg_chunks_per_document': avg_chunks_per_doc,
            'avg_tokens_per_chunk': avg_tokens_per_chunk,
            'total_chunks_created': sum(d['total_chunks'] for d in successful_docs),
            'chunks_within_size': sum(d['chunks_within_size'] for d in successful_docs),
            'chunks_with_overlap': sum(d['chunks_with_overlap'] for d in successful_docs)
        },
        'chunk_distribution': {
            'small_chunks': total_small,
            'medium_chunks': total_medium,
            'large_chunks': total_large,
            'total_chunks': total_small + total_medium + total_large
        },
        'entities_extracted': dict(all_entities),
        'complexity_analysis': avg_complexity,
        'failed_documents': [d['document_id'] for d in failed_docs],
        'sample_results': successful_docs[:5]  # Primeros 5 documentos como muestra
    }

def main():
    """Función principal del análisis de efectividad"""
    print("🔍 Analizando efectividad del chunking con documentos reales...")
    
    # Verificar que existe el directorio target
    target_dir = "target"
    if not os.path.exists(target_dir):
        print(f"❌ Directorio {target_dir} no encontrado")
        return
    
    # Encontrar todos los archivos JSON
    json_files = find_all_json_files(target_dir)
    
    if not json_files:
        print(f"❌ No se encontraron archivos output.json en {target_dir}")
        return
    
    print(f"✅ Encontrados {len(json_files)} documentos para procesar")
    
    # Inicializar componentes
    processor = DocumentProcessor()
    chunker = DocumentChunker()
    
    # Procesar todos los documentos
    results = []
    for i, json_path in enumerate(json_files, 1):
        print(f"\n📄 [{i}/{len(json_files)}] Procesando: {Path(json_path).parent.name}")
        
        try:
            result = process_single_document(json_path, processor, chunker)
            results.append(result)
            
            if result['status'] == 'success':
                print(f"   ✅ {result['total_chunks']} chunks creados, {result['success_rate']:.1f}% éxito")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error procesando {json_path}: {e}")
            results.append({
                'document_id': Path(json_path).parent.name,
                'status': 'error',
                'error': str(e)
            })
            print(f"   ❌ Error: {e}")
    
    # Generar reporte global
    print(f"\n📊 Generando reporte global...")
    global_report = generate_global_report(results)
    
    # Guardar resultados
    output_path = "logs/chunking_effectiveness_report.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(global_report, f, indent=2, ensure_ascii=False)
    
    # Mostrar resumen
    print(f"\n🎉 Análisis completado!")
    print(f"📄 Documentos procesados: {global_report['summary']['total_documents']}")
    print(f"✅ Documentos exitosos: {global_report['summary']['successful_documents']}")
    print(f"❌ Documentos fallidos: {global_report['summary']['failed_documents']}")
    print(f"📊 Tasa de éxito promedio: {global_report['chunking_metrics']['avg_success_rate']:.1f}%")
    print(f"🔢 Chunks creados en total: {global_report['chunking_metrics']['total_chunks_created']}")
    print(f"📈 Promedio de chunks por documento: {global_report['chunking_metrics']['avg_chunks_per_document']:.1f}")
    print(f"📝 Promedio de tokens por chunk: {global_report['chunking_metrics']['avg_tokens_per_chunk']:.1f}")
    
    # Distribución de chunks
    dist = global_report['chunk_distribution']
    print(f"📊 Distribución de chunks:")
    print(f"   - Pequeños (<50 tokens): {dist['small_chunks']} ({dist['small_chunks']/dist['total_chunks']*100:.1f}%)")
    print(f"   - Medianos (50-200 tokens): {dist['medium_chunks']} ({dist['medium_chunks']/dist['total_chunks']*100:.1f}%)")
    print(f"   - Grandes (>200 tokens): {dist['large_chunks']} ({dist['large_chunks']/dist['total_chunks']*100:.1f}%)")
    
    # Entidades extraídas
    entities = global_report['entities_extracted']
    print(f"🔍 Entidades extraídas:")
    for entity_type, count in entities.items():
        print(f"   - {entity_type}: {count}")
    
    print(f"\n💾 Reporte detallado guardado en: {output_path}")
    
    # Evaluación de efectividad
    success_rate = global_report['chunking_metrics']['avg_success_rate']
    if success_rate >= 95:
        print("✅ Sistema de chunking funcionando EXCELENTE")
    elif success_rate >= 85:
        print("✅ Sistema de chunking funcionando BIEN")
    elif success_rate >= 70:
        print("⚠️  Sistema de chunking necesita MEJORAS")
    else:
        print("❌ Sistema de chunking necesita REVISIÓN URGENTE")

if __name__ == "__main__":
    main() 