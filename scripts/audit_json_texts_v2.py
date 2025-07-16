#!/usr/bin/env python3
"""
Script para auditar archivos output.json en target/ usando la nueva lógica de extracción de texto.
"""
import os
import json

TARGET_DIR = "target"

empty_texts = []
non_empty_texts = []
total = 0

for root, dirs, files in os.walk(TARGET_DIR):
    if "output.json" in files:
        json_path = os.path.join(root, "output.json")
        total += 1
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Extraer texto de todos los elementos del array 'texts'
                texts_array = data.get('texts', [])
                full_text = ' '.join([t.get('text', '') for t in texts_array if t.get('text')])
                
                if not full_text or not full_text.strip():
                    empty_texts.append(json_path)
                else:
                    non_empty_texts.append((json_path, len(full_text)))
        except Exception as e:
            print(f"Error leyendo {json_path}: {e}")

print(f"\nTotal de archivos output.json encontrados: {total}")
print(f"Archivos con texto extraído vacío: {len(empty_texts)}")
print(f"Archivos con texto útil: {len(non_empty_texts)}")

if empty_texts:
    print("\nEjemplos de archivos vacíos:")
    for path in empty_texts[:5]:
        print(f"  - {path}")

if non_empty_texts:
    print("\nEjemplos de archivos con texto útil:")
    for path, length in non_empty_texts[:5]:
        print(f"  - {path} (longitud: {length} caracteres)")
        
    # Mostrar un ejemplo del texto extraído
    if non_empty_texts:
        example_path, example_length = non_empty_texts[0]
        print(f"\nEjemplo de texto extraído de {example_path}:")
        try:
            with open(example_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                texts_array = data.get('texts', [])
                full_text = ' '.join([t.get('text', '') for t in texts_array if t.get('text')])
                print(f"Primeros 200 caracteres: {full_text[:200]}...")
        except Exception as e:
            print(f"Error leyendo ejemplo: {e}") 