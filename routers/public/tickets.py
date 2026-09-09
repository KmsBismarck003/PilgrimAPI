"""
Pilgrim Gateway - Conector Público de Tickets, Pagos y Reembolsos
Enruta compras, checkout, validación de cupones y devoluciones hacia el microservicio de tickets.
"""
from fastapi import APIRouter, Request, Response
from pilgrim.core.config import SERVICES
from pilgrim.core.proxy import proxy_request

router = APIRouter(tags=["Público - Tickets y Pagos"])

@router.api_route("/api/tickets", methods=["GET", "POST"])
@router.api_route("/api/tickets/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def tickets_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta operaciones de tickets hacia el microservicio de tickets."""
    target_path = f"/{sub_path}" if sub_path else ""
    return await proxy_request(request, SERVICES["tickets"], target_path)

@router.api_route("/api/payments", methods=["GET", "POST"])
@router.api_route("/api/payments/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def payments_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta pasarela de pagos hacia el microservicio de tickets (/payments)."""
    target_path = f"/payments/{sub_path}" if sub_path else "/payments"
    return await proxy_request(request, SERVICES["tickets"], target_path)

@router.api_route("/api/refunds", methods=["GET", "POST"])
@router.api_route("/api/refunds/{sub_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def refunds_proxy(request: Request, sub_path: str = "") -> Response:
    """Enruta solicitudes de reembolso hacia el microservicio de tickets (/refund)."""
    target_path = f"/refund/{sub_path}" if sub_path else "/refund"
    return await proxy_request(request, SERVICES["tickets"], target_path)
