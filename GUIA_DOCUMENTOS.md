# 📄 Guía de Uso: Análisis de Documentos con el Chatbot

## 🎯 Capacidades del Chatbot

El chatbot ahora puede **leer y analizar documentos completos** incluyendo:
- 📕 **PDFs** (con texto o escaneados usando OCR)
- 📘 **Documentos Word** (DOCX, DOC)
- 📄 **Archivos de texto** (TXT, MD)
- 📷 **Imágenes con texto** (PNG, JPG con OCR)

---

## 🚀 Cómo Usar

### Opción 1: Análisis Automático (sin pregunta específica)

1. Ve a http://localhost:5000/chatbot
2. Arrastra tu documento PDF (o haz clic para seleccionar)
3. Verás un preview con el nombre y tamaño del archivo
4. **Deja el campo de pregunta vacío**
5. Haz clic en **"📖 Analizar documento"**

**El chatbot automáticamente te dará:**
- ✅ Tema principal y propósito del documento
- ✅ Puntos clave más importantes
- ✅ Estructura y secciones principales
- ✅ Datos relevantes (fechas, números, nombres)

### Opción 2: Pregunta Específica

1. Sube tu documento
2. En el campo de pregunta escribe algo como:
   - "¿Cuál es el tema principal?"
   - "Resume este documento"
   - "¿Qué dice sobre la resolución?"
   - "Extrae todas las fechas importantes"
   - "¿Quiénes son los involucrados?"
3. Haz clic en **"📖 Analizar documento"**

**El chatbot responderá específicamente tu pregunta** basándose en todo el contenido del documento.

---

## 📋 Ejemplo con tu documento

### Documento: R.G.R. 107-2021-GRU-GGR-GERFFS.pdf

**Forma 1: Análisis general**
```
1. Sube el PDF
2. Deja la pregunta vacía
3. Analizar documento
→ El chatbot leerá las 10 páginas y te dará un resumen completo
```

**Forma 2: Preguntas específicas**
```
Pregunta: "¿De qué trata esta resolución?"
→ Respuesta específica sobre el contenido

Pregunta: "¿Cuál es la fecha y número de resolución?"
→ Extrae datos específicos

Pregunta: "¿Qué normas o leyes se mencionan?"
→ Lista todas las referencias legales

Pregunta: "Resume los puntos principales de esta resolución"
→ Resumen ejecutivo del documento
```

---

## 💡 Tipos de Preguntas que Puedes Hacer

### Preguntas Generales
- "Resume este documento"
- "¿De qué trata?"
- "¿Cuál es el tema principal?"
- "Dame los puntos más importantes"

### Preguntas de Extracción
- "¿Qué fechas se mencionan?"
- "¿Quiénes son los involucrados?"
- "¿Cuáles son los números de resolución?"
- "Lista todas las especies mencionadas"

### Preguntas Específicas
- "¿Qué dice sobre [tema específico]?"
- "¿Cuál es la sanción o consecuencia?"
- "¿Qué requisitos se necesitan?"
- "¿Cuál es el plazo establecido?"

### Preguntas de Análisis
- "¿Cuáles son las implicaciones de este documento?"
- "¿Qué diferencias hay con [otro documento]?"
- "¿Es favorable o desfavorable?"

---

## 🔧 Características Técnicas

### Procesamiento de PDFs
- **PDFs con texto seleccionable**: Extracción directa instantánea
- **PDFs escaneados/imágenes**: OCR automático en español
- **PDFs mixtos**: Combina extracción + OCR según sea necesario

### Documentos Largos
- ✅ Sin límite de páginas
- ✅ Lee el documento completo
- ✅ Analiza todo el contenido (no solo los primeros párrafos)
- ✅ La IA procesa hasta 4000 caracteres del documento para dar respuestas

### Estadísticas que Muestra
- 📊 Número total de palabras
- 📊 Número total de caracteres
- 📄 Nombre del archivo
- 📄 Tamaño en KB

---

## 🎨 Interfaz Mejorada

### Preview de Documentos
Muestra:
- 📕 Icono según tipo de archivo (PDF, Word, TXT)
- 📄 Nombre completo del archivo
- 📊 Tamaño del archivo
- 💬 Campo opcional para preguntas

### Respuestas Formateadas
- ✅ Fondo con color para mejor legibilidad
- ✅ Formato markdown (negritas, listas)
- ✅ Separación clara entre secciones
- ✅ Sugerencias de preguntas adicionales

---

## 🔄 Flujo Completo de Trabajo

