import roslibpy
import time

def main():
    HOST = '192.168.3.122'
    PORT = 9090

    print(f"Conectando a Rosbridge en {HOST}:{PORT}...")
    client = roslibpy.Ros(host=HOST, port=PORT)

    try:
        client.run()
        print("¡Conectado! Obteniendo tópicos y tipos...\n")
        
        topics = client.get_topics()
        
        print(f"{'Tópico':<45} | {'Tipo'}")
        print("-" * 70)
        
        for topic in sorted(topics):
            # get_topic_type is a service call to /rosapi/topic_type
            try:
                ttype = client.get_topic_type(topic)
                print(f"{topic:<45} | {ttype}")
            except:
                print(f"{topic:<45} | Error obteniendo tipo")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.terminate()

if __name__ == '__main__':
    main()
