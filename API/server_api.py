"""
API Unificada de Premios Nobel
Combina todas las funcionalidades de las Etapas 2, 3 y 4
Incluye consultas, modificaciones, autenticación y rate limiting
"""

from fastapi import FastAPI, HTTPException, status, Depends, Request
from typing import List, Optional, Dict, Any
import json
import os
import uvicorn
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Etapa1 import data_handler
from models import (
    PrizeBase, LaureateBase, PrizeCreate, PrizeUpdate, 
    SecurityInfo, APIStatus
)
from security_config import (
    get_current_user, require_admin, limiter, RATE_LIMITS
)
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# --- Configuración Inicial ---
app = FastAPI(
    title="API de Premios Nobel",
    version="3.0.0"
)

# Configurar rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

NOBEL_PRIZES_DATA: List[Dict[str, Any]] = []
LOCAL_JSON_FILE = "nobel_prizes.json"

@app.on_event("startup")
async def startup_event():
    """Función que se ejecuta al iniciar la aplicación FastAPI."""
    global NOBEL_PRIZES_DATA
    print("🚀 Iniciando API Unificada de Premios Nobel...")
    print("📊 Cargando datos de premios Nobel...")
    
    if not os.path.exists(LOCAL_JSON_FILE):
        print(f"📥 El archivo '{LOCAL_JSON_FILE}' no se encontró. Descargando...")
        if not data_handler.download_nobel_prizes_data():
            print("❌ ERROR: No se pudieron descargar los datos. La API funcionará sin datos.")
            NOBEL_PRIZES_DATA = []
            return

    NOBEL_PRIZES_DATA = data_handler.load_nobel_prizes_data()
    if not NOBEL_PRIZES_DATA:
        print("⚠️ ADVERTENCIA: Se cargó una lista vacía de premios.")
    else:
        print(f"✅ Se cargaron {len(NOBEL_PRIZES_DATA)} premios Nobel exitosamente.")
    print("🔐 Seguridad habilitada: Autenticación Basic + Rate Limiting")
    print("🌐 API lista en: http://localhost:8001")

def save_nobel_prizes_data_to_file():
    """Guarda el estado actual de NOBEL_PRIZES_DATA en el archivo JSON local."""
    try:
        data_to_save = {"prizes": NOBEL_PRIZES_DATA}
        with open(LOCAL_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        return True
    except IOError as e:
        print(f"❌ ERROR: No se pudo guardar los datos: {e}")
        return False

# --- Endpoints de Información y Estado ---

@app.get("/", response_model=APIStatus, tags=["Información"])
@limiter.limit(RATE_LIMITS["default"])
async def read_root(request: Request):
    """
    Endpoint raíz de la API Unificada.
    Proporciona información del estado de la API.
    """
    return APIStatus(
        status="active",
        version="3.0.0",
        total_prizes=len(NOBEL_PRIZES_DATA),
        security_enabled=True,
        message="¡Bienvenido a la API Unificada de Premios Nobel! Accede a /docs para ver la documentación completa."
    )

@app.get("/security/info", response_model=SecurityInfo, tags=["Seguridad"])
@limiter.limit(RATE_LIMITS["default"])
async def get_security_info(request: Request):
    """
    Retorna información detallada sobre la configuración de seguridad de la API.
    """
    return SecurityInfo(
        authentication="HTTP Basic Authentication",
        rate_limits=RATE_LIMITS,
        protected_endpoints={
            "POST": ["/prizes"],
            "PUT": ["/prizes/{year}/{category}"],
            "DELETE": ["/prizes/{year}/{category}"]
        },
        admin_only=["DELETE /prizes/{year}/{category}"],
        message="Los endpoints POST, PUT y DELETE requieren autenticación. DELETE requiere permisos de administrador."
    )

# --- Endpoints de Consulta (GET) - Sin autenticación ---

@app.get("/prizes", response_model=List[PrizeBase], tags=["Consultas"])
@limiter.limit(RATE_LIMITS["default"])
async def get_all_nobel_prizes(request: Request):
    """
    Retorna todos los premios Nobel disponibles.
    """
    if not NOBEL_PRIZES_DATA:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se encontraron datos de premios Nobel."
        )
    return NOBEL_PRIZES_DATA

@app.get("/prizes/year/{year}", response_model=List[PrizeBase], tags=["Consultas"])
@limiter.limit(RATE_LIMITS["default"])
async def get_prizes_by_year(request: Request, year: str):
    """
    Retorna los premios Nobel de un año específico.
    """
    prizes = data_handler.get_prize_by_year(NOBEL_PRIZES_DATA, year)
    if not prizes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No se encontraron premios para el año {year}."
        )
    return prizes

@app.get("/prizes/category/{category}", response_model=List[PrizeBase], tags=["Consultas"])
@limiter.limit(RATE_LIMITS["default"])
async def get_prizes_by_category(request: Request, category: str):
    """
    Retorna los premios Nobel de una categoría específica.
    """
    prizes = data_handler.get_prize_by_category(NOBEL_PRIZES_DATA, category)
    if not prizes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No se encontraron premios para la categoría '{category}'."
        )
    return prizes

@app.get("/prizes/motivation/{year}/{category}", response_model=Optional[str], tags=["Consultas"])
@limiter.limit(RATE_LIMITS["default"])
async def get_prize_motivation(request: Request, year: str, category: str):
    """
    Retorna la motivación general de un premio específico por año y categoría.
    """
    motivation = data_handler.get_prize_motivation(NOBEL_PRIZES_DATA, year, category)
    if motivation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No se encontró el premio de {category.capitalize()} en {year} o no tiene motivación general."
        )
    return motivation

