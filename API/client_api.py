# api_client.py
import requests
import json
import sys


BASE_URL = "http://127.0.0.1:8001"

# Credenciales de autenticación
CREDENTIALS = {
    "user": {"username": "user", "password": "user123"},
    "admin": {"username": "admin", "password": "admin123"}
}

# --- Funciones Auxiliares ---
def print_json_response(title: str, response_json: dict | list):
    """Imprime una respuesta JSON de forma legible."""
    print(f"\n--- {title} ---")
    print(json.dumps(response_json, indent=2, ensure_ascii=False))
    print("-" * (len(title) + 8))

def handle_response(response: requests.Response, success_message: str):
    """Maneja la respuesta de una solicitud HTTP."""
    if response.status_code >= 200 and response.status_code < 300:
        print(f"\nÉXITO: {success_message} (Código de estado: {response.status_code})")
        try:
            # Algunas respuestas (como 204 No Content) no tienen JSON
            if response.content:
                print_json_response("Detalles de la Respuesta", response.json())
        except json.JSONDecodeError:
            print("Respuesta exitosa, pero sin contenido JSON o contenido inválido.")
    else:
        print(f"\nERROR: Falló la solicitud (Código de estado: {response.status_code})")
        try:
            error_details = response.json()
            print_json_response("Detalles del Error", error_details)
        except json.JSONDecodeError:
            print("No se pudieron decodificar los detalles del error o la respuesta no es JSON.")
            print(f"Contenido de la respuesta: {response.text}")

def get_credentials(require_admin: bool = False):
    """Obtiene las credenciales del usuario."""
    print("\n--- Autenticación Requerida ---")
    if require_admin:
        print("⚠️  Esta operación requiere permisos de administrador.")
    
    print("Ingrese sus credenciales:")
    username = input("Usuario: ")
    password = input("Contraseña: ")
    
    # Validar que las credenciales coincidan con las configuradas
    if username == CREDENTIALS["user"]["username"] and password == CREDENTIALS["user"]["password"]:
        print("✅ Autenticación exitosa como usuario normal")
        return username, password
    elif username == CREDENTIALS["admin"]["username"] and password == CREDENTIALS["admin"]["password"]:
        if require_admin:
            print("✅ Autenticación exitosa como administrador")
        else:
            print("✅ Autenticación exitosa como administrador")
        return username, password
    else:
        print("❌ Credenciales incorrectas. Usando credenciales de usuario normal por defecto.")
        return CREDENTIALS["user"]["username"], CREDENTIALS["user"]["password"]

# --- Funciones para las Operaciones GET ---

def get_all_prizes():
    """Obtiene y muestra todos los premios Nobel."""
    print("Obteniendo todos los premios Nobel...")
    try:
        response = requests.get(f"{BASE_URL}/prizes")
        handle_response(response, "Premios Nobel obtenidos exitosamente.")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

def get_prizes_by_year():
    """Obtiene y muestra premios Nobel de un año específico."""
    year = input("Ingrese el año para buscar premios: ")
    print(f"Obteniendo premios Nobel del año {year}...")
    try:
        response = requests.get(f"{BASE_URL}/prizes/year/{year}")
        handle_response(response, f"Premios para el año {year} obtenidos exitosamente.")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

def get_prizes_by_category():
    """Obtiene y muestra premios Nobel de una categoría específica."""
    category = input("Ingrese la categoría para buscar premios (ej. physics, chemistry, peace): ")
    print(f"Obteniendo premios Nobel de la categoría '{category}'...")
    try:
        response = requests.get(f"{BASE_URL}/prizes/category/{category}")
        handle_response(response, f"Premios para la categoría '{category}' obtenidos exitosamente.")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

def get_prize_motivation():
    """Obtiene y muestra la motivación de un premio específico."""
    year = input("Ingrese el año del premio: ")
    category = input("Ingrese la categoría del premio: ")
    print(f"Obteniendo motivación para el premio de {category} en {year}...")
    try:
        response = requests.get(f"{BASE_URL}/prizes/motivation/{year}/{category}")
        handle_response(response, f"Motivación del premio de {category} en {year} obtenida exitosamente.")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

