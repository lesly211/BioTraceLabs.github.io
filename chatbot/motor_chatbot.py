"""
Motor del chatbot OSINFOR - Lógica de conversación y verificación de inventario.
Gestiona el flujo de mensajes y la integración entre visión y base de datos.
"""

import json
from datetime import datetime
from typing import Optional
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
        print("[Chatbot] Motor del chatbot OSINFOR inicializado.")

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
