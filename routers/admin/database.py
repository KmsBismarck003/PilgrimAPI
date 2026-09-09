"""
Pilgrim Gateway - Conector de Base de Datos y Backups para Admin
Enruta peticiones de gestión de base de datos hacia el microservicio admin.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

router = APIRouter(tags=["Admin - Base de Datos"])

@router.api_route("/api/database", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@router.api_route("/api/database/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def database_proxy(request: Request, sub_path: str = "") -> Response:
    """Reenvía operaciones de backup, restore, optimización y esquemas hacia el microservicio admin."""
    target_path = f"/database/{sub_path}" if sub_path else "/database"
    return await proxy_request(request, SERVICES["admin"], target_path)
