"""
Módulo de identificación de árboles mediante imágenes.
Utiliza la API de Google Gemini Vision para analizar fotos
e identificar especies arbóreas.
"""

import google.generativeai as genai
import base64
import json
import re
import os
from pathlib import Path
from PIL import Image
import io


# Prompt especializado para identificación de árboles amazónicos
PROMPT_IDENTIFICACION = """
Eres un experto botánico especializado en la flora amazónica del Perú y árbol forestal.
Analiza cuidadosamente la imagen proporcionada e identifica la especie arbórea.

Considera las siguientes características para tu análisis:
- Forma y textura de la corteza
- Tipo y disposición de las hojas
- Presencia de flores o frutos
- Arquitectura general del árbol
- Raíces o contrafuertes visibles
- Color y textura general

Responde ÚNICAMENTE en formato JSON con la siguiente estructura exacta:
{
  "identificado": true/false,
  "nombre_comun": "nombre común en español",
  "nombre_cientifico": "Género especie",
  "familia": "Familia botánica",
  "confianza": 0.0-1.0,
  "caracteristicas_observadas": ["característica 1", "característica 2"],
  "descripcion": "Breve descripción de por qué identificaste esta especie",
  "es_arbol": true/false,
  "advertencias": "Cualquier advertencia sobre la identificación o si la imagen no es clara",
  "nombres_alternativos": ["posible especie 2", "posible especie 3"]
}

Si no puedes identificar con certeza, establece "identificado": false y explica en "advertencias".
Si la imagen no muestra un árbol, establece "es_arbol": false.
"""


class IdentificadorArboles:
    """Clase para identificar especies arbóreas mediante fotos usando Gemini Vision."""

    def __init__(self, api_key: str):
        """
        Inicializa el identificador con la API key de Google Gemini.
        
        Args:
            api_key: Clave de la API de Google Gemini
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        print("[Vision] Identificador de árboles inicializado con Gemini Vision.")

    def identificar_desde_bytes(self, imagen_bytes: bytes) -> dict:
        """
        Identifica un árbol a partir de bytes de imagen.
        
        Args:
            imagen_bytes: Bytes de la imagen
            
        Returns:
            Diccionario con resultados de la identificación
        """
        try:
            # Verificar y procesar la imagen
            imagen_pil = Image.open(io.BytesIO(imagen_bytes))

            # Redimensionar si es muy grande (para optimizar el uso de la API)
            max_size = (1024, 1024)
            imagen_pil.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convertir a bytes optimizados
            buffer = io.BytesIO()
            formato = 'JPEG' if imagen_pil.mode != 'RGBA' else 'PNG'
            if imagen_pil.mode == 'RGBA':
                imagen_pil = imagen_pil.convert('RGB')
            imagen_pil.save(buffer, format='JPEG', quality=85)
            imagen_bytes_opt = buffer.getvalue()

            # Llamar a la API de Gemini
            response = self.model.generate_content([
                PROMPT_IDENTIFICACION,
                {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(imagen_bytes_opt).decode()
                }
            ])

            # Parsear respuesta JSON
            resultado = self._parsear_respuesta(response.text)
            return resultado

        except Exception as e:
            print(f"[Vision] Error al identificar imagen: {e}")
            return {
                "identificado": False,
                "error": str(e),
                "nombre_comun": None,
                "nombre_cientifico": None,
                "confianza": 0.0,
                "advertencias": f"Error al procesar la imagen: {str(e)}"
            }

    def identificar_desde_path(self, ruta_imagen: str) -> dict:
        """
        Identifica un árbol a partir de la ruta de una imagen.
        
        Args:
            ruta_imagen: Ruta del archivo de imagen
            
        Returns:
            Diccionario con resultados de la identificación
        """
        with open(ruta_imagen, 'rb') as f:
            imagen_bytes = f.read()
        return self.identificar_desde_bytes(imagen_bytes)

    def _parsear_respuesta(self, texto_respuesta: str) -> dict:
        """
        Extrae y parsea el JSON de la respuesta del modelo.
        
        Args:
            texto_respuesta: Texto de respuesta del modelo
            
        Returns:
            Diccionario con los datos parseados
        """
        try:
            # Buscar JSON en la respuesta (el modelo puede incluir texto extra)
            # Patrón para encontrar el bloque JSON
            patron_json = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(patron_json, texto_respuesta, re.DOTALL)

            if matches:
                # Intentar parsear el JSON más largo encontrado
                for match in sorted(matches, key=len, reverse=True):
                    try:
                        resultado = json.loads(match)
                        # Validar que tiene los campos esperados
                        if 'identificado' in resultado:
                            return resultado
                    except json.JSONDecodeError:
                        continue

            # Si no se encontró JSON válido, extraer del markdown
            if '```json' in texto_respuesta:
                json_block = texto_respuesta.split('```json')[1].split('```')[0].strip()
                return json.loads(json_block)
            elif '```' in texto_respuesta:
                json_block = texto_respuesta.split('```')[1].split('```')[0].strip()
                return json.loads(json_block)

            # Último recurso: parsear directamente
            return json.loads(texto_respuesta)

        except Exception as e:
            print(f"[Vision] Error parseando respuesta: {e}")
            print(f"[Vision] Respuesta raw: {texto_respuesta[:500]}")
            # Retornar resultado básico extraído del texto
            return {
                "identificado": False,
                "nombre_comun": None,
                "nombre_cientifico": None,
                "confianza": 0.0,
                "descripcion": texto_respuesta[:300],
                "advertencias": "No se pudo parsear la respuesta del modelo correctamente",
                "raw_response": texto_respuesta
            }


def demo_sin_api() -> dict:
    """
    Retorna una identificación de demostración cuando no hay API key.
    Útil para pruebas sin conexión.
    """
    import random
    especies_demo = [
        {"nombre_comun": "Caoba", "nombre_cientifico": "Swietenia macrophylla", "confianza": 0.87},
        {"nombre_comun": "Cedro", "nombre_cientifico": "Cedrela odorata", "confianza": 0.82},
        {"nombre_comun": "Tornillo", "nombre_cientifico": "Cedrelinga cateniformis", "confianza": 0.79},
        {"nombre_comun": "Lupuna", "nombre_cientifico": "Ceiba pentandra", "confianza": 0.91},
        {"nombre_comun": "Shihuahuaco", "nombre_cientifico": "Dipteryx micrantha", "confianza": 0.75},
    ]
    especie = random.choice(especies_demo)
    return {
        "identificado": True,
        "nombre_comun": especie["nombre_comun"],
        "nombre_cientifico": especie["nombre_cientifico"],
        "familia": "Fabaceae",
        "confianza": especie["confianza"],
        "caracteristicas_observadas": ["Corteza rugosa", "Hojas compuestas", "Copa amplia"],
        "descripcion": f"MODO DEMO - Identificación simulada de {especie['nombre_comun']}",
        "es_arbol": True,
        "advertencias": "⚠️ MODO DEMO: Configure su API Key de Google Gemini para identificación real.",
        "nombres_alternativos": []
    }
