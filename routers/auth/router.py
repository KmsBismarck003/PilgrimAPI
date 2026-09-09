"""
Pilgrim Gateway - Router de Autenticación Central (Auth)
Enruta login, verify, logout, registro y auditoría hacia el microservicio de Auth.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

auth_router = APIRouter(tags=["Autenticación"])

@auth_router.api_route("/api/auth", methods=["GET", "POST"])
@auth_router.api_route("/api/auth/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def auth_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta cualquier llamada de autenticación directamente al microservicio de Auth."""
    target_path = f"/{sub_path}" if sub_path else ""
    return await proxy_request(request, SERVICES["auth"], target_path)
