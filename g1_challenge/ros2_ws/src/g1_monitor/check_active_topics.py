import roslibpy
import time
import threading

def main():
    HOST = '192.168.3.122'
    PORT = 9090

    print(f"Conectando a Rosbridge en {HOST}:{PORT}...")
    client = roslibpy.Ros(host=HOST, port=PORT)
    
    active_topics = set()
    
    def callback_factory(topic_name):
        def callback(msg):
            active_topics.add(topic_name)
        return callback

    try:
        client.run()
        print("¡Conectado! Suscribiéndose a tópicos para ver cuáles publican datos (10 segundos)...\n")
        
        candidates = [
            ('/camera/imu', 'sensor_msgs/Imu'),
            ('/scan_head', 'sensor_msgs/LaserScan'),
            ('/scan_livox', 'sensor_msgs/LaserScan'),
            ('/client_count', 'std_msgs/Int32'),
            ('/clock', 'rosgraph_msgs/Clock'),
            ('/tf_static', 'tf2_msgs/TFMessage'),
            ('/rosout', 'rcl_interfaces/Log')
        ]
        
        topics = []
        for name, msg_type in candidates:
            topic = roslibpy.Topic(client, name, msg_type)
            topic.subscribe(callback_factory(name))
            topics.append(topic)
            
        # Esperar 10 segundos
        for i in range(10):
            print(f"Escuchando... {10-i} segundos restantes", end='\r')
            time.sleep(1)
            
        print("\n\nResultados de tópicos activos con datos:")
        print("-" * 50)
        if not active_topics:
            print("Ninguno de los tópicos candidatos envió datos en los últimos 10 segundos.")
        else:
            for t in active_topics:
                print(f"✅ RECIBIENDO DATOS: {t}")
                
        # Unsubscribe
        for t in topics:
            t.unsubscribe()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.terminate()

if __name__ == '__main__':
    main()
