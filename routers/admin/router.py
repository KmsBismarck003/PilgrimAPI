"""
Pilgrim Gateway - Router Principal del Rol ADMIN
Punto de agregación central para todos los conectores del Administrador.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

from .database import router as database_router
from .users import router as users_router
from .ads import router as ads_router
from .config import router as config_router
from .audit import router as audit_router
from .b2b import router as b2b_router
from .monitoring import router as monitoring_router
from .content import router as content_router

admin_router = APIRouter()

# Incluir sub-módulos ordenados de Admin
admin_router.include_router(database_router)
admin_router.include_router(users_router)
admin_router.include_router(ads_router)
admin_router.include_router(config_router)
admin_router.include_router(audit_router)
admin_router.include_router(b2b_router)
admin_router.include_router(monitoring_router)
admin_router.include_router(content_router)

# ─── Endpoints de Analítica y Big Data para Admin ──────────────────────────────
@admin_router.api_route("/api/analytics", methods=["GET", "POST", "DELETE", "PUT", "PATCH"])
@admin_router.api_route("/api/analytics/{sub_path:path}", methods=["GET", "POST", "DELETE", "PUT", "PATCH"])
async def analytics_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta peticiones de Machine Learning hacia analytics."""
    target_path = f"/api/analytics/{sub_path}" if sub_path else "/api/analytics"
    return await proxy_request(request, SERVICES["analytics"], target_path)

@admin_router.api_route("/api/bigdata", methods=["GET", "POST", "DELETE", "PUT", "PATCH"])
@admin_router.api_route("/api/bigdata/{sub_path:path}", methods=["GET", "POST", "DELETE", "PUT", "PATCH"])
async def bigdata_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta peticiones de Big Data hacia analytics_bigdata."""
    target_path = f"/api/analytics/{sub_path}" if sub_path else "/api/analytics"
    return await proxy_request(request, SERVICES["analytics_bigdata"], target_path)

# ─── Endpoints de Estadísticas de Admin ───────────────────────────────────────
@admin_router.api_route("/api/stats/admin", methods=["GET"])
@admin_router.api_route("/api/stats/admin/{sub_path:path}", methods=["GET", "POST"])
async def stats_admin_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta estadísticas exclusivas de administración hacia el microservicio de stats."""
    target_path = f"/admin/{sub_path}" if sub_path else "/admin"
    return await proxy_request(request, SERVICES["stats"], target_path)

# ─── Endpoints de Mercancía (Aprobación Admin) ────────────────────────────────
@admin_router.api_route("/api/merchandise", methods=["GET", "POST", "PUT", "DELETE"])
@admin_router.api_route("/api/merchandise/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def merch_proxy(request: Request, sub_path: str = "") -> Response:
    target_path = f"/{sub_path}" if sub_path else ""
    return await proxy_request(request, SERVICES["merchandise"], target_path)

# ─── Reenvío genérico de /api/admin/{sub_path:path} hacia Microservicio Admin ──
@admin_router.api_route("/api/admin/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def fallback_admin_proxy(request: Request, sub_path: str = "") -> Response:
    """Captura cualquier ruta adicional de admin y la despacha al microservicio admin."""
    if sub_path.startswith("uploads"):
        target_path = f"/{sub_path}"
    else:
        target_path = f"/admin/{sub_path}"
    return await proxy_request(request, SERVICES["admin"], target_path)

@admin_router.api_route("/api/admin", methods=["GET", "POST"])
async def root_admin_proxy(request: Request) -> Response:
    return await proxy_request(request, SERVICES["admin"], "")