def search_laureates():
    """Busca premios por nombre y apellido de laureado."""
    firstname = input("Ingrese el nombre del laureado: ")
    surname = input("Ingrese el apellido del laureado: ")
    print(f"Buscando premios para {firstname} {surname}...")
    try:
        # Se usan parámetros de consulta (query parameters)
        response = requests.get(f"{BASE_URL}/laureates/search?firstname={firstname}&surname={surname}")
        handle_response(response, f"Premios para {firstname} {surname} obtenidos exitosamente.")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

def get_laureates_by_year_category():
    """Obtiene los laureados de un premio específico por año y categoría."""
    year = input("Ingrese el año del premio: ")
    category = input("Ingrese la categoría del premio: ")
    print(f"Obteniendo laureados del premio de {category} en {year}...")
    try:
        response = requests.get(f"{BASE_URL}/laureates/{year}/{category}")
        handle_response(response, f"Laureados del premio de {category} en {year} obtenidos exitosamente.")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

def get_api_info():
    """Obtiene información de la API."""
    print("Obteniendo información de la API...")
    try:
        response = requests.get(f"{BASE_URL}/")
        handle_response(response, "Información de la API obtenida exitosamente.")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

def get_security_info():
    """Obtiene información de seguridad de la API."""
    print("Obteniendo información de seguridad...")
    try:
        response = requests.get(f"{BASE_URL}/security/info")
        handle_response(response, "Información de seguridad obtenida exitosamente.")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

# --- Funciones para las Operaciones POST, PUT, DELETE ---

def create_nobel_prize():
    """Crea un nuevo premio Nobel."""
    print("\n--- Crear Nuevo Premio Nobel ---")
    
    # Obtener credenciales
    username, password = get_credentials()
    
    year = input("Año del premio (ej. 2025): ")
    category = input("Categoría del premio (ej. peace, literature, medicine): ")
    overall_motivation = input("Motivación general del premio (opcional, dejar vacío si no hay): ")

    laureates_data = []
    add_more_laureates = 's'
    while add_more_laureates.lower() == 's':
        print(f"--- Datos del Laureado {len(laureates_data) + 1} ---")
        laureate_firstname = input("Nombre del laureado: ")
        laureate_surname = input("Apellido del laureado (opcional): ")
        laureate_motivation = input("Motivación específica del laureado (opcional): ")
        laureate_share = input("Share del laureado (ej. 1, 1/2, opcional): ")

        laureate_info = {
            "firstname": laureate_firstname,
            "surname": laureate_surname if laureate_surname else None,
            "motivation": laureate_motivation if laureate_motivation else None,
            "share": laureate_share if laureate_share else None
        }
        laureates_data.append(laureate_info)
        add_more_laureates = input("¿Desea añadir otro laureado? (s/n): ")

    prize_data = {
        "year": year,
        "category": category,
        "laureates": laureates_data
    }
    if overall_motivation:
        prize_data["overallMotivation"] = overall_motivation

    print("Enviando solicitud POST para crear premio...")
    try:
        response = requests.post(f"{BASE_URL}/prizes", json=prize_data, auth=(username, password))
        handle_response(response, "Premio creado exitosamente.")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

