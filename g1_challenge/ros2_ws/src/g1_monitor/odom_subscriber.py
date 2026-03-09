import time
import math
import os
import sys
import roslibpy

# Añadir el path para importar DatabaseManager
# Buscamos la carpeta 'g1_challenge' subiendo desde el script
script_dir = os.path.dirname(os.path.abspath(__file__))
# El script está en g1_challenge/ros2_ws/src/g1_monitor/odom_subscriber.py
# g1_challenge es 3 niveles arriba
g1_challenge_root = os.path.abspath(os.path.join(script_dir, '../../../'))
if g1_challenge_root not in sys.path:
    sys.path.append(g1_challenge_root)

from database.database_manager import DatabaseManager

def quaternion_to_yaw(q):
    """Convierte un cuaternión (x, y, z, w) a ángulo Yaw."""
    x, y, z, w = q['x'], q['y'], q['z'], q['w']
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 * (2.0 * (y * y + z * z))
    yaw = math.atan2(t3, 1.0 - t4)
    return yaw

def main():
    # CONFIGURACIÓN
    HOST = '192.168.3.122' # IP de PC Isaac Sim
    PORT = 9090
    # El script está en g1_challenge/ros2_ws/src/g1_monitor/odom_subscriber.py
    # La DB está en g1_challenge/database/g1_telemetry.db
    g1_challenge_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
    DB_PATH = os.path.join(g1_challenge_root, 'database/g1_telemetry.db')

    print(f"Conectando a Rosbridge en {HOST}:{PORT}...")
    client = roslibpy.Ros(host=HOST, port=PORT)
    
    # Inicializar Base de Datos
    db = DatabaseManager(DB_PATH)
    
    # Estado actual del robot (para el muestreo de 2Hz)
    robot_log_data = {'x': 0.0, 'y': 0.0, 'yaw': 0.0}

    def callback(message):
        nonlocal robot_log_data
        pos = message['pose']['pose']['position']
        ori = message['pose']['pose']['orientation']
        
        robot_log_data['x'] = pos['x']
        robot_log_data['y'] = pos['y']
        robot_log_data['yaw'] = quaternion_to_yaw(ori)

    listener = roslibpy.Topic(client, '/odom', 'nav_msgs/Odometry')

    client.on('error', lambda err: print(f"Error de conexión: {err}"))
    client.on('close', lambda reason: print(f"Conexión cerrada: {reason}"))

    try:
        client.run()
        print("¡Conectado! Iniciando registro en DB a 2Hz...")
        listener.subscribe(callback)

        while client.is_connected:
            # Muestreo a 2Hz (Día 2 - Optimización)
            start_time = time.time()
            
            x, y, yaw = robot_log_data['x'], robot_log_data['y'], robot_log_data['yaw']
            db.insert_telemetry(x, y, yaw)
            
            print(f"Log guardado: X={x:.2f}, Y={y:.2f}, Yaw={math.degrees(yaw):.2f}°")
            
            # Ajuste para mantener los 2Hz (0.5s de periodo)
            elapsed = time.time() - start_time
            sleep_time = max(0, 0.5 - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nDeteniendo el registro...")
    except Exception as e:
        print(f"Error en el suscriptor: {e}")
    finally:
        listener.unsubscribe()
        client.terminate()
        print("Sesión terminada.")

if __name__ == '__main__':
    main()
