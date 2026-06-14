# 🌳 OSINFOR - Sistema de Verificación Forestal con IA

Sistema de chatbot inteligente para verificación de árboles en el inventario forestal de OSINFOR (Organismo de Supervisión de los Recursos Forestales y de Fauna Silvestre del Perú).

## ✨ Características

- **Identificación visual de árboles** mediante IA con visión artificial
- **Chatbot conversacional** experto en temas forestales amazónicos
- **Sistema de trazabilidad forestal** completo (BioTrace)
- **Verificación de inventario** contra base de datos OSINFOR
- **Tres proveedores de IA** soportados: Groq, Grok (xAI) y Gemini

## 🚀 Proveedores de IA Soportados

El sistema soporta tres proveedores de IA con diferentes características:

### 1. Groq (Recomendado para velocidad)
- **Velocidad**: ULTRARRÁPIDO (10x-100x más rápido que otros)
- **Modelos**: Llama 3.2 Vision (90B) + Llama 3.3 (70B)
- **Precio**: Muy competitivo (~$0.005/imagen)
- **Créditos gratis**: $25 USD al registrarte
- **Guía**: Ver `COMO_OBTENER_GROQ_API_KEY.md`
- **Consola**: https://console.groq.com/

### 2. Grok - xAI (Recomendado para calidad)
- **Velocidad**: Rápido
- **Modelos**: Grok 4.3 (Vision + Texto)
- **Precio**: Moderado (~$0.01/imagen)
- **Créditos gratis**: $25 USD al registrarte
- **Guía**: Ver `COMO_OBTENER_GROK_API_KEY.md`
- **Consola**: https://console.x.ai/

### 3. Gemini - Google (Recomendado para desarrollo)
- **Velocidad**: Normal
- **Modelos**: Gemini 1.5 Flash
- **Precio**: GRATIS (límite 15 req/min)
- **Créditos gratis**: Ilimitado (con rate limit)
- **Guía**: Ver `COMO_OBTENER_API_KEY.md`
- **Consola**: https://aistudio.google.com/app/apikey

## 📋 Requisitos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Una API key de Groq, Grok o Gemini

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repo>
cd chatbotOsinfor
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar API Key

Abre el archivo `.env` y configura tu API key preferida:

```env
# Opción 1: Groq (más rápido) - RECOMENDADO
GROQ_API_KEY=gsk_tu_clave_aqui

# Opción 2: Grok (xAI) - mejor calidad
# XAI_API_KEY=xai-tu_clave_aqui

# Opción 3: Gemini (Google) - gratis
# GEMINI_API_KEY=AIza_tu_clave_aqui
```

**Prioridad**: Si configuras múltiples APIs, se usará: Groq > Grok > Gemini

### 4. Iniciar el servidor
```bash
python app.py
```

El servidor estará disponible en: http://localhost:5000

## 📖 Guías de Configuración

Según el proveedor que elijas:

- **Groq**: Lee `COMO_OBTENER_GROQ_API_KEY.md`
- **Grok (xAI)**: Lee `COMO_OBTENER_GROK_API_KEY.md`  
- **Gemini**: Lee `COMO_OBTENER_API_KEY.md`

## 🎯 Uso

### Chatbot de Verificación Forestal
1. Abre http://localhost:5000/chatbot
2. **Sube una foto** de un árbol para identificarlo
3. **Haz preguntas** sobre especies forestales, trazabilidad, etc.
4. El sistema verificará si el árbol está en el inventario OSINFOR

### Sistema BioTrace (Trazabilidad)
1. Abre http://localhost:5000/biotrace/
2. Sistema completo de trazabilidad forestal con 3 roles:
   - **Titular**: Registra censos y trozos
   - **Transportista**: Genera guías de transporte
   - **Centro de Transformación**: Recibe y verifica madera

## 🏗️ Estructura del Proyecto

```
chatbotOsinfor/
├── app.py                      # Aplicación principal Flask
├── .env                        # Configuración (API keys)
├── requirements.txt            # Dependencias Python
│
├── chatbot/
│   └── motor_chatbot.py       # Lógica del chatbot (Groq/Grok/Gemini)
│
├── identificador/
│   ├── vision_groq.py         # Identificador con Groq (Llama Vision)
│   ├── vision_grok.py         # Identificador con Grok (xAI)
│   └── vision_arboles.py      # Identificador con Gemini
│
├── database/
│   ├── db_manager.py          # Gestión de inventario forestal
│   └── trazabilidad_manager.py # Sistema de trazabilidad
│
├── templates/                  # Plantillas HTML
├── static/                     # CSS, JS, imágenes
└── biotrace/                   # Sistema BioTrace (nuevo diseño)
```

## 🔧 Tecnologías

- **Backend**: Flask (Python)
- **IA**: Groq / Grok (xAI) / Gemini (Google)
- **Base de datos**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Visión artificial**: PIL, OpenCV, scikit-image

## 🌟 Características de IA

### Identificación Visual (Llama 3.2 Vision / Grok Vision / Gemini Vision)
- Identifica especies arbóreas por foto
- Analiza corteza, hojas, flores, frutos
- Confianza de identificación (0-100%)
- Nombres común y científico
- Familia botánica

### Chatbot Conversacional (Llama 3.3 / Grok 4.3 / Gemini)
- Experto en flora amazónica peruana
- Responde sobre trazabilidad forestal
- Información sobre especies protegidas
- Legislación forestal OSINFOR/SERFOR
- Conceptos como DAP, volumen de madera, etc.

## 📊 Base de Datos

El sistema incluye:
- **Inventario forestal**: Árboles, especies, ubicaciones
- **Planes de manejo**: Resoluciones, titulares, vigencia
- **Trazabilidad**: Censos, guías, recepciones
- **Historial**: Consultas realizadas

## 🔒 Seguridad

- Las API keys están en `.env` (no se suben a Git)
- Validación de imágenes antes de procesarlas
- Rate limiting en las APIs
- Sanitización de entradas de usuario

## 🚨 Problemas Comunes

### "Invalid API key"
- Verifica que copiaste la clave completa
- Groq empieza con `gsk_`
- Grok empieza con `xai-`
- Gemini empieza con `AIza`

### "Insufficient credits"
- Revisa tu balance en la consola del proveedor
- Agrega créditos o cambia a Gemini (gratis)

### El servidor no inicia
- Verifica que tienes Python 3.10+
- Instala todas las dependencias: `pip install -r requirements.txt`
- Revisa que el puerto 5000 esté libre

## 📝 Licencia

Este proyecto es de código abierto para fines educativos y de investigación.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Haz un fork del proyecto
2. Crea una rama para tu feature
3. Envía un pull request

## 📧 Contacto

Para preguntas sobre OSINFOR y verificación forestal, visita: https://www.osinfor.gob.pe/

---

**Desarrollado con ❤️ para la conservación forestal del Perú**
