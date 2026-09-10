import requests

BASE_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"


def search_wikipedia(query: str) -> dict:
    """Busca un compuesto en Wikipedia y devuelve un resumen corto.

    Args:
        query: termino a buscar, por ejemplo 'Aspirin'.

    Returns:
        dict con 'title', 'summary' y 'url'. Si falla, devuelve un dict con la clave 'error'.
    """
    termino = query.strip().replace(" ", "_")
    try:
        resp = requests.get(BASE_URL + termino, timeout=10)
    except requests.RequestException as e:
        return {"error": f"No se pudo conectar a Wikipedia: {e}"}

    if resp.status_code != 200:
        return {"error": f"Pagina no encontrada (status {resp.status_code})"}

    data = resp.json()
    return {
        "title": data.get("title", query),
        "summary": data.get("extract", "Sin resumen disponible"),
        "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
    }
