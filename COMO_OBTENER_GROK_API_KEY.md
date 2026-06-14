# 🤖 Cómo Obtener tu API Key de Grok (xAI)

## Pasos para obtener tu API Key de Grok

### 1️⃣ Ve a xAI Console
Abre tu navegador y ve a: **https://console.x.ai/**

### 2️⃣ Crea una Cuenta o Inicia Sesión
- Si no tienes cuenta, haz clic en **"Sign Up"**
- Completa el registro (necesitarás un email válido)
- Si ya tienes cuenta, haz clic en **"Sign In"**

### 3️⃣ Accede a la Sección de API Keys
Una vez dentro del dashboard:
- Busca el menú lateral o la sección **"API Keys"**
- Haz clic en **"Create new API key"** o **"Generate API key"**

### 4️⃣ Copiar la Clave
- Se generará una clave que comienza con `xai-`
- Ejemplo: `xai-abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx`
- **IMPORTANTE**: Copia la clave INMEDIATAMENTE, no podrás verla de nuevo
- Haz clic en el botón de **copiar** 📋

### 5️⃣ Pegar en el Proyecto
1. Abre el archivo `.env` en la raíz del proyecto
2. Busca la línea que dice `XAI_API_KEY=`
3. Pega tu clave después del `=`
4. Debe quedar así:
   ```env
   XAI_API_KEY=xai-abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx
   ```
5. **Guarda el archivo** (Ctrl + S)

### 6️⃣ Reiniciar el Servidor
- Detén el servidor Flask si está corriendo (Ctrl + C en la terminal)
- Vuelve a ejecutar: `py app.py`
- Verás el mensaje: **"Identificador con Grok Vision (xAI) inicializado"** ✅

## ⚠️ Formato Correcto

### ✅ CORRECTO
```
xai-abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx
xai-1234567890abcdefghijklmnopqrstuvwxyz123456
```
- Comienza con `xai-`
- Seguido de caracteres alfanuméricos
- Longitud aproximada: 48-52 caracteres

### ❌ INCORRECTO
```
AIzaSy...           ← Este es de Gemini, no Grok
AQ.Ab8...           ← Este es OAuth2, no Grok
TU_API_KEY_AQUI     ← Placeholder, necesitas reemplazarlo
```

## 💰 Precio y Planes

### Plan Gratuito (Free Tier)
xAI ofrece créditos iniciales gratuitos para probar Grok:
- **$25 USD en créditos** al registrarte
- Válidos por **1 mes**
- Suficiente para ~1,000-2,000 consultas (dependiendo del modelo)

### Precios Aproximados (después de créditos gratuitos)
- **Grok-2-Vision**: ~$0.01-0.02 USD por imagen
- **Grok-2 (texto)**: ~$0.0001-0.0005 USD por mensaje

### Recargar Créditos
Si se acaban tus créditos:
1. Ve a **Billing** en https://console.x.ai/
2. Agrega una tarjeta de crédito
3. Compra créditos adicionales

## 🆚 Grok vs Gemini

### Ventajas de Grok
- ✅ Modelo más reciente y actualizado
- ✅ Mejor comprensión de contexto
- ✅ Respuestas más naturales
- ✅ Acceso a información más reciente

### Ventajas de Gemini
- ✅ Completamente GRATIS (15 req/min)
- ✅ Límites más generosos para uso personal
- ✅ Integración más madura

### ¿Cuál elegir?
- **Para pruebas/hobby**: Gemini (gratis)
- **Para producción/mejor calidad**: Grok
- **Alternativa**: El sistema soporta ambos, puedes configurar los dos y alternar

## 🔒 Seguridad

**NUNCA** compartas tu API Key:
- ❌ No la subas a GitHub/GitLab públicos
- ❌ No la pongas en capturas de pantalla
- ❌ No la compartas en Discord/Slack/etc.
- ✅ El archivo `.env` ya está en `.gitignore`

### Si tu clave se filtra:
1. Ve inmediatamente a https://console.x.ai/
2. Revoca la clave comprometida
3. Genera una nueva
4. Actualiza tu archivo `.env`

## 🆘 Problemas Comunes

### "Invalid API key"
- Verifica que copiaste la clave completa (incluyendo `xai-`)
- No debe tener espacios al inicio o al final
- Verifica que la clave esté activa en el dashboard

### "Insufficient credits"
- Revisa tu balance en https://console.x.ai/billing
- Agrega créditos si es necesario
- O cambia temporalmente a Gemini (gratis)

### "Rate limit exceeded"
- Has superado el límite de solicitudes por minuto
- Espera 60 segundos y vuelve a intentar
- Considera actualizar tu plan si es frecuente

### "Model not found"
- Verifica que el modelo `grok-2-vision-1212` esté disponible
- Revisa la documentación de xAI para modelos actuales
- El código se actualizará automáticamente si el modelo cambia

## 📖 Documentación Oficial

- **xAI Console**: https://console.x.ai/
- **Documentación API**: https://docs.x.ai/
- **Precios**: https://x.ai/pricing
- **Status del servicio**: https://status.x.ai/

## 🔄 Configuración en el Proyecto

### Archivo `.env` completo
```env
# Opción 1: Grok (xAI) - Recomendado para mejor calidad
XAI_API_KEY=xai-tu_clave_aqui

# Opción 2: Gemini (Google) - Gratis pero con límites
GEMINI_API_KEY=AIza_tu_clave_aqui

# Prioridad: Si ambas están configuradas, se usa Grok primero
```

### Verificar Configuración
Al iniciar el servidor (`py app.py`), deberías ver:
```
[Vision Grok] Identificador de árboles inicializado con Grok Vision.
[Chatbot Grok] Modelo de conversación Grok activado.
[App] Identificador con Grok Vision (xAI) inicializado.
...
API Gemini/Grok: Configurada
```

## 🚀 Empezar a Usar

Una vez configurado:
1. Abre http://localhost:5000/chatbot
2. Verás "Grok (xAI) activo" en el header
3. **Haz preguntas**: "¿Qué es la caoba?"
4. **Sube fotos**: Arrastra una imagen de un árbol
5. ¡Disfruta de respuestas con IA de última generación!

---

**¿Prefieres usar Gemini gratis?** Lee la guía `COMO_OBTENER_API_KEY.md`
