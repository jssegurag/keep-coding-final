# 03. Implementación del Sistema de Chunking - MVP RAG

## 🎯 Objetivo
Implementar el sistema de chunking con fallback recursivo para dividir documentos legales en fragmentos manejables, preservando la estructura semántica y los metadatos, siguiendo los principios de arquitectura limpia establecidos.

## 📋 Tareas a Ejecutar

### Verificación de Prerrequisitos
Antes de implementar el chunking, verificar que los pasos anteriores estén completos:

#### ✅ Pasos Completados:
- [x] **Paso 1**: Entorno configurado (`config/settings.py`, `requirements.txt`)
- [x] **Paso 2**: Validación de embeddings completada
- [x] **Datos de entrada**: `src/resources/metadata/studio_results_20250715_2237.csv` disponible
- [x] **Estructura de carpetas**: `src/chunking/`, `src/utils/`, `tests/unit/` creadas

#### 🔍 Verificación Automática:
```bash
# Verificar configuración
python -c "from config.settings import CHUNK_SIZE, CHUNK_OVERLAP; print(f'✅ Configuración: CHUNK_SIZE={CHUNK_SIZE}, CHUNK_OVERLAP={CHUNK_OVERLAP}')"

# Verificar datos de entrada
ls -la src/resources/metadata/studio_results_20250715_2237.csv

# Verificar estructura
ls -la src/chunking/ src/utils/ tests/unit/

# Verificar logs del paso 2
ls -la logs/embedding_validation_results.json
```

### Checklist para el Paso 3
**Antes de Implementar:**
- [ ] Verificar configuración de chunking en `config/settings.py`
- [ ] Validar que los datos de entrada existan y sean accesibles
- [ ] Confirmar que las dependencias estén instaladas
- [ ] Revisar logs del paso 2 para entender patrones de documentos

**Durante la Implementación:**
- [ ] Implementar chunking adaptativo con fallback recursivo
- [ ] Preservar contexto jurídico y metadatos
- [ ] Manejar casos edge (textos muy cortos/largos)
- [ ] Validar calidad de chunks con métricas establecidas

**Después de Implementar:**
- [ ] Validar que embeddings funcionen mejor con nuevos chunks
- [ ] Medir mejora en métricas de validación del paso 2
- [ ] Ajustar parámetros si es necesario
- [ ] Documentar optimizaciones y lecciones aprendidas

