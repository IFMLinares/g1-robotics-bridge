import roslibpy
import time

def main():
    HOST = '192.168.3.122'
    PORT = 9090

    print(f"Conectando a Rosbridge en {HOST}:{PORT}...")
    client = roslibpy.Ros(host=HOST, port=PORT)

    try:
        client.run()
        print("¡Conectado! Obteniendo lista de tópicos...\n")
        
        # Obtener tópicos
        topics = client.get_topics()
        
        if not topics:
            print("No se encontraron tópicos activos.")
        else:
            print(f"{'Tópico':<30} | {'Tipo'}")
            print("-" * 50)
            for topic in sorted(topics):
                # Intentar obtener el tipo (algunas versiones de roslibpy devuelven lista de strings)
                # Si get_topics ya trae los tipos, adjustar el print
                print(f"{topic:<30}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.terminate()

if __name__ == '__main__':
    main()
