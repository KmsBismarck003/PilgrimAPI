"""
Pilgrim API Gateway - Configuración Central
Carga de variables de entorno y mapeo a los microservicios internos de LAIKA Club.
"""
import os
from typing import Dict

# Configuración de URLs de destino de microservicios (compatibilidad local y Docker por Rangos Estructurados)
SERVICES: Dict[str, str] = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8101"),
    "admin": os.getenv("ADMIN_SERVICE_URL", "http://127.0.0.1:8102"),
    "stats": os.getenv("STATS_SERVICE_URL", "http://127.0.0.1:8103"),
    "events": os.getenv("EVENTS_SERVICE_URL", "http://127.0.0.1:8201"),
    "tickets": os.getenv("TICKETS_SERVICE_URL", "http://127.0.0.1:8202"),
    "merchandise": os.getenv("MERCHANDISE_SERVICE_URL", "http://127.0.0.1:8203"),
    "wearables": os.getenv("WEARABLES_SERVICE_URL", "http://127.0.0.1:8204"),
    "achievements": os.getenv("ACHIEVEMENTS_SERVICE_URL", "http://127.0.0.1:8301"),
    "analytics": os.getenv("ANALYTICS_SERVICE_URL", "http://127.0.0.1:8302"),
    "analytics_bigdata": os.getenv("ANALYTICS_BIGDATA_URL", "http://127.0.0.1:8303"),
}

# Parámetros del servidor Pilgrim
PILGRIM_HOST = os.getenv("PILGRIM_HOST", "0.0.0.0")
PILGRIM_PORT = int(os.getenv("PILGRIM_PORT", "8000"))
CACHE_TTL = int(os.getenv("PILGRIM_CACHE_TTL", "60"))
PROXY_TIMEOUT = float(os.getenv("PILGRIM_PROXY_TIMEOUT", "35.0"))

# Base de datos (para consultas de contingencia como anuncios activos)
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "laika_club")
