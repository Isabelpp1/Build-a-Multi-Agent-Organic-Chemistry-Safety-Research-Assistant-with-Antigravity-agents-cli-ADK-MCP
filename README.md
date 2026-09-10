# Asistente de laboratorio de química orgánica

Sistema multiagente construido con Google ADK y MCP. Recibe el nombre de un compuesto y genera una hoja de laboratorio con su contexto histórico (Wikipedia), las existencias en el inventario y el procedimiento de síntesis con sus precauciones (base SQLite local).

## Arquitectura

```
usuario
  └─ chemical_parser          extrae el compuesto -> target_chemical
       └─ parallel_researchers
            ├─ wikipedia_specialist     tool nativo (requests)
            └─ lab_inventory_specialist servidor MCP sobre sqlite
       └─ report_assembler     arma la hoja final en markdown
```

Los dos investigadores corren en paralelo con `ParallelAgent`; el pipeline completo es un `SequentialAgent`.

## Archivos

| Archivo | Descripción |
|---|---|
| `init_db.py` | Crea y llena `lab_inventory.db` |
| `wikipedia_tool.py` | Función `search_wikipedia` usada como tool de ADK |
| `mcp_sqlite_server.py` | Servidor FastMCP con `search_inventory` y `get_synthesis_procedure` |
| `app/agent.py` | Definición de los agentes y el pipeline |
| `tests/eval/` | Dataset y configuración de evaluación con LLM como juez |

## Instalación

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install google-agents-cli
gcloud auth application-default login

uv pip install requests mcp --index-url https://pypi.org/simple
uv lock --default-index https://pypi.org/simple

python init_db.py
```

## Uso

```bash
# prueba rápida
agents-cli run "aspirin" -v

# interfaz web
agents-cli playground

# evaluación
agents-cli eval run --dataset tests/eval/datasets/chemistry_dataset.json
```

En el playground hay que seleccionar `app` en el menú de aplicaciones.

## Compuestos cargados

- salicylic acid
- acetic anhydride
- p-aminophenol
- aspirin (sin existencias)
- acetaminophen

Procedimientos de síntesis disponibles: aspirin, acetaminophen.

## Despliegue en Cloud Run (opcional)

El servidor MCP debe cambiar de `stdio` a `sse` y en `app/agent.py` se reemplaza `StdioConnectionParams` por `SseConnectionParams` apuntando a la URL del servicio. Luego:

```bash
gcloud run deploy lab-inventory-mcp --source . --allow-unauthenticated
agents-cli scaffold enhance --deployment-target cloud_run --yes
agents-cli deploy --project PROJECT_ID --region REGION
```
