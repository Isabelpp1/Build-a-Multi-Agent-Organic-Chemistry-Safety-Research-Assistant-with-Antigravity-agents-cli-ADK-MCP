import sqlite3

DB = "lab_inventory.db"


def crear_tablas(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            compound_name TEXT UNIQUE,
            formula TEXT,
            cas_number TEXT,
            quantity_g REAL,
            purity TEXT,
            location TEXT,
            hazard_ghs TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS synthesis_procedures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_compound TEXT UNIQUE,
            reagents_required TEXT,
            procedure_steps TEXT,
            safety_precautions TEXT
        )
    """)


def cargar_datos(cur):
    reactivos = [
        ("salicylic acid", "C7H6O3", "69-72-7", 500.0, "99%", "Estante A-12",
         "Nocivo en caso de ingestion, lesiones oculares graves"),
        ("acetic anhydride", "C4H6O3", "108-24-7", 1000.0, "99%", "Gabinete inflamables C-2",
         "Liquido inflamable, corrosivo, nocivo por inhalacion"),
        ("p-aminophenol", "C6H7NO", "123-30-8", 250.0, "98%", "Estante B-4",
         "Nocivo en caso de ingestion, posible mutageno"),
        ("aspirin", "C9H8O4", "50-78-2", 0.0, "N/A (sin existencias)", "Estante A-1",
         "Nocivo en caso de ingestion"),
        ("acetaminophen", "C8H9NO2", "103-90-2", 10.0, "99%", "Estante A-2",
         "Nocivo en caso de ingestion"),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO inventory
            (compound_name, formula, cas_number, quantity_g, purity, location, hazard_ghs)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, reactivos)

    procedimientos = [
        ("aspirin",
         "salicylic acid, acetic anhydride",
         "Hacer reaccionar acido salicilico con anhidrido acetico usando acido fosforico como catalizador. "
         "Calentar en baño maria a 50 C durante 15 minutos. Dejar enfriar, agregar agua con hielo para "
         "cristalizar, filtrar al vacio y recristalizar en etanol.",
         "Trabajar dentro de la campana de extraccion. El anhidrido acetico es corrosivo e inflamable. "
         "El acido salicilico es irritante."),
        ("acetaminophen",
         "p-aminophenol, acetic anhydride",
         "Suspender p-aminofenol en agua, agregar anhidrido acetico y calentar suavemente hasta disolver. "
         "Agitar 10 minutos, enfriar en baño de hielo para cristalizar, filtrar y lavar los cristales con agua fria.",
         "Trabajar dentro de la campana de extraccion. El anhidrido acetico es corrosivo e inflamable. "
         "El p-aminofenol es nocivo."),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO synthesis_procedures
            (target_compound, reagents_required, procedure_steps, safety_precautions)
        VALUES (?, ?, ?, ?)
    """, procedimientos)


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    crear_tablas(cur)
    cargar_datos(cur)
    conn.commit()
    conn.close()
    print(f"Base {DB} lista")


if __name__ == "__main__":
    main()
