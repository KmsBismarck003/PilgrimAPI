"""
Pilgrim Gateway - Router de Conexión del Rol OPERADOR (Staff)
Estructura desacoplada y lista para la migración de 'laika-operador'.
Enruta escaneo de accesos, validación de boletos QR y telemetría de puertas.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

operador_router = APIRouter(tags=["Operador / Staff"])

@operador_router.api_route("/api/staff", methods=["GET", "POST"])
@operador_router.api_route("/api/staff/{sub_path:path}", methods=["GET", "POST", "PUT", "PATCH"])
async def operador_staff_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta validación de tickets y control de acceso hacia el microservicio de boletos/tickets."""
    target_path = f"/{sub_path}" if sub_path else ""
    return await proxy_request(request, SERVICES["tickets"], target_path)

@operador_router.api_route("/api/stats/staff", methods=["GET"])
@operador_router.api_route("/api/stats/staff/{sub_path:path}", methods=["GET"])
async def operador_stats_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta las estadísticas de aforo y escaneos de puertas hacia el microservicio de stats."""
    target_path = f"/staff/{sub_path}" if sub_path else "/staff"
    return await proxy_request(request, SERVICES["stats"], target_path)
