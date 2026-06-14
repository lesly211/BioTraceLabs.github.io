"""
Script para insertar datos de prueba en el sistema BioTrace
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "inventario_osinfor.db"

def insertar_datos_prueba():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    try:
        # Verificar si ya existen usuarios
        usuarios = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        
        if usuarios == 0:
            print("[Setup] Insertando usuarios de prueba...")
            
            # Usuarios con contraseñas en texto plano para pruebas
            conn.execute("""
                INSERT INTO usuarios (nombre, email, password_hash, rol, concesion, empresa, dni, placa)
                VALUES 
                ('Carlos Mamani', 'titular@biotrace.com', 'titular2026', 'titular', 'CON-2024-LOR-001', 'Concesión Forestal Amazonas SAC', '12345678', NULL),
                ('Pedro Quispe', 'chofer@biotrace.com', 'chofer2026', 'chofer', NULL, 'Transportes Selva SAC', '87654321', 'ABC-123'),
                ('Centro Loreto', 'centro@biotrace.com', 'centro2026', 'centro_transformacion', NULL, 'Centro de Transformación Loreto S.A.', '11223344', NULL)
            """)
            print("✓ Usuarios creados")
        else:
            print("[Setup] Usuarios ya existen")
        
        # Verificar si ya existen trozos
        trozos = conn.execute("SELECT COUNT(*) FROM censos_trozo").fetchone()[0]
        
        if trozos == 0:
            print("[Setup] Insertando trozos de prueba...")
            
            conn.execute("""
                INSERT INTO censos_trozo 
                (codigo_unico_trozo, titular_id, numero_parcela, especie, nombre_cientifico, 
                 coordenadas_gps, latitud, longitud, dap_cm, longitud_troza, volumen_m3, 
                 estado, plan_manejo_referencia, verificado_legal, fecha_hora)
                VALUES 
                ('TRZ-2026-LOR-001', 1, 'A-01', 'Caoba', 'Swietenia macrophylla', 
                 '-3.745,-73.253', -3.745, -73.253, 85.5, 6.5, 2.84, 
                 'EN_TRANSITO', 'PM-2024-LOR-001', 1, datetime('now', '-2 days')),
                 
                ('TRZ-2026-UCL-002', 1, 'B-02', 'Cedro', 'Cedrela odorata', 
                 '-8.377,-74.542', -8.377, -74.542, 72.3, 5.8, 1.94, 
                 'REGISTRADO', 'PM-2024-UCL-001', 1, datetime('now', '-1 day')),
                 
                ('TRZ-2026-MDD-003', 1, 'C-03', 'Shihuahuaco', 'Dipteryx micrantha', 
                 '-12.589,-70.123', -12.589, -70.123, 95.0, 7.2, 4.11, 
                 'REGISTRADO', 'PM-2024-MDD-001', 0, datetime('now'))
            """)
            print("✓ Trozos creados")
        else:
            print("[Setup] Trozos ya existen")
        
        # Verificar si ya existe guía de transporte
        guias = conn.execute("SELECT COUNT(*) FROM guias_transporte").fetchone()[0]
        
        if guias == 0:
            print("[Setup] Insertando guía de transporte de prueba...")
            
            # Obtener el ID del primer trozo
            trozo = conn.execute("SELECT id FROM censos_trozo WHERE codigo_unico_trozo='TRZ-2026-LOR-001'").fetchone()
            
            if trozo:
                conn.execute("""
                    INSERT INTO guias_transporte 
                    (censo_trozo_id, chofer_id, numero_guia, placa_vehiculo, origen, destino, 
                     fecha_salida, estado, observaciones)
                    VALUES 
                    (?, 2, 'GT-20260613-12345', 'ABC-123', 'Loreto', 'Lima', 
                     datetime('now', '-1 day'), 'EN_RUTA', 'Transporte de caoba')
                """, (trozo[0],))
                
                guia_id = conn.lastrowid
                print(f"✓ Guía creada con ID: {guia_id}")
                
                # Crear checkpoints para la guía
                print("[Setup] Creando checkpoints...")
                checkpoints = [
                    (guia_id, 'Iquitos', 'Loreto', 1, 'COMPLETADO', datetime('now', '-1 day')),
                    (guia_id, 'Pucallpa', 'Ucayali', 2, 'EN_PROGRESO', None),
                    (guia_id, 'Tingo María', 'Huánuco', 3, 'PENDIENTE', None),
                    (guia_id, 'Huánuco', 'Huánuco', 4, 'PENDIENTE', None),
                    (guia_id, 'Lima', 'Lima', 5, 'PENDIENTE', None)
                ]
                
                for cp in checkpoints:
                    if cp[5]:  # Si tiene fecha
                        conn.execute("""
                            INSERT INTO checkpoints_ruta 
                            (guia_transporte_id, nombre_checkpoint, departamento, orden, estado, fecha_registro)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, cp)
                    else:
                        conn.execute("""
                            INSERT INTO checkpoints_ruta 
                            (guia_transporte_id, nombre_checkpoint, departamento, orden, estado)
                            VALUES (?, ?, ?, ?, ?)
                        """, cp[:5])
                
                print("✓ Checkpoints creados")
        else:
            print("[Setup] Guías ya existen")
        
        conn.commit()
        print("\n✅ Datos de prueba insertados correctamente")
        print("\n📋 Credenciales de acceso:")
        print("   Titular: titular@biotrace.com / titular2026")
        print("   Chofer:  chofer@biotrace.com / chofer2026")
        print("   Centro:  centro@biotrace.com / centro2026")
        print("\n🔗 URL de prueba para tracking:")
        print("   http://localhost:5000/biotrace/pages/tracking_ruta.html?codigo=TRZ-2026-LOR-001")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    from datetime import datetime, timedelta
    
    # Función helper para fechas
    def datetime(base, offset):
        from datetime import datetime as dt, timedelta
        if offset.startswith('-'):
            days = int(offset.split()[0][1:])
            return (dt.now() - timedelta(days=days)).isoformat()
        return dt.now().isoformat()
    
    insertar_datos_prueba()
