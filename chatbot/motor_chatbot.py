"""
Motor del chatbot OSINFOR - Lógica de conversación y verificación de inventario.
Gestiona el flujo de mensajes y la integración entre visión y base de datos.
Soporta múltiples proveedores de IA: Grok (xAI) y Gemini (Google).
Permite procesar documentos (PDF, DOCX, imágenes) convirtiéndolos a texto plano.
"""

import json
from datetime import datetime
from typing import Optional
import os
from pathlib import Path
from database.db_manager import (
    buscar_arbol_por_especie,
    registrar_consulta,
    obtener_estadisticas,
    obtener_historial,
    listar_todas_especies
)


# Estados del chatbot
ESTADO_BIENVENIDA = "bienvenida"
ESTADO_ESPERANDO_FOTO = "esperando_foto"
ESTADO_MOSTRANDO_RESULTADO = "mostrando_resultado"
ESTADO_MENU = "menu"


class ChatbotOsinfor:
    """Chatbot para verificación de árboles en el inventario forestal OSINFOR."""

    def __init__(self):
        self.estado = ESTADO_BIENVENIDA
        self.ultimo_resultado = None
        self.modelo_conversacion = None
        self.chat_session = None
        self.proveedor_ia = None
        
        # Intentar inicializar con Groq primero, luego Grok, luego Gemini
        groq_key = os.getenv("GROQ_API_KEY", "")
        xai_key = os.getenv("XAI_API_KEY", "")
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        
        # Prioridad 1: Groq (inferencia ultrarrápida)
        if groq_key and groq_key not in ["TU_API_KEY_AQUI", "COLOCA_AQUI_TU_GROQ_API_KEY", ""]:
            try:
                from identificador.vision_groq import ChatbotGroq
                self.modelo_conversacion = ChatbotGroq(
                    api_key=groq_key,
                    instrucciones_sistema=self._obtener_instrucciones_sistema()
                )
                self.proveedor_ia = "groq"
                print("[Chatbot] Modelo de conversación Groq (Llama 3.3) activado.")
            except Exception as e:
                print(f"[Chatbot] Error al inicializar Groq: {e}")
                self.modelo_conversacion = None
        
        # Prioridad 2: Grok (xAI)
        if not self.modelo_conversacion and xai_key and xai_key not in ["TU_API_KEY_AQUI", "COLOCA_AQUI_TU_GROK_API_KEY", ""]:
            try:
                from identificador.vision_grok import ChatbotGrok
                self.modelo_conversacion = ChatbotGrok(
                    api_key=xai_key,
                    instrucciones_sistema=self._obtener_instrucciones_sistema()
                )
                self.proveedor_ia = "grok"
                print("[Chatbot] Modelo de conversación Grok (xAI) activado.")
            except Exception as e:
                print(f"[Chatbot] Error al inicializar Grok: {e}")
                self.modelo_conversacion = None
        
        # Prioridad 3: Gemini (Google)
        if not self.modelo_conversacion and gemini_key and gemini_key not in ["TU_API_KEY_AQUI", "COLOCA_AQUI_TU_API_KEY_CORRECTA", ""]:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                self.modelo_conversacion = genai.GenerativeModel(
                    model_name='gemini-1.5-flash',
                    system_instruction=self._obtener_instrucciones_sistema()
                )
                self.proveedor_ia = "gemini"
                print("[Chatbot] Modelo de conversación Gemini activado.")
            except Exception as e:
                print(f"[Chatbot] Error al inicializar Gemini: {e}")
                self.modelo_conversacion = None
        
        print("[Chatbot] Motor del chatbot OSINFOR inicializado.")
    
    def _obtener_instrucciones_sistema(self) -> str:
        """Retorna las instrucciones del sistema para el chatbot conversacional."""
        stats = obtener_estadisticas()
        especies = listar_todas_especies()
        especies_lista = ", ".join([f"{e['nombre_comun']} ({e['nombre_cientifico']})" 
                                   for e in especies[:10]])
        
        return f"""Eres un asistente experto en temas forestales y conservación, especializado en el inventario forestal de OSINFOR (Organismo de Supervisión de los Recursos Forestales y de Fauna Silvestre) del Perú.

INFORMACIÓN DEL SISTEMA:
- Total de árboles registrados: {stats.get('total_arboles', 0)}
- Especies diferentes: {stats.get('total_especies', 0)}
- Planes de manejo vigentes: {stats.get('total_planes', 0)}
- Especies protegidas: {stats.get('especies_protegidas', 0)}

ALGUNAS ESPECIES EN EL INVENTARIO:
{especies_lista}

TUS CAPACIDADES:
1. Responder preguntas sobre especies forestales del Perú (especialmente amazónicas)
2. Explicar temas de trazabilidad forestal y planes de manejo
3. Informar sobre especies protegidas y legislación forestal
4. Dar consejos sobre identificación de árboles
5. Explicar el funcionamiento del sistema de verificación OSINFOR
6. Responder sobre conceptos como DAP, volumen de madera, inventarios forestales, etc.

IMPORTANTE:
- Responde de forma clara, concisa y amigable
- Usa emojis forestales cuando sea apropiado: 🌳 🌲 🍃 🌿 🪵 📋
- Si te preguntan sobre verificar un árbol específico, recomienda subir una foto
- Si no sabes algo, sé honesto y sugiere consultar con especialistas
- Prioriza la información sobre las especies que están en el inventario
- Enfócate en temas forestales, no respondas sobre temas no relacionados

ESTILO:
- Profesional pero accesible
- Educativo y orientado a la conservación
- Usa lenguaje técnico solo cuando sea necesario, explicándolo siempre"""

    def procesar_imagen(self, imagen_bytes: bytes, identificador) -> dict:
        """
        Procesa una imagen subida por el usuario.
        
        Args:
            imagen_bytes: Bytes de la imagen
            identificador: Instancia del IdentificadorArboles
            
        Returns:
            Respuesta completa del chatbot con resultado de verificación
        """
        # Paso 1: Identificar el árbol con Gemini Vision
        print("[Chatbot] Procesando imagen con Vision API...")
        identificacion = identificador.identificar_desde_bytes(imagen_bytes)

        # Paso 2: Si se identificó, buscar en el inventario
        resultado_inventario = []
        estado_verificacion = "NO_IDENTIFICADO"

        if identificacion.get("identificado") and identificacion.get("es_arbol", True):
            nombre_cientifico = identificacion.get("nombre_cientifico", "")
            nombre_comun = identificacion.get("nombre_comun", "")

            # Buscar por nombre científico primero
            if nombre_cientifico:
                resultado_inventario = buscar_arbol_por_especie(
                    nombre_cientifico=nombre_cientifico
                )

            # Si no encontró, buscar por nombre común
            if not resultado_inventario and nombre_comun:
                resultado_inventario = buscar_arbol_por_especie(
                    nombre_comun=nombre_comun
                )

            estado_verificacion = "ENCONTRADO" if resultado_inventario else "NO_ENCONTRADO"

        # Paso 3: Construir respuesta del chatbot
        respuesta = self._construir_respuesta(
            identificacion=identificacion,
            resultado_inventario=resultado_inventario,
            estado_verificacion=estado_verificacion
        )

        # Paso 4: Registrar en historial
        codigo_arbol = resultado_inventario[0]['codigo_arbol'] if resultado_inventario else None
        registrar_consulta(
            especie=identificacion.get("nombre_cientifico") or identificacion.get("nombre_comun", "Desconocida"),
            confianza=identificacion.get("confianza", 0.0),
            codigo=codigo_arbol,
            resultado=estado_verificacion,
            imagen="[imagen_subida]",
            detalles={"identificacion": identificacion, "inventario": resultado_inventario[:2]}
        )

        self.ultimo_resultado = respuesta
        self.estado = ESTADO_MOSTRANDO_RESULTADO
        return respuesta

    def _construir_respuesta(self, identificacion: dict, resultado_inventario: list, estado_verificacion: str) -> dict:
        """Construye la respuesta estructurada del chatbot."""

        confianza = identificacion.get("confianza", 0.0)
        nombre_comun = identificacion.get("nombre_comun", "Desconocida")
        nombre_cientifico = identificacion.get("nombre_cientifico", "")

        # Determinar nivel de confianza
        if confianza >= 0.85:
            nivel_confianza = "alta"
            icono_confianza = "🟢"
        elif confianza >= 0.65:
            nivel_confianza = "media"
            icono_confianza = "🟡"
        else:
            nivel_confianza = "baja"
            icono_confianza = "🔴"

        # Construir mensaje principal según el estado
        if not identificacion.get("identificado"):
            mensaje_principal = (
                "🌿 No pude identificar con certeza la especie arbórea en esta imagen. "
                "Asegúrate de que la foto sea clara y muestre características del árbol "
                "(corteza, hojas, copa o frutos)."
            )
            tipo_alerta = "warning"

        elif not identificacion.get("es_arbol", True):
            mensaje_principal = "🌱 La imagen no parece mostrar un árbol. Por favor, sube una foto de un árbol."
            tipo_alerta = "warning"

        elif estado_verificacion == "ENCONTRADO":
            arboles_encontrados = len(resultado_inventario)
            planes = set(r['codigo_plan'] for r in resultado_inventario if r.get('codigo_plan'))
            mensaje_principal = (
                f"✅ ¡La especie **{nombre_comun}** (*{nombre_cientifico}*) "
                f"SÍ está registrada en el inventario forestal OSINFOR. "
                f"Se encontraron **{arboles_encontrados} ejemplar(es)** distribuidos en "
                f"**{len(planes)} plan(es) de manejo**."
            )
            tipo_alerta = "success"

        else:  # NO_ENCONTRADO
            mensaje_principal = (
                f"❌ La especie **{nombre_comun}** (*{nombre_cientifico}*) "
                f"NO se encuentra en el inventario forestal actual. "
                "Esto puede indicar extracción ilegal o que el árbol no está bajo ningún plan de manejo vigente."
            )
            tipo_alerta = "danger"

        # Detalles de la identificación
        detalles_identificacion = {
            "nombre_comun": nombre_comun,
            "nombre_cientifico": nombre_cientifico,
            "familia": identificacion.get("familia", ""),
            "confianza_pct": round(confianza * 100, 1),
            "nivel_confianza": nivel_confianza,
            "icono_confianza": icono_confianza,
            "caracteristicas": identificacion.get("caracteristicas_observadas", []),
            "descripcion": identificacion.get("descripcion", ""),
            "advertencias": identificacion.get("advertencias", ""),
            "alternativos": identificacion.get("nombres_alternativos", [])
        }

        # Detalles del inventario
        detalles_inventario = []
        for arbol in resultado_inventario:
            plan_estado = arbol.get('plan_estado', 'DESCONOCIDO')
            plan_icono = "✅" if plan_estado == "VIGENTE" else "⚠️"

            detalles_inventario.append({
                "codigo_arbol": arbol.get('codigo_arbol'),
                "ubicacion": arbol.get('ubicacion_descripcion'),
                "latitud": arbol.get('latitud'),
                "longitud": arbol.get('longitud'),
                "dap_cm": arbol.get('dap_cm'),
                "altura_m": arbol.get('altura_m'),
                "estado_fitosanitario": arbol.get('estado_fitosanitario'),
                "fecha_registro": arbol.get('fecha_registro'),
                "observaciones": arbol.get('observaciones'),
                "plan_codigo": arbol.get('codigo_plan'),
                "plan_nombre": arbol.get('plan_nombre'),
                "plan_titular": arbol.get('titular'),
                "plan_resolucion": arbol.get('resolucion_aprobacion'),
                "plan_vencimiento": arbol.get('fecha_vencimiento'),
                "plan_region": arbol.get('region'),
                "plan_estado": plan_estado,
                "plan_icono": plan_icono
            })

        # Recomendaciones
        recomendaciones = self._generar_recomendaciones(
            identificacion, estado_verificacion, resultado_inventario
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "estado_verificacion": estado_verificacion,
            "tipo_alerta": tipo_alerta,
            "mensaje_principal": mensaje_principal,
            "identificacion": detalles_identificacion,
            "inventario": detalles_inventario,
            "recomendaciones": recomendaciones,
            "total_encontrados": len(resultado_inventario)
        }

    def _generar_recomendaciones(self, identificacion: dict, estado: str, inventario: list) -> list[str]:
        """Genera recomendaciones basadas en el resultado de la verificación."""
        recomendaciones = []

        confianza = identificacion.get("confianza", 0.0)
        protegida_info = ""

        if estado == "ENCONTRADO":
            recomendaciones.append("📋 Verifique la resolución de aprobación del plan de manejo.")
            recomendaciones.append("🗓️ Confirme que el plan de manejo se encuentre vigente.")
            if confianza < 0.85:
                recomendaciones.append("🔍 La confianza de identificación es moderada; confirme la especie con un especialista.")
            # Verificar si hay árboles en mal estado
            en_mal_estado = [a for a in inventario if a.get('estado_fitosanitario') == 'Malo']
            if en_mal_estado:
                recomendaciones.append("⚠️ Existen ejemplares en mal estado fitosanitario que requieren atención.")

        elif estado == "NO_ENCONTRADO":
            recomendaciones.append("🚨 Reporte esta situación a OSINFOR si detecta actividad de extracción.")
            recomendaciones.append("📞 Contacte a las autoridades forestales locales (SERFOR/GORE).")
            recomendaciones.append("📸 Documente la ubicación GPS exacta del árbol.")
            if identificacion.get("protegida"):
                recomendaciones.append("⛔ Esta especie está protegida. La extracción no autorizada es un delito.")

        elif estado == "NO_IDENTIFICADO":
            recomendaciones.append("📷 Tome una foto con mejor iluminación y enfoque.")
            recomendaciones.append("🍃 Capture detalles de hojas, corteza o frutos para mejor identificación.")
            recomendaciones.append("👨‍🔬 Consulte con un botánico o especialista forestal si necesita identificación precisa.")

        return recomendaciones

    def obtener_mensaje_bienvenida(self) -> str:
        """Retorna el mensaje de bienvenida del chatbot."""
        stats = obtener_estadisticas()
        return {
            "tipo": "bienvenida",
            "stats": stats,
            "mensaje": (
                f"¡Bienvenido al Sistema de Verificación Forestal OSINFOR! 🌳\n\n"
                f"Estoy aquí para ayudarte a verificar si un árbol está incluido en el "
                f"**inventario forestal** y **planes de manejo vigentes**.\n\n"
                f"📊 Estado actual del inventario:\n"
                f"• **{stats.get('total_arboles', 0)}** árboles registrados\n"
                f"• **{stats.get('total_especies', 0)}** especies diferentes\n"
                f"• **{stats.get('total_planes', 0)}** planes de manejo vigentes\n"
                f"• **{stats.get('especies_protegidas', 0)}** especies protegidas monitoreadas\n\n"
                f"📸 **¿Cómo usar?** Sube una foto del árbol que deseas verificar."
            )
        }

    def obtener_historial_reciente(self) -> list[dict]:
        """Obtiene el historial de consultas recientes."""
        return obtener_historial(limite=5)

    def obtener_especies_disponibles(self) -> list[dict]:
        """Lista las especies en el inventario."""
        return listar_todas_especies()
    
    def procesar_documento(self, filepath: str, force_ocr: bool = False) -> dict:
        """
        Procesa un documento (PDF, DOCX, imagen) y lo convierte a texto plano.
        
        Args:
            filepath: Ruta al archivo del documento
            force_ocr: Forzar OCR incluso si el PDF tiene texto
            
        Returns:
            Resultado del procesamiento con el texto extraído
        """
        try:
            # Importar el módulo de conversión
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from conversacion_a_texto_plano import convert_to_text
            
            # Convertir documento a texto
            texto_extraido = convert_to_text(filepath, force_ocr=force_ocr)
            
            # Verificar si hay errores en la extracción
            if texto_extraido.startswith("[Error") or texto_extraido.startswith("[OCR no disponible"):
                return {
                    "tipo": "error",
                    "mensaje": texto_extraido,
                    "exito": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Contar palabras y caracteres
            palabras = len(texto_extraido.split())
            caracteres = len(texto_extraido)
            
            return {
                "tipo": "documento_procesado",
                "exito": True,
                "texto": texto_extraido,
                "estadisticas": {
                    "palabras": palabras,
                    "caracteres": caracteres,
                    "archivo": os.path.basename(filepath)
                },
                "mensaje": f"✅ Documento procesado exitosamente: {palabras} palabras, {caracteres} caracteres.",
                "timestamp": datetime.now().isoformat()
            }
            
        except ImportError as e:
            return {
                "tipo": "error",
                "mensaje": f"❌ Error al importar módulo de conversión: {str(e)}. Verifica que 'conversacion_a_texto_plano.py' esté en el directorio raíz.",
                "exito": False,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "tipo": "error",
                "mensaje": f"❌ Error al procesar documento: {str(e)}",
                "exito": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def procesar_documento_y_consultar(self, filepath: str, pregunta: str = None, force_ocr: bool = False) -> dict:
        """
        Procesa un documento y permite hacer preguntas sobre su contenido.
        
        Args:
            filepath: Ruta al archivo del documento
            pregunta: Pregunta opcional sobre el documento
            force_ocr: Forzar OCR incluso si el PDF tiene texto
            
        Returns:
            Respuesta del chatbot con el análisis del documento
        """
        # Primero procesar el documento
        resultado_doc = self.procesar_documento(filepath, force_ocr)
        
        if not resultado_doc.get("exito"):
            return resultado_doc
        
        texto_documento = resultado_doc["texto"]
        
        # Si no hay pregunta, solo retornar el documento procesado
        if not pregunta:
            return resultado_doc
        
        # Si hay pregunta, usar el modelo conversacional para responder
        if not self.modelo_conversacion:
            return {
                "tipo": "documento_procesado",
                "exito": True,
                "texto": texto_documento,
                "estadisticas": resultado_doc["estadisticas"],
                "mensaje": resultado_doc["mensaje"] + "\n\n⚠️ Para hacer preguntas sobre el documento, configura una API Key de IA.",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Construir prompt con el contexto del documento
            prompt_completo = f"""Analiza el siguiente documento y responde la pregunta del usuario.

DOCUMENTO:
{texto_documento[:4000]}{'...(documento truncado)' if len(texto_documento) > 4000 else ''}

PREGUNTA DEL USUARIO:
{pregunta}

Responde de forma clara y concisa basándote en el contenido del documento."""
            
            # Generar respuesta según el proveedor
            if self.proveedor_ia == "groq":
                respuesta_texto = self.modelo_conversacion.enviar_mensaje(prompt_completo)
            elif self.proveedor_ia == "grok":
                respuesta_texto = self.modelo_conversacion.enviar_mensaje(prompt_completo)
            elif self.proveedor_ia == "gemini":
                if not self.chat_session:
                    self.chat_session = self.modelo_conversacion.start_chat(history=[])
                response = self.chat_session.send_message(prompt_completo)
                respuesta_texto = response.text
            else:
                raise Exception("Proveedor de IA no reconocido")
            
            return {
                "tipo": "documento_consultado",
                "exito": True,
                "pregunta": pregunta,
                "respuesta": respuesta_texto,
                "estadisticas": resultado_doc["estadisticas"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "tipo": "documento_procesado",
                "exito": True,
                "texto": texto_documento,
                "estadisticas": resultado_doc["estadisticas"],
                "mensaje": resultado_doc["mensaje"] + f"\n\n❌ Error al analizar con IA: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def procesar_mensaje_texto(self, mensaje: str) -> dict:
        """
        Procesa un mensaje de texto del usuario y genera una respuesta conversacional.
        
        Args:
            mensaje: Texto del mensaje del usuario
            
        Returns:
            Respuesta del chatbot con texto y tipo
        """
        if not self.modelo_conversacion:
            return {
                "tipo": "texto",
                "respuesta": (
                    "⚠️ La función de conversación requiere una API Key de IA configurada.\n\n"
                    "**Opciones disponibles:**\n"
                    "• **Groq**: Configura GROQ_API_KEY en https://console.groq.com/ (Recomendado - ultrarrápido)\n"
                    "• **Grok (xAI)**: Configura XAI_API_KEY en https://console.x.ai/\n"
                    "• **Gemini (Google)**: Configura GEMINI_API_KEY en https://aistudio.google.com/app/apikey\n\n"
                    "🌳 Mientras tanto, puedes subir una foto de un árbol para verificarlo en el inventario."
                ),
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Generar respuesta según el proveedor
            if self.proveedor_ia == "groq":
                # Usar Groq (ChatbotGroq tiene su propio manejo de historial)
                respuesta_texto = self.modelo_conversacion.enviar_mensaje(mensaje)
            
            elif self.proveedor_ia == "grok":
                # Usar Grok (ChatbotGrok tiene su propio manejo de historial)
                respuesta_texto = self.modelo_conversacion.enviar_mensaje(mensaje)
            
            elif self.proveedor_ia == "gemini":
                # Usar Gemini
                if not self.chat_session:
                    self.chat_session = self.modelo_conversacion.start_chat(history=[])
                response = self.chat_session.send_message(mensaje)
                respuesta_texto = response.text
            
            else:
                raise Exception("Proveedor de IA no reconocido")
            
            # Detectar si el usuario pregunta por una especie específica
            especies = listar_todas_especies()
            especie_mencionada = None
            for especie in especies:
                nombre_comun = especie['nombre_comun'].lower()
                nombre_cientifico = especie['nombre_cientifico'].lower()
                if nombre_comun in mensaje.lower() or nombre_cientifico in mensaje.lower():
                    especie_mencionada = especie
                    break
            
            # Si menciona una especie, agregar datos del inventario
            datos_inventario = None
            if especie_mencionada:
                resultado_busqueda = buscar_arbol_por_especie(
                    nombre_cientifico=especie_mencionada['nombre_cientifico']
                )
                if resultado_busqueda:
                    datos_inventario = {
                        "especie": especie_mencionada['nombre_comun'],
                        "nombre_cientifico": especie_mencionada['nombre_cientifico'],
                        "total_arboles": len(resultado_busqueda),
                        "planes": list(set(r['codigo_plan'] for r in resultado_busqueda if r.get('codigo_plan'))),
                        "primer_arbol": resultado_busqueda[0] if resultado_busqueda else None
                    }
            
            return {
                "tipo": "texto",
                "respuesta": respuesta_texto,
                "datos_inventario": datos_inventario,
                "timestamp": datetime.now().isoformat(),
                "tiene_modelo": True
            }
            
        except Exception as e:
            print(f"[Chatbot] Error en conversación: {e}")
            return {
                "tipo": "texto",
                "respuesta": (
                    f"❌ Lo siento, ocurrió un error al procesar tu mensaje: {str(e)}\n\n"
                    "Intenta reformular tu pregunta o sube una foto para identificar un árbol."
                ),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
