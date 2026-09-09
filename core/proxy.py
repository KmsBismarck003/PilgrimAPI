"""
Pilgrim API Gateway - Motor de Reenvío (Proxy Engine)
Reenvía peticiones HTTP de forma asíncrona hacia los microservicios internos.
"""
from fastapi import Request, Response
import httpx
import traceback
from .config import PROXY_TIMEOUT, CACHE_TTL
from .cache import get_cached_response, set_cached_response

HOP_BY_HOP_REQUEST_HEADERS = {"host", "content-length", "connection"}
HOP_BY_HOP_RESPONSE_HEADERS = {"content-encoding", "transfer-encoding", "content-length"}

async def proxy_request(
    request: Request,
    target_base_url: str,
    target_path: str,
    cacheable: bool = False,
    override_method: str = None
) -> Response:
    """
    Reenvía una petición HTTP entrante hacia el microservicio correspondiente.
    """
    method = override_method or request.method
    base_target_url = f"{target_base_url.rstrip('/')}/{target_path.lstrip('/')}"
    query_str = str(request.query_params)
    cache_key = f"{base_target_url}?{query_str}" if query_str else base_target_url

    # Verificación de Caché pública (Solo GET)
    if method == "GET" and cacheable:
        cached = get_cached_response(cache_key)
        if cached:
            return Response(
                content=cached["content"],
                status_code=cached["status"],
                headers=cached["headers"]
            )

    # Filtrar headers de la petición entrante
    forward_headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in HOP_BY_HOP_REQUEST_HEADERS
    }

    try:
        content = await request.body()
        
        timeout_config = httpx.Timeout(PROXY_TIMEOUT, connect=3.0)
        async with httpx.AsyncClient(timeout=timeout_config) as client:
            resp = await client.request(
                method=method,
                url=base_target_url,
                params=dict(request.query_params),
                headers=forward_headers,
                content=content if method in ["POST", "PUT", "PATCH", "DELETE"] else None
            )

            # Filtrar headers de respuesta
            resp_headers = {
                k: v for k, v in resp.headers.items()
                if k.lower() not in HOP_BY_HOP_RESPONSE_HEADERS
            }

            resp_content = resp.content
            resp_status = resp.status_code

            # Actualizar caché si aplica
            if method == "GET" and cacheable and resp_status == 200:
                set_cached_response(cache_key, resp_content, resp_status, resp_headers, ttl=CACHE_TTL)

            return Response(
                content=resp_content,
                status_code=resp_status,
                headers=resp_headers
            )

    except httpx.ConnectError:
        return Response(
            content=f'{{"detail": "Pilgrim Gateway: No se pudo conectar al microservicio destino ({target_base_url})"}}',
            status_code=502,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        tb = traceback.format_exc()
        return Response(
            content=f'{{"detail": "Pilgrim Gateway Error: {str(e)}", "traceback": "{tb}"}}',
            status_code=502,
            headers={"Content-Type": "application/json"}
        )
