"""
Módulo mejorado para extracción de filtros de consultas
"""
import re
from typing import Dict, List, Optional
from src.utils.text_utils import normalize_text, extract_legal_entities

class FilterExtractor:
    def __init__(self):
        # Patrones específicos para consultas legales (más estrictos)
        self.patterns = {
            'demandante': [
                r'(?:el\s+)?demandante\s+(?:es\s+)?([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{2,})',
                r'([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{2,})\s+(?:es\s+el\s+)?demandante',
                r'demandante:\s*([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{2,})'
            ],
            'demandado': [
                r'(?:el\s+)?demandado\s+(?:es\s+)?([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{2,})',
                r'([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{2,})\s+(?:es\s+el\s+)?demandado',
                r'demandado:\s*([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{2,})'
            ],
            'cuantia': [
                r'(?:cuantía|monto|valor)\s+(?:es\s+)?(\$?[\d,\.]+)',
                r'(\$?[\d,\.]+)\s+(?:es\s+la\s+)?cuantía',
                r'por\s+(\$?[\d,\.]+)'
            ],
            'fecha': [
                r'(?:fecha|día)\s+(?:es\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+(?:es\s+la\s+)?fecha',
                r'el\s+(\d{1,2}\s+de\s+[a-z]+\s+de\s+\d{4})'
            ],
            'tipo_medida': [
                r'(?:tipo\s+de\s+)?medida\s+(?:es\s+)?([a-záéíóúñ\s]+)',
                r'([a-záéíóúñ\s]+)\s+(?:es\s+el\s+)?tipo\s+de\s+medida',
                r'(embargo|medida\s+cautelar|secuestro|prohibición)'
            ]
        }
        
        # Términos de medida mapeados
        self.measure_mapping = {
            'embargo': 'Embargo',
            'medida cautelar': 'Medida Cautelar',
            'secuestro': 'Secuestro',
            'prohibición': 'Prohibición',
            'suspensión': 'Suspensión'
        }
        
        # Palabras genéricas que no deben extraerse como nombres
        self.generic_words = {
            'informacion', 'información', 'hay', 'sobre', 'acerca', 'respecto',
            'datos', 'detalles', 'particular', 'especifico', 'específico',
            'cual', 'cuál', 'que', 'qué', 'como', 'cómo', 'donde', 'dónde',
            'cuando', 'cuándo', 'porque', 'por qué', 'para', 'con', 'sin',
            'sobre', 'bajo', 'entre', 'desde', 'hasta', 'durante', 'antes',
            'después', 'mientras', 'aunque', 'pero', 'sin embargo', 'además'
        }
    
    def extract_filters(self, query: str) -> Dict[str, any]:
        """Extraer filtros de la consulta con validaciones estrictas"""
        filters = {}
        
        # Normalizar consulta
        normalized_query = normalize_text(query)
        
        # Extraer entidades legales
        entities = extract_legal_entities(query)
        
        # Procesar cada tipo de filtro con validaciones estrictas
        for filter_type, patterns in self.patterns.items():
            value = self._extract_with_patterns(query, patterns)
            
            if value and self._is_valid_filter_value(value, filter_type):
                if filter_type == 'demandante':
                    filters['demandante_normalized'] = normalize_text(value)
                elif filter_type == 'demandado':
                    filters['demandado_normalized'] = normalize_text(value)
                elif filter_type == 'cuantia':
                    amount_clean = ''.join(filter(str.isdigit, value))
                    if len(amount_clean) >= 3:  # Al menos 3 dígitos para ser válido
                        filters['cuantia_normalized'] = amount_clean
                elif filter_type == 'fecha':
                    filters['fecha_normalized'] = value
                elif filter_type == 'tipo_medida':
                    normalized_measure = normalize_text(value)
                    for key, mapped_value in self.measure_mapping.items():
                        if key in normalized_measure:
                            filters['tipo_medida'] = mapped_value
                            break
        
        # Usar entidades extraídas como respaldo solo si son válidas
        if not filters.get('demandante_normalized') and entities['names']:
            name = entities['names'][0]
            if self._is_valid_name(name):
                filters['demandante_normalized'] = normalize_text(name)
        
        if not filters.get('cuantia_normalized') and entities['amounts']:
            amount_clean = ''.join(filter(str.isdigit, entities['amounts'][0]))
            if len(amount_clean) >= 3:  # Al menos 3 dígitos
                filters['cuantia_normalized'] = amount_clean
        
        if not filters.get('fecha_normalized') and entities['dates']:
            filters['fecha_normalized'] = entities['dates'][0]
        
        return filters
    
    def _is_valid_filter_value(self, value: str, filter_type: str) -> bool:
        """Validar si un valor extraído es válido para el tipo de filtro"""
        if not value or len(value.strip()) < 2:
            return False
        
        value_lower = value.lower().strip()
        
        # Validaciones específicas por tipo
        if filter_type in ['demandante', 'demandado']:
            # Verificar que no contenga palabras genéricas
            words = value_lower.split()
            if any(word in self.generic_words for word in words):
                return False
            
            # Verificar que tenga al menos 2 palabras o sea un nombre válido
            if len(words) < 2 and len(value.strip()) < 5:
                return False
            
            # Verificar que no sea solo palabras genéricas
            if all(word in self.generic_words for word in words):
                return False
        
        elif filter_type == 'cuantia':
            # Verificar que contenga números
            if not any(c.isdigit() for c in value):
                return False
        
        elif filter_type == 'fecha':
            # Verificar formato básico de fecha
            if not re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', value):
                return False
        
        return True
    
    def _is_valid_name(self, name: str) -> bool:
        """Validar si un nombre extraído es válido"""
        if not name or len(name.strip()) < 3:
            return False
        
        name_lower = name.lower().strip()
        words = name_lower.split()
        
        # Verificar que no contenga palabras genéricas
        if any(word in self.generic_words for word in words):
            return False
        
        # Verificar que no sea solo palabras genéricas
        if all(word in self.generic_words for word in words):
            return False
        
        return True
    
    def _extract_with_patterns(self, text: str, patterns: List[str]) -> Optional[str]:
        """Extraer valor usando múltiples patrones"""
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        return None
    
    def validate_filters(self, filters: Dict[str, any]) -> Dict[str, any]:
        """Validar y limpiar filtros"""
        validated = {}
        
        for key, value in filters.items():
            if value and str(value).strip():
                # Limpiar espacios extra
                cleaned_value = str(value).strip()
                
                # Validaciones específicas
                if 'normalized' in key:
                    # Asegurar que esté normalizado
                    cleaned_value = normalize_text(cleaned_value)
                
                validated[key] = cleaned_value
        
        return validated 