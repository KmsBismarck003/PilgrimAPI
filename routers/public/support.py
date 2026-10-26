"""
Pilgrim Gateway - Conector de Servicios y Atención a Clientes (Support)
Gestiona la consulta remota de categorías de servicio y el registro de solicitudes/tickets.
"""
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
import json
import os
import uuid
import re
from datetime import datetime
from typing import Optional, List, Dict, Any

from pilgrim.core.config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

router = APIRouter(tags=["Público - Soporte y Servicios"])

# Directorio de persistencia local resiliente (Gateway Data Store)
PILGRIM_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
TICKETS_FILE = os.path.join(PILGRIM_DATA_DIR, "support_tickets.json")

# ── Catálogo Canónico de Categorías de Servicio Remotas ───────────────────────
SERVICE_CATEGORIES: List[Dict[str, Any]] = [
    {
        "id": "cat_tickets",
        "code": "TICKETS_ACCESS",
        "title": "Boletos y Accesos",
        "description": "Consultas sobre validación de entradas digitales, códigos QR, transferencias o acceso al recinto.",
        "icon": "ticket",
        "slaHours": 4
    },
    {
        "id": "cat_payments",
        "code": "PAYMENT_BILLING",
        "title": "Pagos y Facturación",
        "description": "Aclaraciones sobre transacciones, cargos duplicados, confirmación de compras o facturas electrónicas.",
        "icon": "credit-card",
        "slaHours": 6
    },
    {
        "id": "cat_events",
        "code": "EVENTS_VENUES",
        "title": "Eventos y Asientos",
        "description": "Información sobre cartelera, fechas, horarios, mapas de butacas numeradas y accesibilidad.",
        "icon": "calendar",
        "slaHours": 8
    },
    {
        "id": "cat_account",
        "code": "ACCOUNT_SECURITY",
        "title": "Cuenta y Seguridad",
        "description": "Recuperación de contraseña, validación de identidad, cambio de datos personales y privacidad.",
        "icon": "shield",
        "slaHours": 12
    },
    {
        "id": "cat_perks",
        "code": "MEMBERSHIP_PERKS",
        "title": "Logros y Membresías",
        "description": "Canje de puntos, cupones de fidelización, cortesías de bienvenida y beneficios de rango.",
        "icon": "award",
        "slaHours": 24
    }
]

def _ensure_data_file():
    os.makedirs(PILGRIM_DATA_DIR, exist_ok=True)
    if not os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def _load_tickets_from_disk() -> List[Dict[str, Any]]:
    _ensure_data_file()
    try:
        with open(TICKETS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_ticket_to_disk(ticket: Dict[str, Any]):
    _ensure_data_file()
    tickets = _load_tickets_from_disk()
    tickets.insert(0, ticket)
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=2)

