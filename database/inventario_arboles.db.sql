-- =====================================================
-- OSINFOR - Base de Datos de Inventario Forestal
-- Script de inicialización de la BD de árboles legales
-- =====================================================

CREATE TABLE IF NOT EXISTS especies_arboles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_comun TEXT NOT NULL,
    nombre_cientifico TEXT NOT NULL UNIQUE,
    familia TEXT,
    descripcion TEXT,
    habitat TEXT,
    altura_max_m REAL,
    estado_conservacion TEXT, -- LC, NT, VU, EN, CR
    protegida BOOLEAN DEFAULT FALSE,
    imagen_referencia TEXT
);

CREATE TABLE IF NOT EXISTS inventario_arboles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_arbol TEXT NOT NULL UNIQUE,
    especie_id INTEGER NOT NULL,
    ubicacion_descripcion TEXT,
    latitud REAL,
    longitud REAL,
    dap_cm REAL,  -- Diámetro a la Altura del Pecho
    altura_m REAL,
    estado_fitosanitario TEXT, -- Bueno, Regular, Malo
    fecha_registro DATE,
    plan_manejo_id INTEGER,
    observaciones TEXT,
    FOREIGN KEY (especie_id) REFERENCES especies_arboles(id),
    FOREIGN KEY (plan_manejo_id) REFERENCES planes_manejo(id)
);

CREATE TABLE IF NOT EXISTS planes_manejo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_plan TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    titular TEXT,
    resolucion_aprobacion TEXT,
    fecha_aprobacion DATE,
    fecha_vencimiento DATE,
    area_ha REAL,
    region TEXT,
    estado TEXT DEFAULT 'VIGENTE'  -- VIGENTE, VENCIDO, SUSPENDIDO
);

CREATE TABLE IF NOT EXISTS historial_consultas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_consulta DATETIME DEFAULT CURRENT_TIMESTAMP,
    especie_identificada TEXT,
    confianza_identificacion REAL,
    codigo_arbol TEXT,
    resultado TEXT,  -- ENCONTRADO, NO_ENCONTRADO
    imagen_path TEXT,
    detalles_json TEXT
);

-- =====================================================
-- DATOS INICIALES - Especies comunes del Perú
-- =====================================================

INSERT INTO planes_manejo (codigo_plan, nombre, titular, resolucion_aprobacion, fecha_aprobacion, fecha_vencimiento, area_ha, region, estado) VALUES
('PM-2024-001', 'Plan de Manejo Forestal Amazónico Norte', 'Comunidad Nativa San Martín', 'R.D. 045-2024-OSINFOR', '2024-01-15', '2034-01-15', 5000.0, 'Loreto', 'VIGENTE'),
('PM-2024-002', 'Plan de Manejo Forestal Madre de Dios', 'Empresa Forestal Andes SAC', 'R.D. 078-2024-OSINFOR', '2024-03-20', '2034-03-20', 3500.0, 'Madre de Dios', 'VIGENTE'),
('PM-2023-003', 'Plan de Manejo Ucayali Sostenible', 'Cooperativa Forestal Ucayali', 'R.D. 112-2023-OSINFOR', '2023-06-10', '2033-06-10', 7200.0, 'Ucayali', 'VIGENTE'),
('PM-2022-004', 'Plan de Manejo Junín Verde', 'Asociación Madereros Junín', 'R.D. 089-2022-OSINFOR', '2022-09-05', '2032-09-05', 2100.0, 'Junín', 'VIGENTE'),
('PM-2021-005', 'Plan de Manejo Huánuco Forestal', 'Empresa Maderera Huallaga', 'R.D. 034-2021-OSINFOR', '2021-04-18', '2031-04-18', 4300.0, 'Huánuco', 'VIGENTE');

INSERT INTO especies_arboles (nombre_comun, nombre_cientifico, familia, descripcion, habitat, altura_max_m, estado_conservacion, protegida) VALUES
('Caoba', 'Swietenia macrophylla', 'Meliaceae', 'Árbol maderable de gran valor comercial, madera rojiza muy apreciada', 'Bosque húmedo tropical', 40.0, 'VU', TRUE),
('Cedro', 'Cedrela odorata', 'Meliaceae', 'Árbol maderable de olor característico, muy utilizado en carpintería', 'Bosque húmedo y seco tropical', 35.0, 'VU', TRUE),
('Tornillo', 'Cedrelinga cateniformis', 'Fabaceae', 'Árbol de gran porte, madera resistente muy utilizada en construcción', 'Bosque húmedo tropical', 45.0, 'LC', FALSE),
('Lupuna', 'Ceiba pentandra', 'Malvaceae', 'El árbol más grande de la Amazonía, con raíces tablares características', 'Bosque húmedo tropical', 60.0, 'LC', FALSE),
('Ishpingo', 'Amburana cearensis', 'Fabaceae', 'Árbol aromático, su madera es muy apreciada por su fragancia', 'Bosque seco tropical', 30.0, 'VU', TRUE),
('Capirona', 'Calycophyllum spruceanum', 'Rubiaceae', 'Árbol de corteza lisa característica, madera dura y resistente', 'Bosque ribereño', 30.0, 'LC', FALSE),
('Shihuahuaco', 'Dipteryx micrantha', 'Fabaceae', 'Una de las maderas más duras del Perú, árbol de gran longevidad', 'Bosque húmedo tropical', 50.0, 'NT', TRUE),
('Cumala', 'Virola sebifera', 'Myristicaceae', 'Árbol de uso múltiple, semillas con alto contenido de grasa', 'Bosque húmedo tropical', 35.0, 'LC', FALSE),
('Moena', 'Aniba amazonica', 'Lauraceae', 'Árbol aromático, madera utilizada en carpintería fina', 'Bosque húmedo tropical', 30.0, 'NT', TRUE),
('Aguano Masha', 'Swietenia humilis', 'Meliaceae', 'Especie hermana de la Caoba, madera de alta calidad', 'Bosque seco tropical', 25.0, 'EN', TRUE),
('Palo de Rosa', 'Aniba rosaeodora', 'Lauraceae', 'Árbol en peligro de extinción, rico en linalool', 'Bosque húmedo tropical', 20.0, 'EN', TRUE),
('Castana', 'Bertholletia excelsa', 'Lecythidaceae', 'Árbol longevo productor de nueces de Brasil, clave en la economía amazónica', 'Bosque húmedo tropical', 50.0, 'VU', TRUE),
('Huasaí', 'Euterpe oleracea', 'Arecaceae', 'Palmera productora de açaí, importante recurso no maderable', 'Bosque ribereño', 20.0, 'LC', FALSE),
('Copaiba', 'Copaifera reticulata', 'Fabaceae', 'Árbol productor de aceite medicinal de gran valor', 'Bosque húmedo tropical', 40.0, 'LC', FALSE),
('Bolaina', 'Guazuma crinita', 'Malvaceae', 'Especie de rápido crecimiento usada en reforestación', 'Bosque secundario', 25.0, 'LC', FALSE);

