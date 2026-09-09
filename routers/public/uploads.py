"""
Pilgrim Gateway - Conector de Archivos Estáticos y Subidas (Uploads)
Enruta descarga y carga de imágenes de anuncios, avatares, comprobantes y mapas.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

router = APIRouter(tags=["Archivos y Uploads"])

@router.api_route("/api/admin/uploads", methods=["GET", "POST"])
@router.api_route("/api/admin/uploads/{file_path:path}", methods=["GET", "POST", "DELETE"])
async def admin_uploads_proxy(request: Request, file_path: str = "") -> Response:
    """Enruta subidas administrativas hacia el microservicio admin."""
    target_path = f"/uploads/{file_path}" if file_path else "/uploads"
    return await proxy_request(request, SERVICES["admin"], target_path)

@router.api_route("/api/uploads", methods=["GET", "POST"])
@router.api_route("/api/uploads/{file_path:path}", methods=["GET", "POST", "DELETE"])
async def api_uploads_proxy(request: Request, file_path: str = "") -> Response:
    """Enruta archivos subidos hacia el microservicio admin."""
    target_path = f"/uploads/{file_path}" if file_path else "/uploads"
    return await proxy_request(request, SERVICES["admin"], target_path)

@router.api_route("/uploads/{file_path:path}", methods=["GET"])
async def raw_uploads_proxy(request: Request, file_path: str = "") -> Response:
    """Acceso público a archivos estáticos subidos."""
    target_path = f"/uploads/{file_path}" if file_path else "/uploads"
    return await proxy_request(request, SERVICES["admin"], target_path, cacheable=True)
