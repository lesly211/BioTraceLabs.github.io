# 🌳 OSINFOR - Sistema de Verificación y Trazabilidad Forestal con IA

Sistema integral de verificación forestal que combina:
1. **Chatbot Verificador**: Identifica árboles mediante fotografías con IA y verifica su legalidad
2. **Trazabilidad con Visión por Computadora**: Seguimiento de madera desde el bosque hasta centros de transformación con comparación automática de imágenes de cortes transversales

## 🚀 Instalación y uso

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar la API Key de Gemini
```bash
# Copia el archivo de ejemplo
copy .env.example .env

# Edita .env y coloca tu API Key de Google Gemini
# Obtén tu clave GRATIS en: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=tu_clave_aqui
```

### 3. Ejecutar la aplicación
```bash
python app.py
```
Abre tu navegador en:
- **Sistema de Trazabilidad**: http://localhost:5000
- **Chatbot Verificador**: http://localhost:5000/chatbot

---

## 🎯 Funcionalidades Principales

### 1. Sistema de Trazabilidad "BIO TRACE LABS" (Ruta `/`)

Sistema completo de trazabilidad forestal con **comparación automática de imágenes**:

#### Flujo de Trabajo:
1. **Titular** registra trozo de madera:
   - Sube foto del corte transversal
   - Ingresa datos (especie, DAP, GPS, etc.)
   - Genera código QR único

2. **Chofer** crea guía de transporte:
   - Escanea/ingresa código del trozo
   - Genera guía de transporte digital

3. **Centro de Transformación** verifica recepción:
   - Sube foto del corte transversal recibido
   - **Sistema compara automáticamente** con foto original usando:
     - SSIM (Structural Similarity Index)
     - Análisis de histogramas de color
     - Feature matching con ORB (detecta anillos únicos)
     - MSE (Mean Squared Error)
   - Verifica legalidad contra inventario OSINFOR
   - Aprueba o rechaza según similitud y legalidad

#### Métricas de Similitud:
- **≥75%**: Alta similitud → Muy probable misma troza
- **60-74%**: Media similitud → Posiblemente misma troza
- **45-59%**: Baja similitud → Requiere verificación adicional
- **<45%**: Muy baja similitud → Probablemente NO es la misma troza

**Cuentas demo:**
- Titular: `titular@demo.com` / `demo123`
- Chofer: `chofer@demo.com` / `demo123`
- Centro: `centro@demo.com` / `demo123`

### 2. Chatbot Verificador Forestal (Ruta `/chatbot`)

Sistema de identificación de árboles con Google Gemini Vision:
- Sube foto de árbol o corte
- IA identifica la especie
- Verifica si está en inventario legal OSINFOR
- Genera informe detallado con datos del plan de manejo

---

## 📁 Estructura del proyecto
```
chatbotOsinfor/
├── app.py                           # Servidor Flask principal
├── requirements.txt                 # Dependencias Python
├── .env                             # Variables de entorno
├── database/
│   ├── db_manager.py                # Gestión BD inventario forestal
│   ├── trazabilidad_manager.py      # Gestión BD trazabilidad
│   ├── inventario_arboles.db.sql    # Esquema inventario
│   └── trazabilidad_schema.sql      # Esquema trazabilidad
├── identificador/
│   ├── vision_arboles.py            # Identificación con Gemini Vision
│   └── comparador_imagenes.py       # **NUEVO**: Comparación de imágenes con OpenCV
├── chatbot/
│   └── motor_chatbot.py             # Lógica del chatbot
├── templates/
│   ├── index.html                   # UI Chatbot
│   └── trazabilidad.html            # UI Trazabilidad
└── static/
    ├── style.css / app.js           # Frontend chatbot
    └── trazabilidad.css / trazabilidad.js  # Frontend trazabilidad
```

## 🔧 Tecnologías Utilizadas

### Backend
- **Flask**: Servidor web y API REST
- **SQLite**: Base de datos (inventario + trazabilidad)
- **Google Gemini Vision**: Identificación de especies
- **OpenCV**: Procesamiento de imágenes
- **scikit-image**: Métricas SSIM
- **NumPy**: Computación numérica

### Frontend
- HTML5, CSS3, JavaScript (Vanilla)
- QRCode.js: Generación de códigos QR

### Algoritmos de Comparación de Imágenes
- **SSIM** (Structural Similarity): Compara estructura y patrones de anillos
- **Histogramas**: Compara distribución de colores de madera
- **ORB Feature Matching**: Detecta y compara características únicas (nudos, anillos)
- **MSE**: Error cuadrático medio entre imágenes

## 🌿 Base de datos incluida
- **15 especies** arbóreas amazónicas del Perú
- **5 planes de manejo** vigentes (Loreto, Madre de Dios, Ucayali, Junín, Huánuco)
- **17 árboles** de ejemplo en el inventario
- **3 usuarios demo** para trazabilidad (titular, chofer, centro)
- Especies protegidas: Caoba, Cedro, Shihuahuaco, Palo de Rosa, etc.

## 🔑 Configuración Opcional

### API Key de Gemini (para chatbot)
1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Genera una API Key gratuita
3. Agrégala en el archivo `.env`

**Nota**: El sistema de trazabilidad funciona completamente sin API Key. Solo el chatbot la requiere (tiene modo demo).
