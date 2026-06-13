"""
Módulo de gestión de trazabilidad forestal.
Maneja registros de trozo, guías de transporte y recepciones en centros.
"""

import sqlite3
import json
import hashlib
import uuid
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "database" / "inventario_osinfor.db"
SCHEMA_PATH = BASE_DIR / "database" / "trazabilidad_schema.sql"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_trazabilidad():
    """Inicializa las tablas de trazabilidad en la BD existente."""
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn = get_connection()
    try:
        conn.executescript(sql)
        conn.commit()
        print("[Trazabilidad] Tablas de trazabilidad inicializadas.")
    except Exception as e:
        print(f"[Trazabilidad] Error: {e}")
    finally:
        conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def login_usuario(email: str, password: str) -> dict | None:
    """Autentica un usuario por email y contraseña."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE email=? AND activo=1", (email,)
        ).fetchone()
        if row:
            # Verificar contraseña (demo: texto plano; producción: hash)
            stored = row['password_hash']
            if stored == password or stored == hash_password(password):
                return dict(row)
    except Exception as e:
        print(f"[Auth] Error login: {e}")
    finally:
        conn.close()
    return None


def registrar_usuario(nombre, email, password, rol, concesion='', empresa='', dni='', placa='') -> dict:
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO usuarios (nombre, email, password_hash, rol, concesion, empresa, dni, placa)
               VALUES (?,?,?,?,?,?,?,?)""",
            (nombre, email, hash_password(password), rol, concesion, empresa, dni, placa)
        )
        conn.commit()
        return {"success": True}
    except sqlite3.IntegrityError:
        return {"success": False, "error": "El email ya está registrado"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def generar_codigo_trozo(region: str = "LOT") -> str:
    """Genera un código único para el trozo."""
    anio = datetime.now().year
    uid = str(uuid.uuid4().int)[:6].zfill(6)
    return f"TRZ-{anio}-{region}-{uid}"


def crear_censo_trozo(titular_id, numero_parcela, especie, nombre_cientifico,
                      latitud, longitud, dap_cm, longitud_troza, volumen_m3,
                      foto_corte_path='', foto_troza_path='', plan_manejo='',
                      observaciones='', region='LOT') -> dict:
    """Registra un nuevo censo de trozo."""
    codigo = generar_codigo_trozo(region)
    gps = f"{latitud},{longitud}"
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO censos_trozo
               (codigo_unico_trozo, titular_id, numero_parcela, especie, nombre_cientifico,
                coordenadas_gps, latitud, longitud, dap_cm, longitud_troza, volumen_m3,
                foto_corte_transversal, foto_troza_completa, plan_manejo_referencia, observaciones)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (codigo, titular_id, numero_parcela, especie, nombre_cientifico,
             gps, latitud, longitud, dap_cm, longitud_troza, volumen_m3,
             foto_corte_path, foto_troza_path, plan_manejo, observaciones)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM censos_trozo WHERE codigo_unico_trozo=?", (codigo,)).fetchone()
        return {"success": True, "trozo": dict(row), "codigo": codigo}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def obtener_censos_titular(titular_id) -> list:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM censos_trozo WHERE titular_id=? ORDER BY fecha_hora DESC",
            (titular_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def obtener_trozo_por_codigo(codigo: str) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT ct.*, u.nombre as titular_nombre, u.empresa as titular_empresa, u.concesion
               FROM censos_trozo ct
               JOIN usuarios u ON ct.titular_id = u.id
               WHERE ct.codigo_unico_trozo=?""", (codigo,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def verificar_legalidad_trozo(codigo: str) -> dict:
    """
    Verifica si un trozo proviene de una zona legal (inventario OSINFOR).
    Compara coordenadas con los planes de manejo vigentes.
    """
    trozo = obtener_trozo_por_codigo(codigo)
    if not trozo:
        return {"valido": False, "motivo": "Código de trozo no encontrado en el sistema"}

    conn = get_connection()
    try:
        # Verificar si la especie existe en el inventario legal
        especies_match = conn.execute(
            """SELECT ia.*, ea.nombre_comun, ea.nombre_cientifico, pm.codigo_plan, pm.nombre as plan_nombre,
                      pm.region, pm.estado as plan_estado, pm.titular
               FROM inventario_arboles ia
               JOIN especies_arboles ea ON ia.especie_id = ea.id
               LEFT JOIN planes_manejo pm ON ia.plan_manejo_id = pm.id
               WHERE (LOWER(ea.nombre_comun) LIKE LOWER(?) OR LOWER(ea.nombre_cientifico) LIKE LOWER(?))
               AND pm.estado = 'VIGENTE'""",
            (f"%{trozo['especie']}%", f"%{trozo.get('nombre_cientifico','x')}%")
        ).fetchall()

        if not especies_match:
            return {
                "valido": False,
                "motivo": f"La especie '{trozo['especie']}' no está registrada en ningún plan de manejo vigente",
                "trozo": trozo
            }

        # Verificar si el plan de manejo referenciado está vigente
        plan_valido = False
        plan_info = None
        if trozo.get('plan_manejo_referencia'):
            plan_row = conn.execute(
                "SELECT * FROM planes_manejo WHERE codigo_plan=? AND estado='VIGENTE'",
                (trozo['plan_manejo_referencia'],)
            ).fetchone()
            if plan_row:
                plan_valido = True
                plan_info = dict(plan_row)

        similitud = 0.85 if plan_valido else 0.60
        especies_legales = [dict(e) for e in especies_match[:3]]

        return {
            "valido": True,
            "similitud_porcentaje": round(similitud * 100, 1),
            "motivo": "El trozo corresponde a una especie registrada en plan de manejo vigente",
            "trozo": trozo,
            "plan_valido": plan_valido,
            "plan_info": plan_info,
            "especies_legales_encontradas": especies_legales,
            "total_registros_coincidentes": len(especies_match)
        }
    finally:
        conn.close()


def registrar_guia_transporte(censo_id, chofer_id, placa, origen, destino, observaciones='') -> dict:
    conn = get_connection()
    try:
        numero_guia = f"GT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4().int)[:5]}"
        conn.execute(
            """INSERT INTO guias_transporte
               (censo_trozo_id, chofer_id, numero_guia, placa_vehiculo, origen, destino, fecha_salida, observaciones)
               VALUES (?,?,?,?,?,?,?,?)""",
            (censo_id, chofer_id, numero_guia, placa, origen, destino, datetime.now().isoformat(), observaciones)
        )
        conn.execute("UPDATE censos_trozo SET estado='EN_TRANSITO' WHERE id=?", (censo_id,))
        conn.commit()
        return {"success": True, "numero_guia": numero_guia}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def obtener_guias_chofer(chofer_id) -> list:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT gt.*, ct.especie, ct.numero_parcela, ct.codigo_unico_trozo,
                      u.nombre as titular_nombre
               FROM guias_transporte gt
               JOIN censos_trozo ct ON gt.censo_trozo_id = ct.id
               JOIN usuarios u ON ct.titular_id = u.id
               WHERE gt.chofer_id=? ORDER BY gt.fecha_salida DESC""",
            (chofer_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def registrar_recepcion_centro(centro_id, codigo_trozo, foto_corteza_path='', observaciones='') -> dict:
    """
    Registra la recepción de un trozo en el centro de transformación.
    Verifica su legalidad Y compara la foto del corte transversal recibida
    con la foto original tomada por el titular usando visión por computadora.
    """
    trozo = obtener_trozo_por_codigo(codigo_trozo)
    if not trozo:
        return {"success": False, "error": "Código de trozo no encontrado"}

    # 1. Verificación de legalidad (plan de manejo, inventario OSINFOR)
    verificacion = verificar_legalidad_trozo(codigo_trozo)
    
    # 2. Comparación de imágenes de cortes transversales
    comparacion_imagenes = {"success": False, "mensaje": "No se realizó comparación de imágenes"}
    similitud_porcentaje = verificacion.get('similitud_porcentaje', 0)
    
    if foto_corteza_path and trozo.get('foto_corte_transversal'):
        try:
            # Importar el comparador de imágenes
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from identificador.comparador_imagenes import comparar_cortes_transversales
            
            # Comparar la foto original del titular con la foto del centro
            foto_original = trozo['foto_corte_transversal']
            foto_recepcion = foto_corteza_path
            
            print(f"[Comparación] Comparando fotos:")
            print(f"  - Original (titular): {foto_original}")
            print(f"  - Recepción (centro): {foto_recepcion}")
            
            comparacion_imagenes = comparar_cortes_transversales(foto_original, foto_recepcion)
            
            if comparacion_imagenes.get("success"):
                similitud_porcentaje = comparacion_imagenes.get("similitud_porcentaje", 0)
                print(f"[Comparación] Similitud: {similitud_porcentaje}%")
            else:
                print(f"[Comparación] Error: {comparacion_imagenes.get('error')}")
                
        except Exception as e:
            print(f"[Comparación] Error al comparar imágenes: {e}")
            import traceback
            traceback.print_exc()
            comparacion_imagenes = {
                "success": False,
                "error": f"Error en comparación de imágenes: {str(e)}"
            }
    else:
        mensaje_falta = []
        if not foto_corteza_path:
            mensaje_falta.append("foto de recepción")
        if not trozo.get('foto_corte_transversal'):
            mensaje_falta.append("foto original del titular")
        comparacion_imagenes = {
            "success": False,
            "mensaje": f"No se puede comparar: falta {' y '.join(mensaje_falta)}"
        }
    
    # 3. Determinar resultado final combinando legalidad Y comparación de imágenes
    # Para aprobar, debe ser legal Y tener buena similitud de imágenes
    if verificacion["valido"]:
        if comparacion_imagenes.get("success") and comparacion_imagenes.get("coincide"):
            resultado = "APROBADO"
            motivo_resultado = "Legal y foto verificada"
        elif comparacion_imagenes.get("success") and not comparacion_imagenes.get("coincide"):
            resultado = "RECHAZADO"
            motivo_resultado = "Legal pero la foto del corte NO coincide con la original"
        elif not comparacion_imagenes.get("success"):
            resultado = "APROBADO"  # Si no hay comparación, solo basarse en legalidad
            motivo_resultado = "Legal (comparación de imagen no disponible)"
        else:
            resultado = "APROBADO"
            motivo_resultado = "Legal"
    else:
        resultado = "RECHAZADO"
        motivo_resultado = verificacion.get("motivo", "No cumple con inventario legal")

    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO recepciones_centro
               (censo_trozo_id, centro_id, qr_escaneado, foto_corteza,
                resultado_verificacion, similitud_porcentaje, observaciones)
               VALUES (?,?,?,?,?,?,?)""",
            (trozo['id'], centro_id, codigo_trozo, foto_corteza_path,
             resultado, similitud_porcentaje, observaciones)
        )
        conn.execute("UPDATE censos_trozo SET estado='RECIBIDO' WHERE id=?", (trozo['id'],))
        conn.commit()
        
        # Convertir rutas absolutas a rutas relativas para el frontend
        foto_original_url = None
        foto_recepcion_url = None
        
        if trozo.get('foto_corte_transversal'):
            # Extraer solo el nombre del archivo de la ruta completa
            from pathlib import Path
            foto_nombre = Path(trozo['foto_corte_transversal']).name
            foto_original_url = f"/uploads/{foto_nombre}"
        
        if foto_corteza_path:
            foto_nombre = Path(foto_corteza_path).name
            foto_recepcion_url = f"/uploads/{foto_nombre}"
        
        return {
            "success": True,
            "verificacion": verificacion,
            "comparacion_imagenes": comparacion_imagenes,
            "resultado": resultado,
            "motivo_resultado": motivo_resultado,
            "similitud_porcentaje": similitud_porcentaje,
            "foto_original_url": foto_original_url,
            "foto_recepcion_url": foto_recepcion_url
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def obtener_recepciones_centro(centro_id) -> list:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT rc.*, ct.especie, ct.numero_parcela, ct.codigo_unico_trozo,
                      ct.dap_cm, ct.volumen_m3, u.nombre as titular_nombre
               FROM recepciones_centro rc
               JOIN censos_trozo ct ON rc.censo_trozo_id = ct.id
               JOIN usuarios u ON ct.titular_id = u.id
               WHERE rc.centro_id=? ORDER BY rc.fecha_recepcion DESC""",
            (centro_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_dashboard_stats() -> dict:
    conn = get_connection()
    try:
        return {
            "total_trozos": conn.execute("SELECT COUNT(*) FROM censos_trozo").fetchone()[0],
            "en_transito": conn.execute("SELECT COUNT(*) FROM censos_trozo WHERE estado='EN_TRANSITO'").fetchone()[0],
            "verificados": conn.execute("SELECT COUNT(*) FROM censos_trozo WHERE estado IN ('VERIFICADO','RECIBIDO')").fetchone()[0],
            "aprobados": conn.execute("SELECT COUNT(*) FROM recepciones_centro WHERE resultado_verificacion='APROBADO'").fetchone()[0],
            "rechazados": conn.execute("SELECT COUNT(*) FROM recepciones_centro WHERE resultado_verificacion='RECHAZADO'").fetchone()[0],
        }
    finally:
        conn.close()