### 1. Crear Módulo de Chunking
Crear `src/chunking/document_chunker.py` siguiendo los principios SOLID establecidos:
```python
"""
Módulo para chunking de documentos legales con fallback recursivo
"""
import re
import uuid
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP, MAX_CHUNK_SIZE, MIN_CHUNK_SIZE
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/chunking.log")

@dataclass
class Chunk:
    """Representa un chunk de documento"""
    id: str
    text: str
    position: int
    total_chunks: int
    metadata: Dict
    start_token: int
    end_token: int
    overlap_start: Optional[int] = None
    overlap_end: Optional[int] = None

class DocumentChunker:
    def __init__(self, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
        """
        Inicializar chunker con validación de parámetros.
        
        Args:
            chunk_size: Tamaño máximo de chunk en tokens
            overlap: Overlap entre chunks consecutivos
        """
        # Validar parámetros según configuración
        if chunk_size > MAX_CHUNK_SIZE:
            raise ValueError(f"Chunk size {chunk_size} excede máximo {MAX_CHUNK_SIZE}")
        if chunk_size < MIN_CHUNK_SIZE:
            raise ValueError(f"Chunk size {chunk_size} es menor al mínimo {MIN_CHUNK_SIZE}")
        if overlap >= chunk_size:
            raise ValueError(f"Overlap {overlap} debe ser menor que chunk_size {chunk_size}")
            
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.logger = logger
        
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenizar texto en palabras/palabras"""
        # Tokenización simple por espacios y puntuación
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    def _count_tokens(self, text: str) -> int:
        """Contar tokens en un texto"""
        return len(self._tokenize_text(text))
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """Dividir texto por oraciones"""
        # Patrones para detectar fin de oración
        sentence_patterns = [
            r'[.!?]+[\s\n]*',  # Punto, exclamación, interrogación
            r'[.!?]+["\']+[\s\n]*',  # Con comillas
            r'\n\s*\n',  # Párrafos
        ]
        
        # Combinar patrones
        pattern = '|'.join(sentence_patterns)
        sentences = re.split(pattern, text)
        
        # Limpiar oraciones vacías
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Dividir texto por párrafos"""
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _create_chunk_with_metadata(self, 
                                  text: str, 
                                  position: int, 
                                  total_chunks: int,
                                  base_metadata: Dict,
                                  start_token: int,
                                  end_token: int) -> Chunk:
        """Crear un chunk con metadatos completos"""
        chunk_id = f"{base_metadata.get('document_id', 'doc')}_chunk_{position}"
        
        # Copiar metadatos base y añadir información del chunk
        chunk_metadata = base_metadata.copy()
        chunk_metadata.update({
            'chunk_id': chunk_id,
            'chunk_position': position,
            'total_chunks': total_chunks,
            'start_token': start_token,
            'end_token': end_token,
            'chunk_size': len(text),
            'token_count': self._count_tokens(text)
        })
        
        return Chunk(
            id=chunk_id,
            text=text,
            position=position,
            total_chunks=total_chunks,
            metadata=chunk_metadata,
            start_token=start_token,
            end_token=end_token
        )
    
    def _apply_fallback_recursive(self, text: str, max_size: int) -> List[str]:
        """Aplicar fallback recursivo para textos que exceden el tamaño máximo"""
        if self._count_tokens(text) <= max_size:
            return [text]
        
        # Intentar dividir por párrafos primero
        paragraphs = self._split_by_paragraphs(text)
        if len(paragraphs) > 1:
            result = []
            for paragraph in paragraphs:
                result.extend(self._apply_fallback_recursive(paragraph, max_size))
            return result
        
        # Si no hay párrafos, dividir por oraciones
        sentences = self._split_by_sentences(text)
        if len(sentences) > 1:
            result = []
            current_chunk = ""
            
            for sentence in sentences:
                test_chunk = current_chunk + " " + sentence if current_chunk else sentence
                
                if self._count_tokens(test_chunk) <= max_size:
                    current_chunk = test_chunk
                else:
                    if current_chunk:
                        result.append(current_chunk.strip())
                    current_chunk = sentence
            
            if current_chunk:
                result.append(current_chunk.strip())
            
            return result
        
        # Si no se puede dividir más, truncar (último recurso)
        self.logger.warning(f"Texto no se puede dividir más, truncando: {text[:100]}...")
        return [text[:max_size * 4]]  # Aproximación de tokens a caracteres
    
    def chunk_document(self, text: str, metadata: Dict) -> List[Chunk]:
        """
        Dividir documento en chunks con fallback recursivo
        
        Args:
            text: Texto completo del documento
            metadata: Metadatos del documento
            
        Returns:
            Lista de chunks con metadatos
        """
        self.logger.info(f"Iniciando chunking de documento: {metadata.get('document_id', 'unknown')}")
        
        if not text.strip():
            self.logger.warning("Texto vacío, retornando lista vacía")
            return []
        
        # Intentar dividir por párrafos primero
        paragraphs = self._split_by_paragraphs(text)
        chunks = []
        current_position = 1
        total_tokens = self._count_tokens(text)
        
        for paragraph in paragraphs:
            # Verificar si el párrafo excede el tamaño máximo
            if self._count_tokens(paragraph) > self.chunk_size:
                # Aplicar fallback recursivo
                sub_chunks = self._apply_fallback_recursive(paragraph, self.chunk_size)
                
                for i, sub_chunk in enumerate(sub_chunks):
                    chunk = self._create_chunk_with_metadata(
                        text=sub_chunk,
                        position=current_position,
                        total_chunks=len(sub_chunks),  # Se actualizará al final
                        base_metadata=metadata,
                        start_token=0,  # Se calculará después
                        end_token=0
                    )
                    chunks.append(chunk)
                    current_position += 1
            else:
                # Párrafo normal, crear chunk
                chunk = self._create_chunk_with_metadata(
                    text=paragraph,
                    position=current_position,
                    total_chunks=1,  # Se actualizará al final
                    base_metadata=metadata,
                    start_token=0,
                    end_token=0
                )
                chunks.append(chunk)
                current_position += 1
        
        # Aplicar overlap entre chunks consecutivos
        chunks_with_overlap = self._apply_overlap(chunks)
        
        # Actualizar total_chunks y calcular posiciones de tokens
        total_chunks = len(chunks_with_overlap)
        for i, chunk in enumerate(chunks_with_overlap):
            chunk.total_chunks = total_chunks
            chunk.position = i + 1
            
            # Calcular posiciones de tokens (aproximado)
            chunk.start_token = i * self.chunk_size
            chunk.end_token = min((i + 1) * self.chunk_size, total_tokens)
        
        self.logger.info(f"Chunking completado: {len(chunks_with_overlap)} chunks creados")
        return chunks_with_overlap
    
    def _apply_overlap(self, chunks: List[Chunk]) -> List[Chunk]:
        """Aplicar overlap entre chunks consecutivos"""
        if len(chunks) <= 1:
            return chunks
        
        chunks_with_overlap = []
        
        for i, chunk in enumerate(chunks):
            if i > 0:
                # Añadir overlap del chunk anterior
                prev_chunk = chunks[i - 1]
                overlap_text = prev_chunk.text[-self.overlap:] if len(prev_chunk.text) > self.overlap else prev_chunk.text
                
                # Combinar con el chunk actual
                combined_text = overlap_text + " " + chunk.text
                
                # Crear nuevo chunk con overlap
                new_chunk = self._create_chunk_with_metadata(
                    text=combined_text,
                    position=chunk.position,
                    total_chunks=chunk.total_chunks,
                    base_metadata=chunk.metadata,
                    start_token=chunk.start_token,
                    end_token=chunk.end_token,
                    overlap_start=len(overlap_text),
                    overlap_end=len(overlap_text) + len(chunk.text)
                )
                
                chunks_with_overlap.append(new_chunk)
            else:
                chunks_with_overlap.append(chunk)
        
        return chunks_with_overlap
    
    def validate_chunks(self, chunks: List[Chunk]) -> Dict[str, any]:
        """Validar que los chunks cumplen con los criterios"""
        validation_results = {
            'total_chunks': len(chunks),
            'chunks_within_size': 0,
            'chunks_with_overlap': 0,
            'errors': []
        }
        
        for i, chunk in enumerate(chunks):
            # Verificar tamaño
            token_count = self._count_tokens(chunk.text)
            if token_count <= self.chunk_size:
                validation_results['chunks_within_size'] += 1
            else:
                validation_results['errors'].append(
                    f"Chunk {i+1} excede tamaño máximo: {token_count} > {self.chunk_size}"
                )
            
            # Verificar overlap
            if i > 0 and chunk.overlap_start is not None:
                validation_results['chunks_with_overlap'] += 1
        
        validation_results['success_rate'] = (
            validation_results['chunks_within_size'] / len(chunks) * 100
        )
        
        return validation_results
```

