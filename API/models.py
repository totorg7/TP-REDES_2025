from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class LaureateBase(BaseModel):
    """Modelo base para un Laureado."""
    id: Optional[str] = None
    firstname: str = Field(..., example="Marie", description="Nombre del laureado")
    surname: Optional[str] = Field(None, example="Curie", description="Apellido del laureado")
    motivation: Optional[str] = Field(None, example="for her joint research on the radiation phenomena", description="Motivación específica del laureado")
    share: Optional[str] = Field(None, example="1", description="Porcentaje o fracción de premio compartido")

class PrizeBase(BaseModel):
    """Modelo base para un Premio Nobel."""
    year: str = Field(..., example="2025", description="Año del premio")
    category: str = Field(..., example="chemistry", description="Categoría del premio (ej. physics, chemistry, peace)")
    laureates: Optional[List[LaureateBase]] = Field(None, description="Lista de laureados asociados al premio")
    overallMotivation: Optional[str] = Field(None, example="for the discovery of a new form of energy", description="Motivación general del premio")

class PrizeCreate(PrizeBase):
    """Modelo para crear un nuevo Premio Nobel."""
    pass

class PrizeUpdate(BaseModel):
    """Modelo para actualizar un Premio Nobel. Todos los campos son opcionales."""
    year: Optional[str] = Field(None, example="2025", description="Año del premio")
    category: Optional[str] = Field(None, example="chemistry", description="Categoría del premio")
    laureates: Optional[List[LaureateBase]] = Field(None, description="Lista de laureados")
    overallMotivation: Optional[str] = Field(None, example="for a groundbreaking discovery in AI", description="Motivación general")

class SecurityInfo(BaseModel):
    """Modelo para información de seguridad."""
    authentication: str = Field(..., description="Tipo de autenticación")
    rate_limits: Dict[str, str] = Field(..., description="Límites de rate limiting")
    protected_endpoints: Dict[str, List[str]] = Field(..., description="Endpoints protegidos")
    admin_only: List[str] = Field(..., description="Endpoints solo para administradores")
    message: str = Field(..., description="Mensaje informativo")

class APIStatus(BaseModel):
    """Modelo para el estado de la API."""
    status: str = Field(..., description="Estado de la API")
    version: str = Field(..., description="Versión de la API")
    total_prizes: int = Field(..., description="Total de premios cargados")
    security_enabled: bool = Field(..., description="Si la seguridad está habilitada")
    message: str = Field(..., description="Mensaje de bienvenida") 