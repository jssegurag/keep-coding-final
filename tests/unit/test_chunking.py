"""
Tests unitarios para el sistema de chunking
Siguiendo principios de testing y cobertura completa
"""
import pytest
import tempfile
import json
from unittest.mock import Mock, patch

from src.chunking.document_chunker import (
    DocumentChunker, 
    Chunk, 
    Tokenizer, 
    ChunkValidator,
    IChunkingStrategy,
    SentenceChunkingStrategy,
    ParagraphChunkingStrategy
)
from src.utils.text_utils import (
    normalize_text, 
    extract_legal_entities, 
    clean_text_for_chunking,
    TextNormalizer,
    LegalEntityExtractor,
    TextAnalyzer,
    LegalEntity
)

class TestTokenizer:
    """Tests para la clase Tokenizer"""
    
    def test_tokenize_text(self):
        """Test de tokenización de texto"""
        text = "Este es un texto de prueba con palabras."
        tokens = Tokenizer.tokenize_text(text)
        
        expected = ['este', 'es', 'un', 'texto', 'de', 'prueba', 'con', 'palabras']
        assert tokens == expected
    
    def test_tokenize_text_with_special_chars(self):
        """Test de tokenización con caracteres especiales"""
        text = "¡Hola! ¿Cómo estás? (Bien, gracias)."
        tokens = Tokenizer.tokenize_text(text)
        
        expected = ['hola', 'cómo', 'estás', 'bien', 'gracias']
        assert tokens == expected
    
    def test_count_tokens(self):
        """Test de conteo de tokens"""
        text = "Este es un texto de prueba."
        count = Tokenizer.count_tokens(text)
        assert count == 6  # este, es, un, texto, de, prueba
    
    def test_count_tokens_empty(self):
        """Test de conteo de tokens en texto vacío"""
        count = Tokenizer.count_tokens("")
        assert count == 0
    
    def test_count_tokens_only_special_chars(self):
        """Test de conteo de tokens con solo caracteres especiales"""
        count = Tokenizer.count_tokens("!@#$%^&*()")
        assert count == 0

class TestChunkingStrategies:
    """Tests para las estrategias de chunking"""
    
    def test_sentence_chunking_strategy(self):
        """Test de estrategia de chunking por oraciones"""
        strategy = SentenceChunkingStrategy()
        text = "Primera oración. Segunda oración! Tercera oración?"
        sentences = strategy.split_text(text, 100)
        
        assert len(sentences) == 3
        assert "Primera oración" in sentences[0]
        assert "Segunda oración" in sentences[1]
        assert "Tercera oración" in sentences[2]
    
    def test_paragraph_chunking_strategy(self):
        """Test de estrategia de chunking por párrafos"""
        strategy = ParagraphChunkingStrategy()
        text = "Párrafo uno.\n\nPárrafo dos.\n\nPárrafo tres."
        paragraphs = strategy.split_text(text, 100)
        
        assert len(paragraphs) == 3
        assert "Párrafo uno" in paragraphs[0]
        assert "Párrafo dos" in paragraphs[1]
        assert "Párrafo tres" in paragraphs[2]
    
    def test_strategy_interface(self):
        """Test de que las estrategias implementan la interfaz correctamente"""
        sentence_strategy = SentenceChunkingStrategy()
        paragraph_strategy = ParagraphChunkingStrategy()
        
        assert isinstance(sentence_strategy, IChunkingStrategy)
        assert isinstance(paragraph_strategy, IChunkingStrategy)
        
        # Verificar que tienen el método requerido
        assert hasattr(sentence_strategy, 'split_text')
        assert hasattr(paragraph_strategy, 'split_text')

