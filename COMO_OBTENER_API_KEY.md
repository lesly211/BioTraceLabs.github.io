# 🔑 Cómo Obtener tu API Key de Google Gemini (GRATIS)

## Pasos Rápidos

### 1️⃣ Ve a Google AI Studio
Abre tu navegador y ve a: **https://aistudio.google.com/app/apikey**

### 2️⃣ Inicia Sesión
- Usa tu cuenta de Google (Gmail)
- Si no tienes una, créala gratis en gmail.com

### 3️⃣ Crear la API Key
Una vez dentro verás una pantalla con opciones:
- Haz clic en el botón **"Get API key"** o **"Create API key"**
- Si te pregunta sobre un proyecto, selecciona **"Create API key in new project"**

### 4️⃣ Copiar la Clave
- Se generará una clave que comienza con `AIza...`
- Haz clic en el botón de **copiar** 📋
- La clave se ve así: `AIzaSyD1234567890abcdefghijklmnopqrstuvwxyz`

### 5️⃣ Pegar en el Proyecto
1. Abre el archivo `.env` en la raíz del proyecto
2. Busca la línea que dice `GEMINI_API_KEY=`
3. Pega tu clave después del `=`
4. Debe quedar así:
   ```
   GEMINI_API_KEY=AIzaSyD1234567890abcdefghijklmnopqrstuvwxyz
   ```
5. **Guarda el archivo** (Ctrl + S)

### 6️⃣ Reiniciar el Servidor
- Detén el servidor Flask (Ctrl + C en la terminal)
- Vuelve a ejecutar: `py app.py`
- Verás el mensaje: **"API Gemini: Configurada"** ✅

## ⚠️ Formato Correcto vs Incorrecto

### ✅ CORRECTO
```
AIzaSyD1234567890abcdefghijklmnopqrstuvwxyz
AIzaBbC...
AIzaXyZ...
```
- Comienza con `AIza`
- Tiene aproximadamente 39 caracteres
- Solo letras, números y guiones

### ❌ INCORRECTO
```
AQ.Ab8RN6...          ← Este es OAuth2, NO Gemini
ya29.a0...            ← Este es un token temporal
TU_API_KEY_AQUI       ← Placeholder, necesitas reemplazarlo
```

## 🆓 Es Gratis?

**SÍ, es completamente GRATIS** con límites generosos:
- **15 consultas por minuto** (suficiente para uso normal)
- **1,500 consultas por día**
- **1 millón de tokens por mes**

No necesitas tarjeta de crédito para empezar.

## 🔒 Seguridad

**NUNCA** compartas tu API Key:
- ❌ No la subas a GitHub/GitLab públicos
- ❌ No la pongas en capturas de pantalla
- ✅ El archivo `.env` ya está en `.gitignore`

Si crees que tu clave se filtró:
1. Ve a https://aistudio.google.com/app/apikey
2. Elimina la clave comprometida
3. Crea una nueva

## 🆘 Problemas Comunes

### "API key not valid"
- Verifica que copiaste la clave completa
- No debe tener espacios al inicio o al final
- Verifica que comienza con `AIza`

### "Quota exceeded"
- Esperaste el límite de 15 solicitudes/minuto
- Espera 60 segundos y vuelve a intentar

### "Permission denied"
- Asegúrate de haber habilitado la API de Gemini en tu proyecto
- Ve a https://aistudio.google.com y verifica tu proyecto

## 📞 Ayuda Adicional

Si sigues teniendo problemas:
1. Revisa la documentación oficial: https://ai.google.dev/gemini-api/docs
2. Verifica que tu API key esté activa en el dashboard
3. Prueba regenerar una nueva API key

---

**Una vez configurada, podrás:**
- 🌳 Identificar árboles con IA mediante fotos
- 💬 Hacer preguntas sobre especies forestales
- ✅ Verificar árboles en el inventario OSINFOR
