"""
Pilgrim Gateway - Conector de Auditoría y Trazabilidad para Admin
Enruta auditorías de recuperación de desastres, logs de peticiones y auditoría de accesos.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

router = APIRouter(tags=["Admin - Auditoría y Logs"])

@router.api_route("/api/restore-audit", methods=["GET", "POST"])
@router.api_route("/api/restore-audit/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def restore_audit_proxy(request: Request, sub_path: str = "") -> Response:
    target_path = f"/restore-audit/{sub_path}" if sub_path else "/restore-audit"
    return await proxy_request(request, SERVICES["admin"], target_path)

@router.api_route("/api/logs", methods=["GET", "POST"])
@router.api_route("/api/logs/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def logs_proxy(request: Request, sub_path: str = "") -> Response:
    target_path = f"/logs/{sub_path}" if sub_path else "/logs"
    return await proxy_request(request, SERVICES["admin"], target_path)

@router.api_route("/api/admin/logs", methods=["GET", "POST"])
@router.api_route("/api/admin/logs/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def admin_logs_proxy(request: Request, sub_path: str = "") -> Response:
    target_path = f"/logs/{sub_path}" if sub_path else "/logs"
    return await proxy_request(request, SERVICES["admin"], target_path)
