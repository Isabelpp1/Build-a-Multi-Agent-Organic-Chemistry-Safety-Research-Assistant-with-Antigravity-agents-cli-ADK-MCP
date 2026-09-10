import os
import sys

import google.auth
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioConnectionParams
from google.genai import types
from mcp import StdioServerParameters

# config de Vertex AI si hay credenciales ADC
try:
    _, proyecto = google.auth.default()
    if proyecto:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", proyecto)
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
except Exception:
    pass

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(RAIZ)
from wikipedia_tool import search_wikipedia  # noqa: E402

modelo = Gemini(
    model="gemini-flash-latest",
    retry_options=types.HttpRetryOptions(attempts=3),
)

# 1. parser: saca el nombre del compuesto del mensaje del usuario
parser_agent = Agent(
    name="chemical_parser",
    model=modelo,
    instruction="""
    Lee el mensaje del usuario e identifica el compuesto quimico principal
    (por ejemplo 'aspirin' o 'acetaminophen').
    Responde UNICAMENTE con el nombre del compuesto en ingles y en minusculas,
    sin puntuacion ni palabras adicionales.
    """,
    output_key="target_chemical",
)

# 2a. investigador de Wikipedia
wiki_agent = Agent(
    name="wikipedia_specialist",
    model=modelo,
    instruction="""
    Eres un investigador academico. Busca en Wikipedia informacion sobre
    '{target_chemical}': historia, quien lo descubrio, nombre original y formula.
    Incluye siempre la URL de Wikipedia. Resume los hallazgos de forma breve.
    """,
    output_key="wiki_result",
    tools=[search_wikipedia],
)

# 2b. inventario via servidor MCP (sqlite)
servidor_mcp = os.path.join(RAIZ, "mcp_sqlite_server.py")

herramientas_inventario = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[servidor_mcp],
        )
    )
)

inventory_agent = Agent(
    name="lab_inventory_specialist",
    model=modelo,
    instruction="""
    Eres el encargado de seguridad e inventario del laboratorio de quimica.
    Con tus herramientas MCP:
    1. Busca '{target_chemical}' en el inventario para conocer existencias, pureza y ubicacion.
    2. Revisa si existe un procedimiento de sintesis para '{target_chemical}' y obtén
       reactivos, pasos y precauciones.

    Reglas de seguridad:
    - Si el compuesto o alguno de los reactivos es peligroso, marca la advertencia asi:
      > [!CAUTION] Alerta de riesgo
    - Si el procedimiento involucra materiales peligrosos, indica explicitamente
      que se debe trabajar en CAMPANA DE EXTRACCION.
    """,
    output_key="inventory_result",
    tools=[herramientas_inventario],
)

# 2. los dos investigadores corren al mismo tiempo
parallel_researchers = ParallelAgent(
    name="parallel_researchers",
    sub_agents=[wiki_agent, inventory_agent],
)

# 3. arma la hoja final
assembler_agent = Agent(
    name="report_assembler",
    model=modelo,
    instruction="""
    Eres el jefe del laboratorio de quimica organica.
    Combina la investigacion y el estado del inventario de '{target_chemical}'
    en una hoja de laboratorio bien formateada en markdown.

    Informacion disponible:
    - Contexto de Wikipedia: {wiki_result}
    - Inventario y sintesis: {inventory_result}

    Estructura del reporte:
    # Hoja de laboratorio: {target_chemical}

    ## 1. Contexto historico y academico
    Historia, descubridor y antecedentes. Cita la fuente de Wikipedia.

    ## 2. Existencias en el laboratorio
    Ubicacion, pureza y cantidad disponible. Si faltan reactivos para la sintesis, indica cuales.

    ## 3. Procedimiento de sintesis y seguridad
    Pasos exactos de la reaccion. Resalta las clasificaciones GHS y agrega una advertencia
    visible sobre el uso de campana de extraccion en los pasos con reactivos corrosivos.

    Dirigete al estudiante de forma directa, con un tono motivador y priorizando la seguridad.
    """,
)

organic_chem_pipeline = SequentialAgent(
    name="organic_chem_pipeline",
    sub_agents=[parser_agent, parallel_researchers, assembler_agent],
)

root_agent = organic_chem_pipeline

app = App(root_agent=root_agent, name="app")
