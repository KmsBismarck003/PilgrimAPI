"""
Pilgrim Gateway - Conector de Páginas de Contenido y Notificaciones
Enruta la gestión de páginas estáticas/legales y notificaciones administrativas.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

router = APIRouter(tags=["Admin - Contenido y Notificaciones"])

@router.api_route("/api/pages", methods=["GET", "POST"])
@router.api_route("/api/pages/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def pages_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta operaciones de CMS/Páginas hacia el microservicio admin."""
    target_path = f"/pages/{sub_path}" if sub_path else "/pages"
    return await proxy_request(request, SERVICES["admin"], target_path)

@router.api_route("/api/notifications", methods=["GET", "POST"])
@router.api_route("/api/notifications/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def notifications_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta notificaciones hacia el microservicio admin o auth."""
    target_path = f"/notifications/{sub_path}" if sub_path else "/notifications"
    return await proxy_request(request, SERVICES["admin"], target_path)
