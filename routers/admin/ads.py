"""
Pilgrim Gateway - Conector de Publicidad y Banners para Admin
Gestiona anuncios, subida de creativos y métricas hacia el microservicio admin.
"""
from fastapi import APIRouter, Request, Response
import json
from pilgrim.core.config import SERVICES, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
from pilgrim.core.proxy import proxy_request

router = APIRouter(tags=["Admin - Publicidad"])

@router.get("/api/ads/public")
async def public_ads(request: Request) -> Response:
    """Obtiene anuncios públicos activos."""
    try:
        import pymysql
        conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset="utf8mb4",
            connect_timeout=2,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT a.id, a.title, a.image_url, a.link_url, a.position, a.active, a.event_id 
                FROM ads a 
                LEFT JOIN events e ON a.event_id = e.id 
                WHERE a.active = 1 
                  AND (a.event_id IS NULL OR (e.status = 'published' AND e.ads_enabled = 1))
                ORDER BY a.id DESC
            """)
            rows = cursor.fetchall()
        conn.close()
        for r in rows:
            r['active'] = bool(r.get('active', 0))
        return Response(
            content=json.dumps(rows, default=str),
            status_code=200,
            headers={"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        print(f"[PILGRIM ADS FALLBACK] Error conectando a DB directa, reenviando a microservicio: {e}")
        return await proxy_request(request, SERVICES["admin"], "/ads/public", cacheable=True)

@router.api_route("/api/ads", methods=["GET", "POST"])
@router.api_route("/api/ads/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def ads_proxy(request: Request, sub_path: str = "") -> Response:
    target_path = f"/ads/{sub_path}" if sub_path else "/ads"
    return await proxy_request(request, SERVICES["admin"], target_path)

@router.api_route("/api/admin/ads", methods=["GET", "POST"])
@router.api_route("/api/admin/ads/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def admin_ads_proxy(request: Request, sub_path: str = "") -> Response:
    target_path = f"/ads/{sub_path}" if sub_path else "/ads"
    return await proxy_request(request, SERVICES["admin"], target_path)