### 2. Crear Utilidades de Texto
Crear `src/utils/text_utils.py` para procesamiento de texto legal:
```python
"""
Utilidades para procesamiento de texto legal
"""
import re
import unicodedata
from typing import List, Dict

def normalize_text(text: str) -> str:
    """Normalizar texto para búsqueda"""
    # Convertir a minúsculas
    text = text.lower()
    
    # Remover acentos
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if not unicodedata.combining(c)
    )
    
    # Remover caracteres especiales
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Normalizar espacios
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_legal_entities(text: str) -> Dict[str, List[str]]:
    """Extraer entidades legales del texto"""
    entities = {
        'names': [],
        'dates': [],
        'amounts': [],
        'legal_terms': []
    }
    
    # Patrones para nombres (mayúsculas seguidas de espacios)
    name_pattern = r'\b[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+\b'
    names = re.findall(name_pattern, text)
    entities['names'] = [n.strip() for n in names if len(n.strip()) > 2]
    
    # Patrones para fechas
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{4}',  # DD/MM/YYYY
        r'\d{4}-\d{1,2}-\d{1,2}',  # YYYY-MM-DD
        r'\d{1,2}\s+de\s+[a-z]+\s+de\s+\d{4}'  # DD de MES de YYYY
    ]
    
    for pattern in date_patterns:
        dates = re.findall(pattern, text)
        entities['dates'].extend(dates)
    
    # Patrones para cantidades monetarias
    amount_pattern = r'\$?\d{1,3}(?:\.\d{3})*(?:,\d{2})?'
    amounts = re.findall(amount_pattern, text)
    entities['amounts'] = amounts
    
    # Términos jurídicos comunes
    legal_terms = [
        'demandante', 'demandado', 'embargo', 'medida cautelar',
        'sentencia', 'recurso', 'apelación', 'fundamento',
        'hechos', 'pruebas', 'testigo', 'abogado', 'juez'
    ]
    
    for term in legal_terms:
        if term in text.lower():
            entities['legal_terms'].append(term)
    
    return entities

def clean_text_for_chunking(text: str) -> str:
    """Limpiar texto para chunking"""
    # Remover caracteres de control
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Normalizar saltos de línea
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\r', '\n', text)
    
    # Remover espacios múltiples
    text = re.sub(r' +', ' ', text)
    
    # Remover líneas vacías múltiples
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
    return text.strip()
```

