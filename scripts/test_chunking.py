#!/usr/bin/env python3
"""
Script para probar el sistema de chunking
Siguiendo las mejores prácticas de validación y logging
"""
import sys
import os
import json
import pandas as pd
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chunking.document_chunker import DocumentChunker
from src.utils.text_utils import clean_text_for_chunking, LegalEntityExtractor
from config.settings import CSV_METADATA_PATH, JSON_DOCS_PATH, CHUNK_SIZE, CHUNK_OVERLAP
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/chunking_test.log")

def verify_prerequisites():
    """Verificar que los prerrequisitos estén completos"""
    print("🔍 Verificando prerrequisitos...")
    
    # Verificar archivos de entrada
    if not os.path.exists(CSV_METADATA_PATH):
        raise FileNotFoundError(f"CSV de metadatos no encontrado: {CSV_METADATA_PATH}")
    
    if not os.path.exists(JSON_DOCS_PATH):
        raise FileNotFoundError(f"Directorio de documentos JSON no encontrado: {JSON_DOCS_PATH}")
    
    # Verificar configuración
    from config.settings import CHUNK_SIZE, CHUNK_OVERLAP, MAX_CHUNK_SIZE, MIN_CHUNK_SIZE
    assert CHUNK_SIZE <= MAX_CHUNK_SIZE, f"CHUNK_SIZE {CHUNK_SIZE} excede máximo {MAX_CHUNK_SIZE}"
    assert CHUNK_SIZE >= MIN_CHUNK_SIZE, f"CHUNK_SIZE {CHUNK_SIZE} es menor al mínimo {MIN_CHUNK_SIZE}"
    assert CHUNK_OVERLAP < CHUNK_SIZE, f"CHUNK_OVERLAP {CHUNK_OVERLAP} debe ser menor que CHUNK_SIZE {CHUNK_SIZE}"
    
    # Verificar que existen archivos JSON en el directorio target
    json_files = list(Path(JSON_DOCS_PATH).glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"No se encontraron archivos JSON en {JSON_DOCS_PATH}")
    
    print(f"✅ Prerrequisitos verificados correctamente")
    print(f"   - CSV de metadatos: {CSV_METADATA_PATH}")
    print(f"   - Directorio JSON: {JSON_DOCS_PATH}")
    print(f"   - Archivos JSON encontrados: {len(json_files)}")
    print(f"   - Configuración: CHUNK_SIZE={CHUNK_SIZE}, CHUNK_OVERLAP={CHUNK_OVERLAP}")

def load_test_document():
    """Cargar un documento de prueba"""
    try:
        # Cargar metadatos
        df = pd.read_csv(CSV_METADATA_PATH)
        
        if len(df) == 0:
            raise ValueError("El CSV de metadatos está vacío")
        
        # Tomar el primer documento
        doc_metadata = df.iloc[0].to_dict()
        filename = doc_metadata.get('filename', 'unknown')
        
        # Buscar el archivo JSON correspondiente
        json_path = os.path.join(JSON_DOCS_PATH, f"{filename}.json")
        
        if not os.path.exists(json_path):
            # Buscar cualquier archivo JSON disponible
            json_files = list(Path(JSON_DOCS_PATH).glob("*.json"))
            if json_files:
                json_path = str(json_files[0])
                # Extraer filename del path
                filename = Path(json_path).stem
                doc_metadata['filename'] = filename
            else:
                raise FileNotFoundError(f"No se encontró el archivo JSON: {json_path}")
        
        # Cargar contenido del JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            text = content.get('text', '')
        
        if not text.strip():
            raise ValueError(f"El archivo JSON {json_path} no contiene texto")
        
        return text, doc_metadata, json_path
        
    except Exception as e:
        logger.error(f"Error cargando documento de prueba: {e}")
        raise

def test_chunking_with_real_document():
    """Probar chunking con documento real"""
    print("\n🧪 Probando chunking con documento real...")
    
    # Cargar documento
    text, metadata, json_path = load_test_document()
    
    print(f"   - Documento: {metadata.get('filename', 'unknown')}")
    print(f"   - Tamaño del texto: {len(text)} caracteres")
    print(f"   - Tokens aproximados: {len(text.split())}")
    
    # Limpiar texto
    cleaned_text = clean_text_for_chunking(text)
    print(f"   - Texto limpio: {len(cleaned_text)} caracteres")
    
    # Crear chunker
    chunker = DocumentChunker()
    
    # Crear chunks
    chunks = chunker.chunk_document(cleaned_text, metadata)
    
    # Validar chunks
    validation = chunker.validate_chunks(chunks)
    
    # Mostrar resultados
    print(f"\n✅ Chunking completado:")
    print(f"   - Chunks creados: {len(chunks)}")
    print(f"   - Tasa de éxito: {validation['success_rate']:.1f}%")
    print(f"   - Chunks con overlap: {validation['chunks_with_overlap']}")
    print(f"   - Errores: {len(validation['errors'])}")
    print(f"   - Advertencias: {len(validation['warnings'])}")
    
    # Mostrar ejemplo de chunk
    if chunks:
        example_chunk = chunks[0]
        print(f"\n📄 Ejemplo de chunk:")
        print(f"   - ID: {example_chunk.id}")
        print(f"   - Posición: {example_chunk.position}/{example_chunk.total_chunks}")
        print(f"   - Tokens: {example_chunk.metadata['token_count']}")
        print(f"   - Tamaño: {example_chunk.metadata['chunk_size']} caracteres")
        print(f"   - Texto: {example_chunk.text[:100]}...")
    
    return chunks, validation

