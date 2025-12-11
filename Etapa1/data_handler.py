import requests
import json
import os


NOBEL_PRIZES_URL = "https://api.nobelprize.org/v1/prize.json"
LOCAL_JSON_FILE = "nobel_prizes.json"

def download_nobel_prizes_data(url: str = NOBEL_PRIZES_URL, filename: str = LOCAL_JSON_FILE) -> bool:
    """
    Descarga el archivo JSON de los premios Nobel desde la URL especificada
    y lo guarda localmente.

    Args:
        url (str): La URL desde donde descargar el archivo.
        filename (str): El nombre del archivo local donde se guardará.

    Returns:
        bool: True si la descarga fue exitosa, False en caso contrario.
    """
    print(f"Intentando descargar datos desde: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si el código de estado es un error (4xx o 5xx)
        data = response.json()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Datos descargados y guardados en '{filename}' exitosamente.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar los datos: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        return False
    except IOError as e:
        print(f"Error de E/S al guardar el archivo: {e}")
        return False

def load_nobel_prizes_data(filename: str = LOCAL_JSON_FILE) -> list:
    """
    Carga los datos de los premios Nobel desde el archivo JSON local.

    Args:
        filename (str): El nombre del archivo JSON local.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa un premio Nobel.
              Retorna una lista vacía si el archivo no existe o hay un error.
    """
    if not os.path.exists(filename):
        print(f"El archivo '{filename}' no existe. Intenta descargarlo primero.")
        return []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("prizes", [])
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el JSON desde '{filename}': {e}")
        return []
    except IOError as e:
        print(f"Error de E/S al leer el archivo '{filename}': {e}")
        return []

def get_all_prizes(data: list) -> list:
    """Retorna todos los premios Nobel cargados."""
    return data

def get_prize_by_year(data: list, year: str) -> list:
    """Retorna premios Nobel de un año específico."""
    return [p for p in data if p.get("year") == year]

def get_prize_by_category(data: list, category: str) -> list:
    """Retorna premios Nobel de una categoría específica."""
    return [p for p in data if p.get("category", "").lower() == category.lower()]

def get_prize_motivation(data: list, year: str, category: str) -> str | None:
    """
    Retorna la motivación general de un premio específico por año y categoría.
    Retorna None si no se encuentra el premio o la motivación.
    """
    for prize in data:
        if prize.get("year") == year and prize.get("category", "").lower() == category.lower():
            return prize.get("overallMotivation", "No hay motivación general disponible para este premio.")
    return None

def find_laureate_by_name(data: list, firstname: str, surname: str) -> list:
    """
    Busca premios en los que un laureado específico (por nombre y apellido) esté involucrado.
    Retorna una lista de premios donde el laureado es encontrado.
    """
    found_prizes = []
    for prize in data:
        if "laureates" in prize:
            for laureate in prize["laureates"]:
                if (laureate.get("firstname", "").lower() == firstname.lower() and
                    laureate.get("surname", "").lower() == surname.lower()):
                    found_prizes.append(prize)
                    break 
    return found_prizes

def get_laureates_by_year_and_category(data: list, year: str, category: str) -> list:
    """
    Obtiene los laureados de un premio específico por año y categoría.
    Retorna una lista de laureados (diccionarios) o una lista vacía si no se encuentra el premio.
    """
    for prize in data:
        if (prize.get("year") == year and 
            prize.get("category", "").lower() == category.lower()):
            return prize.get("laureates", [])
    return []

def describe_data_structure(data: list):
    """
    Realiza una descripción de la estructura del archivo de premios Nobel
    para el informe.
    """
    print("\n--- Descripción Detallada del Archivo JSON de Premios Nobel ---")
    if not data:
        print("No hay datos cargados para describir. El archivo JSON podría estar vacío o malformado.")
        return

    num_objects = len(data)
    print(f"El archivo contiene un total de {num_objects} objetos (premios Nobel).")

    # Descripción de las propiedades del objeto típico (tomando el primero)
    if num_objects > 0:
        first_prize = data[0]
        print("\nEjemplo de Estructura de un Objeto 'Premio':")
        print("Cada premio es un diccionario con las siguientes propiedades:")
        for key, value in first_prize.items():
            value_type = type(value).__name__
            print(f"  - '{key}': Tipo de dato -> {value_type}")
            if key == "laureates" and isinstance(value, list) and value:
                print("    Descripción adicional: 'laureates' es una lista de objetos, donde cada objeto representa a un laureado.")
                print("    Ejemplo de Estructura de un Objeto 'Laureado':")
                first_laureate = value[0]
                for l_key, l_value in first_laureate.items():
                    laureate_value_type = type(l_value).__name__
                    print(f"      - '{l_key}': Tipo de dato -> {laureate_value_type}")
                if len(value) > 1:
                    print(f"    (El primer premio de ejemplo tiene {len(value)} laureados.)")
            elif key == "overallMotivation":
                print("    Descripción adicional: Cadena de texto que describe la motivación general del premio.")
            elif key == "year":
                print("    Descripción adicional: Año en que se otorgó el premio (cadena de texto).")
            elif key == "category":
                print("    Descripción adicional: Categoría del premio (ej. 'physics', 'chemistry', 'peace').")

    print("\n--- Fin de la Descripción de la Estructura ---")

if __name__ == "__main__":
    print("--- Iniciando Proceso de Carga y Análisis de Datos (Etapa 1) ---")

    # 1. Descargar el archivo JSON si no existe o se desea actualizar
    if not os.path.exists(LOCAL_JSON_FILE) or input("¿Desea descargar la última versión de los datos? (s/n): ").lower() == 's':
        if not download_nobel_prizes_data():
            print("No se pudo descargar los datos. Abortando la operación.")
            exit()
    # 2. Cargar los datos desde el archivo local
    nobel_prizes = load_nobel_prizes_data()

    if nobel_prizes:
        # 3. Realizar descripción de la estructura para el informe
        describe_data_structure(nobel_prizes)

        # Ejemplos de consultas más claros para depuración/prueba
        print("\n--- Ejecutando Ejemplos de Consultas ---")

        print(f"Número total de premios Nobel cargados: {len(get_all_prizes(nobel_prizes))}")

        # Ejemplo 1: Premios de un año específico
        target_year = "2020" # Puedes cambiar esto
        prizes_by_year = get_prize_by_year(nobel_prizes, target_year)
        print(f"\nConsulta por Año: Premios en el año {target_year}")
        if prizes_by_year:
            print(f"  - Se encontraron {len(prizes_by_year)} premios para el año {target_year}.")
            print(f"  - Categorías de premios en {target_year}: {[p.get('category') for p in prizes_by_year]}")
        else:
            print(f"  - No se encontraron premios para el año {target_year}.")

        # Ejemplo 2: Premios de una categoría específica
        target_category = "chemistry" # Puedes cambiar esto
        prizes_by_category = get_prize_by_category(nobel_prizes, target_category)
        print(f"\nConsulta por Categoría: Premios en la categoría '{target_category.capitalize()}'")
        if prizes_by_category:
            print(f"  - Se encontraron {len(prizes_by_category)} premios en la categoría '{target_category}'.")
            print(f"  - Algunos años en los que se otorgó el premio de {target_category}: {[p.get('year') for p in prizes_by_category[:5]]}...")
        else:
            print(f"  - No se encontraron premios en la categoría '{target_category}'.")

        
        # Ejemplo 3: Buscar laureados por nombre y apellido
        print("\n--- Búsqueda de Premios por Nombre de Laureado ---")
        laureate_firstname = "Marie" 
        laureate_surname = "Curie"
        laureate_prizes = find_laureate_by_name(nobel_prizes, laureate_firstname, laureate_surname)
        if laureate_prizes:
            print(f"Se encontraron premios para '{laureate_firstname} {laureate_surname}':")
            for i, prize in enumerate(laureate_prizes):
                print(f"  Premio {i+1}: Año '{prize.get('year')}', Categoría '{prize.get('category')}'")
                for laureate in prize.get('laureates', []):
                    if (laureate.get("firstname", "").lower() == laureate_firstname.lower() and
                        laureate.get("surname", "").lower() == laureate_surname.lower()):
                        print(f"    Motivación específica de {laureate_firstname} {laureate_surname}: '{laureate.get('motivation', 'No disponible')}'")
        else:
            print(f"No se encontraron premios para '{laureate_firstname} {laureate_surname}'.")

       

    else:
        print("No se pudieron cargar los datos de los premios Nobel. Verifique el archivo local o la descarga.")

    print("\n--- Proceso de Carga y Análisis Finalizado ---")