# ✅ VERIFICACIÓN DETALLADA DE CONSIGNAS - API UNIFICADA

## 📋 **ETAPA 1: Elección y consulta de los datos**

### ✅ **Consigna Cumplida: Elección del archivo JSON**
- **Archivo elegido**: `nobel_prizes.json` de la API oficial de Premios Nobel
- **URL fuente**: `https://api.nobelprize.org/v1/prize.json`
- **Descripción**: Archivo JSON que contiene todos los premios Nobel otorgados

### ✅ **Programa Python para descargar y leer**
**Archivo**: `Etapa1/data_handler.py`

**Funciones implementadas**:
- `download_nobel_prizes_data()`: Descarga el archivo JSON desde la URL oficial
- `load_nobel_prizes_data()`: Lee y carga los datos del archivo JSON local
- `describe_data_structure()`: Analiza y describe la estructura del archivo

### ✅ ** Consultas a los datos**
**Funciones de consulta implementadas**:
- `get_all_prizes()`: Obtiene todos los premios
- `get_prize_by_year()`: Busca premios por año específico
- `get_prize_by_category()`: Busca premios por categoría
- `get_prize_motivation()`: Obtiene motivación de un premio específico
- `find_laureate_by_name()`: Busca premios por nombre de laureado
- `get_laureates_by_year_and_category()`: Obtiene laureados por año y categoría


## 🖥️ ** Desarrollar el servidor API**

### ✅ **Investigación de módulos**
**Módulos utilizados**:
- `fastapi`: Framework para crear APIs REST
- `uvicorn`: Servidor ASGI para ejecutar FastAPI
- `requests`: Para descargar datos (en data_handler.py)

### ✅ **Servidor API funcional**
**Archivo**: `API/server_api.py`

**Funcionalidades del servidor**:
1. **Gestión de consultas** (GET endpoints):
   - `/prizes` - Todos los premios
   - `/prizes/year/{year}` - Premios por año
   - `/prizes/category/{category}` - Premios por categoría
   - `/prizes/motivation/{year}/{category}` - Motivación específica
   - `/laureates/search` - Búsqueda por nombre de laureado
   - `/laureates/{year}/{category}` - Laureados por año y categoría

2. **Gestión de modificaciones** (POST/PUT/DELETE endpoints):
   - `POST /prizes` - Crear nuevo premio
   - `PUT /prizes/{year}/{category}` - Actualizar premio existente
   - `DELETE /prizes/{year}/{category}` - Eliminar premio



### ✅ **Datos que permite cambiar**
- **Crear**: Nuevos premios Nobel con año, categoría, motivación y laureados
- **Actualizar**: Cualquier campo de un premio existente (año, categoría, motivación, laureados)
- **Eliminar**: Premios completos por año y categoría

---

## 💻 **Desarrollar el cliente API**

### ✅ **Cliente API funcional**
**Archivo**: `API/client_api.py`

**Funcionalidades del cliente**:
1. **Operaciones de consulta** (sin autenticación):
   - Obtener todos los premios
   - Buscar por año
   - Buscar por categoría
   - Obtener motivación específica
   - Buscar por nombre de laureado
   - Obtener laureados por año y categoría

2. **Operaciones de modificación** (con autenticación):
   - Crear nuevos premios
   - Actualizar premios existentes
   - Eliminar premios

### ✅ **Verificación de funcionamiento**
**Características del cliente**:
- Interfaz de menú interactivo
- Manejo de errores HTTP
- Respuestas JSON formateadas
- Autenticación automática para operaciones protegidas
- Confirmación para operaciones destructivas

---

## 🔐 **Configuraciones de seguridad**

### ✅ **Consigna Cumplida: Autenticación Basic para POST y DELETE**
**Archivo**: `API/security_config.py`

**Implementación**:
- Autenticación HTTP Basic implementada
- **POST endpoints**: Requieren autenticación
- **DELETE endpoints**: Requieren permisos de administrador
- **GET endpoints**: Sin autenticación (acceso libre)

**Credenciales configuradas**:
- Usuario normal: `user` / `user123`
- Administrador: `admin` / `admin123`

### ✅ ** Política de limitación de solicitudes**
**Implementación**: Rate limiting con `slowapi`

**Límites configurados**:
- **Por defecto**: 100 requests/minuto
- **Administradores**: 200 requests/minuto
- **Usuarios normales**: 50 requests/minuto
- **Operaciones sensibles**: 10 requests/minuto

**Características**:
- Límites por IP del cliente
- Diferentes límites según tipo de usuario
- Límites más estrictos para operaciones de modificación

---


## 🚀 **INSTRUCCIONES DE USO**

### Ejecutar server API :
```bash
cd API
pip install -r requirements.txt
python server_api.py
```

### Acceder a la documentación:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

### Ejecutar el cliente:
```bash
python client_api.py
```