INSERT INTO inventario_arboles (codigo_arbol, especie_id, ubicacion_descripcion, latitud, longitud, dap_cm, altura_m, estado_fitosanitario, fecha_registro, plan_manejo_id, observaciones) VALUES
('ARB-PM001-001', 1, 'Sector Norte, Parcela A-1', -3.745, -73.253, 85.5, 32.0, 'Bueno', '2024-02-10', 1, 'Árbol adulto, apto para aprovechamiento'),
('ARB-PM001-002', 1, 'Sector Norte, Parcela A-2', -3.748, -73.258, 72.3, 28.5, 'Bueno', '2024-02-10', 1, 'En etapa de madurez'),
('ARB-PM001-003', 2, 'Sector Centro, Parcela B-1', -3.751, -73.261, 65.0, 25.0, 'Regular', '2024-02-15', 1, 'Presencia de plagas, requiere tratamiento'),
('ARB-PM001-004', 3, 'Sector Sur, Parcela C-3', -3.760, -73.270, 110.5, 38.0, 'Bueno', '2024-02-20', 1, 'Árbol de gran porte, excelente condición'),
('ARB-PM001-005', 12, 'Sector Este, Parcela D-1', -3.742, -73.245, 155.0, 45.0, 'Bueno', '2024-03-01', 1, 'Árbol madre, no sujeto a aprovechamiento'),
('ARB-PM002-001', 7, 'Bloque 1, Compartimento 1', -12.589, -70.123, 95.0, 42.0, 'Bueno', '2024-04-05', 2, 'Diámetro superior al mínimo permitido'),
('ARB-PM002-002', 7, 'Bloque 1, Compartimento 2', -12.592, -70.130, 88.5, 38.5, 'Bueno', '2024-04-05', 2, 'Árbol en buen estado fitosanitario'),
('ARB-PM002-003', 4, 'Bloque 2, Compartimento 1', -12.598, -70.138, 220.0, 55.0, 'Bueno', '2024-04-10', 2, 'Árbol emergente, referencia del dosel'),
('ARB-PM002-004', 9, 'Bloque 2, Compartimento 3', -12.601, -70.142, 58.0, 22.0, 'Regular', '2024-04-10', 2, 'Árbol joven, no apto aún para aprovechamiento'),
('ARB-PM003-001', 6, 'Ribera Río Ucayali, Zona A', -8.375, -74.548, 70.0, 28.0, 'Bueno', '2023-07-15', 3, 'Árbol en zona de ribera'),
('ARB-PM003-002', 8, 'Interior del bosque, Zona B', -8.382, -74.555, 55.5, 30.0, 'Bueno', '2023-07-20', 3, 'Especie abundante en la zona'),
('ARB-PM003-003', 14, 'Zona C, Colpa', -8.390, -74.562, 80.0, 35.0, 'Bueno', '2023-07-25', 3, 'Árbol productor de aceite'),
('ARB-PM004-001', 5, 'Sector Montaña, Parcela 1', -11.203, -74.895, 62.0, 25.0, 'Bueno', '2022-10-10', 4, 'Especie aromática característica de la zona'),
('ARB-PM004-002', 15, 'Sector Valle, Parcela 2', -11.210, -74.902, 45.0, 20.0, 'Bueno', '2022-10-15', 4, 'Especie de rápido crecimiento'),
('ARB-PM005-001', 10, 'Zona Alta, Parcela A', -9.925, -76.238, 55.0, 22.0, 'Regular', '2021-05-20', 5, 'Especie en peligro, monitoreo especial'),
('ARB-PM005-002', 11, 'Zona Media, Parcela B', -9.930, -76.245, 40.0, 18.0, 'Malo', '2021-05-25', 5, 'Árbol afectado por tala ilegal en zona adyacente'),
('ARB-PM005-003', 13, 'Zona Baja, Ribera', -9.940, -76.252, 25.0, 18.0, 'Bueno', '2021-06-01', 5, 'Palma en buen estado, producción activa');
