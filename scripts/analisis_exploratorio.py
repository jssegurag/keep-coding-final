import pandas as pd

# Cargar el dataset
csv_path = 'src/resources/metadata/pipeline_metadata_flat.csv'
df = pd.read_csv(csv_path)

# Número de documentos y columnas
print(f"Documentos: {df.shape[0]}, Campos: {df.shape[1]}")

# Análisis de vacíos y cardinalidad
resumen = []
total = df.shape[0]
for col in df.columns:
    vacios = df[col].isnull().sum() + (df[col] == '').sum()
    cardinalidad = df[col].nunique(dropna=True)
    resumen.append({
        'campo': col,
        'vacios': vacios,
        'porc_vacios': vacios / total * 100,
        'cardinalidad': cardinalidad
    })

resumen_df = pd.DataFrame(resumen)
# Filtrar campos con menos del 70% de vacíos
resumen_df = resumen_df[resumen_df['porc_vacios'] < 70]
# Ordenar por menor porcentaje de vacíos y mayor cardinalidad
resumen_df = resumen_df.sort_values(by=['porc_vacios', 'cardinalidad'])

# Mostrar los campos seleccionados
print(resumen_df.to_string(index=False))

# Generar lista de campos seleccionados para indexar
campos_para_indexar = resumen_df['campo'].tolist()
print('\nCampos seleccionados para indexar (menos del 70% de vacíos):')
print(campos_para_indexar)

# Ejemplo de cómo filtrar un diccionario de metadatos para indexar solo estos campos
print('\nEjemplo de filtrado de metadatos:')
print('''
def filtrar_metadatos(metadatos, campos_permitidos):
    return {k: v for k, v in metadatos.items() if k in campos_permitidos}

# Uso:
# metadatos_filtrados = filtrar_metadatos(metadatos_originales, campos_para_indexar)
''') 