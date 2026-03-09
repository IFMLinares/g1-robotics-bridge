import roslibpy
import time

def main():
    HOST = '192.168.3.122'
    PORT = 9090

    print(f"Conectando a Rosbridge en {HOST}:{PORT} para inspeccionar /tf...")
    client = roslibpy.Ros(host=HOST, port=PORT)

    def callback(message):
        for transform in message.get('transforms', []):
            parent = transform.get('header', {}).get('frame_id')
            child = transform.get('child_frame_id')
            print(f"Transform Detectado: {parent} -> {child}")
        
    listener = roslibpy.Topic(client, '/tf', 'tf2_msgs/TFMessage')

    try:
        client.run()
        listener.subscribe(callback)
        print("Escuchando /tf por 10 segundos para mapear el árbol de transformaciones...")
        time.sleep(10)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        listener.unsubscribe()
        client.terminate()
        print("\nInspección finalizada.")

if __name__ == '__main__':
    main()
