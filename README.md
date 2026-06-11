# 🌳 OSINFOR - Chatbot Verificador Forestal con IA

Sistema de verificación forestal inteligente que identifica árboles mediante fotografías y verifica si están incluidos en el **inventario forestal** y **planes de manejo vigentes** de OSINFOR.

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
Abre tu navegador en: **http://localhost:5000**

---

## 📁 Estructura del proyecto
```
chatbotOsinfor/
├── app.py                    # Servidor Flask principal
├── requirements.txt          # Dependencias Python
├── .env                      # Variables de entorno (crear desde .env.example)
├── database/
│   ├── db_manager.py         # Gestión de la base de datos SQLite
│   └── inventario_arboles.db.sql  # Esquema e datos iniciales
├── identificador/
│   └── vision_arboles.py     # Identificación con Gemini Vision API
├── chatbot/
│   └── motor_chatbot.py      # Lógica del chatbot y verificación
├── templates/
│   └── index.html            # Interfaz web principal
└── static/
    ├── style.css             # Estilos (Dark theme)
    └── app.js                # JavaScript frontend
```

## 🔧 Modos de operación

| Modo | Descripción |
|------|-------------|
| **Con API Key** | Identificación real de árboles con Google Gemini Vision |
| **Modo Demo** | Identificación simulada para pruebas sin API Key |

## 🌿 Base de datos incluida
- **15 especies** arbóreas amazónicas del Perú
- **5 planes de manejo** vigentes (Loreto, Madre de Dios, Ucayali, Junín, Huánuco)
- **17 árboles** de ejemplo en el inventario
- Especies protegidas: Caoba, Cedro, Shihuahuaco, Palo de Rosa, etc.

## 🔑 API Key de Gemini (gratuita)
1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Crea una cuenta o inicia sesión con Google
3. Genera una API Key gratuita
4. Cópiala en el archivo `.env`
