"""
Utilidades para procesamiento de texto legal
Siguiendo principios de responsabilidad única y reutilización
"""
import re
import unicodedata
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class LegalEntity:
    """Representa una entidad legal extraída del texto"""
    entity_type: str
    value: str
    position: int
    confidence: float

class TextNormalizer:
    """Clase responsable de normalización de texto"""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalizar texto para búsqueda"""
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover acentos
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if not unicodedata.combining(c)
        )
        
        # Remover caracteres especiales pero preservar algunos
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
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

class LegalEntityExtractor:
    """Clase responsable de extraer entidades legales del texto"""
    
    def __init__(self):
        self.legal_terms = [
            'demandante', 'demandado', 'embargo', 'medida cautelar',
            'sentencia', 'recurso', 'apelación', 'fundamento',
            'hechos', 'pruebas', 'testigo', 'abogado', 'juez',
            'tribunal', 'juzgado', 'fiscal', 'procurador', 'notario',
            'acta', 'escritura', 'contrato', 'testamento', 'herencia',
            'divorcio', 'custodia', 'pensión', 'alimentos', 'hipoteca',
            'desahucio', 'arrendamiento', 'compraventa', 'donación'
        ]
    
    def extract_legal_entities(self, text: str) -> Dict[str, List[str]]:
        """Extraer entidades legales del texto"""
        entities = {
            'names': [],
            'dates': [],
            'amounts': [],
            'legal_terms': [],
            'document_numbers': [],
            'court_names': []
        }
        
        # Patrones para nombres (mayúsculas seguidas de espacios)
        name_pattern = r'\b[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+\b'
        names = re.findall(name_pattern, text)
        entities['names'] = [n.strip() for n in names if len(n.strip()) > 2]
        
        # Patrones para fechas
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',  # DD/MM/YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',  # YYYY-MM-DD
            r'\d{1,2}\s+de\s+[a-z]+\s+de\s+\d{4}',  # DD de MES de YYYY
            r'\d{1,2}\s+[a-z]+\s+\d{4}'  # DD MES YYYY
        ]
        
        for pattern in date_patterns:
            dates = re.findall(pattern, text)
            entities['dates'].extend(dates)
        
        # Patrones para cantidades monetarias
        amount_patterns = [
            r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?',  # $1,000,000.00
            r'\$\d{1,3}(?:\.\d{3})*(?:,\d{2})?',  # $1.000.000,00
            r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:pesos|dólares|euros)',  # Con moneda
            r'\d+\s*(?:mil|millones|billones)\s*(?:pesos|dólares|euros)'  # Texto
        ]
        
        for pattern in amount_patterns:
            amounts = re.findall(pattern, text)
            entities['amounts'].extend(amounts)
        
        # Términos jurídicos
        for term in self.legal_terms:
            if term in text.lower():
                entities['legal_terms'].append(term)
        
        # Números de documento
        doc_patterns = [
            r'[A-Z]{2,4}\d{6,10}',  # RCCI2150725299
            r'exp\.?\s*\d{4}/\d{4}',  # exp. 2024/2024
            r'causa\s*\d{4}/\d{4}',  # causa 2024/2024
        ]
        
        for pattern in doc_patterns:
            docs = re.findall(pattern, text, re.IGNORECASE)
            entities['document_numbers'].extend(docs)
        
        # Nombres de tribunales
        court_patterns = [
            r'[A-Z][A-Z\s]+(?:TRIBUNAL|JUZGADO|CORTE)',
            r'(?:TRIBUNAL|JUZGADO|CORTE)\s+[A-Z][A-Z\s]+',
        ]
        
        for pattern in court_patterns:
            courts = re.findall(pattern, text)
            entities['court_names'].extend(courts)
        
        return entities
    
    def extract_entities_with_positions(self, text: str) -> List[LegalEntity]:
        """Extraer entidades con posiciones en el texto"""
        entities = []
        
        # Buscar nombres
        name_pattern = r'\b[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+\b'
        for match in re.finditer(name_pattern, text):
            if len(match.group().strip()) > 2:
                entities.append(LegalEntity(
                    entity_type='name',
                    value=match.group().strip(),
                    position=match.start(),
                    confidence=0.8
                ))
        
        # Buscar fechas
        date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
        for match in re.finditer(date_pattern, text):
            entities.append(LegalEntity(
                entity_type='date',
                value=match.group(),
                position=match.start(),
                confidence=0.9
            ))
        
        # Buscar cantidades
        amount_pattern = r'\$?\d{1,3}(?:\.\d{3})*(?:,\d{2})?'
        for match in re.finditer(amount_pattern, text):
            entities.append(LegalEntity(
                entity_type='amount',
                value=match.group(),
                position=match.start(),
                confidence=0.7
            ))
        
        return entities

class TextAnalyzer:
    """Clase para análisis de texto legal"""
    
    @staticmethod
    def calculate_text_complexity(text: str) -> Dict[str, float]:
        """Calcular métricas de complejidad del texto"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Longitud promedio de oraciones
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Longitud promedio de palabras
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Densidad de palabras únicas
        unique_words = set(words)
        lexical_diversity = len(unique_words) / len(words) if words else 0
        
        return {
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'lexical_diversity': lexical_diversity,
            'total_words': len(words),
            'total_sentences': len(sentences)
        }
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Detectar idioma del texto (simplificado)"""
        # Contar caracteres específicos del español
        spanish_chars = len(re.findall(r'[áéíóúñÁÉÍÓÚÑ]', text))
        total_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if total_chars > 0:
            spanish_ratio = spanish_chars / total_chars
            if spanish_ratio > 0.01:  # Más del 1% de caracteres españoles
                return 'es'
        
        return 'en'  # Por defecto inglés
    
    @staticmethod
    def extract_key_phrases(text: str, max_phrases: int = 10) -> List[str]:
        """Extraer frases clave del texto"""
        # Dividir en oraciones
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Filtrar oraciones por longitud
        key_sentences = [s for s in sentences if 10 <= len(s.split()) <= 50]
        
        # Ordenar por longitud (las más largas suelen ser más informativas)
        key_sentences.sort(key=lambda x: len(x), reverse=True)
        
        return key_sentences[:max_phrases]

# Funciones de conveniencia para mantener compatibilidad
def normalize_text(text: str) -> str:
    """Normalizar texto para búsqueda"""
    return TextNormalizer.normalize_text(text)

def extract_legal_entities(text: str) -> Dict[str, List[str]]:
    """Extraer entidades legales del texto"""
    extractor = LegalEntityExtractor()
    return extractor.extract_legal_entities(text)

def clean_text_for_chunking(text: str) -> str:
    """Limpiar texto para chunking"""
    return TextNormalizer.clean_text_for_chunking(text) 