"""
Módulo para chunking de documentos legales con fallback recursivo
Siguiendo principios SOLID y arquitectura limpia
"""
import re
import uuid
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

from config.settings import CHUNK_SIZE, CHUNK_OVERLAP, MAX_CHUNK_SIZE, MIN_CHUNK_SIZE
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/chunking.log")

@dataclass
class Chunk:
    """Representa un chunk de documento con metadatos completos"""
    id: str
    text: str
    position: int
    total_chunks: int
    metadata: Dict
    start_token: int
    end_token: int
    overlap_start: Optional[int] = None
    overlap_end: Optional[int] = None

class IChunkingStrategy(ABC):
    """Interfaz para estrategias de chunking"""
    
    @abstractmethod
    def split_text(self, text: str, max_size: int) -> List[str]:
        """Dividir texto según la estrategia"""
        pass

class SentenceChunkingStrategy(IChunkingStrategy):
    """Estrategia de chunking por oraciones"""
    
    def split_text(self, text: str, max_size: int) -> List[str]:
        """Dividir texto por oraciones"""
        sentence_patterns = [
            r'[.!?]+[\s\n]*',  # Punto, exclamación, interrogación
            r'[.!?]+["\']+[\s\n]*',  # Con comillas
            r'\n\s*\n',  # Párrafos
        ]
        
        pattern = '|'.join(sentence_patterns)
        sentences = re.split(pattern, text)
        
        return [s.strip() for s in sentences if s.strip()]

class ParagraphChunkingStrategy(IChunkingStrategy):
    """Estrategia de chunking por párrafos"""
    
    def split_text(self, text: str, max_size: int) -> List[str]:
        """Dividir texto por párrafos"""
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]

class Tokenizer:
    """Clase responsable de tokenización de texto"""
    
    @staticmethod
    def tokenize_text(text: str) -> List[str]:
        """Tokenizar texto en palabras"""
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    @staticmethod
    def count_tokens(text: str) -> int:
        """Contar tokens en un texto"""
        return len(Tokenizer.tokenize_text(text))

class ChunkValidator:
    """Clase responsable de validar chunks"""
    
    def __init__(self, max_chunk_size: int):
        self.max_chunk_size = max_chunk_size
    
    def validate_chunks(self, chunks: List[Chunk]) -> Dict[str, any]:
        """Validar que los chunks cumplen con los criterios"""
        validation_results = {
            'total_chunks': len(chunks),
            'chunks_within_size': 0,
            'chunks_with_overlap': 0,
            'errors': [],
            'warnings': []
        }
        
        for i, chunk in enumerate(chunks):
            # Verificar tamaño
            token_count = Tokenizer.count_tokens(chunk.text)
            if token_count <= self.max_chunk_size:
                validation_results['chunks_within_size'] += 1
            else:
                validation_results['errors'].append(
                    f"Chunk {i+1} excede tamaño máximo: {token_count} > {self.max_chunk_size}"
                )
            
            # Verificar overlap
            if i > 0 and chunk.overlap_start is not None:
                validation_results['chunks_with_overlap'] += 1
            
            # Verificar metadatos
            if not chunk.metadata.get('document_id'):
                validation_results['warnings'].append(
                    f"Chunk {i+1} sin document_id en metadatos"
                )
        
        validation_results['success_rate'] = (
            validation_results['chunks_within_size'] / len(chunks) * 100
        ) if len(chunks) > 0 else 0
        
        return validation_results

