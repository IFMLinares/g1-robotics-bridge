import time
import roslibpy

def main():
    # CONFIGURACIÓN
    # Reemplaza con la IP de tu PC que corre Isaac Sim
    HOST = 'localhost' 
    PORT = 9090

    print(f"Conectando a Rosbridge en {HOST}:{PORT}...")
    
    client = roslibpy.Ros(host=HOST, port=PORT)

    # Definir el tópico cmd_vel
    # El tipo es geometry_msgs/Twist
    talker = roslibpy.Topic(client, '/cmd_vel', 'geometry_msgs/Twist')

    try:
        client.run()
        print("¡Conectado exitosamente!")

        while client.is_connected:
            # Creamos un mensaje Twist para mover el robot
            # Linear X: Velocidad frontal (m/s)
            # Angular Z: Velocidad de giro (rad/s)
            
            print("Enviando comando: Avance frontal (0.2 m/s)")
            
            message = roslibpy.Message({
                'linear': {'x': 0.2, 'y': 0.0, 'z': 0.0},
                'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}
            })
            
            talker.publish(message)
            time.sleep(1) # Publicar cada segundo

    except KeyboardInterrupt:
        print("\nDeteniendo el publicador...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        talker.unadvertise()
        client.terminate()
        print("Conexión cerrada.")

if __name__ == '__main__':
    main()
