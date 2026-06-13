"""
Aplicación principal Flask del chatbot OSINFOR.
Maneja las rutas de la API y el servidor web.
"""

import os
import sys
import json
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import base64

# Añadir el directorio raíz al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

# Cargar variables de entorno
load_dotenv()

# Importar módulos del proyecto
from database.db_manager import initialize_database, obtener_estadisticas
from database.trazabilidad_manager import (
    initialize_trazabilidad, login_usuario, crear_censo_trozo,
    obtener_censos_titular, obtener_trozo_por_codigo, verificar_legalidad_trozo,
    registrar_guia_transporte, obtener_guias_chofer, registrar_recepcion_centro,
    obtener_recepciones_centro, get_dashboard_stats
)
from chatbot.motor_chatbot import ChatbotOsinfor

# Inicializar la aplicación Flask
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configuración
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo para imágenes
UPLOAD_FOLDER = ROOT_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Variables globales
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
chatbot = ChatbotOsinfor()
identificador = None


def inicializar_identificador():
    """Inicializa el identificador de árboles (con o sin API key)."""
    global identificador
    if GEMINI_API_KEY and GEMINI_API_KEY != "TU_API_KEY_AQUI":
        try:
            from identificador.vision_arboles import IdentificadorArboles
            identificador = IdentificadorArboles(api_key=GEMINI_API_KEY)
            print("[App] Identificador con Gemini Vision inicializado.")
        except Exception as e:
            print(f"[App] Error al inicializar Gemini: {e}")
            identificador = None
    else:
        print("[App] No se configuro API Key. Usando modo demo.")
        identificador = None


# ============================================================
# RUTAS WEB
# ============================================================

@app.route('/')
def index():
    """Página principal — sistema BioTrace con diseño actualizado."""
    from flask import redirect
    return redirect('/biotrace/index.html')


@app.route('/biotrace/')
@app.route('/biotrace/<path:filename>')
def biotrace_files(filename='index.html'):
    """Sirve archivos del sistema BioTrace con rutas relativas correctas."""
    return send_from_directory('biotrace', filename)


@app.route('/trazabilidad')
def trazabilidad_old():
    """Sistema de trazabilidad antiguo (legacy)."""
    return render_template('trazabilidad.html')


@app.route('/chatbot')
def chatbot_page():
    """Página del chatbot original."""
    return render_template('index.html')


# ============================================================
# API TRAZABILIDAD — 3 ROLES DE USUARIO
# ============================================================

@app.route('/api/traz/login', methods=['POST'])
def traz_login():
    data = request.get_json()
    usuario = login_usuario(data.get('email',''), data.get('password',''))
    if usuario:
        usuario.pop('password_hash', None)
        return jsonify({'success': True, 'usuario': usuario})
    return jsonify({'success': False, 'error': 'Email o contraseña incorrectos'}), 401


@app.route('/api/traz/censo', methods=['POST'])
def traz_censo():
    """Dueño de título: registra un nuevo trozo y genera código único."""
    try:
        foto_corte_path = ''
        foto_troza_path = ''
        uploads = ROOT_DIR / 'uploads'
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
        region = plan.split('-')[2] if plan and len(plan.split('-')) > 2 else 'LOT'
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
            region=region[:3].upper() if region else 'LOT'
        )
        return jsonify(res)
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/traz/trozos/<int:titular_id>')
def traz_trozos(titular_id):
    trozos = obtener_censos_titular(titular_id)
    return jsonify({'success': True, 'trozos': trozos})


@app.route('/api/traz/trozo/<codigo>')
def traz_trozo(codigo):
    t = obtener_trozo_por_codigo(codigo)
    if t:
        return jsonify({'success': True, 'trozo': t})
    return jsonify({'success': False, 'error': 'No encontrado'}), 404


@app.route('/api/traz/trozo-by-id/<int:trozo_id>')
def traz_trozo_by_id(trozo_id):
    from database.trazabilidad_manager import get_connection
    conn = get_connection()
    try:
        row = conn.execute('SELECT * FROM censos_trozo WHERE id=?', (trozo_id,)).fetchone()
        if row:
            return jsonify({'success': True, 'trozo': dict(row)})
        return jsonify({'success': False, 'error': 'No encontrado'}), 404
    finally:
        conn.close()


@app.route('/api/traz/verificar/<codigo>')
def traz_verificar(codigo):
    verificacion = verificar_legalidad_trozo(codigo)
    return jsonify({'success': True, 'verificacion': verificacion})


@app.route('/api/traz/guia', methods=['POST'])
def traz_guia():
    data = request.get_json()
    trozo = obtener_trozo_por_codigo(data.get('codigo_trozo',''))
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
    guias = obtener_guias_chofer(chofer_id)
    return jsonify({'success': True, 'guias': guias})


@app.route('/api/traz/recepcion', methods=['POST'])
def traz_recepcion():
    try:
        foto_path = ''
        if 'foto_corteza' in request.files:
            f = request.files['foto_corteza']
            if f.filename:
                p = ROOT_DIR / 'uploads' / f"corteza_{f.filename}"
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
    pedidos = obtener_recepciones_centro(centro_id)
    return jsonify({'success': True, 'pedidos': pedidos})


