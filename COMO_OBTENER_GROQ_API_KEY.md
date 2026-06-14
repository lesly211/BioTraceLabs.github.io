# 🚀 Cómo Obtener tu API Key de Groq

## Pasos para obtener tu API Key de Groq

### 1️⃣ Ve a Groq Console
Abre tu navegador y ve a: **https://console.groq.com/**

### 2️⃣ Crea una Cuenta o Inicia Sesión
- Si no tienes cuenta, haz clic en **"Sign Up"**
- Completa el registro (necesitarás un email válido)
- Si ya tienes cuenta, haz clic en **"Sign In"**

### 3️⃣ Accede a la Sección de API Keys
Una vez dentro del dashboard:
- Busca el menú lateral o la sección **"API Keys"**
- Haz clic en **"Create API Key"** o **"+ New Key"**

### 4️⃣ Copiar la Clave
- Se generará una clave que comienza con `gsk_`
- Ejemplo: `gsk_abcd1234efgh5678ijkl9012mnop3456qrst7890uvwxyzABCDEFGH`
- **IMPORTANTE**: Copia la clave INMEDIATAMENTE, no podrás verla de nuevo
- Haz clic en el botón de **copiar** 📋

### 5️⃣ Pegar en el Proyecto
1. Abre el archivo `.env` en la raíz del proyecto
2. Busca la línea que dice `GROQ_API_KEY=`
3. Pega tu clave después del `=`
4. Debe quedar así:
   ```env
   GROQ_API_KEY=gsk_abcd1234efgh5678ijkl9012mnop3456qrst7890uvwxyzABCDEFGH
   ```
5. **Guarda el archivo** (Ctrl + S)

### 6️⃣ Reiniciar el Servidor
- Detén el servidor Flask si está corriendo (Ctrl + C en la terminal)
- Vuelve a ejecutar: `py app.py`
- Verás el mensaje: **"Identificador con Groq Vision (Llama 3.2) inicializado"** ✅

## ⚠️ Formato Correcto

### ✅ CORRECTO
```
gsk_abcd1234efgh5678ijkl9012mnop3456qrst7890uvwxyzABCDEFGH
gsk_1234567890abcdefghijklmnopqrstuvwxyz1234567890AB
```
- Comienza con `gsk_`
- Seguido de caracteres alfanuméricos
- Longitud aproximada: 52-56 caracteres

### ❌ INCORRECTO
```
xai-...             ← Este es de Grok (xAI), no Groq
AIzaSy...           ← Este es de Gemini, no Groq
TU_API_KEY_AQUI     ← Placeholder, necesitas reemplazarlo
```

## 💰 Precio y Planes

### Plan Gratuito (Free Tier)
Groq ofrece créditos iniciales gratuitos para probar:
- **$25 USD en créditos** al registrarte (puede variar)
- Válidos por **1 mes**
- Suficiente para ~2,000-5,000 consultas (dependiendo del modelo)

### Precios Aproximados (después de créditos gratuitos)
- **Llama 3.2 Vision (90B)**: ~$0.005-0.01 USD por imagen
- **Llama 3.3 (70B, texto)**: ~$0.0001-0.0003 USD por mensaje
- **Mixtral**: ~$0.0002-0.0005 USD por mensaje

### Ventaja de Groq: **VELOCIDAD**
- ⚡ **10x-100x más rápido** que otros proveedores
- Usa chips LPU (Language Processing Units) propietarios
- Ideal para aplicaciones en tiempo real

### Recargar Créditos
Si se acaban tus créditos:
1. Ve a **Billing** en https://console.groq.com/
2. Agrega una tarjeta de crédito
3. Compra créditos adicionales

## 🆚 Groq vs Grok vs Gemini

### Ventajas de Groq
- ✅ **ULTRARRÁPIDO** (inferencia en milisegundos)
- ✅ Llama 3.3 (70B) - excelente calidad/precio
- ✅ Llama 3.2 Vision (90B) - soporte de imágenes
- ✅ Mixtral disponible
- ✅ Precio muy competitivo

### Ventajas de Grok (xAI)
- ✅ Modelo más reciente (Grok 4.3)
- ✅ Mejor comprensión de contexto
- ✅ Respuestas más naturales
- ✅ Acceso a información más reciente

### Ventajas de Gemini
- ✅ Completamente GRATIS (15 req/min)
- ✅ Límites más generosos para uso personal
- ✅ Integración más madura

