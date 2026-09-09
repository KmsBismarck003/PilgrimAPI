"""
Pilgrim Gateway - Conector de Configuración del Sistema para Admin
Gestiona banderas de características (feature flags), parámetros globales y algoritmos (Lucky Seat).
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

router = APIRouter(tags=["Admin - Configuración"])

@router.api_route("/api/config", methods=["GET", "PUT", "POST"])
@router.api_route("/api/config/{sub_path:path}", methods=["GET", "PUT", "POST", "DELETE", "PATCH"])
async def config_proxy(request: Request, sub_path: str = "") -> Response:
    target_path = f"/config/{sub_path}" if sub_path else "/config"
    return await proxy_request(request, SERVICES["admin"], target_path)

@router.api_route("/api/admin/config", methods=["GET", "PUT", "POST"])
@router.api_route("/api/admin/config/{sub_path:path}", methods=["GET", "PUT", "POST", "DELETE", "PATCH"])
async def admin_config_proxy(request: Request, sub_path: str = "") -> Response:
    target_path = f"/config/{sub_path}" if sub_path else "/config"
    return await proxy_request(request, SERVICES["admin"], target_path)
