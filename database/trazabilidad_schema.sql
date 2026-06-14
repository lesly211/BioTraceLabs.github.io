-- =====================================================
-- BIO TRACE LABS - Sistema de Trazabilidad Forestal
-- Esquema adicional para los 3 roles de usuario
-- =====================================================

-- Tabla de usuarios del sistema
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('titular', 'chofer', 'centro_transformacion')),
    concesion TEXT,         -- Código de concesión (para titulares)
    empresa TEXT,           -- Nombre de empresa o centro
    dni TEXT,
    placa TEXT,             -- Para choferes
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de censos / registros de trozo (lo hace el titular)
CREATE TABLE IF NOT EXISTS censos_trozo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_unico_trozo TEXT NOT NULL UNIQUE,  -- Código único generado
    titular_id INTEGER NOT NULL,
    numero_parcela TEXT NOT NULL,
    especie TEXT NOT NULL,
    nombre_cientifico TEXT,
    coordenadas_gps TEXT,          -- "lat,lon"
    latitud REAL,
    longitud REAL,
    dap_cm REAL,                   -- Diámetro a la Altura del Pecho
    longitud_troza REAL,           -- metros
    volumen_m3 REAL,
    foto_corte_transversal TEXT,   -- path de la foto
    foto_troza_completa TEXT,      -- path de la foto
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado TEXT DEFAULT 'REGISTRADO' CHECK(estado IN ('REGISTRADO','EN_TRANSITO','RECIBIDO','VERIFICADO')),
    qr_generado TEXT,              -- data del QR
    observaciones TEXT,
    verificado_legal BOOLEAN DEFAULT FALSE,
    plan_manejo_referencia TEXT,   -- Código del plan de manejo
    FOREIGN KEY (titular_id) REFERENCES usuarios(id)
);

-- Tabla de guías de transporte (asocia trozo con chofer)
CREATE TABLE IF NOT EXISTS guias_transporte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    censo_trozo_id INTEGER NOT NULL,
    chofer_id INTEGER NOT NULL,
    numero_guia TEXT NOT NULL UNIQUE,
    placa_vehiculo TEXT NOT NULL,
    origen TEXT NOT NULL,
    destino TEXT NOT NULL,
    fecha_salida DATETIME,
    fecha_llegada DATETIME,
    estado TEXT DEFAULT 'PENDIENTE' CHECK(estado IN ('PENDIENTE','EN_RUTA','ENTREGADO','CANCELADO')),
    observaciones TEXT,
    FOREIGN KEY (censo_trozo_id) REFERENCES censos_trozo(id),
    FOREIGN KEY (chofer_id) REFERENCES usuarios(id)
);

-- Tabla de recepciones en centros de transformación
CREATE TABLE IF NOT EXISTS recepciones_centro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guia_transporte_id INTEGER,
    censo_trozo_id INTEGER NOT NULL,
    centro_id INTEGER NOT NULL,
    qr_escaneado TEXT,             -- contenido del QR escaneado
    foto_corteza TEXT,             -- foto subida por el centro
    fecha_recepcion DATETIME DEFAULT CURRENT_TIMESTAMP,
    resultado_verificacion TEXT CHECK(resultado_verificacion IN ('APROBADO','RECHAZADO','PENDIENTE')),
    motivo_rechazo TEXT,
    similitud_porcentaje REAL,     -- % de coincidencia con zona legal
    observaciones TEXT,
    FOREIGN KEY (guia_transporte_id) REFERENCES guias_transporte(id),
    FOREIGN KEY (censo_trozo_id) REFERENCES censos_trozo(id),
    FOREIGN KEY (centro_id) REFERENCES usuarios(id)
);

-- Tabla de checkpoints/puntos de control en la ruta (NUEVO)
CREATE TABLE IF NOT EXISTS checkpoints_ruta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guia_transporte_id INTEGER NOT NULL,
    nombre_checkpoint TEXT NOT NULL,      -- Nombre del punto de control (ej: "Iquitos", "Pucallpa")
    departamento TEXT NOT NULL,            -- Departamento del checkpoint
    latitud REAL,
    longitud REAL,
    orden INTEGER NOT NULL,                -- Orden del checkpoint en la ruta (1, 2, 3...)
    estado TEXT DEFAULT 'PENDIENTE' CHECK(estado IN ('PENDIENTE','EN_PROGRESO','COMPLETADO')),
    fecha_registro DATETIME,               -- Cuando el chofer registró que pasó por aquí
    observaciones TEXT,
    foto_checkpoint TEXT,                  -- Foto opcional del checkpoint
    FOREIGN KEY (guia_transporte_id) REFERENCES guias_transporte(id)
);

-- =====================================================
-- DATOS DE DEMO
-- =====================================================

INSERT OR IGNORE INTO usuarios (nombre, email, password_hash, rol, concesion, empresa, dni) VALUES
('Carlos Mamani', 'titular@demo.com', 'demo123', 'titular', 'CON-2024-LOT-001', 'Concesión Forestal Norte SAC', '12345678'),
('Pedro Quispe', 'chofer@demo.com', 'demo123', 'chofer', NULL, 'Transportes Amazónicos', '87654321'),
('Centro Loreto', 'centro@demo.com', 'demo123', 'centro_transformacion', NULL, 'Centro de Transformación Loreto S.A.', '11223344');

INSERT OR IGNORE INTO censos_trozo (codigo_unico_trozo, titular_id, numero_parcela, especie, nombre_cientifico, coordenadas_gps, latitud, longitud, dap_cm, longitud_troza, volumen_m3, fecha_hora, estado, plan_manejo_referencia, verificado_legal) VALUES
('TRZ-2024-LOT-000001', 1, 'A-01', 'Caoba', 'Swietenia macrophylla', '-3.745,-73.253', -3.745, -73.253, 85.5, 6.5, 2.84, '2024-03-15 08:30:00', 'VERIFICADO', 'PM-2024-001', TRUE),
('TRZ-2024-LOT-000002', 1, 'A-02', 'Cedro', 'Cedrela odorata', '-3.748,-73.258', -3.748, -73.258, 72.3, 5.8, 1.94, '2024-03-16 09:15:00', 'EN_TRANSITO', 'PM-2024-001', TRUE),
('TRZ-2024-MDD-000003', 1, 'B-01', 'Shihuahuaco', 'Dipteryx micrantha', '-12.589,-70.123', -12.589, -70.123, 95.0, 7.2, 4.11, '2024-04-10 07:45:00', 'REGISTRADO', 'PM-2024-002', FALSE);
