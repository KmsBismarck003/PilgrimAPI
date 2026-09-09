"""
Pilgrim API Gateway - LAIKA Club
Puerta de enlace asíncrona, desacoplada y orientada a dominios y roles.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pilgrim.core.config import SERVICES, PILGRIM_HOST, PILGRIM_PORT
from pilgrim.routers import (
    admin_router,
    auth_router,
    gestor_router,
    operador_router,
    public_router
)

import os
import time
import traceback
from datetime import datetime
from fastapi import Request

app = FastAPI(
    title="Pilgrim API Gateway - Laika Club",
    description="Gateway de comunicación desacoplada y enrutamiento por roles para la plataforma LAIKA Club",
    version="2.0.0"
)

# ─── Middleware de Logging para Pruebas en tiradero/logpruebas ────────────────
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tiradero", "logpruebas")

@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    os.makedirs(LOG_DIR, exist_ok=True)
    api_log_path = os.path.join(LOG_DIR, "api_gateway.log")
    err_log_path = os.path.join(LOG_DIR, "errores_sistema.log")
    
    start_time = time.time()
    method = request.method
    url_path = request.url.path
    client_ip = request.client.host if request.client else "unknown"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        status_code = response.status_code

        log_line = f"[{timestamp}] {method} {url_path} -> {status_code} ({duration_ms}ms) | Client: {client_ip}\n"
        try:
            with open(api_log_path, "a", encoding="utf-8") as f:
                f.write(log_line)
        except Exception:
            pass

        if status_code >= 400:
            err_line = f"[{timestamp}] [HTTP {status_code}] {method} {url_path} | Client: {client_ip} | Duration: {duration_ms}ms\n"
            try:
                with open(err_log_path, "a", encoding="utf-8") as f:
                    f.write(err_line)
            except Exception:
                pass

        return response
    except Exception as exc:
        duration_ms = round((time.time() - start_time) * 1000, 2)
        err_line = f"[{timestamp}] [CRITICAL 500] {method} {url_path} | Exception: {str(exc)}\n{traceback.format_exc()}\n"
        try:
            with open(err_log_path, "a", encoding="utf-8") as f:
                f.write(err_line)
        except Exception:
            pass
        raise exc

# Configuración de CORS universal para permitir conexiones desde cualquier app cliente
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*", # Permite cualquier origen compatible con allow_credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Registro de Routers Modulares por Dominio / Rol ──────────────────────────
# 1. Apartado dedicado del Administrador (laika-admin)
app.include_router(admin_router)

# 2. Módulo central de Autenticación
app.include_router(auth_router)

# 3. Apartado del Gestor / Manager (laika-gestor)
app.include_router(gestor_router)

# 4. Apartado del Operador / Staff (laika-operador)
app.include_router(operador_router)

# 5. Recursos públicos y transversales
app.include_router(public_router)


# ─── Endpoints de Estado y Salud del Gateway ──────────────────────────────────
@app.get("/")
def root():
    """Estado general de Pilgrim Gateway y catálogo de microservicios enrutados."""
    return {
        "gateway": "Pilgrim API Gateway",
        "version": "2.0.0",
        "status": "online",
        "architecture": "modular-domain-driven",
        "roles": {
            "admin": "/api/admin, /api/database, /api/ads, /api/config, /api/restore-audit, /api/monitoring",
            "auth": "/api/auth",
            "gestor": "/api/manager, /api/stats/manager",
            "operador": "/api/staff, /api/stats/staff",
            "public": "/api/events, /api/venues, /api/tickets, /api/payments, /api/refunds, /api/stats, /uploads"
        },
        "target_services": SERVICES
    }

@app.get("/api/health")
def health():
    """Chequeo de salud del gateway."""
    return {"status": "healthy", "service": "pilgrim"}

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Iniciando Pilgrim API Gateway en {PILGRIM_HOST}:{PILGRIM_PORT}...")
    uvicorn.run("pilgrim.main:app", host=PILGRIM_HOST, port=PILGRIM_PORT, reload=True)