### ¿Cuál elegir?
- **Para velocidad extrema**: Groq (recomendado)
- **Para mejor calidad/contexto**: Grok (xAI)
- **Para pruebas/hobby**: Gemini (gratis)
- **Alternativa**: El sistema soporta los tres, puedes configurarlos y alternar

## 🔒 Seguridad

**NUNCA** compartas tu API Key:
- ❌ No la subas a GitHub/GitLab públicos
- ❌ No la pongas en capturas de pantalla
- ❌ No la compartas en Discord/Slack/etc.
- ✅ El archivo `.env` ya está en `.gitignore`

### Si tu clave se filtra:
1. Ve inmediatamente a https://console.groq.com/
2. Revoca la clave comprometida
3. Genera una nueva
4. Actualiza tu archivo `.env`

## 🆘 Problemas Comunes

### "Invalid API key" / "Authentication failed"
- Verifica que copiaste la clave completa (incluyendo `gsk_`)
- No debe tener espacios al inicio o al final
- Verifica que la clave esté activa en el dashboard

### "Insufficient credits" / "Rate limit exceeded"
- Revisa tu balance en https://console.groq.com/billing
- Agrega créditos si es necesario
- O cambia temporalmente a Gemini (gratis)

### "Model not found" / "Model not supported"
- Verifica que el modelo `llama-3.2-90b-vision-preview` esté disponible
- Para conversación usa: `llama-3.3-70b-versatile`
- Revisa la documentación de Groq para modelos actuales

### Error al importar librería `groq`
- Asegúrate de instalar: `pip install groq`
- O reinstala todas las dependencias: `pip install -r requirements.txt`

## 📖 Documentación Oficial

- **Groq Console**: https://console.groq.com/
- **Documentación API**: https://console.groq.com/docs
- **Modelos disponibles**: https://console.groq.com/docs/models
- **Playground**: https://console.groq.com/playground
- **GitHub**: https://github.com/groq

## 🔄 Configuración en el Proyecto

### Archivo `.env` completo
```env
# Opción 1: Groq - Recomendado para velocidad extrema (10x-100x más rápido)
GROQ_API_KEY=gsk_tu_clave_aqui

# Opción 2: Grok (xAI) - Recomendado para mejor calidad
XAI_API_KEY=xai-tu_clave_aqui

# Opción 3: Gemini (Google) - Gratis pero con límites
GEMINI_API_KEY=AIza_tu_clave_aqui

# Prioridad: Groq > Grok > Gemini
```

### Verificar Configuración
Al iniciar el servidor (`py app.py`), deberías ver:
```
[Vision Groq] Identificador de árboles inicializado con llama-3.2-90b-vision-preview.
[Chatbot Groq] Modelo de conversación llama-3.3-70b-versatile activado.
[App] Identificador con Groq Vision (Llama 3.2) inicializado.
...
API: Groq (Llama 3.3)
```

## 🚀 Empezar a Usar

Una vez configurado:
1. Abre http://localhost:5000/chatbot
2. Verás "Groq (Llama 3.3) activo" en el header
3. **Haz preguntas**: "¿Qué es la caoba?"
4. **Sube fotos**: Arrastra una imagen de un árbol
5. ¡Disfruta de respuestas **ULTRARRÁPIDAS** con Groq!

## ⚡ Ventajas de Usar Groq en Este Proyecto

### Velocidad
- **Identificación de imágenes**: 0.5-2 segundos (vs 5-10 segundos con otros)
- **Respuestas de chat**: 0.1-0.5 segundos (vs 2-5 segundos con otros)
- **Mejor experiencia de usuario**: Respuestas casi instantáneas

### Calidad
- **Llama 3.2 Vision (90B)**: Comparable a GPT-4 Vision
- **Llama 3.3 (70B)**: Excelente para conversación natural
- **Precisión**: Alta en identificación de especies arbóreas

### Costo
- **Más barato** que GPT-4 Vision y Grok
- **Más rápido** que Gemini
- **Mejor relación calidad/precio/velocidad**

## 🌳 Modelos Usados en Este Proyecto

### Para Identificación de Árboles (Visión)
- **Modelo**: `llama-3.2-90b-vision-preview`
- **Capacidades**: Análisis de imágenes, identificación de especies
- **Ventajas**: Rápido, preciso, multimodal

### Para Conversación (Texto)
- **Modelo**: `llama-3.3-70b-versatile`
- **Capacidades**: Conversación natural, respuestas contextuales
- **Ventajas**: Muy rápido, versátil, excelente comprensión

---

**¿Tienes problemas?** Prueba con Gemini (gratis) primero, lee la guía `COMO_OBTENER_API_KEY.md`
