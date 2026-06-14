"""
Módulo de identificación de árboles mediante imágenes usando Groq.
Utiliza la API de Groq con modelos Llama Vision para analizar fotos
e identificar especies arbóreas con inferencia ultrarrápida.
"""

from groq import Groq
import base64
import json
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


class IdentificadorArbolesGroq:
    """Clase para identificar especies arbóreas mediante fotos usando Groq (Llama Vision)."""

    def __init__(self, api_key: str):
        """
        Inicializa el identificador con la API key de Groq.
        
        Args:
            api_key: Clave de la API de Groq
        """
        self.client = Groq(api_key=api_key)
        # Llama 3.2 Vision soporta imágenes
        self.model = "llama-3.2-90b-vision-preview"
        print(f"[Vision Groq] Identificador de árboles inicializado con {self.model}.")

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
            if imagen_pil.mode == 'RGBA':
                imagen_pil = imagen_pil.convert('RGB')
            imagen_pil.save(buffer, format='JPEG', quality=85)
            imagen_bytes_opt = buffer.getvalue()

            # Convertir a base64
            imagen_base64 = base64.b64encode(imagen_bytes_opt).decode('utf-8')
            
            # Llamar a la API de Groq Vision
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": PROMPT_IDENTIFICACION
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{imagen_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )

            # Extraer respuesta
            texto_respuesta = response.choices[0].message.content
            
            # Parsear respuesta JSON
            resultado = self._parsear_respuesta(texto_respuesta)
            return resultado

        except Exception as e:
            print(f"[Vision Groq] Error al identificar imagen: {e}")
            import traceback
            traceback.print_exc()
            return {
                "identificado": False,
                "error": str(e),
                "nombre_comun": None,
                "nombre_cientifico": None,
                "confianza": 0.0,
                "advertencias": f"Error al procesar la imagen con Groq: {str(e)}"
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
            # Buscar JSON en la respuesta
            import re
            
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
            print(f"[Vision Groq] Error parseando respuesta: {e}")
            print(f"[Vision Groq] Respuesta raw: {texto_respuesta[:500]}")
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


class ChatbotGroq:
    """Clase para conversación con Groq sobre temas forestales."""
    
    def __init__(self, api_key: str, instrucciones_sistema: str):
        """
        Inicializa el chatbot conversacional con Groq.
        
        Args:
            api_key: Clave de la API de Groq
            instrucciones_sistema: Instrucciones del sistema para el contexto
        """
        self.client = Groq(api_key=api_key)
        # Usar Llama 3.3 que es excelente para conversación
        self.model = "llama-3.3-70b-versatile"
        self.instrucciones_sistema = instrucciones_sistema
        self.historial = []
        print(f"[Chatbot Groq] Modelo de conversación {self.model} activado.")
    
    def enviar_mensaje(self, mensaje: str) -> str:
        """
        Envía un mensaje y obtiene una respuesta.
        
        Args:
            mensaje: Mensaje del usuario
            
        Returns:
            Respuesta del chatbot
        """
        try:
            # Agregar mensaje al historial
            self.historial.append({"role": "user", "content": mensaje})
            
            # Preparar mensajes (sistema + historial)
            mensajes = [
                {"role": "system", "content": self.instrucciones_sistema}
            ] + self.historial
            
            # Llamar a la API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=mensajes,
                temperature=0.7,
                max_tokens=1500
            )
            
            respuesta = response.choices[0].message.content
            
            # Agregar respuesta al historial
            self.historial.append({"role": "assistant", "content": respuesta})
            
            # Mantener historial limitado (últimos 10 mensajes)
            if len(self.historial) > 20:
                self.historial = self.historial[-20:]
            
            return respuesta
            
        except Exception as e:
            print(f"[Chatbot Groq] Error: {e}")
            import traceback
            traceback.print_exc()
            raise