### 3. Crear Tests Unitarios
Crear `tests/unit/test_chunking.py` siguiendo el patrón establecido en `test_configuration.py`:
```python
"""
Tests unitarios para el sistema de chunking
"""
import pytest
from src.chunking.document_chunker import DocumentChunker, Chunk
from src.utils.text_utils import normalize_text, extract_legal_entities, clean_text_for_chunking

class TestDocumentChunker:
    
    def setup_method(self):
        """Configurar antes de cada test"""
        self.chunker = DocumentChunker(chunk_size=100, overlap=20)
    
    def test_tokenize_text(self):
        """Test de tokenización de texto"""
        text = "Este es un texto de prueba con palabras."
        tokens = self.chunker._tokenize_text(text)
        
        expected = ['este', 'es', 'un', 'texto', 'de', 'prueba', 'con', 'palabras']
        assert tokens == expected
    
    def test_count_tokens(self):
        """Test de conteo de tokens"""
        text = "Este es un texto de prueba."
        count = self.chunker._count_tokens(text)
        assert count == 6  # este, es, un, texto, de, prueba
    
    def test_split_by_sentences(self):
        """Test de división por oraciones"""
        text = "Primera oración. Segunda oración! Tercera oración?"
        sentences = self.chunker._split_by_sentences(text)
        
        assert len(sentences) == 3
        assert "Primera oración" in sentences[0]
        assert "Segunda oración" in sentences[1]
        assert "Tercera oración" in sentences[2]
    
    def test_split_by_paragraphs(self):
        """Test de división por párrafos"""
        text = "Párrafo uno.\n\nPárrafo dos.\n\nPárrafo tres."
        paragraphs = self.chunker._split_by_paragraphs(text)
        
        assert len(paragraphs) == 3
        assert "Párrafo uno" in paragraphs[0]
        assert "Párrafo dos" in paragraphs[1]
        assert "Párrafo tres" in paragraphs[2]
    
    def test_fallback_recursive(self):
        """Test de fallback recursivo"""
        # Texto que excede el tamaño máximo
        long_text = "Esta es una oración muy larga " * 50
        
        chunks = self.chunker._apply_fallback_recursive(long_text, 50)
        
        assert len(chunks) > 1
        for chunk in chunks:
            assert self.chunker._count_tokens(chunk) <= 50
    
    def test_chunk_document_simple(self):
        """Test de chunking de documento simple"""
        text = "Párrafo uno. " * 10 + "\n\n" + "Párrafo dos. " * 10
        metadata = {'document_id': 'test_doc', 'demandante': 'Juan Pérez'}
        
        chunks = self.chunker.chunk_document(text, metadata)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
        assert all(chunk.metadata['document_id'] == 'test_doc' for chunk in chunks)
    
    def test_chunk_document_large(self):
        """Test de chunking de documento grande"""
        # Crear texto que exceda el tamaño máximo
        text = "Esta es una oración de prueba. " * 100
        metadata = {'document_id': 'large_doc'}
        
        chunks = self.chunker.chunk_document(text, metadata)
        
        assert len(chunks) > 1
        for chunk in chunks:
            assert self.chunker._count_tokens(chunk.text) <= self.chunker.chunk_size
    
    def test_validate_chunks(self):
        """Test de validación de chunks"""
        # Crear chunks de prueba
        chunks = [
            Chunk(
                id="test_1",
                text="Texto corto",
                position=1,
                total_chunks=2,
                metadata={'document_id': 'test'},
                start_token=0,
                end_token=10
            ),
            Chunk(
                id="test_2",
                text="Otro texto corto",
                position=2,
                total_chunks=2,
                metadata={'document_id': 'test'},
                start_token=10,
                end_token=20
            )
        ]
        
        validation = self.chunker.validate_chunks(chunks)
        
        assert validation['total_chunks'] == 2
        assert validation['chunks_within_size'] == 2
        assert validation['success_rate'] == 100.0

class TestTextUtils:
    
    def test_normalize_text(self):
        """Test de normalización de texto"""
        text = "NÚRY WILLÉLMA ROMERO GÓMEZ"
        normalized = normalize_text(text)
        
        assert normalized == "nury willelma romero gomez"
        assert "á" not in normalized
        assert "é" not in normalized
    
    def test_extract_legal_entities(self):
        """Test de extracción de entidades legales"""
        text = "El demandante JUAN PÉREZ solicita embargo por $1,000,000 el 15/01/2024"
        entities = extract_legal_entities(text)
        
        assert "JUAN PÉREZ" in entities['names']
        assert "$1,000,000" in entities['amounts']
        assert "15/01/2024" in entities['dates']
        assert "demandante" in entities['legal_terms']
        assert "embargo" in entities['legal_terms']
    
    def test_clean_text_for_chunking(self):
        """Test de limpieza de texto para chunking"""
        text = "Texto  con   espacios   múltiples.\r\n\r\n\r\nLíneas vacías."
        cleaned = clean_text_for_chunking(text)
        
        assert "   " not in cleaned
        assert "\r\n\r\n\r\n" not in cleaned
        assert "\n\n" in cleaned
```