class TestChunkValidator:
    """Tests para la clase ChunkValidator"""
    
    def setup_method(self):
        """Configurar antes de cada test"""
        self.validator = ChunkValidator(max_chunk_size=100)
    
    def test_validate_chunks_success(self):
        """Test de validación exitosa de chunks"""
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
        
        validation = self.validator.validate_chunks(chunks)
        
        assert validation['total_chunks'] == 2
        assert validation['chunks_within_size'] == 2
        assert validation['success_rate'] == 100.0
        assert len(validation['errors']) == 0
    
    def test_validate_chunks_with_errors(self):
        """Test de validación con errores"""
        # Crear chunk que excede el tamaño máximo
        long_text = "Esta es una oración muy larga " * 20
        chunks = [
            Chunk(
                id="test_1",
                text=long_text,
                position=1,
                total_chunks=1,
                metadata={'document_id': 'test'},
                start_token=0,
                end_token=100
            )
        ]
        
        validation = self.validator.validate_chunks(chunks)
        
        assert validation['total_chunks'] == 1
        assert validation['chunks_within_size'] == 0
        assert validation['success_rate'] == 0.0
        assert len(validation['errors']) == 1
        assert "excede tamaño máximo" in validation['errors'][0]
    
    def test_validate_chunks_without_document_id(self):
        """Test de validación con chunks sin document_id"""
        chunks = [
            Chunk(
                id="test_1",
                text="Texto",
                position=1,
                total_chunks=1,
                metadata={},  # Sin document_id
                start_token=0,
                end_token=10
            )
        ]
        
        validation = self.validator.validate_chunks(chunks)
        
        assert len(validation['warnings']) == 1
        assert "sin document_id" in validation['warnings'][0]

class TestDocumentChunker:
    """Tests para la clase DocumentChunker"""
    
    def setup_method(self):
        """Configurar antes de cada test"""
        self.chunker = DocumentChunker(chunk_size=100, overlap=20)
    
    def test_validate_parameters_valid(self):
        """Test de validación de parámetros válidos"""
        # No debe lanzar excepción
        chunker = DocumentChunker(chunk_size=100, overlap=20)
        assert chunker.chunk_size == 100
        assert chunker.overlap == 20
    
    def test_validate_parameters_invalid_size(self):
        """Test de validación de parámetros inválidos"""
        with pytest.raises(ValueError, match="excede máximo"):
            DocumentChunker(chunk_size=2000, overlap=20)
        
        with pytest.raises(ValueError, match="es menor al mínimo"):
            DocumentChunker(chunk_size=10, overlap=20)
    
    def test_validate_parameters_invalid_overlap(self):
        """Test de validación de overlap inválido"""
        with pytest.raises(ValueError, match="debe ser menor que chunk_size"):
            DocumentChunker(chunk_size=100, overlap=100)
    
    def test_fallback_recursive(self):
        """Test de fallback recursivo"""
        # Texto que excede el tamaño máximo
        long_text = "Esta es una oración muy larga " * 50
        
        chunks = self.chunker._apply_fallback_recursive(long_text, 50)
        
        assert len(chunks) > 1
        for chunk in chunks:
            assert Tokenizer.count_tokens(chunk) <= 50
    
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
            assert Tokenizer.count_tokens(chunk.text) <= self.chunker.chunk_size
    
    def test_chunk_document_empty(self):
        """Test de chunking de documento vacío"""
        chunks = self.chunker.chunk_document("", {'document_id': 'empty'})
        assert len(chunks) == 0
    
    def test_chunk_document_whitespace_only(self):
        """Test de chunking de documento con solo espacios"""
        chunks = self.chunker.chunk_document("   \n\n   ", {'document_id': 'whitespace'})
        assert len(chunks) == 0
    
    def test_apply_overlap(self):
        """Test de aplicación de overlap"""
        chunks = [
            Chunk(
                id="test_1",
                text="Primer chunk",
                position=1,
                total_chunks=2,
                metadata={'document_id': 'test'},
                start_token=0,
                end_token=10
            ),
            Chunk(
                id="test_2",
                text="Segundo chunk",
                position=2,
                total_chunks=2,
                metadata={'document_id': 'test'},
                start_token=10,
                end_token=20
            )
        ]
        
        chunks_with_overlap = self.chunker._apply_overlap(chunks)
        
        assert len(chunks_with_overlap) == 2
        assert chunks_with_overlap[0].overlap_start is None
        assert chunks_with_overlap[1].overlap_start is not None
    
    def test_validate_chunks(self):
        """Test de validación de chunks"""
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
    """Tests para las utilidades de texto"""
    
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
    
    def test_text_normalizer(self):
        """Test de la clase TextNormalizer"""
        normalizer = TextNormalizer()
        
        # Test normalize_text
        text = "¡Hola! ¿Cómo estás?"
        normalized = normalizer.normalize_text(text)
        assert "¡" not in normalized
        assert "¿" not in normalized
        assert "estas" in normalized  # Sin acentos después de normalizar
        
        # Test clean_text_for_chunking
        text = "Texto\r\ncon\r\nsaltos\r\n\r\n\r\nde\r\nlínea"
        cleaned = normalizer.clean_text_for_chunking(text)
        assert "\r\n" not in cleaned
        assert "\n\n" in cleaned
    
    def test_legal_entity_extractor(self):
        """Test de la clase LegalEntityExtractor"""
        extractor = LegalEntityExtractor()
        
        text = """
        El demandante JUAN PÉREZ solicita embargo por $1,000,000 el 15/01/2024.
        Documento RCCI2150725299 del TRIBUNAL SUPERIOR.
        """
        
        entities = extractor.extract_legal_entities(text)
        
        assert "JUAN PÉREZ" in entities['names']
        assert "$1,000,000" in entities['amounts']
        assert "15/01/2024" in entities['dates']
        assert "RCCI2150725299" in entities['document_numbers']
        assert "TRIBUNAL SUPERIOR" in entities['court_names']
        assert "demandante" in entities['legal_terms']
        assert "embargo" in entities['legal_terms']
    
    def test_text_analyzer(self):
        """Test de la clase TextAnalyzer"""
        analyzer = TextAnalyzer()
        
        text = "Esta es la primera oración. Esta es la segunda oración. Esta es la tercera oración."
        
        complexity = analyzer.calculate_text_complexity(text)
        
        assert complexity['total_words'] > 0
        assert complexity['total_sentences'] == 3
        assert complexity['avg_sentence_length'] > 0
        assert complexity['avg_word_length'] > 0
        assert 0 <= complexity['lexical_diversity'] <= 1
    
    def test_detect_language(self):
        """Test de detección de idioma"""
        analyzer = TextAnalyzer()
        
        # Texto en español
        spanish_text = "El demandante solicita embargo por daños y perjuicios."
        assert analyzer.detect_language(spanish_text) == 'es'
        
        # Texto en inglés
        english_text = "The plaintiff requests an injunction for damages."
        assert analyzer.detect_language(english_text) == 'en'
    
    def test_extract_key_phrases(self):
        """Test de extracción de frases clave"""
        analyzer = TextAnalyzer()
        
        text = """
        Esta es una oración corta.
        Esta es una oración más larga que contiene más información importante.
        Esta es otra oración corta.
        Esta es una oración muy larga que contiene mucha información detallada sobre el caso legal.
        """
        
        phrases = analyzer.extract_key_phrases(text, max_phrases=2)
        
        assert len(phrases) <= 2
        # Las frases más largas deberían aparecer primero
        assert len(phrases[0]) >= len(phrases[1]) if len(phrases) > 1 else True

