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
        print("[App] ⚠️ No se configuró API Key. Usando modo demo.")
        identificador = None


# ============================================================
# RUTAS WEB
# ============================================================

@app.route('/')
def index():
    """Página principal del chatbot."""
    return render_template('index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


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
    print("  🌳 OSINFOR - Sistema de Verificación Forestal")
    print("  Chatbot de Identificación de Árboles")
    print("="*60)

    # Inicializar base de datos
    print("\n[1/3] Inicializando base de datos...")
    initialize_database()

    # Inicializar identificador visual
    print("[2/3] Configurando identificador de árboles...")
    inicializar_identificador()

    # Mostrar estado
    print("[3/3] Servidor listo.\n")
    print(f"  📊 Base de datos: {ROOT_DIR / 'database' / 'inventario_osinfor.db'}")
    print(f"  🔑 API Gemini: {'✅ Configurada' if GEMINI_API_KEY and GEMINI_API_KEY != 'TU_API_KEY_AQUI' else '⚠️ No configurada (modo demo)'}")
    print(f"  🌐 Interfaz web: http://localhost:5000")
    print("="*60 + "\n")


if __name__ == '__main__':
    inicializar_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
