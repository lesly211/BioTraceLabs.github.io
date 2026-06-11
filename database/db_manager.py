"""
Módulo de gestión de la base de datos del inventario forestal OSINFOR.
Maneja la conexión, inicialización y consultas a la BD SQLite.
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

# Ruta base del proyecto
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "database" / "inventario_osinfor.db"
SQL_INIT_PATH = BASE_DIR / "database" / "inventario_arboles.db.sql"


def get_connection():
    """Retorna una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Acceso por nombre de columna
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    """Inicializa la base de datos con el esquema y datos iniciales."""
    if DB_PATH.exists():
        print(f"[DB] Base de datos ya existe en: {DB_PATH}")
        return

    print(f"[DB] Creando base de datos en: {DB_PATH}")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(SQL_INIT_PATH, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    conn = get_connection()
    try:
        conn.executescript(sql_script)
        conn.commit()
        print("[DB] Base de datos inicializada correctamente.")
    except Exception as e:
        print(f"[DB] Error al inicializar: {e}")
        raise
    finally:
        conn.close()


def buscar_arbol_por_especie(nombre_cientifico: str = None, nombre_comun: str = None) -> list[dict]:
    """
    Busca árboles en el inventario por especie (nombre científico o común).
    Retorna lista de árboles encontrados con sus detalles.
    """
    conn = get_connection()
    resultados = []

    try:
        if nombre_cientifico:
            # Búsqueda por nombre científico (parcial, insensible a mayúsculas)
            query = """
                SELECT 
                    ia.codigo_arbol,
                    ea.nombre_comun,
                    ea.nombre_cientifico,
                    ea.familia,
                    ea.estado_conservacion,
                    ea.protegida,
                    ia.ubicacion_descripcion,
                    ia.latitud,
                    ia.longitud,
                    ia.dap_cm,
                    ia.altura_m,
                    ia.estado_fitosanitario,
                    ia.fecha_registro,
                    ia.observaciones,
                    pm.codigo_plan,
                    pm.nombre as plan_nombre,
                    pm.titular,
                    pm.resolucion_aprobacion,
                    pm.fecha_vencimiento,
                    pm.region,
                    pm.estado as plan_estado
                FROM inventario_arboles ia
                JOIN especies_arboles ea ON ia.especie_id = ea.id
                LEFT JOIN planes_manejo pm ON ia.plan_manejo_id = pm.id
                WHERE LOWER(ea.nombre_cientifico) LIKE LOWER(?)
                ORDER BY ia.codigo_arbol
            """
            cursor = conn.execute(query, (f'%{nombre_cientifico}%',))

        elif nombre_comun:
            query = """
                SELECT 
                    ia.codigo_arbol,
                    ea.nombre_comun,
                    ea.nombre_cientifico,
                    ea.familia,
                    ea.estado_conservacion,
                    ea.protegida,
                    ia.ubicacion_descripcion,
                    ia.latitud,
                    ia.longitud,
                    ia.dap_cm,
                    ia.altura_m,
                    ia.estado_fitosanitario,
                    ia.fecha_registro,
                    ia.observaciones,
                    pm.codigo_plan,
                    pm.nombre as plan_nombre,
                    pm.titular,
                    pm.resolucion_aprobacion,
                    pm.fecha_vencimiento,
                    pm.region,
                    pm.estado as plan_estado
                FROM inventario_arboles ia
                JOIN especies_arboles ea ON ia.especie_id = ea.id
                LEFT JOIN planes_manejo pm ON ia.plan_manejo_id = pm.id
                WHERE LOWER(ea.nombre_comun) LIKE LOWER(?)
                ORDER BY ia.codigo_arbol
            """
            cursor = conn.execute(query, (f'%{nombre_comun}%',))
        else:
            return []

        resultados = [dict(row) for row in cursor.fetchall()]

    except Exception as e:
        print(f"[DB] Error en búsqueda: {e}")
    finally:
        conn.close()

    return resultados


def obtener_estadisticas() -> dict:
    """Retorna estadísticas generales del inventario."""
    conn = get_connection()
    stats = {}

    try:
        stats['total_arboles'] = conn.execute(
            "SELECT COUNT(*) FROM inventario_arboles"
        ).fetchone()[0]

        stats['total_especies'] = conn.execute(
            "SELECT COUNT(DISTINCT especie_id) FROM inventario_arboles"
        ).fetchone()[0]

        stats['total_planes'] = conn.execute(
            "SELECT COUNT(*) FROM planes_manejo WHERE estado='VIGENTE'"
        ).fetchone()[0]

        stats['especies_protegidas'] = conn.execute(
            "SELECT COUNT(DISTINCT especie_id) FROM inventario_arboles ia "
            "JOIN especies_arboles ea ON ia.especie_id=ea.id WHERE ea.protegida=1"
        ).fetchone()[0]

        stats['por_region'] = [
            dict(row) for row in conn.execute(
                "SELECT region, COUNT(*) as total FROM planes_manejo "
                "GROUP BY region ORDER BY total DESC"
            ).fetchall()
        ]

    except Exception as e:
        print(f"[DB] Error estadísticas: {e}")
    finally:
        conn.close()

    return stats


def registrar_consulta(especie: str, confianza: float, codigo: str, resultado: str, imagen: str, detalles: dict):
    """Registra una consulta del chatbot en el historial."""
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO historial_consultas 
               (especie_identificada, confianza_identificacion, codigo_arbol, resultado, imagen_path, detalles_json)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (especie, confianza, codigo, resultado, imagen, json.dumps(detalles, ensure_ascii=False))
        )
        conn.commit()
    except Exception as e:
        print(f"[DB] Error al registrar consulta: {e}")
    finally:
        conn.close()


def obtener_historial(limite: int = 10) -> list[dict]:
    """Retorna las últimas consultas del historial."""
    conn = get_connection()
    historial = []
    try:
        cursor = conn.execute(
            "SELECT * FROM historial_consultas ORDER BY fecha_consulta DESC LIMIT ?",
            (limite,)
        )
        historial = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"[DB] Error historial: {e}")
    finally:
        conn.close()
    return historial


def listar_todas_especies() -> list[dict]:
    """Lista todas las especies registradas en el inventario."""
    conn = get_connection()
    especies = []
    try:
        cursor = conn.execute(
            """SELECT ea.*, COUNT(ia.id) as total_en_inventario
               FROM especies_arboles ea
               LEFT JOIN inventario_arboles ia ON ea.id = ia.especie_id
               GROUP BY ea.id
               ORDER BY ea.nombre_comun"""
        )
        especies = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"[DB] Error listando especies: {e}")
    finally:
        conn.close()
    return especies
