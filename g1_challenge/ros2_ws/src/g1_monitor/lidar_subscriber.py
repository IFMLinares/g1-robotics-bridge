import time
import roslibpy

def main():
    # CONFIGURACIÓN
    HOST = '192.168.3.122' # IP de PC Isaac Sim
    PORT = 9090
    TOPIC = '/g1_robot/pointcloud'
    TYPE = 'sensor_msgs/PointCloud2'

    print(f"Conectando a Rosbridge en {HOST}:{PORT}...")
    client = roslibpy.Ros(host=HOST, port=PORT)

    # Variables para medir frecuencia (Hz)
    last_time = time.time()
    count = 0

    def callback(message):
        nonlocal last_time, count
        count += 1
        
        # Cada segundo mostramos estadísticas básicas
        current_time = time.time()
        if (current_time - last_time) >= 1.0:
            hz = count / (current_time - last_time)
            # El mensaje PointCloud2 tiene campos como 'width', 'height', 'point_step', 'row_step'
            width = message.get('width', 0)
            height = message.get('height', 0)
            total_points = width * height
            
            print(f"[{time.strftime('%H:%M:%S')}] Recibido LiDAR: {hz:.2f} Hz | Puntos: {total_points}")
            
            count = 0
            last_time = current_time

    listener = roslibpy.Topic(client, TOPIC, TYPE)

    client.on('error', lambda err: print(f"Error de conexión: {err}"))
    client.on('close', lambda reason: print(f"Conexión cerrada: {reason}"))

    try:
        client.run()
        print(f"¡Conectado! Escuchando {TOPIC}...")
        listener.subscribe(callback)

        while client.is_connected:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nDeteniendo el suscriptor LiDAR...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        listener.unsubscribe()
        client.terminate()
        print("Sesión terminada.")

if __name__ == '__main__':
    main()