class DocumentChunker:
    """
    Clase principal para chunking de documentos legales
    Implementa fallback recursivo y preserva metadatos
    """
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
        """
        Inicializar chunker con validación de parámetros.
        
        Args:
            chunk_size: Tamaño máximo de chunk en tokens
            overlap: Overlap entre chunks consecutivos
        """
        self._validate_parameters(chunk_size, overlap)
        
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.logger = logger
        self.validator = ChunkValidator(chunk_size)
        
        # Estrategias de chunking
        self.paragraph_strategy = ParagraphChunkingStrategy()
        self.sentence_strategy = SentenceChunkingStrategy()
    
    def _validate_parameters(self, chunk_size: int, overlap: int):
        """Validar parámetros de configuración"""
        if chunk_size > MAX_CHUNK_SIZE:
            raise ValueError(f"Chunk size {chunk_size} excede máximo {MAX_CHUNK_SIZE}")
        if chunk_size < MIN_CHUNK_SIZE:
            raise ValueError(f"Chunk size {chunk_size} es menor al mínimo {MIN_CHUNK_SIZE}")
        if overlap >= chunk_size:
            raise ValueError(f"Overlap {overlap} debe ser menor que chunk_size {chunk_size}")
    
    def _create_chunk_with_metadata(self, 
                                  text: str, 
                                  position: int, 
                                  total_chunks: int,
                                  base_metadata: Dict,
                                  start_token: int,
                                  end_token: int,
                                  overlap_start: Optional[int] = None,
                                  overlap_end: Optional[int] = None) -> Chunk:
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
            'token_count': Tokenizer.count_tokens(text)
        })
        
        return Chunk(
            id=chunk_id,
            text=text,
            position=position,
            total_chunks=total_chunks,
            metadata=chunk_metadata,
            start_token=start_token,
            end_token=end_token,
            overlap_start=overlap_start,
            overlap_end=overlap_end
        )
    
    def _apply_fallback_recursive(self, text: str, max_size: int) -> List[str]:
        """Aplicar fallback recursivo para textos que exceden el tamaño máximo"""
        if Tokenizer.count_tokens(text) <= max_size:
            return [text]
        
        # Intentar dividir por párrafos primero
        paragraphs = self.paragraph_strategy.split_text(text, max_size)
        if len(paragraphs) > 1:
            result = []
            for paragraph in paragraphs:
                result.extend(self._apply_fallback_recursive(paragraph, max_size))
            return result
        
        # Si no hay párrafos, dividir por oraciones
        sentences = self.sentence_strategy.split_text(text, max_size)
        if len(sentences) > 1:
            result = []
            current_chunk = ""
            
            for sentence in sentences:
                test_chunk = current_chunk + " " + sentence if current_chunk else sentence
                
                if Tokenizer.count_tokens(test_chunk) <= max_size:
                    current_chunk = test_chunk
                else:
                    if current_chunk:
                        result.append(current_chunk.strip())
                    current_chunk = sentence
            
            if current_chunk:
                result.append(current_chunk.strip())
            
            return result
        
        # Si no se puede dividir más, dividir por palabras
        words = text.split()
        if len(words) > max_size:
            result = []
            current_chunk = ""
            
            for word in words:
                test_chunk = current_chunk + " " + word if current_chunk else word
                
                if Tokenizer.count_tokens(test_chunk) <= max_size:
                    current_chunk = test_chunk
                else:
                    if current_chunk:
                        result.append(current_chunk.strip())
                    current_chunk = word
            
            if current_chunk:
                result.append(current_chunk.strip())
            
            return result
        
        # Si no se puede dividir más, truncar (último recurso)
        self.logger.warning(f"Texto no se puede dividir más, truncando: {text[:100]}...")
        return [text[:max_size * 4]]  # Aproximación de tokens a caracteres
    
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
        paragraphs = self.paragraph_strategy.split_text(text, self.chunk_size)
        chunks = []
        current_position = 1
        total_tokens = Tokenizer.count_tokens(text)
        
        for paragraph in paragraphs:
            # Verificar si el párrafo excede el tamaño máximo
            if Tokenizer.count_tokens(paragraph) > self.chunk_size:
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
    
    def validate_chunks(self, chunks: List[Chunk]) -> Dict[str, any]:
        """Validar que los chunks cumplen con los criterios"""
        return self.validator.validate_chunks(chunks) 