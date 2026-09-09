"""
Pilgrim API Gateway - Sistema de Caché en Memoria
Mantiene respuestas cacheadas para recursos públicos de alto tráfico.
"""
import time
from typing import Dict, Any, Optional

GET_CACHE: Dict[str, Any] = {}

def get_cached_response(url_key: str) -> Optional[Dict[str, Any]]:
    """Recupera una respuesta cacheada si aún no ha expirado."""
    if url_key in GET_CACHE:
        entry = GET_CACHE[url_key]
        if time.time() < entry['expires']:
            return entry
        else:
            del GET_CACHE[url_key]
    return None

def set_cached_response(url_key: str, content: bytes, status: int, headers: dict, ttl: int = 60) -> None:
    """Almacena una respuesta en la caché con un tiempo de vida (TTL) en segundos."""
    GET_CACHE[url_key] = {
        "content": content,
        "status": status,
        "headers": headers,
        "expires": time.time() + ttl
    }

def clear_cache() -> None:
    """Limpia toda la caché en memoria."""
    GET_CACHE.clear()
