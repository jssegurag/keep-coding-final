# 09_refactor_indexing_metadata_jsonfix.md

## Refactorización MVP v2: Indexación Robusta de Metadatos con JSON Fix

### 🎯 Objetivo
Asegurar que todos los metadatos relevantes de los documentos sean indexados, independientemente de la estructura o inconsistencias de los JSON, permitiendo búsquedas y correlaciones efectivas en el sistema RAG.

---

## 1. Diagnóstico Actual

- Actualmente solo se indexan algunos campos fijos (ej: demandante).
- Los campos de los JSON de metadata pueden variar entre documentos.
- Hay documentos con metadatos incompletos, mal formateados o con errores de estructura.
- No se aprovechan todos los datos útiles para la búsqueda y la trazabilidad.

---

## 2. Estrategia de Refactorización

### 2.1. Extracción y Normalización Universal de Metadatos

- Extraer **el 100% de los atributos** presentes en el JSON de metadata de cada documento, sin omitir ninguno, para máxima trazabilidad y cobertura de búsqueda.
- Recorrer recursivamente los objetos y arrays para aplanar la estructura y obtener todos los valores relevantes.
- Normalizar los nombres de los campos (snake_case, sin tildes, etc.) para consistencia.

### 2.2. Manejo de Inconsistencias con JSON Fix

- Integrar la librería [jsonfix](https://github.com/IBM/jsonfix) o lógica equivalente para:
  - Corregir JSON mal formateados o incompletos.
  - Rellenar campos faltantes con valores por defecto (`null` o string vacío).
  - Garantizar que siempre se obtenga un diccionario válido para indexar.

### 2.3. Indexación Flexible

- Al indexar cada chunk, adjuntar el diccionario completo de metadatos extraídos y normalizados.
- Si un campo no existe en un documento, simplemente no se incluye o se deja vacío.
- Documentar los campos más frecuentes para facilitar futuras consultas y filtros.

### 2.4. Testing y Validación

- Crear un set de documentos de prueba con JSONs variados (completos, incompletos, mal formateados).
- Validar que todos los metadatos útiles se indexan y son accesibles en la búsqueda.
- Probar búsquedas por campos que antes no estaban disponibles (ej: demandados, cuantías, resoluciones).

---

## 3. Tareas Específicas

- [ ] Investigar e integrar jsonfix o lógica de reparación de JSON.
- [ ] Refactorizar el pipeline de indexación para extraer y aplanar todos los metadatos.
- [ ] Normalizar nombres de campos y valores.
- [ ] Adaptar la función de indexación para aceptar metadatos flexibles.
- [ ] Actualizar los tests unitarios y de integración.
- [ ] Documentar los cambios y los nuevos campos indexados.
- [ ] Validar la mejora en la cobertura de búsqueda y trazabilidad.

---

## 4. Criterios de Éxito

- Todos los metadatos relevantes de cada documento están indexados y accesibles.
- El sistema no falla ante JSONs incompletos o mal formateados.
- Se pueden realizar búsquedas y correlaciones por cualquier campo presente en la metadata.
- Los tests de indexación y búsqueda pasan con documentos heterogéneos.

---

## 5. Referencias

- [jsonfix - IBM](https://github.com/IBM/jsonfix)
- [Documentación ChromaDB](https://docs.trychroma.com/)
- [Best practices RAG metadata](https://www.pinecone.io/learn/series/metadata/) 