"""
Script de ejecución directa para Pilgrim API Gateway.
Permite iniciar el gateway asegurando que la raíz del proyecto esté en sys.path.
"""
import os
import sys

# Asegurar que el directorio raíz de LaikaClub esté en el PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import uvicorn
from pilgrim.core.config import PILGRIM_HOST, PILGRIM_PORT

if __name__ == "__main__":
    print(f"==================================================")
    print(f"  PILGRIM API GATEWAY - LAIKA CLUB v2.0.0")
    print(f"  Escuchando en: http://{PILGRIM_HOST}:{PILGRIM_PORT}")
    print(f"  Modo: Desacoplado por Dominios y Roles")
    print(f"==================================================")
    uvicorn.run("pilgrim.main:app", host=PILGRIM_HOST, port=PILGRIM_PORT, reload=False)
