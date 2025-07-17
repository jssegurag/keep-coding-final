import pandas as pd
import os
import sys
import unittest
from pathlib import Path

# Agregar el directorio src al path para importar módulos
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

class TestMetadataFlattening(unittest.TestCase):
    
    def setUp(self):
        """Configurar rutas de archivos para las pruebas"""
        self.base_path = Path(__file__).parent.parent.parent
        self.original_file = self.base_path / 'src' / 'resources' / 'metadata' / 'pipeline_metadata.csv'
        self.flat_file = self.base_path / 'src' / 'resources' / 'metadata' / 'pipeline_metadata_flat.csv'
        
    def test_file_exists(self):
        """Verificar que el archivo plano fue generado"""
        self.assertTrue(self.flat_file.exists(), 
                       f"El archivo {self.flat_file} no existe")
        
    def test_original_file_exists(self):
        """Verificar que el archivo original existe"""
        self.assertTrue(self.original_file.exists(), 
                       f"El archivo original {self.original_file} no existe")
        
    def test_required_columns_present(self):
        """Verificar que las columnas requeridas están presentes"""
        df = pd.read_csv(self.flat_file)
        required_columns = ['id', 'document_id', 'json_path']
        
        for col in required_columns:
            self.assertIn(col, df.columns, 
                         f"La columna requerida '{col}' no está presente")
            
    def test_data_integrity(self):
        """Verificar integridad de datos entre archivo original y plano"""
        df_original = pd.read_csv(self.original_file)
        df_flat = pd.read_csv(self.flat_file)
        
        # Verificar que el número de filas es el mismo
        self.assertEqual(len(df_original), len(df_flat), 
                        "El número de filas debe ser el mismo")
        
        # Verificar que los IDs coinciden
        self.assertTrue(df_original['id'].equals(df_flat['id']), 
                       "Los IDs deben coincidir entre archivos")
        
        # Verificar que document_ids coinciden
        self.assertTrue(df_original['document_id'].equals(df_flat['document_id']), 
                       "Los document_ids deben coincidir entre archivos")
        
        # Verificar que json_paths coinciden
        self.assertTrue(df_original['json_path'].equals(df_flat['json_path']), 
                       "Los json_paths deben coincidir entre archivos")
        
    def test_no_empty_metadata_columns(self):
        """Verificar que no hay columnas de metadatos completamente vacías"""
        df = pd.read_csv(self.flat_file)
        
        # Obtener columnas de metadatos (excluyendo las requeridas)
        metadata_columns = [col for col in df.columns 
                          if col not in ['id', 'document_id', 'json_path']]
        
        # Verificar que al menos algunas columnas tienen datos
        non_empty_columns = []
        for col in metadata_columns:
            if df[col].notna().any():
                non_empty_columns.append(col)
                
        self.assertGreater(len(non_empty_columns), 0, 
                          "Debe haber al menos algunas columnas de metadatos con datos")
        
    def test_metadata_extraction_quality(self):
        """Verificar calidad de extracción de metadatos"""
        df_original = pd.read_csv(self.original_file)
        df_flat = pd.read_csv(self.flat_file)
        
        # Verificar que al menos algunos documentos tienen metadatos extraídos
        metadata_columns = [col for col in df_flat.columns 
                          if col not in ['id', 'document_id', 'json_path']]
        
        # Contar filas con al menos un metadato no vacío
        rows_with_metadata = 0
        for _, row in df_flat.iterrows():
            if any(pd.notna(row[col]) for col in metadata_columns):
                rows_with_metadata += 1
                
        self.assertGreater(rows_with_metadata, 0, 
                          "Al menos algunas filas deben tener metadatos extraídos")
        
        # Verificar que el porcentaje de filas con metadatos es razonable (>50%)
        percentage_with_metadata = (rows_with_metadata / len(df_flat)) * 100
        self.assertGreater(percentage_with_metadata, 50, 
                          f"Al menos 50% de las filas deben tener metadatos (actual: {percentage_with_metadata:.1f}%)")
        
    def test_column_naming_convention(self):
        """Verificar que las columnas siguen la convención de nombres"""
        df = pd.read_csv(self.flat_file)
        
        # Verificar que las columnas de metadatos usan guiones bajos
        metadata_columns = [col for col in df.columns 
                          if col not in ['id', 'document_id', 'json_path']]
        
        for col in metadata_columns:
            # Verificar que no hay espacios en blanco
            self.assertNotIn(' ', col, 
                            f"La columna '{col}' no debe contener espacios")
            
            # Verificar que usa guiones bajos para separar niveles
            if '_' in col:
                self.assertTrue(col.replace('_', '').isalnum(), 
                              f"La columna '{col}' debe usar solo caracteres alfanuméricos y guiones bajos")
        
    def test_data_types(self):
        """Verificar tipos de datos apropiados"""
        df = pd.read_csv(self.flat_file)
        
        # Verificar que las columnas requeridas tienen tipos apropiados
        self.assertTrue(pd.api.types.is_numeric_dtype(df['id']), 
                       "La columna 'id' debe ser numérica")
        
        self.assertTrue(pd.api.types.is_string_dtype(df['document_id']), 
                       "La columna 'document_id' debe ser string")
        
        self.assertTrue(pd.api.types.is_string_dtype(df['json_path']), 
                       "La columna 'json_path' debe ser string")
        
    def test_no_duplicate_rows(self):
        """Verificar que no hay filas duplicadas"""
        df = pd.read_csv(self.flat_file)
        
        # Verificar duplicados basados en las columnas identificadoras
        duplicates = df.duplicated(subset=['id', 'document_id'], keep=False)
        self.assertFalse(duplicates.any(), 
                        "No debe haber filas duplicadas basadas en id y document_id")
        
    def test_file_size_reasonable(self):
        """Verificar que el tamaño del archivo es razonable"""
        file_size = self.flat_file.stat().st_size
        
        # Verificar que el archivo no está vacío
        self.assertGreater(file_size, 0, 
                          "El archivo no debe estar vacío")
        
        # Verificar que el archivo no es excesivamente grande (>100MB)
        self.assertLess(file_size, 100 * 1024 * 1024, 
                       "El archivo no debe ser mayor a 100MB")
        
    def test_csv_format_valid(self):
        """Verificar que el formato CSV es válido"""
        try:
            df = pd.read_csv(self.flat_file)
            # Si llegamos aquí, el CSV es válido
            self.assertTrue(True, "El archivo CSV es válido")
        except Exception as e:
            self.fail(f"El archivo CSV no es válido: {str(e)}")

if __name__ == '__main__':
    unittest.main(verbosity=2) 