### 4. Crear Script de Prueba
Crear `scripts/test_chunking.py` con validación de prerrequisitos:
```python
#!/usr/bin/env python3
"""
Script para probar el sistema de chunking
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chunking.document_chunker import DocumentChunker
from src.utils.text_utils import clean_text_for_chunking
from config.settings import CSV_METADATA_PATH, JSON_DOCS_PATH
import pandas as pd

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
    
    print("✅ Prerrequisitos verificados correctamente")

def main():
    print("🧪 Probando sistema de chunking...")
    
    # Verificar prerrequisitos
    verify_prerequisites()
    
    # Crear chunker
    chunker = DocumentChunker()
    
    try:
        # Cargar metadatos
        df = pd.read_csv(CSV_METADATA_PATH)
        
        # Probar con el primer documento
        if len(df) > 0:
            doc_metadata = df.iloc[0].to_dict()
            
            # Cargar contenido
            json_path = os.path.join(JSON_DOCS_PATH, f"{doc_metadata['filename']}.json")
            
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    text = content.get('text', '')
                
                # Limpiar texto
                cleaned_text = clean_text_for_chunking(text)
                
                # Crear chunks
                chunks = chunker.chunk_document(cleaned_text, doc_metadata)
                
                # Validar chunks
                validation = chunker.validate_chunks(chunks)
                
                print(f"✅ Chunking completado:")
                print(f"   - Documento: {doc_metadata['filename']}")
                print(f"   - Chunks creados: {len(chunks)}")
                print(f"   - Tasa de éxito: {validation['success_rate']:.1f}%")
                print(f"   - Chunks con overlap: {validation['chunks_with_overlap']}")
                
                # Mostrar ejemplo de chunk
                if chunks:
                    example_chunk = chunks[0]
                    print(f"\n📄 Ejemplo de chunk:")
                    print(f"   - ID: {example_chunk.id}")
                    print(f"   - Posición: {example_chunk.position}/{example_chunk.total_chunks}")
                    print(f"   - Tokens: {example_chunk.metadata['token_count']}")
                    print(f"   - Texto: {example_chunk.text[:100]}...")
                
            else:
                print(f"❌ No se encontró el archivo JSON: {json_path}")
        else:
            print("❌ No hay documentos en el CSV")
            
    except Exception as e:
        print(f"❌ Error durante el testing: {e}")

if __name__ == "__main__":
    main()
```