@app.route('/api/traz/stats')
def traz_stats():
    stats = get_dashboard_stats()
    stats_osinfor = obtener_estadisticas()
    stats.update(stats_osinfor)
    return jsonify({'success': True, 'stats': stats})


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


@app.route('/uploads/<path:filename>')
def uploaded_files(filename):
    """Sirve archivos subidos desde la carpeta uploads."""
    return send_from_directory(str(UPLOAD_FOLDER), filename)


# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/api/bienvenida', methods=['GET'])
def api_bienvenida():
    """Retorna el mensaje de bienvenida y estadísticas del sistema."""
    try:
        respuesta = chatbot.obtener_mensaje_bienvenida()
        respuesta['api_configurada'] = bool(GEMINI_API_KEY and GEMINI_API_KEY != "TU_API_KEY_AQUI")
        return jsonify({"success": True, "data": respuesta})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/verificar-arbol', methods=['POST'])
def api_verificar_arbol():
    """
    Endpoint principal: recibe una imagen y verifica si el árbol
    está en el inventario forestal.
    
    Acepta:
    - Multipart form data con campo 'imagen'
    - JSON con campo 'imagen_base64'
    """
    try:
        imagen_bytes = None

        # Obtener imagen desde multipart o base64
        if 'imagen' in request.files:
            archivo = request.files['imagen']
            if archivo.filename == '':
                return jsonify({"success": False, "error": "No se seleccionó ningún archivo"}), 400
            imagen_bytes = archivo.read()

        elif request.is_json and 'imagen_base64' in request.json:
            imagen_b64 = request.json['imagen_base64']
            # Remover el prefijo de data URL si existe
            if ',' in imagen_b64:
                imagen_b64 = imagen_b64.split(',')[1]
            imagen_bytes = base64.b64decode(imagen_b64)

        else:
            return jsonify({"success": False, "error": "No se proporcionó ninguna imagen"}), 400

        if len(imagen_bytes) == 0:
            return jsonify({"success": False, "error": "El archivo de imagen está vacío"}), 400

        # Usar identificador real o demo
        if identificador:
            id_usar = identificador
        else:
            # Crear un identificador de demo
            from identificador.vision_arboles import demo_sin_api

            class IdentificadorDemo:
                def identificar_desde_bytes(self, bytes_img):
                    return demo_sin_api()

            id_usar = IdentificadorDemo()

        # Procesar con el chatbot
        resultado = chatbot.procesar_imagen(imagen_bytes, id_usar)
        return jsonify({"success": True, "data": resultado})

    except Exception as e:
        print(f"[App] Error en verificar-arbol: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Error interno: {str(e)}"}), 500


@app.route('/api/estadisticas', methods=['GET'])
def api_estadisticas():
    """Retorna estadísticas del inventario forestal."""
    try:
        stats = obtener_estadisticas()
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/historial', methods=['GET'])
def api_historial():
    """Retorna el historial de consultas recientes."""
    try:
        historial = chatbot.obtener_historial_reciente()
        return jsonify({"success": True, "data": historial})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/especies', methods=['GET'])
def api_especies():
    """Lista todas las especies en el inventario."""
    try:
        especies = chatbot.obtener_especies_disponibles()
        return jsonify({"success": True, "data": especies})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def api_health():
    """Verificación de estado del servicio."""
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "api_gemini": bool(GEMINI_API_KEY and GEMINI_API_KEY != "TU_API_KEY_AQUI"),
        "modo_demo": not bool(GEMINI_API_KEY and GEMINI_API_KEY != "TU_API_KEY_AQUI")
    })


# ============================================================
# INICIALIZACIÓN
# ============================================================

def inicializar_app():
    """Inicializa todos los componentes de la aplicación."""
    print("\n" + "="*60)
    print("  OSINFOR - Sistema de Verificacion Forestal")
    print("  Chatbot de Identificacion de Arboles")
    print("="*60)

    # Inicializar base de datos
    print("\n[1/4] Inicializando base de datos inventario...")
    initialize_database()

    # Inicializar tablas de trazabilidad
    print("[2/4] Inicializando base de datos de trazabilidad...")
    initialize_trazabilidad()

    # Inicializar identificador visual
    print("[3/4] Configurando identificador de arboles...")
    inicializar_identificador()

    # Mostrar estado
    print("[4/4] Servidor listo.\n")
    print(f"  Base de datos: {ROOT_DIR / 'database' / 'inventario_osinfor.db'}")
    api_status = 'Configurada' if GEMINI_API_KEY and GEMINI_API_KEY != 'TU_API_KEY_AQUI' else 'No configurada (modo demo)'
    print(f"  API Gemini: {api_status}")
    print(f"  Interfaz web: http://localhost:5000")
    print("="*60 + "\n")


if __name__ == '__main__':
    inicializar_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
