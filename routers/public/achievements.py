"""
Pilgrim Gateway - Conector de Logros, Recompensas y Gamificación
Enruta logros, insignias, cupones y validación de fidelidad hacia el microservicio de achievements.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

router = APIRouter(tags=["Público - Logros y Fidelidad"])

@router.api_route("/api/achievements", methods=["GET", "POST"])
@router.api_route("/api/achievements/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def achievements_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta operaciones de logros hacia el microservicio de achievements."""
    target_path = f"/{sub_path}" if sub_path else ""
    return await proxy_request(request, SERVICES["achievements"], target_path)
