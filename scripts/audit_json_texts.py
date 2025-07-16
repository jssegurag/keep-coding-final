#!/usr/bin/env python3
"""
Script para auditar archivos output.json en target/ y reportar el estado del campo 'text'.
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
                text = data.get('text', '')
                if not text or not text.strip():
                    empty_texts.append(json_path)
                else:
                    non_empty_texts.append((json_path, len(text)))
        except Exception as e:
            print(f"Error leyendo {json_path}: {e}")

print(f"\nTotal de archivos output.json encontrados: {total}")
print(f"Archivos con campo 'text' vacío: {len(empty_texts)}")
print(f"Archivos con texto útil: {len(non_empty_texts)}")

if empty_texts:
    print("\nEjemplos de archivos vacíos:")
    for path in empty_texts[:5]:
        print(f"  - {path}")

if non_empty_texts:
    print("\nEjemplos de archivos con texto útil:")
    for path, length in non_empty_texts[:5]:
        print(f"  - {path} (longitud: {length} caracteres)") 