def test_entity_extraction(chunks):
    """Probar extracción de entidades en chunks"""
    print("\n🔍 Probando extracción de entidades...")
    
    extractor = LegalEntityExtractor()
    all_text = " ".join(chunk.text for chunk in chunks)
    
    entities = extractor.extract_legal_entities(all_text)
    
    print(f"✅ Entidades extraídas:")
    print(f"   - Nombres: {len(entities['names'])}")
    print(f"   - Fechas: {len(entities['dates'])}")
    print(f"   - Cantidades: {len(entities['amounts'])}")
    print(f"   - Términos legales: {len(entities['legal_terms'])}")
    print(f"   - Números de documento: {len(entities['document_numbers'])}")
    print(f"   - Tribunales: {len(entities['court_names'])}")
    
    # Mostrar ejemplos
    if entities['names']:
        print(f"   - Ejemplo nombres: {entities['names'][:3]}")
    if entities['dates']:
        print(f"   - Ejemplo fechas: {entities['dates'][:3]}")
    if entities['amounts']:
        print(f"   - Ejemplo cantidades: {entities['amounts'][:3]}")
    if entities['legal_terms']:
        print(f"   - Ejemplo términos: {entities['legal_terms'][:5]}")
    
    return entities

def test_chunk_quality_metrics(chunks):
    """Calcular métricas de calidad de chunks"""
    print("\n📊 Calculando métricas de calidad...")
    
    total_tokens = sum(chunk.metadata['token_count'] for chunk in chunks)
    avg_tokens = total_tokens / len(chunks) if chunks else 0
    
    # Verificar distribución de tamaños
    small_chunks = sum(1 for chunk in chunks if chunk.metadata['token_count'] < 50)
    medium_chunks = sum(1 for chunk in chunks if 50 <= chunk.metadata['token_count'] <= 200)
    large_chunks = sum(1 for chunk in chunks if chunk.metadata['token_count'] > 200)
    
    print(f"✅ Métricas de calidad:")
    print(f"   - Total de chunks: {len(chunks)}")
    print(f"   - Total de tokens: {total_tokens}")
    print(f"   - Promedio de tokens por chunk: {avg_tokens:.1f}")
    print(f"   - Chunks pequeños (<50 tokens): {small_chunks}")
    print(f"   - Chunks medianos (50-200 tokens): {medium_chunks}")
    print(f"   - Chunks grandes (>200 tokens): {large_chunks}")
    
    # Verificar overlap
    chunks_with_overlap = sum(1 for chunk in chunks if chunk.overlap_start is not None)
    overlap_percentage = (chunks_with_overlap / len(chunks)) * 100 if chunks else 0
    print(f"   - Chunks con overlap: {chunks_with_overlap} ({overlap_percentage:.1f}%)")
    
    return {
        'total_chunks': len(chunks),
        'total_tokens': total_tokens,
        'avg_tokens': avg_tokens,
        'small_chunks': small_chunks,
        'medium_chunks': medium_chunks,
        'large_chunks': large_chunks,
        'overlap_percentage': overlap_percentage
    }

def save_test_results(chunks, validation, entities, metrics):
    """Guardar resultados del test"""
    print("\n💾 Guardando resultados del test...")
    
    results = {
        'test_info': {
            'timestamp': pd.Timestamp.now().isoformat(),
            'chunk_size': CHUNK_SIZE,
            'chunk_overlap': CHUNK_OVERLAP,
            'total_chunks': len(chunks)
        },
        'validation': validation,
        'entities': entities,
        'metrics': metrics,
        'sample_chunks': [
            {
                'id': chunk.id,
                'position': chunk.position,
                'token_count': chunk.metadata['token_count'],
                'text_preview': chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text
            }
            for chunk in chunks[:5]  # Solo los primeros 5 chunks como muestra
        ]
    }
    
    # Guardar en logs
    output_path = "logs/chunking_test_results.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Resultados guardados en: {output_path}")

def main():
    """Función principal del script de prueba"""
    print("🧪 Iniciando pruebas del sistema de chunking...")
    
    try:
        # Verificar prerrequisitos
        verify_prerequisites()
        
        # Probar chunking con documento real
        chunks, validation = test_chunking_with_real_document()
        
        # Probar extracción de entidades
        entities = test_entity_extraction(chunks)
        
        # Calcular métricas de calidad
        metrics = test_chunk_quality_metrics(chunks)
        
        # Guardar resultados
        save_test_results(chunks, validation, entities, metrics)
        
        # Resumen final
        print(f"\n🎉 Pruebas completadas exitosamente!")
        print(f"   - Chunks creados: {len(chunks)}")
        print(f"   - Tasa de éxito: {validation['success_rate']:.1f}%")
        print(f"   - Entidades extraídas: {sum(len(v) for v in entities.values())}")
        
        if validation['success_rate'] >= 95:
            print("   ✅ Sistema de chunking funcionando correctamente")
        else:
            print("   ⚠️  Sistema de chunking necesita ajustes")
        
    except Exception as e:
        logger.error(f"Error durante las pruebas: {e}")
        print(f"❌ Error durante las pruebas: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 