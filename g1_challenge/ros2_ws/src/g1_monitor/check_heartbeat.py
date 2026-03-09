import roslibpy
import time

def main():
    HOST = '192.168.3.122'
    PORT = 9090

    print(f"Buscando 'señales de vida' en {HOST}:{PORT}...")
    client = roslibpy.Ros(host=HOST, port=PORT)

    # El tópico /clock es el mejor indicador de si el simulador está "corriendo"
    clock_listener = roslibpy.Topic(client, '/clock', 'rosgraph_msgs/msg/Clock')
    
    data_received = {"count": 0}

    def callback(msg):
        data_received["count"] += 1

    try:
        client.run()
        print("Conectado. Escuchando /clock por 5 segundos...")
        clock_listener.subscribe(callback)
        
        time.sleep(5)
        
        if data_received["count"] > 0:
            print(f"✅ ¡Éxito! Se recibieron {data_received['count']} mensajes de /clock.")
            print("El simulador está enviando tiempo. El problema es específico de los tópicos de posición.")
        else:
            print("❌ CERO mensajes en /clock.")
            print("Posibles causas:")
            print("1. El simulador está PAUSADO (dale al botón PLAY en Isaac Sim).")
            print("2. El bridge no está recibiendo datos de la simulación.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        clock_listener.unsubscribe()
        client.terminate()

if __name__ == '__main__':
    main()
