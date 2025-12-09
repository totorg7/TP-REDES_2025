"""
Configuración de seguridad para la API Unificada de Premios Nobel
Incluye autenticación Basic y rate limiting
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configuración de autenticación Basic
security = HTTPBasic()

# Configuración de rate limiting
limiter = Limiter(key_func=get_remote_address)

# Credenciales de usuario (en producción, esto debería estar en una base de datos)
USERS = {
    "admin": {
        "username": "admin",
        "password": "admin123",  # En producción, usar hash bcrypt
        "role": "admin"
    },
    "user": {
        "username": "user", 
        "password": "user123",
        "role": "user"
    }
}

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Verifica las credenciales del usuario y retorna el usuario autenticado.
    """
    username = credentials.username
    password = credentials.password
    
    if username not in USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    user = USERS[username]
    if not secrets.compare_digest(password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user

def require_admin(user: Dict = Depends(get_current_user)):
    """
    Verifica que el usuario tenga rol de administrador.
    """
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return user

# Límites de rate limiting
RATE_LIMITS = {
    "default": "100/minute",      # Límite por defecto
    "admin": "200/minute",        # Límite para administradores
    "user": "50/minute",          # Límite para usuarios normales
    "strict": "10/minute"         # Límite estricto para operaciones sensibles
}

def get_rate_limit_for_user(user: Optional[Dict] = None) -> str:
    """
    Retorna el límite de rate limiting apropiado para el usuario.
    """
    if user and user["role"] == "admin":
        return RATE_LIMITS["admin"]
    elif user:
        return RATE_LIMITS["user"]
    else:
        return RATE_LIMITS["default"] 