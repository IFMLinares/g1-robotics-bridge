import roslibpy
import time

def main():
    HOST = '192.168.3.122'
    PORT = 9090

    client = roslibpy.Ros(host=HOST, port=PORT)
    test_topics = ['/tf', '/tf_static', '/cmd_vel']
    
    counts = {t: 0 for t in test_topics}

    def create_callback(topic_name):
        def cb(msg):
            counts[topic_name] += 1
        return cb

    try:
        client.run()
        print(f"Monitoreando actividad en {test_topics} por 10 segundos...")
        
        # Suscribirse sin especificar tipo para ver si llega ALGO
        listeners = []
        for t in test_topics:
            l = roslibpy.Topic(client, t, None) # None para tipo genérico
            l.subscribe(create_callback(t))
            listeners.append(l)

        time.sleep(10)
        
        print("\nResultados de actividad:")
        for t, count in counts.items():
            print(f"- {t}: {count} mensajes recibidos")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.terminate()

if __name__ == '__main__':
    main()
