"""
Pilgrim Gateway - Conector B2B Corporativo para Admin
Gestiona organizaciones aliadas, contratos corporativos y gestores asignados.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

router = APIRouter(tags=["Admin - B2B"])

@router.api_route("/api/admin/b2b", methods=["GET", "POST"])
@router.api_route("/api/admin/b2b/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def admin_b2b_proxy(request: Request, sub_path: str = "") -> Response:
    target_path = f"/admin/b2b/{sub_path}" if sub_path else "/admin/b2b"
    return await proxy_request(request, SERVICES["admin"], target_path)

@router.api_route("/api/b2b", methods=["GET", "POST"])
@router.api_route("/api/b2b/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def b2b_proxy(request: Request, sub_path: str = "") -> Response:
    target_path = f"/admin/b2b/{sub_path}" if sub_path else "/admin/b2b"
    return await proxy_request(request, SERVICES["admin"], target_path)
