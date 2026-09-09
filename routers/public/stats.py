"""
Pilgrim Gateway - Conector de Estadísticas Públicas
Enruta estadísticas de cartelera y conteos generales hacia el microservicio de stats.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

router = APIRouter(tags=["Público - Estadísticas"])

@router.api_route("/api/stats", methods=["GET"])
@router.api_route("/api/stats/{sub_path:path}", methods=["GET", "POST"])
async def stats_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta estadísticas generales hacia el microservicio de stats."""
    target_path = f"/{sub_path}" if sub_path else ""
    return await proxy_request(request, SERVICES["stats"], target_path)
