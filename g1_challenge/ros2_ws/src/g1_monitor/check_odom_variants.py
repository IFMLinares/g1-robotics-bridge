import roslibpy
import time

def main():
    HOST = '192.168.3.122'
    PORT = 9090

    client = roslibpy.Ros(host=HOST, port=PORT)
    
    # Lista de tópicos comunes para odometría
    variants = [
        ('/odom', 'nav_msgs/Odometry'),
        ('/odometry', 'nav_msgs/Odometry'),
        ('/raw_odom', 'nav_msgs/Odometry'),
        ('/visual_odom', 'nav_msgs/Odometry'),
        ('/ground_truth/odom', 'nav_msgs/Odometry'),
        ('/pose', 'geometry_msgs/Pose'),
        ('/pose_stamped', 'geometry_msgs/PoseStamped')
    ]

    listeners = []

    def make_callback(topic_name):
        def callback(message):
            print(f"[{time.strftime('%H:%M:%S')}] ¡DATOS RECIBIDOS EN {topic_name}!")
        return callback

    try:
        client.run()
        print(f"Conectado a {HOST}:{PORT}. Probando variantes de tópicos...")

        for name, msg_type in variants:
            topic = roslibpy.Topic(client, name, msg_type)
            topic.subscribe(make_callback(name))
            listeners.append(topic)
            print(f"Suscrito a {name} ({msg_type})")

        print("\nEsperando mensajes (60 segundos)... MUEVE EL ROBOT en ISAAC SIM.")
        time.sleep(60)

    except KeyboardInterrupt:
        print("\nPrueba detenida.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        for listener in listeners:
            listener.unsubscribe()
        client.terminate()
        print("Conexión cerrada.")

if __name__ == '__main__':
    main()