## ✅ Criterios de Éxito
- [ ] **Prerrequisitos verificados**: Datos de entrada y configuración válidos
- [ ] **Módulo `DocumentChunker` implementado**: Con validación de parámetros
- [ ] **Fallback recursivo funcionando**: Para textos que exceden el tamaño máximo
- [ ] **Overlap aplicado**: Entre chunks consecutivos según configuración
- [ ] **Metadatos preservados**: Completos y consistentes en cada chunk
- [ ] **Tests unitarios pasando**: Con cobertura > 80%
- [ ] **Validación de chunks funcionando**: Con métricas de calidad
- [ ] **Utilidades de texto implementadas**: Para procesamiento legal
- [ ] **Integración con paso 2**: Chunks compatibles con validación de embeddings

## 🔍 Verificación
Ejecutar los siguientes comandos en orden:

```bash
# 1. Verificar prerrequisitos
python -c "from config.settings import *; print('✅ Configuración cargada correctamente')"

# 2. Verificar datos de entrada
ls -la src/resources/metadata/studio_results_20250715_2237.csv
ls -la target/

# 3. Ejecutar tests unitarios
python -m pytest tests/unit/test_chunking.py -v

# 4. Probar chunking con validación
python scripts/test_chunking.py

# 5. Verificar logs
cat logs/chunking.log

# 6. Validar integración con paso 2
python -c "from src.chunking.document_chunker import DocumentChunker; print('✅ Chunking integrado correctamente')"
```

## 📊 Métricas de Calidad
- **Tasa de éxito**: > 95% de chunks dentro del tamaño máximo configurado
- **Overlap**: Todos los chunks consecutivos deben tener overlap según `CHUNK_OVERLAP`
- **Metadatos**: Todos los chunks deben preservar metadatos completos y consistentes
- **Fallback**: Textos grandes deben dividirse sin pérdida de información
- **Validación**: Chunks deben ser compatibles con el modelo de embeddings del paso 2

## 🔗 Integración con Otros Pasos

### Con Paso 1 (Configuración):
- Usa configuración centralizada de `config/settings.py`
- Sigue estructura de carpetas establecida
- Utiliza logging consistente con `src/utils/logger.py`

### Con Paso 2 (Validación de Embeddings):
- Chunks generados deben ser compatibles con `paraphrase-multilingual-mpnet-base-v2`
- Usar los mismos documentos de prueba del paso 2
- Validar que embeddings funcionen mejor con chunks optimizados

### Con Paso 4 (Indexación):
- Preparar chunks para indexación en ChromaDB
- Preservar metadatos para filtrado híbrido
- Mantener trazabilidad documento-chunk

## 📝 Notas Importantes
- El chunking debe preservar la estructura semántica de los documentos legales
- El fallback recursivo es crítico para documentos con párrafos largos
- Los metadatos deben ser completos y consistentes
- La validación debe ejecutarse después de cada chunking
- **Verificar prerrequisitos antes de implementar** para evitar errores

## 🛠️ Troubleshooting

### Problemas Comunes y Soluciones

#### Error: "CSV de metadatos no encontrado"
```bash
# Solución: Verificar que el archivo existe
ls -la src/resources/metadata/studio_results_20250715_2237.csv
# Si no existe, copiar desde la ubicación correcta
```

#### Error: "Directorio de documentos JSON no encontrado"
```bash
# Solución: Crear directorio target si no existe
mkdir -p target/
# Verificar que contiene archivos JSON de documentos
ls -la target/*.json
```

#### Error: "CHUNK_SIZE excede máximo"
```bash
# Solución: Verificar configuración en config/settings.py
python -c "from config.settings import CHUNK_SIZE, MAX_CHUNK_SIZE; print(f'CHUNK_SIZE={CHUNK_SIZE}, MAX_CHUNK_SIZE={MAX_CHUNK_SIZE}')"
# Ajustar CHUNK_SIZE si es necesario
```

#### Error: "No se pudieron crear chunks"
```bash
# Solución: Verificar que el texto no esté vacío
# Revisar logs para más detalles
cat logs/chunking.log
```

#### Tests fallando
```bash
# Solución: Verificar que todas las dependencias estén instaladas
pip install -r requirements.txt
# Ejecutar tests con más detalle
python -m pytest tests/unit/test_chunking.py -v -s
``` 