@app.get("/laureates/search", response_model=List[PrizeBase], tags=["Laureados"])
@limiter.limit(RATE_LIMITS["default"])
async def search_laureates(request: Request, firstname: str, surname: str):
    """
    Busca premios en los que un laureado específico esté involucrado.
    """
    found_prizes = data_handler.find_laureate_by_name(NOBEL_PRIZES_DATA, firstname, surname)
    if not found_prizes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No se encontraron premios para el laureado '{firstname} {surname}'."
        )
    return found_prizes

@app.get("/laureates/{year}/{category}", response_model=List[LaureateBase], tags=["Laureados"])
@limiter.limit(RATE_LIMITS["default"])
async def get_laureates_by_year_category(request: Request, year: str, category: str):
    """
    Obtiene los laureados de un premio específico por año y categoría.
    """
    laureates = data_handler.get_laureates_by_year_and_category(NOBEL_PRIZES_DATA, year, category)
    if not laureates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No se encontraron laureados para el premio de {category.capitalize()} en {year}."
        )
    return laureates

# --- Endpoints de Modificación (POST/PUT/DELETE) - Con autenticación ---

@app.post("/prizes", response_model=PrizeBase, status_code=status.HTTP_201_CREATED, tags=["Modificaciones"])
@limiter.limit(RATE_LIMITS["strict"])
async def create_nobel_prize(
    request: Request,
    prize: PrizeCreate,
    current_user: Dict = Depends(get_current_user)
):
    """
    Crea un nuevo premio Nobel.
    
    **Requiere autenticación Basic.**
    
    - Usuario normal: puede crear premios
    - Administrador: puede crear premios
    """
    # Verificar si ya existe un premio con el mismo año y categoría
    for existing_prize in NOBEL_PRIZES_DATA:
        if (existing_prize.get("year") == prize.year and
                existing_prize.get("category", "").lower() == prize.category.lower()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un premio en el año {prize.year} para la categoría '{prize.category}'."
            )

    new_prize_data = prize.model_dump(exclude_unset=True)
    
    # Generar IDs para los laureados si no vienen
    for laureate in new_prize_data.get("laureates", []):
        if "id" not in laureate or not laureate["id"]:
            laureate["id"] = f"{laureate.get('firstname', '')}{laureate.get('surname', '')}{prize.year}".replace(" ", "").lower()
            if not laureate["id"]:
                laureate["id"] = str(hash(json.dumps(laureate) + str(len(NOBEL_PRIZES_DATA))))

    NOBEL_PRIZES_DATA.append(new_prize_data)

    if not save_nobel_prizes_data_to_file():
        print("⚠️ ADVERTENCIA: No se pudo guardar el nuevo premio en el archivo JSON.")

    return new_prize_data

@app.put("/prizes/{year}/{category}", response_model=PrizeBase, tags=["Modificaciones"])
@limiter.limit(RATE_LIMITS["strict"])
async def update_nobel_prize(
    request: Request,
    year: str, 
    category: str, 
    prize_update: PrizeUpdate,
    current_user: Dict = Depends(get_current_user)
):
    """
    Actualiza un premio Nobel existente por año y categoría.
    
    **Requiere autenticación Basic.**
    
    - Usuario normal: puede actualizar premios
    - Administrador: puede actualizar premios
    """
    target_category = category.lower()
    found_index = -1
    for i, prize in enumerate(NOBEL_PRIZES_DATA):
        if prize.get("year") == year and prize.get("category", "").lower() == target_category:
            found_index = i
            break

    if found_index == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el premio de '{category}' en el año {year}."
        )

    existing_prize = NOBEL_PRIZES_DATA[found_index]
    update_data = prize_update.model_dump(exclude_unset=True)
    
    if "laureates" in update_data and update_data["laureates"] is not None:
        existing_prize["laureates"] = update_data["laureates"]
        for laureate in existing_prize.get("laureates", []):
            if "id" not in laureate or not laureate["id"]:
                laureate["id"] = f"{laureate.get('firstname', '')}{laureate.get('surname', '')}{existing_prize.get('year', '')}".replace(" ", "").lower()
                if not laureate["id"]:
                    laureate["id"] = str(hash(json.dumps(laureate) + str(len(NOBEL_PRIZES_DATA))))
        del update_data["laureates"]

    existing_prize.update(update_data)

    if not save_nobel_prizes_data_to_file():
        print("⚠️ ADVERTENCIA: No se pudieron guardar las actualizaciones en el archivo JSON.")

    return existing_prize

@app.delete("/prizes/{year}/{category}", status_code=status.HTTP_204_NO_CONTENT, tags=["Modificaciones"])
@limiter.limit(RATE_LIMITS["strict"])
async def delete_nobel_prize(
    request: Request,
    year: str, 
    category: str,
    current_user: Dict = Depends(require_admin)
):
    """
    Elimina un premio Nobel específico por año y categoría.
    
    **Requiere autenticación Basic con permisos de administrador.**
    
    - Usuario normal: ❌ NO puede eliminar premios
    - Administrador: ✅ Puede eliminar premios
    """
    global NOBEL_PRIZES_DATA
    target_category = category.lower()
    initial_len = len(NOBEL_PRIZES_DATA)
    
    NOBEL_PRIZES_DATA = [
        p for p in NOBEL_PRIZES_DATA
        if not (p.get("year") == year and p.get("category", "").lower() == target_category)
    ]

    if len(NOBEL_PRIZES_DATA) == initial_len:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el premio de '{category}' en el año {year} para eliminar."
        )

    if not save_nobel_prizes_data_to_file():
        print("⚠️ ADVERTENCIA: No se pudo guardar la eliminación en el archivo JSON.")
    
    return None

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)