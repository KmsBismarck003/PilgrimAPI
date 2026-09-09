"""
Pilgrim Gateway - Conector Público de Eventos y Recintos
Enruta cartelera de eventos, detalles, filtrado de fechas y recintos hacia el microservicio de eventos.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

router = APIRouter(tags=["Público - Eventos y Recintos"])

@router.api_route("/api/events", methods=["GET", "POST"])
@router.api_route("/api/events/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def events_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta eventos, activando caché pública cuando corresponda."""
    target_path = f"/{sub_path}" if sub_path else ""
    is_cacheable = "public" in sub_path
    return await proxy_request(request, SERVICES["events"], target_path, cacheable=is_cacheable)

@router.api_route("/api/venues", methods=["GET", "POST"])
@router.api_route("/api/venues/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def venues_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta recintos y mapas de asientos hacia el microservicio de eventos."""
    target_path = f"/venues/{sub_path}" if sub_path else "/venues"
    return await proxy_request(request, SERVICES["events"], target_path)
