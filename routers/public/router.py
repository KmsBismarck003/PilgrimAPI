"""
Pilgrim Gateway - Router Principal de Recursos Públicos
Agrupa los conectores de eventos, boletos, estadísticas, logros y archivos.
"""
from fastapi import APIRouter
from .events import router as events_router
from .tickets import router as tickets_router
from .stats import router as stats_router
from .achievements import router as achievements_router
from .uploads import router as uploads_router
from .merchandise import router as merchandise_router
from .support import router as support_router

public_router = APIRouter()

public_router.include_router(events_router)
public_router.include_router(tickets_router)
public_router.include_router(stats_router)
public_router.include_router(achievements_router)
public_router.include_router(uploads_router)
public_router.include_router(merchandise_router)
public_router.include_router(support_router)

