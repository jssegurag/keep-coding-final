#!/usr/bin/env python3
"""
Script para ejecutar el sistema RAG Legal completo.

Este script permite ejecutar tanto el servidor API FastAPI como la interfaz
de usuario Streamlit, proporcionando una experiencia completa del sistema
RAG Legal para abogados que procesan oficios jurídicos.
"""

import subprocess
import sys
import os
import time
import signal
import threading
from typing import List, Optional

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas."""
    required_packages = [
        'streamlit',
        'fastapi',
        'uvicorn',
        'requests',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Faltan las siguientes dependencias: {', '.join(missing_packages)}")
        print("Instale las dependencias con: pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def start_api_server():
    """Iniciar el servidor API FastAPI."""
    print("🚀 Iniciando servidor API FastAPI...")
    
    try:
        # Comando para iniciar el servidor API
        cmd = [
            sys.executable, "-m", "uvicorn",
            "src.api.main:app",
            "--host", "0.0.0.0",
            "--port", "8001",
            "--reload"
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar un momento para que el servidor se inicie
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Servidor API iniciado en http://localhost:8001")
            return process
        else:
            print("❌ Error iniciando el servidor API")
            return None
            
    except Exception as e:
        print(f"❌ Error iniciando servidor API: {e}")
        return None

def start_streamlit_app():
    """Iniciar la aplicación Streamlit."""
    print("🎨 Iniciando aplicación Streamlit...")
    
    try:
        # Comando para iniciar Streamlit
        cmd = [
            sys.executable, "-m", "streamlit",
            "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "true"
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar un momento para que la aplicación se inicie
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Aplicación Streamlit iniciada en http://localhost:8501")
            return process
        else:
            print("❌ Error iniciando la aplicación Streamlit")
            return None
            
    except Exception as e:
        print(f"❌ Error iniciando Streamlit: {e}")
        return None

def wait_for_api():
    """Esperar a que la API esté disponible."""
    import requests
    
    print("⏳ Esperando a que la API esté disponible...")
    
    for i in range(30):  # Esperar hasta 30 segundos
        try:
            response = requests.get("http://localhost:8001/api/v1/system/health", timeout=2)
            if response.status_code == 200:
                print("✅ API disponible")
                return True
        except:
            pass
        
        time.sleep(1)
        print(f"⏳ Esperando... ({i+1}/30)")
    
    print("❌ La API no está disponible después de 30 segundos")
    return False

def main():
    """Función principal."""
    print("🏛️ Sistema RAG Legal - Iniciando...")
    print("=" * 50)
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Iniciar servidor API
    api_process = start_api_server()
    if not api_process:
        print("❌ No se pudo iniciar el servidor API")
        sys.exit(1)
    
    # Esperar a que la API esté disponible
    if not wait_for_api():
        print("❌ La API no está respondiendo")
        api_process.terminate()
        sys.exit(1)
    
    # Iniciar aplicación Streamlit
    streamlit_process = start_streamlit_app()
    if not streamlit_process:
        print("❌ No se pudo iniciar la aplicación Streamlit")
        api_process.terminate()
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Sistema RAG Legal iniciado exitosamente!")
    print("=" * 50)
    print("📊 API REST: http://localhost:8001")
    print("📊 Documentación API: http://localhost:8001/docs")
    print("🎨 Interfaz de Usuario: http://localhost:8501")
    print("=" * 50)
    print("Presione Ctrl+C para detener el sistema")
    print("=" * 50)
    
    try:
        # Mantener los procesos ejecutándose
        while True:
            time.sleep(1)
            
            # Verificar si los procesos siguen ejecutándose
            if api_process.poll() is not None:
                print("❌ El servidor API se detuvo inesperadamente")
                break
                
            if streamlit_process.poll() is not None:
                print("❌ La aplicación Streamlit se detuvo inesperadamente")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo el sistema...")
        
        # Terminar procesos
        if api_process:
            api_process.terminate()
            print("✅ Servidor API detenido")
            
        if streamlit_process:
            streamlit_process.terminate()
            print("✅ Aplicación Streamlit detenida")
        
        print("👋 Sistema detenido exitosamente")

if __name__ == "__main__":
    main() 