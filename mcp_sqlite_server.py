import os
import sys
import sqlite3
from mcp.server.fastmcp import FastMCP

# stdout queda reservado para el protocolo MCP, cualquier log va a stderr
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_inventory.db")

mcp = FastMCP("LabInventoryServer")


def _consulta(sql, params):
    conn = sqlite3.connect(DB_PATH)
    try:
        return conn.execute(sql, params).fetchone()
    finally:
        conn.close()


@mcp.tool()
def search_inventory(compound: str) -> str:
    """Consulta el inventario del laboratorio para un compuesto.

    Args:
        compound: nombre del compuesto, por ejemplo 'salicylic acid'.

    Returns:
        Existencias, pureza, ubicacion y advertencias GHS del compuesto.
    """
    try:
        fila = _consulta("""
            SELECT compound_name, formula, cas_number, quantity_g, purity, location, hazard_ghs
            FROM inventory
            WHERE LOWER(compound_name) = LOWER(?)
        """, (compound.strip(),))
    except sqlite3.Error as e:
        print(f"error db: {e}", file=sys.stderr)
        return f"Error en la base de datos: {e}"

    if not fila:
        return f"El compuesto '{compound}' no esta registrado en el inventario."

    nombre, formula, cas, cantidad, pureza, ubicacion, riesgo = fila
    return (
        "--- INVENTARIO DE LABORATORIO ---\n"
        f"Compuesto: {nombre}\n"
        f"Formula: {formula}\n"
        f"CAS: {cas}\n"
        f"Existencias: {cantidad} g\n"
        f"Pureza: {pureza}\n"
        f"Ubicacion: {ubicacion}\n"
        f"Riesgos GHS: {riesgo}\n"
    )


@mcp.tool()
def get_synthesis_procedure(target_compound: str) -> str:
    """Devuelve el procedimiento de sintesis y precauciones de un compuesto.

    Args:
        target_compound: compuesto a sintetizar, por ejemplo 'aspirin'.

    Returns:
        Reactivos necesarios, pasos del procedimiento y precauciones de seguridad.
    """
    try:
        fila = _consulta("""
            SELECT target_compound, reagents_required, procedure_steps, safety_precautions
            FROM synthesis_procedures
            WHERE LOWER(target_compound) = LOWER(?)
        """, (target_compound.strip(),))
    except sqlite3.Error as e:
        print(f"error db: {e}", file=sys.stderr)
        return f"Error en la base de datos: {e}"

    if not fila:
        return f"No hay procedimiento registrado para '{target_compound}'."

    objetivo, reactivos, pasos, seguridad = fila
    return (
        f"--- PROCEDIMIENTO DE SINTESIS: {objetivo.upper()} ---\n"
        f"Reactivos: {reactivos}\n"
        f"Pasos: {pasos}\n"
        f"Precauciones: {seguridad}\n"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
