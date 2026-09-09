from .admin import admin_router
from .auth import auth_router
from .gestor import gestor_router
from .operador import operador_router
from .public import public_router

__all__ = [
    "admin_router",
    "auth_router",
    "gestor_router",
    "operador_router",
    "public_router"
]
