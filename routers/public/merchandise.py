"""
Pilgrim Gateway - Conector Público de Mercancía
Enruta operaciones del catálogo de mercancía, carrito y compras.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

router = APIRouter(tags=["Público - Mercancía"])

@router.api_route("/api/merchandise", methods=["GET", "POST"])
@router.api_route("/api/merchandise/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def merchandise_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta mercancía hacia el microservicio correspondiente."""
    target_path = f"/{sub_path}" if sub_path else ""
    return await proxy_request(request, SERVICES["merchandise"], target_path)
