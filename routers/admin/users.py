"""
Pilgrim Gateway - Conector de Gestión de Usuarios para Admin
Enruta operaciones CRUD de usuarios, permisos, reseteo de claves y avatares hacia el microservicio de Auth.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

router = APIRouter(tags=["Admin - Usuarios"])

@router.api_route("/api/admin/users", methods=["GET", "POST"])
@router.api_route("/api/admin/users/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def admin_users_proxy(request: Request, sub_path: str = "") -> Response:
    """Reenvía la gestión de usuarios hacia el microservicio de Auth (/admin/users)."""
    target_path = f"/admin/users/{sub_path}" if sub_path else "/admin/users"
    return await proxy_request(request, SERVICES["auth"], target_path)

@router.api_route("/api/users", methods=["GET", "POST"])
@router.api_route("/api/users/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def users_proxy(request: Request, sub_path: str = "") -> Response:
    """Reenvía endpoints de usuarios genéricos hacia Auth."""
    target_path = f"/users/{sub_path}" if sub_path else "/users"
    return await proxy_request(request, SERVICES["auth"], target_path)
