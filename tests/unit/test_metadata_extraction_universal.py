"""
Tests unitarios para la extracción universal de metadatos
Siguiendo principios SOLID y GRASP
"""
import pytest
import json
from unittest.mock import Mock, patch
from src.infrastructure.pipeline_steps.metadata_extraction_step import MetadataExtractionStep

class TestMetadataExtractionUniversal:
    """
    Tests unitarios para MetadataExtractionStep con funcionalidad universal.
    Responsabilidad única: Validar el comportamiento de extracción universal.
    """
    
    def setup_method(self):
        """Configurar antes de cada test"""
        self.extractor = MetadataExtractionStep()
    
    def test_extract_all_metadata_recursive_simple_dict(self):
        """Test de extracción recursiva con diccionario simple"""
        test_data = {
            'demandante': {
                'nombresPersonaDemandante': 'JUAN',
                'apellidosPersonaDemandante': 'PÉREZ'
            },
            'fecha': '2024-01-15',
            'cuantia': 500000
        }
        
        metadata = self.extractor._extract_all_metadata_recursive(test_data)
        
        assert 'demandante_nombres_persona_demandante' in metadata
        assert 'demandante_apellidos_persona_demandante' in metadata
        assert 'fecha' in metadata
        assert 'cuantia' in metadata
        assert metadata['demandante_nombres_persona_demandante'] == 'JUAN'
        assert metadata['demandante_apellidos_persona_demandante'] == 'PÉREZ'
        assert metadata['fecha'] == '2024-01-15'
        assert metadata['cuantia'] == 500000
    
    def test_extract_all_metadata_recursive_nested_structures(self):
        """Test de extracción recursiva con estructuras anidadas complejas"""
        test_data = {
            'demandante': {
                'persona': {
                    'nombres': 'MARÍA',
                    'apellidos': 'GARCÍA',
                    'identificacion': {
                        'tipo': 'CC',
                        'numero': '12345678'
                    }
                },
                'empresa': {
                    'nombre': 'EMPRESA ABC',
                    'nit': '900123456-7'
                }
            },
            'resoluciones': [
                {'numero': '001', 'fecha': '2024-01-01'},
                {'numero': '002', 'fecha': '2024-01-02'}
            ]
        }
        
        metadata = self.extractor._extract_all_metadata_recursive(test_data)
        
        # Verificar campos anidados
        assert 'demandante_persona_nombres' in metadata
        assert 'demandante_persona_apellidos' in metadata
        assert 'demandante_persona_identificacion_tipo' in metadata
        assert 'demandante_persona_identificacion_numero' in metadata
        assert 'demandante_empresa_nombre' in metadata
        assert 'demandante_empresa_nit' in metadata
        
        # Verificar arrays
        assert 'resoluciones_0_numero' in metadata
        assert 'resoluciones_0_fecha' in metadata
        assert 'resoluciones_1_numero' in metadata
        assert 'resoluciones_1_fecha' in metadata
        
        # Verificar valores
        assert metadata['demandante_persona_nombres'] == 'MARÍA'
        assert metadata['demandante_persona_identificacion_tipo'] == 'CC'
        assert metadata['resoluciones_0_numero'] == '001'
    
    def test_normalize_field_name(self):
        """Test de normalización de nombres de campos"""
        # Test con espacios y caracteres especiales
        assert self.extractor._normalize_field_name('Nombre Empresa') == 'nombre_empresa'
        assert self.extractor._normalize_field_name('TipoIdentificación') == 'tipo_identificacion'
        assert self.extractor._normalize_field_name('Número_Identificación') == 'numero_identificacion'
        
        # Test con prefijo
        assert self.extractor._normalize_field_name('demandante', 'persona') == 'persona_demandante'
    
    def test_repair_and_parse_json_valid(self):
        """Test de reparación y parseo de JSON válido"""
        valid_json = '{"demandante": {"nombres": "JUAN", "apellidos": "PÉREZ"}}'
        result = self.extractor._repair_and_parse_json(valid_json)
        
        assert result is not None
        assert 'demandante' in result
        assert result['demandante']['nombres'] == 'JUAN'
    
    def test_repair_and_parse_json_malformed(self):
        """Test de reparación y parseo de JSON mal formateado"""
        malformed_json = '{"demandante": {"nombres": "JUAN", "apellidos": "PÉREZ",}}'  # Coma extra
        result = self.extractor._repair_and_parse_json(malformed_json)
        
        assert result is not None
        assert 'demandante' in result
        assert result['demandante']['nombres'] == 'JUAN'
    
    def test_repair_and_parse_json_invalid(self):
        """Test de reparación y parseo de JSON inválido"""
        invalid_json = '{"demandante": {"nombres": "JUAN", "apellidos": "PÉREZ"'  # Sin cerrar
        result = self.extractor._repair_and_parse_json(invalid_json)
        
        # Debería intentar reparar y fallar
        assert result is None
    
    def test_basic_json_repair(self):
        """Test de reparación básica de JSON"""
        # Test con comas finales
        malformed = '{"key": "value",}'
        repaired = self.extractor._basic_json_repair(malformed)
        assert repaired == '{"key": "value"}'
        
        # Test con caracteres de control
        malformed = '{"key": "value\u0000"}'
        repaired = self.extractor._basic_json_repair(malformed)
        assert '\u0000' not in repaired
    
    def test_extract_universal_content_metadata_with_json(self):
        """Test de extracción universal de metadatos con contenido JSON"""
        ocr_results = {
            'json': {
                'demandante': {
                    'nombresPersonaDemandante': 'JUAN',
                    'apellidosPersonaDemandante': 'PÉREZ'
                },
                'fecha': '2024-01-15',
                'texts': [
                    {'text': 'Texto 1', 'confidence': 0.95},
                    {'text': 'Texto 2', 'confidence': 0.88}
                ]
            },
            'text': 'Texto completo',
            'html': '<html>...</html>'
        }
        
        metadata = self.extractor._extract_universal_content_metadata(ocr_results)
        
        # Verificar metadatos básicos
        assert 'ocr_formats_available' in metadata
        assert 'has_json_content' in metadata
        assert 'has_text_content' in metadata
        assert 'has_html_content' in metadata
        
        # Verificar metadatos extraídos universalmente
        assert 'demandante_nombres_persona_demandante' in metadata
        assert 'demandante_apellidos_persona_demandante' in metadata
        assert 'fecha' in metadata
        assert 'texts_0_text' in metadata
        assert 'texts_0_confidence' in metadata
        assert 'texts_1_text' in metadata
        assert 'texts_1_confidence' in metadata
        
        # Verificar valores
        assert metadata['demandante_nombres_persona_demandante'] == 'JUAN'
        assert metadata['fecha'] == '2024-01-15'
        assert metadata['texts_0_confidence'] == 0.95
    
    def test_extract_universal_content_metadata_with_json_string(self):
        """Test de extracción universal con JSON como string"""
        ocr_results = {
            'json': '{"demandante": {"nombresPersonaDemandante": "MARÍA", "apellidosPersonaDemandante": "GARCÍA"}}',
            'text': 'Texto completo'
        }
        
        metadata = self.extractor._extract_universal_content_metadata(ocr_results)
        
        # Verificar que se extrajeron los metadatos
        assert 'demandante_nombres_persona_demandante' in metadata
        assert 'demandante_apellidos_persona_demandante' in metadata
        assert metadata['demandante_nombres_persona_demandante'] == 'MARÍA'
        assert metadata['demandante_apellidos_persona_demandante'] == 'GARCÍA'
    
    def test_extract_universal_content_metadata_without_json(self):
        """Test de extracción universal sin contenido JSON"""
        ocr_results = {
            'text': 'Texto completo',
            'html': '<html>...</html>'
        }
        
        metadata = self.extractor._extract_universal_content_metadata(ocr_results)
        
        # Verificar metadatos básicos
        assert 'ocr_formats_available' in metadata
        assert 'has_json_content' in metadata
        assert 'has_text_content' in metadata
        assert 'has_html_content' in metadata
        
        # Verificar que no hay metadatos JSON
        assert metadata['has_json_content'] == False
        assert metadata['has_text_content'] == True
        assert metadata['has_html_content'] == True
    
    def test_execute_with_universal_extraction(self):
        """Test de ejecución completa con extracción universal"""
        input_data = {
            'file_path': '/tmp/test.pdf',
            'ocr_results': {
                'json': {
                    'demandante': {
                        'nombresPersonaDemandante': 'JUAN',
                        'apellidosPersonaDemandante': 'PÉREZ'
                    },
                    'fecha': '2024-01-15',
                    'cuantia': 500000
                }
            },
            'step_results': {
                'ocr': {'cache_used': False}
            }
        }
        
        # Mock del archivo
        with patch('os.path.exists', return_value=True):
            with patch('os.stat') as mock_stat:
                mock_stat.return_value.st_size = 1024
                mock_stat.return_value.st_ctime = 1642200000
                mock_stat.return_value.st_mtime = 1642200000
                mock_stat.return_value.st_atime = 1642200000
                
                result = self.extractor.execute(input_data)
        
        # Verificar resultado
        assert 'metadata' in result
        assert 'step_results' in result
        assert result['step_results']['metadata_extraction']['status'] == 'completed'
        assert result['step_results']['metadata_extraction']['metadata_extracted'] == True
        assert 'total_metadata_fields' in result['step_results']['metadata_extraction']
        
        # Verificar metadatos extraídos
        metadata = result['metadata']
        assert 'demandante_nombres_persona_demandante' in metadata
        assert 'demandante_apellidos_persona_demandante' in metadata
        assert 'fecha' in metadata
        assert 'cuantia' in metadata
        assert 'filename' in metadata  # Del archivo
        assert 'file_size' in metadata  # Del archivo
    
    def test_can_execute_validation(self):
        """Test de validación de capacidad de ejecución"""
        # Test con datos válidos
        valid_data = {
            'file_path': '/tmp/test.pdf',
            'ocr_results': {'json': {'test': 'data'}}
        }
        
        with patch('os.path.exists', return_value=True):
            assert self.extractor.can_execute(valid_data) == True
        
        # Test con archivo inexistente
        with patch('os.path.exists', return_value=False):
            assert self.extractor.can_execute(valid_data) == False
        
        # Test sin ocr_results
        invalid_data = {
            'file_path': '/tmp/test.pdf'
        }
        with patch('os.path.exists', return_value=True):
            assert self.extractor.can_execute(invalid_data) == False
    
    def test_get_step_info(self):
        """Test de información del paso"""
        assert self.extractor.get_step_name() == "metadata_extraction"
        assert self.extractor.get_step_description() == "Extracción universal de metadata del documento y contenido OCR" 