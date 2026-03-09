import roslibpy
import time

def main():
    HOST = '192.168.3.122'
    PORT = 9090

    client = roslibpy.Ros(host=HOST, port=PORT)
    # Lista extendida de posibles tópicos de posición
    test_topics = [
        '/odom', 
        '/tf', 
        '/global_pose', 
        '/localization_pose', 
        '/initialpose',
        '/cmd_vel'
    ]
    
    counts = {t: 0 for t in test_topics}

    def create_callback(topic_name):
        def cb(msg):
            counts[topic_name] += 1
        return cb

    try:
        client.run()
        print(f"Monitoreando actividad de RED en {test_topics} por 15 segundos...")
        
        listeners = []
        for t in test_topics:
            # Intentamos suscribirnos de forma genérica
            l = roslibpy.Topic(client, t, None)
            l.subscribe(create_callback(t))
            listeners.append(l)

        # Iniciar una pequeña espera
        time.sleep(15)
        
        print("\n--- RESULTADOS DE TELEMETRÍA ---")
        for t, count in counts.items():
            status = "ACTIVO ✅" if count > 0 else "SIN DATOS ❌"
            print(f"{t:<20} | {count:<5} mensajes | {status}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.terminate()

if __name__ == '__main__':
    main()
