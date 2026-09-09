"""
Pilgrim Gateway - Router de Conexión del Rol GESTOR (Manager)
Estructura desacoplada y lista para la migración de 'laika-gestor'.
Enruta gestión de eventos propios, recintos, reportes de gestor y analítica.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

gestor_router = APIRouter(tags=["Gestor / Manager"])

@gestor_router.api_route("/api/manager", methods=["GET", "POST", "PUT", "DELETE"])
@gestor_router.api_route("/api/manager/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gestor_events_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta todas las operaciones del gestor de eventos hacia el microservicio de eventos (/manager)."""
    target_path = f"/manager/{sub_path}" if sub_path else "/manager"
    return await proxy_request(request, SERVICES["events"], target_path)

@gestor_router.api_route("/api/stats/manager", methods=["GET"])
@gestor_router.api_route("/api/stats/manager/{sub_path:path}", methods=["GET"])
async def gestor_stats_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta las métricas y dashboards del gestor hacia el microservicio de estadísticas."""
    target_path = f"/manager/{sub_path}" if sub_path else "/manager"
    return await proxy_request(request, SERVICES["stats"], target_path)
