import sqlite3

conn = sqlite3.connect('database/inventario_osinfor.db')

# Obtener trozo en tránsito
trozo = conn.execute("SELECT id FROM censos_trozo WHERE codigo_unico_trozo='TRZ-2024-LOT-000002'").fetchone()

if trozo:
    trozo_id = trozo[0]
    print(f"Trozo ID: {trozo_id}")
    
    # Buscar si ya tiene guía
    guia = conn.execute(f"SELECT id FROM guias_transporte WHERE censo_trozo_id={trozo_id}").fetchone()
    
    if not guia:
        # Crear guía
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO guias_transporte 
            (censo_trozo_id, chofer_id, numero_guia, placa_vehiculo, origen, destino, fecha_salida, estado)
            VALUES ({trozo_id}, 2, 'GT-20260614-001', 'ABC-123', 'Loreto', 'Lima', datetime('now'), 'EN_RUTA')
        """)
        conn.commit()
        guia_id = cursor.lastrowid
        print(f"Guia creada: {guia_id}")
    else:
        guia_id = guia[0]
        print(f"Guia existente: {guia_id}")
    
    # Crear checkpoints
    checkpoints_exist = conn.execute(f"SELECT COUNT(*) FROM checkpoints_ruta WHERE guia_transporte_id={guia_id}").fetchone()[0]
    
    if checkpoints_exist == 0:
        print("Creando checkpoints...")
        conn.execute(f"""
            INSERT INTO checkpoints_ruta (guia_transporte_id, nombre_checkpoint, departamento, orden, estado, fecha_registro)
            VALUES 
            ({guia_id}, 'Iquitos', 'Loreto', 1, 'COMPLETADO', datetime('now', '-1 day')),
            ({guia_id}, 'Pucallpa', 'Ucayali', 2, 'EN_PROGRESO', NULL),
            ({guia_id}, 'Tingo Maria', 'Huanuco', 3, 'PENDIENTE', NULL),
            ({guia_id}, 'Huanuco', 'Huanuco', 4, 'PENDIENTE', NULL),
            ({guia_id}, 'Lima', 'Lima', 5, 'PENDIENTE', NULL)
        """)
        conn.commit()
        print("Checkpoints creados!")
    else:
        print(f"Checkpoints ya existen: {checkpoints_exist}")
    
    print("\nURL para probar:")
    print("http://localhost:5000/biotrace/pages/tracking_ruta.html?codigo=TRZ-2024-LOT-000002")

conn.close()