class TestIntegration:
    """Tests de integración"""
    
    def test_full_chunking_pipeline(self):
        """Test del pipeline completo de chunking"""
        # Crear chunker
        chunker = DocumentChunker(chunk_size=100, overlap=20)
        
        # Texto de prueba
        text = """
        PRIMER PÁRRAFO. Este es el primer párrafo del documento legal.
        Contiene información sobre el demandante JUAN PÉREZ.
        
        SEGUNDO PÁRRAFO. Este es el segundo párrafo.
        Contiene información sobre el demandado MARÍA GARCÍA.
        Solicita embargo por $500,000 el 20/01/2024.
        
        TERCER PÁRRAFO. Este es el tercer párrafo muy largo que contiene mucha información
        detallada sobre el caso legal y los fundamentos de la demanda presentada ante el
        tribunal correspondiente con el número de expediente RCCI2150725299.
        """
        
        # Limpiar texto
        cleaned_text = clean_text_for_chunking(text)
        
        # Metadatos
        metadata = {
            'document_id': 'test_integration',
            'demandante': 'JUAN PÉREZ',
            'demandado': 'MARÍA GARCÍA',
            'fecha': '2024-01-20'
        }
        
        # Crear chunks
        chunks = chunker.chunk_document(cleaned_text, metadata)
        
        # Validar chunks
        validation = chunker.validate_chunks(chunks)
        
        # Verificar resultados
        assert len(chunks) > 0
        assert validation['success_rate'] > 90  # Al menos 90% de éxito
        assert all(chunk.metadata['document_id'] == 'test_integration' for chunk in chunks)
        
        # Verificar que se extrajeron entidades
        extractor = LegalEntityExtractor()
        all_text = " ".join(chunk.text for chunk in chunks)
        entities = extractor.extract_legal_entities(all_text)
        
        assert "JUAN PÉREZ" in entities['names']
        assert "MARÍA GARCÍA" in entities['names']
        assert "$500,000" in entities['amounts']
        assert "20/01/2024" in entities['dates']
        assert "RCCI2150725299" in entities['document_numbers'] 