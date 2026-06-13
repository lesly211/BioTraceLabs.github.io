"""
BIO TRACE LABS — Sistema de Trazabilidad Forestal
API Flask con 3 roles: Titular, Chofer, Centro de Transformación
"""

import os
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# ── Configuración de rutas ──────────────────────────────────
ROOT_DIR = Path(__file__).parent
load_dotenv()

# ── Importar módulos de trazabilidad ───────────────────────
from database.db_manager import initialize_database, obtener_estadisticas
from database.trazabilidad_manager import (
    initialize_trazabilidad, login_usuario, crear_censo_trozo,
    obtener_censos_titular, obtener_trozo_por_codigo, verificar_legalidad_trozo,
    registrar_guia_transporte, obtener_guias_chofer, registrar_recepcion_centro,
    obtener_recepciones_centro, get_dashboard_stats, get_connection
)

# ── Inicializar Flask ───────────────────────────────────────
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB máx para fotos
UPLOADS_DIR = ROOT_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


# ============================================================
# RUTAS WEB
# ============================================================

@app.route('/')
def index():
    """Página principal del sistema de trazabilidad."""
    return render_template('trazabilidad.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


# ============================================================
# API — AUTENTICACIÓN
# ============================================================

@app.route('/api/traz/login', methods=['POST'])
def traz_login():
    data = request.get_json()
    usuario = login_usuario(data.get('email', ''), data.get('password', ''))
    if usuario:
        usuario.pop('password_hash', None)
        return jsonify({'success': True, 'usuario': usuario})
    return jsonify({'success': False, 'error': 'Email o contraseña incorrectos'}), 401


# ============================================================
# API — ROL TITULAR (Dueño de Título Habilitante)
# ============================================================

@app.route('/api/traz/censo', methods=['POST'])
def traz_censo():
    """Registra un nuevo trozo censado y devuelve su código único."""
    try:
        uploads = UPLOADS_DIR
        foto_corte_path = ''
        foto_troza_path = ''

        if 'foto_corte' in request.files:
            f = request.files['foto_corte']
            if f.filename:
                p = uploads / f"corte_{f.filename}"
                f.save(str(p))
                foto_corte_path = str(p)

        if 'foto_troza' in request.files:
            f = request.files['foto_troza']
            if f.filename:
                p = uploads / f"troza_{f.filename}"
                f.save(str(p))
                foto_troza_path = str(p)

        plan = request.form.get('plan_manejo', '')
        partes = plan.split('-')
        region = partes[2] if len(partes) > 2 else 'LOT'

        res = crear_censo_trozo(
            titular_id=int(request.form.get('titular_id', 1)),
            numero_parcela=request.form.get('numero_parcela', ''),
            especie=request.form.get('especie', ''),
            nombre_cientifico=request.form.get('nombre_cientifico', ''),
            latitud=float(request.form.get('latitud', 0) or 0),
            longitud=float(request.form.get('longitud', 0) or 0),
            dap_cm=float(request.form.get('dap_cm', 0) or 0),
            longitud_troza=float(request.form.get('longitud_troza', 0) or 0),
            volumen_m3=float(request.form.get('volumen_m3', 0) or 0),
            foto_corte_path=foto_corte_path,
            foto_troza_path=foto_troza_path,
            plan_manejo=plan,
            observaciones=request.form.get('observaciones', ''),
            region=region[:3].upper()
        )
        return jsonify(res)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/traz/trozos/<int:titular_id>')
def traz_trozos(titular_id):
    """Lista todos los trozos registrados por un titular."""
    trozos = obtener_censos_titular(titular_id)
    return jsonify({'success': True, 'trozos': trozos})


@app.route('/api/traz/trozo/<codigo>')
def traz_trozo(codigo):
    """Obtiene la información completa de un trozo por su código."""
    t = obtener_trozo_por_codigo(codigo)
    if t:
        return jsonify({'success': True, 'trozo': t})
    return jsonify({'success': False, 'error': 'Código no encontrado'}), 404


@app.route('/api/traz/trozo-by-id/<int:trozo_id>')
def traz_trozo_by_id(trozo_id):
    """Obtiene un trozo por su ID interno (para mostrar QR desde historial)."""
    conn = get_connection()
    try:
        row = conn.execute('SELECT * FROM censos_trozo WHERE id=?', (trozo_id,)).fetchone()
        if row:
            return jsonify({'success': True, 'trozo': dict(row)})
        return jsonify({'success': False, 'error': 'No encontrado'}), 404
    finally:
        conn.close()


# ============================================================
# API — ROL CHOFER
# ============================================================

@app.route('/api/traz/guia', methods=['POST'])
def traz_guia():
    """Genera una guía de transporte para un trozo."""
    data = request.get_json()
    trozo = obtener_trozo_por_codigo(data.get('codigo_trozo', ''))
    if not trozo:
        return jsonify({'success': False, 'error': 'Código de trozo no encontrado'}), 404
    res = registrar_guia_transporte(
        censo_id=trozo['id'],
        chofer_id=int(data.get('chofer_id', 1)),
        placa=data.get('placa', 'S/P'),
        origen=data.get('origen', ''),
        destino=data.get('destino', ''),
        observaciones=data.get('observaciones', '')
    )
    return jsonify(res)


@app.route('/api/traz/guias/<int:chofer_id>')
def traz_guias(chofer_id):
    """Lista las guías de transporte de un chofer."""
    guias = obtener_guias_chofer(chofer_id)
    return jsonify({'success': True, 'guias': guias})


# ============================================================
# API — ROL CENTRO DE TRANSFORMACIÓN PRIMARIA
# ============================================================

@app.route('/api/traz/verificar/<codigo>')
def traz_verificar(codigo):
    """Verifica la legalidad de un trozo por su código QR."""
    verificacion = verificar_legalidad_trozo(codigo)
    return jsonify({'success': True, 'verificacion': verificacion})


@app.route('/api/traz/recepcion', methods=['POST'])
def traz_recepcion():
    """Registra la recepción de un trozo en el centro y verifica su legalidad."""
    try:
        foto_path = ''
        if 'foto_corteza' in request.files:
            f = request.files['foto_corteza']
            if f.filename:
                p = UPLOADS_DIR / f"corteza_{f.filename}"
                f.save(str(p))
                foto_path = str(p)

        res = registrar_recepcion_centro(
            centro_id=int(request.form.get('centro_id', 1)),
            codigo_trozo=request.form.get('codigo_trozo', ''),
            foto_corteza_path=foto_path,
            observaciones=request.form.get('observaciones', '')
        )
        return jsonify(res)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/traz/pedidos/<int:centro_id>')
def traz_pedidos(centro_id):
    """Lista el historial de recepciones de un centro."""
    pedidos = obtener_recepciones_centro(centro_id)
    return jsonify({'success': True, 'pedidos': pedidos})


# ============================================================
# API — ESTADÍSTICAS GENERALES
# ============================================================

@app.route('/api/traz/stats')
def traz_stats():
    """Estadísticas del sistema: trozos, inventario OSINFOR, verificaciones."""
    stats = get_dashboard_stats()
    stats.update(obtener_estadisticas())
    return jsonify({'success': True, 'stats': stats})


@app.route('/api/health')
def api_health():
    return jsonify({'status': 'ok', 'version': '2.0.0', 'sistema': 'BIO TRACE LABS'})


# ============================================================
# INICIALIZACIÓN
# ============================================================

def inicializar_app():
    print("\n" + "="*55)
    print("  🌿 BIO TRACE LABS — Trazabilidad Forestal")
    print("  Sistema con 3 roles: Titular · Chofer · Centro")
    print("="*55)

    print("\n[1/3] Inicializando inventario OSINFOR...")
    initialize_database()

    print("[2/3] Inicializando módulo de trazabilidad...")
    initialize_trazabilidad()

    print("[3/3] Servidor listo.")
    print(f"\n  🌐 Web: http://localhost:5000")
    print(f"  📁 Uploads: {UPLOADS_DIR}")
    print("="*55 + "\n")


if __name__ == '__main__':
    inicializar_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