def update_nobel_prize():
    """Actualiza un premio Nobel existente."""
    print("\n--- Actualizar Premio Nobel ---")
    
    # Obtener credenciales
    username, password = get_credentials()
    
    year_to_update = input("Año del premio a actualizar: ")
    category_to_update = input("Categoría del premio a actualizar: ")

    update_payload = {}
    print("Ingrese los nuevos valores (dejar vacío para no cambiar):")
    
    new_year = input("Nuevo año (opcional): ")
    if new_year: update_payload["year"] = new_year

    new_category = input("Nueva categoría (opcional): ")
    if new_category: update_payload["category"] = new_category

    new_overall_motivation = input("Nueva motivación general (opcional): ")
    if new_overall_motivation: update_payload["overallMotivation"] = new_overall_motivation
    elif new_overall_motivation == "": # Para permitir borrar la motivación
        update_payload["overallMotivation"] = None

    # Preguntar si desea actualizar laureados
    update_laureates_choice = input("¿Desea actualizar la lista completa de laureados? (s/n): ")
    if update_laureates_choice.lower() == 's':
        new_laureates_data = []
        add_more_laureates = 's'
        while add_more_laureates.lower() == 's':
            print(f"--- Datos del Nuevo Laureado {len(new_laureates_data) + 1} ---")
            laureate_id = input("ID del laureado (si se conoce y quiere mantenerlo, dejar vacío para generar): ")
            laureate_firstname = input("Nombre del laureado: ")
            laureate_surname = input("Apellido del laureado (opcional): ")
            laureate_motivation = input("Motivación específica del laureado (opcional): ")
            laureate_share = input("Share del laureado (opcional): ")

            laureate_info = {
                "firstname": laureate_firstname,
                "surname": laureate_surname if laureate_surname else None,
                "motivation": laureate_motivation if laureate_motivation else None,
                "share": laureate_share if laureate_share else None,
                "id": laureate_id if laureate_id else None # Incluir ID si se proporciona
            }
            new_laureates_data.append(laureate_info)
            add_more_laureates = input("¿Desea añadir otro laureado? (s/n): ")
        update_payload["laureates"] = new_laureates_data
    elif update_laureates_choice.lower() == '': # Si se deja vacío, también se podría interpretar como no cambiar
        pass # No hacer nada si no se quiere cambiar

    if not update_payload:
        print("No se especificaron campos para actualizar. Operación cancelada.")
        return

    print(f"Enviando solicitud PUT para actualizar premio {year_to_update}/{category_to_update}...")
    try:
        response = requests.put(f"{BASE_URL}/prizes/{year_to_update}/{category_to_update}", 
                              json=update_payload, auth=(username, password))
        handle_response(response, "Premio actualizado exitosamente.")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

def delete_nobel_prize():
    """Elimina un premio Nobel específico."""
    print("\n--- Eliminar Premio Nobel ---")
    
    # Obtener credenciales de administrador
    username, password = get_credentials(require_admin=True)
    
    year_to_delete = input("Año del premio a eliminar: ")
    category_to_delete = input("Categoría del premio a eliminar: ")
    
    confirm = input(f"¿Está seguro que desea eliminar el premio de {category_to_delete} en {year_to_delete}? (s/n): ")
    if confirm.lower() != 's':
        print("Operación de eliminación cancelada.")
        return

    print(f"Enviando solicitud DELETE para {year_to_delete}/{category_to_delete}...")
    try:
        response = requests.delete(f"{BASE_URL}/prizes/{year_to_delete}/{category_to_delete}", 
                                 auth=(username, password))
        handle_response(response, "Premio eliminado exitosamente.")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

# --- Menú Principal del Cliente ---

def main_menu():
    """Muestra el menú principal y gestiona las opciones del usuario."""
    while True:
        print("\n===================================")
        print("  Cliente API de Premios Nobel")
        print("===================================")
        print("--- Información de la API ---")
        print("0. Información de la API")
        print("00. Información de Seguridad")
        print("--- Operaciones de Consulta (GET) ---")
        print("1. Obtener todos los premios")
        print("2. Obtener premios por año")
        print("3. Obtener premios por categoría")
        print("4. Obtener motivación de un premio específico")
        print("5. Buscar premios por laureado (nombre y apellido)")
        print("6. Obtener laureados por año y categoría")
        print("--- Operaciones de Modificación (CRUD) ---")
        print("7. Crear un nuevo premio Nobel (POST)")
        print("8. Actualizar un premio Nobel existente (PUT)")
        print("9. Eliminar un premio Nobel (DELETE)")
        print("10. Salir")
        print("===================================")

        choice = input("Seleccione una opción: ")

        if choice == '0':
            get_api_info()
        elif choice == '00':
            get_security_info()
        elif choice == '1':
            get_all_prizes()
        elif choice == '2':
            get_prizes_by_year()
        elif choice == '3':
            get_prizes_by_category()
        elif choice == '4':
            get_prize_motivation()
        elif choice == '5':
            search_laureates()
        elif choice == '6':
            get_laureates_by_year_category()
        elif choice == '7':
            create_nobel_prize()
        elif choice == '8':
            update_nobel_prize()
        elif choice == '9':
            delete_nobel_prize()
        elif choice == '10':
            print("Saliendo del cliente API. ¡Hasta luego!")
            sys.exit()
        else:
            print("Opción no válida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    main_menu() 