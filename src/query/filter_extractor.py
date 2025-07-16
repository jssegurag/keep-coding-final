"""
Módulo mejorado para extracción de filtros de consultas
"""
import re
from typing import Dict, List, Optional
from src.utils.text_utils import normalize_text, extract_legal_entities

class FilterExtractor:
    def __init__(self):
        # Patrones específicos para consultas legales
        self.patterns = {
            'demandante': [
                r'(?:demandante|actor|solicitante)\s+(?:es\s+)?([A-ZÁÉÍÓÚÑ\s]+)',
                r'(?:el\s+)?demandante\s+([A-ZÁÉÍÓÚÑ\s]+)',
                r'([A-ZÁÉÍÓÚÑ\s]+)\s+(?:es\s+el\s+)?demandante'
            ],
            'demandado': [
                r'(?:demandado|demandada|entidad)\s+(?:es\s+)?([A-ZÁÉÍÓÚÑ\s]+)',
                r'(?:el\s+)?demandado\s+([A-ZÁÉÍÓÚÑ\s]+)',
                r'([A-ZÁÉÍÓÚÑ\s]+)\s+(?:es\s+el\s+)?demandado'
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
    
    def extract_filters(self, query: str) -> Dict[str, any]:
        """Extraer filtros de la consulta"""
        filters = {}
        
        # Normalizar consulta
        normalized_query = normalize_text(query)
        
        # Extraer entidades legales
        entities = extract_legal_entities(query)
        
        # Procesar cada tipo de filtro
        for filter_type, patterns in self.patterns.items():
            value = self._extract_with_patterns(query, patterns)
            
            if value:
                if filter_type == 'demandante':
                    filters['demandante_normalized'] = normalize_text(value)
                elif filter_type == 'demandado':
                    filters['demandado_normalized'] = normalize_text(value)
                elif filter_type == 'cuantia':
                    amount_clean = ''.join(filter(str.isdigit, value))
                    filters['cuantia_normalized'] = amount_clean
                elif filter_type == 'fecha':
                    filters['fecha_normalized'] = value
                elif filter_type == 'tipo_medida':
                    normalized_measure = normalize_text(value)
                    for key, mapped_value in self.measure_mapping.items():
                        if key in normalized_measure:
                            filters['tipo_medida'] = mapped_value
                            break
        
        # Usar entidades extraídas como respaldo
        if not filters.get('demandante_normalized') and entities['names']:
            filters['demandante_normalized'] = normalize_text(entities['names'][0])
        
        if not filters.get('cuantia_normalized') and entities['amounts']:
            amount_clean = ''.join(filter(str.isdigit, entities['amounts'][0]))
            filters['cuantia_normalized'] = amount_clean
        
        if not filters.get('fecha_normalized') and entities['dates']:
            filters['fecha_normalized'] = entities['dates'][0]
        
        return filters
    
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