```
1. SUBIR DOCUMENTO
   ↓
2. [Opcional] Escribir pregunta específica
   ↓
3. Clic en "Analizar documento"
   ↓
4. Sistema extrae texto (con OCR si es necesario)
   ↓
5. IA analiza el contenido completo
   ↓
6. Muestra respuesta con:
   - Estadísticas del documento
   - Respuesta a tu pregunta (si la hubo)
   - O análisis automático completo
   ↓
7. Puedes hacer más preguntas en el chat
   (el chatbot recuerda el documento)
```

---

## 📝 Ejemplos Prácticos

### Ejemplo 1: Analizar Resolución Forestal
```
Documento: R.G.R. 107-2021-GRU-GGR-GERFFS.pdf
Pregunta: "¿Qué resolución es y de qué trata?"

Respuesta esperada:
"Esta es la Resolución Gerencial Regional N° 107-2021-GRU-GGR-GERFFS 
emitida por... [detalles específicos del documento]"
```

### Ejemplo 2: Extraer Información Específica
```
Documento: plan_manejo.pdf
Pregunta: "¿Cuántas especies de árboles se mencionan y cuáles son?"

Respuesta esperada:
"Se mencionan 15 especies:
1. Cedro (Cedrela odorata)
2. Caoba (Swietenia macrophylla)
..."
```

### Ejemplo 3: Análisis Automático
```
Documento: informe_tecnico.pdf
Pregunta: [vacío - sin pregunta]

Respuesta esperada:
"Análisis del documento:

Tema Principal: Informe técnico de evaluación forestal...
Puntos Clave:
- Área evaluada: 250 hectáreas
- Especies identificadas: 32
- Estado de conservación: bueno
..."
```

---

## ⚠️ Requisitos

### Para OCR (PDFs escaneados e imágenes)
Asegúrate de tener instalado **Tesseract OCR**:

**Windows:**
```bash
# Descargar e instalar desde:
https://github.com/UB-Mannheim/tesseract/wiki
```

**Linux:**
```bash
sudo apt install tesseract-ocr tesseract-ocr-spa
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

### Dependencias Python
Ya están en `requirements.txt`:
- `pypdf` - Leer PDFs
- `python-docx` - Leer Word
- `pytesseract` - OCR
- `pdf2image` - Convertir PDF a imagen para OCR

---

## 🎯 Casos de Uso

### 1. Análisis de Documentos Legales
- Resoluciones administrativas
- Planes de manejo forestal
- Contratos y acuerdos
- Normativas y reglamentos

### 2. Documentos Técnicos
- Informes técnicos
- Estudios de impacto ambiental
- Inventarios forestales
- Evaluaciones

### 3. Documentos Administrativos
- Actas de reuniones
- Memorandos
- Oficios
- Reportes

### 4. Material de Referencia
- Manuales
- Guías técnicas
- Procedimientos
- Instructivos

---

## 🚀 Prueba Ahora

1. **Reinicia el navegador** (para cargar los nuevos cambios)
2. Ve a http://localhost:5000/chatbot
3. Sube tu PDF: `R.G.R. 107-2021-GRU-GGR-GERFFS.pdf`
4. Prueba sin pregunta primero (análisis automático)
5. Luego haz preguntas específicas sobre el contenido

---

## 💬 Preguntas Frecuentes

**P: ¿Cuántas páginas puede procesar?**
R: Sin límite. Puede procesar documentos de cualquier tamaño.

**P: ¿Funciona con PDFs escaneados?**
R: Sí, usa OCR automático para extraer texto de imágenes.

**P: ¿Recuerda el documento después de analizarlo?**
R: Sí, puedes hacer múltiples preguntas sobre el mismo documento en la conversación.

**P: ¿Funciona sin API key de IA?**
R: Sí, extrae el texto del documento, pero necesitas una API key (Groq/Grok/Gemini) para el análisis inteligente y respuestas.

**P: ¿Qué tan preciso es?**
R: Muy preciso para PDFs con texto. Para PDFs escaneados depende de la calidad de la imagen.

---

## 🎉 ¡Todo Listo!

El chatbot está completamente configurado para **leer y analizar documentos completos** como el que mencionaste. Pruébalo ahora y verás toda la información que puede extraer de tus PDFs.

**Características Principales:**
✅ Lee documentos completos (todas las páginas)
✅ OCR para documentos escaneados
✅ Análisis automático inteligente
✅ Responde preguntas específicas
✅ Interfaz fácil de usar
✅ Formato profesional de respuestas
