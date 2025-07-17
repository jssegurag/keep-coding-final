# Guía de Desarrollo - Sistema de Consultas Semánticas (Paso 5)

## Introducción
Este documento describe el desarrollo e integración del sistema de consultas (query system) para el pipeline RAG jurídico, alineado con la arquitectura y buenas prácticas de los pasos previos:
- Paso 1: Setup y entorno
- Paso 2: Validación de embeddings
- Paso 3: Chunking adaptativo
- Paso 4: Indexación robusta

Se detallan los criterios de diseño, integración, pruebas y los **ajustes realizados** respecto al plan original, para lograr un chat jurídico interactivo, semántico y profesional.

---

## 1. Principios de Diseño y Arquitectura
- **Búsqueda siempre semántica:** El sistema consulta todos los chunks indexados usando embeddings, sin filtrar por literalidad de nombres, empresas o términos generales.
- **Correlación inteligente con metadatos:** Se extraen entidades de la consulta (nombres, fechas, cuantías, expedientes, etc.) y, tras la búsqueda, se correlacionan con los metadatos de los chunks encontrados para enriquecer la respuesta.
- **Uso de filtros solo para consultas estructuradas:** Los filtros literales solo se aplican para campos estructurados (número de expediente, fecha, cuantía, tipo de medida), nunca para nombres o términos generales.
- **Respuestas enriquecidas y trazables:** El sistema muestra los metadatos relevantes y resalta coincidencias con la consulta del usuario.
- **Principios SOLID y GRASP:** Separación de responsabilidades, bajo acoplamiento, alta cohesión, lógica de correlación modular y extensible.

---

## 2. Integración con Pasos Previos
- **Embeddings:** Se usan los embeddings validados en el paso 2 (`paraphrase-multilingual-mpnet-base-v2`).
- **Chunking:** Se aprovechan los chunks optimizados y sus metadatos del paso 3.
- **Indexación:** Se consulta la base ChromaDB generada en el paso 4, usando los metadatos normalizados.
- **Configuración centralizada:** Todos los parámetros relevantes están en `config/settings.py`.

---

## 3. Ajustes Realizados sobre el Plan Original
- **Eliminación de filtros literales por defecto:** Ahora la búsqueda es siempre semántica, salvo para campos estructurados.
- **Correlación post-búsqueda:** Las entidades extraídas de la consulta se usan para enriquecer la respuesta, no para filtrar resultados salvo casos estructurados.
- **Mejora en extracción de entidades:** Se refinaron los patrones y lógica para evitar falsos positivos y mejorar la robustez.
- **Pruebas unitarias orientadas a casos reales:** Los tests ahora cubren consultas por nombres, cuantías, fechas y expedientes reales.
- **Respuestas con trazabilidad:** Todas las respuestas incluyen fuente (documento, chunk) y resumen de metadatos relevantes.
- **Preservación de SOLID/GRASP:** Refactorización para mantener bajo acoplamiento y alta cohesión.

---

## 4. Flujo de Consulta
1. El usuario realiza una consulta en lenguaje natural.
2. El sistema extrae entidades y posibles filtros (solo usa filtros para campos estructurados).
3. Se realiza búsqueda semántica en todos los chunks indexados.
4. Se correlacionan las entidades extraídas con los metadatos de los resultados.
5. Se genera una respuesta enriquecida, profesional y trazable usando LLM (Gemini).
6. Se retorna la respuesta al usuario, incluyendo fuente y metadatos relevantes.

---

## 5. Pruebas y Validación
- **Tests unitarios:** Incluyen casos de consultas generales y estructuradas, validando extracción de entidades, uso de filtros y formato de respuesta.
- **Pruebas con documentos reales:** Se usan expedientes y metadatos reales para validar la efectividad del sistema.
- **Scripts de evaluación y modo interactivo:** Permiten probar el sistema en modo chat y evaluar la calidad de las respuestas.

---

## 6. Comandos Útiles
```bash
# Ejecutar pruebas unitarias
python -m pytest tests/unit/test_query_system.py -v

# Probar consultas interactivas
python scripts/interactive_query.py

# Evaluar calidad de respuestas
python scripts/evaluate_queries.py
```

---

## 7. Estado y Próximos Pasos
- **Sistema de consultas semánticas implementado y validado.**
- **Pendiente:** Optimización de prompts, integración con interfaz de usuario y monitoreo en producción.

---

## 8. Documentación de Ajustes en @05_implement_query_system.md
- Se documentaron los cambios en la lógica de filtros, correlación de entidades y formato de respuesta.
- Se actualizaron los criterios de éxito y verificación para reflejar la nueva lógica semántica.
- Se añadieron ejemplos y scripts de prueba alineados a la nueva arquitectura.

---

> **Este desarrollo garantiza un sistema de consultas robusto, flexible y alineado a las mejores prácticas de ingeniería de software y procesamiento jurídico automatizado. 