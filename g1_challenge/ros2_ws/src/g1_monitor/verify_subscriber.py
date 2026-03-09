import roslibpy
import time

def main():
    HOST = '192.168.3.122'
    PORT = 9090

    client = roslibpy.Ros(host=HOST, port=PORT)
    
    def on_message(message):
        print(f"[{time.strftime('%H:%M:%S')}] Recibido en /cmd_vel: {message}")

    listener = roslibpy.Topic(client, '/cmd_vel', 'geometry_msgs/Twist')
    
    # Manejadores de eventos para diagnóstico
    client.on('error', lambda err: print(f"Error de conexión: {err}"))
    client.on('close', lambda reason: print(f"Conexión cerrada con el bridge: {reason}"))

    try:
        client.run()
        print(f"Escuchando en {HOST}:{PORT}/cmd_vel... (Presiona Ctrl+C para detener)")
        listener.subscribe(on_message)
        
        while client.is_connected:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nDeteniendo el verificador...")
    finally:
        listener.unsubscribe()
        client.terminate()

if __name__ == '__main__':
    main()
