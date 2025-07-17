import pandas as pd

# Cargar el dataset
df = pd.read_csv('src/resources/metadata/pipeline_metadata_flat.csv')

print('Analizando expedientes con más metadatos...')
print('='*60)

# Contar campos no vacíos para cada expediente
metadata_counts = []
for idx, row in df.iterrows():
    non_empty_fields = sum(1 for val in row.values if pd.notna(val) and val != '')
    metadata_counts.append({
        'document_id': row['document_id'],
        'non_empty_fields': non_empty_fields
    })

metadata_df = pd.DataFrame(metadata_counts)
top_5 = metadata_df.nlargest(5, 'non_empty_fields')

print('Top 5 expedientes con más metadatos:')
print(top_5.to_string(index=False))

print('\nDetalles del expediente con más metadatos:')
best_doc = top_5.iloc[0]['document_id']
best_row = df[df['document_id'] == best_doc].iloc[0]

print(f'Document ID: {best_doc}')
print(f'Campos no vacíos: {top_5.iloc[0]["non_empty_fields"]}')

print('\nMetadatos disponibles:')
non_empty_metadata = [(col, val) for col, val in best_row.items() if pd.notna(val) and val != '']
for col, val in non_empty_metadata[:20]:  # Mostrar los primeros 20 campos
    print(f'{col}: {val}')

print(f'\nTotal de metadatos disponibles: {len(non_empty_metadata)}')

# Verificar si está indexado en ChromaDB
print('\nVerificando si está indexado en ChromaDB...')
try:
    from src.indexing.chroma_indexer import ChromaIndexer
    indexer = ChromaIndexer()
    result = indexer.search_similar('test', n_results=1, where={'document_id': best_doc})
    if result.get('total_results', 0) > 0:
        print(f'✅ El expediente {best_doc} está indexado en ChromaDB')
        print(f'Chunks encontrados: {result.get("total_results", 0)}')
    else:
        print(f'❌ El expediente {best_doc} NO está indexado en ChromaDB')
except Exception as e:
    print(f'Error verificando ChromaDB: {e}') 