"""
Pilgrim Gateway - Conector de Analítica y Módulo MATIS
Enruta peticiones de inteligencia de negocios (MATIS Big Data) y analítica general.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

router = APIRouter(tags=["Público - Analítica y MATIS"])

@router.api_route("/api/analytics/matis", methods=["GET", "POST"])
@router.api_route("/api/analytics/matis/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def matis_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta peticiones del módulo MATIS hacia el microservicio BigData (Python / Spark)."""
    target_path = f"/api/analytics/matis/{sub_path}" if sub_path else "/api/analytics/matis"
    return await proxy_request(request, SERVICES["analytics_bigdata"], target_path)

@router.api_route("/api/analytics", methods=["GET", "POST"])
@router.api_route("/api/analytics/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def analytics_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta analítica hacia BigData (Python / Spark) o Java Analytics según corresponda."""
    target_path = f"/api/analytics/{sub_path}" if sub_path else "/api/analytics"
    
    if (sub_path.startswith("matis") or 
        sub_path.startswith("ml") or 
        sub_path.startswith("vault") or
        sub_path.startswith("scrape") or
        sub_path in ["3d", "predict", "anomalies", "clean", "full", "incremental", "status"]):
        return await proxy_request(request, SERVICES["analytics_bigdata"], target_path)
    
    resp = await proxy_request(request, SERVICES["analytics_bigdata"], target_path)
    if resp.status_code == 404:
        return await proxy_request(request, SERVICES["analytics"], target_path)
    return resp