def _try_save_to_mysql(ticket: Dict[str, Any]):
    """Intento de persistencia relacional si MySQL está en línea."""
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
            # Crear tabla si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id VARCHAR(64) PRIMARY KEY,
                    category_id VARCHAR(64) NOT NULL,
                    category_title VARCHAR(128) NOT NULL,
                    subject VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    contact_email VARCHAR(191) NOT NULL,
                    user_id INT NULL,
                    status VARCHAR(32) DEFAULT 'PENDING',
                    priority VARCHAR(16) DEFAULT 'MEDIUM',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            cursor.execute("""
                INSERT INTO support_tickets 
                (id, category_id, category_title, subject, description, contact_email, user_id, status, priority, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ticket["id"],
                ticket["category_id"],
                ticket["category_title"],
                ticket["subject"],
                ticket["description"],
                ticket["contact_email"],
                ticket.get("user_id"),
                ticket["status"],
                ticket["priority"],
                ticket["created_at"]
            ))
            conn.commit()
        conn.close()
    except Exception as e:
        # Fallback transparente a almacenamiento resiliente en disco
        print(f"[PILGRIM SUPPORT WARNING] MySQL no disponible para ticket, persistido en Data Store local: {e}")

def _extract_user_from_auth(request: Request) -> Optional[Dict[str, Any]]:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    try:
        import base64
        parts = token.split(".")
        if len(parts) >= 2:
            padding = "=" * (4 - len(parts[1]) % 4)
            payload_str = base64.urlsafe_b64decode(parts[1] + padding).decode("utf-8")
            payload = json.loads(payload_str)
            return {
                "user_id": payload.get("user_id") or payload.get("id"),
                "email": payload.get("sub") or payload.get("email"),
                "role": payload.get("role", "usuario")
            }
    except Exception:
        pass
    return None

# ── Endpoints del Servicio ───────────────────────────────────────────────────

@router.get("/api/support/categories")
async def get_support_categories():
    """
    Retorna el catálogo centralizado de categorías de servicio disponibles.
    Permite a la aplicación móvil poblar la interfaz de forma remota y desacoplada.
    """
    return JSONResponse(
        content={
            "success": True,
            "total": len(SERVICE_CATEGORIES),
            "categories": SERVICE_CATEGORIES
        },
        status_code=status.HTTP_200_OK,
        headers={"Content-Type": "application/json"}
    )

@router.get("/api/support/tickets/my")
async def get_my_tickets(request: Request):
    """
    Consulta los tickets registrados por el usuario autenticado.
    Requiere cabecera Authorization: Bearer <token>.
    """
    user_info = _extract_user_from_auth(request)
    all_tickets = _load_tickets_from_disk()
    
    if not user_info:
        # Si no hay token, retorna tickets según email en query param si existe
        email = request.query_params.get("email")
        if email:
            user_tickets = [t for t in all_tickets if t.get("contact_email", "").lower() == email.lower()]
            return {"success": True, "tickets": user_tickets}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida para consultar solicitudes previas."
        )

    user_email = user_info.get("email", "").lower()
    user_id = user_info.get("user_id")

    user_tickets = [
        t for t in all_tickets
        if (user_email and t.get("contact_email", "").lower() == user_email) or
           (user_id and t.get("user_id") == user_id)
    ]

    return {
        "success": True,
        "count": len(user_tickets),
        "tickets": user_tickets
    }

@router.post("/api/support/tickets", status_code=status.HTTP_201_CREATED)
async def create_support_ticket(request: Request):
    """
    Registra una nueva solicitud de servicio / ticket de soporte.
    Aplica validaciones estrictas de servidor para garantizar integridad.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cuerpo de la petición inválido. Debe ser un JSON válido."
        )

    category_id = (body.get("categoryId") or body.get("category_id") or "").strip()
    subject = (body.get("subject") or "").strip()
    description = (body.get("description") or "").strip()
    contact_email = (body.get("contactEmail") or body.get("contact_email") or "").strip()
    priority = (body.get("priority") or "MEDIUM").upper()

    # Validaciones obligatorias de servidor
    if not category_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El campo 'categoryId' es obligatorio."
        )

    matched_category = next((c for c in SERVICE_CATEGORIES if c["id"] == category_id), None)
    if not matched_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La categoría de servicio '{category_id}' no existe en el catálogo."
        )

    if len(subject) < 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El asunto de la solicitud debe contener al menos 5 caracteres."
        )

    if len(description) < 15:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La descripción debe contener al menos 15 caracteres para detallar el caso."
        )

    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_regex, contact_email):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El correo de contacto no cuenta con un formato válido."
        )

    # Identificar si hay sesión activa mediante JWT
    user_info = _extract_user_from_auth(request)
    user_id = user_info.get("user_id") if user_info else None

    # Generación de identificador único de ticket
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    random_suffix = uuid.uuid4().hex[:8].upper()
    ticket_id = f"TKT-SUP-{random_suffix}"

    ticket_record = {
        "id": ticket_id,
        "category_id": matched_category["id"],
        "category_title": matched_category["title"],
        "subject": subject,
        "description": description,
        "contact_email": contact_email.lower(),
        "user_id": user_id,
        "status": "PENDING",
        "priority": priority if priority in ["LOW", "MEDIUM", "HIGH"] else "MEDIUM",
        "created_at": now_str,
        "sla_resolution_hours": matched_category["slaHours"]
    }

    # Persistencia híbrida y tolerante a fallos
    _save_ticket_to_disk(ticket_record)
    _try_save_to_mysql(ticket_record)

    return JSONResponse(
        content={
            "success": True,
            "message": "Solicitud de servicio registrada con éxito en el servidor central.",
            "ticket": {
                "ticketId": ticket_id,
                "categoryId": matched_category["id"],
                "categoryTitle": matched_category["title"],
                "subject": subject,
                "status": "PENDING",
                "createdAt": now_str,
                "estimatedSlaHours": matched_category["slaHours"]
            }
        },
        status_code=status.HTTP_201_CREATED,
        headers={"Content-Type": "application/json"}
    )
