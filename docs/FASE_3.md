# Fase 3: Integración de ROS API y Foxglove Bridge (Transmisión Web y Sensores)

En esta fase se documenta cómo se expanden las capacidades de comunicación de alta densidad hacia el exterior de NVIDIA Isaac Sim. Se explica la exposición de la estructura (introspección) del ecosistema ROS 2 y la transmisión optimizada de video y nubes de puntos mediante WebSockets de alto rendimiento, logrando visualizar la cámara del robot remotamente.

---

## 1. Introspección del Sistema con ROS API (`rosapi_node`)

Para que interfaces externas y puentes (como `rosbridge` o clientes visuales) puedan auto-descubrir y listar los flujos de datos activos (qué tópicos, nodos o servicios están disponibles), utilizan los servicios que levanta el paquete `rosapi`.

### Comando de ejecución:

```bash
ros2 run rosapi rosapi_node
```

### Explicación Técnica Detallada:

*   **`ros2 run`**: Comando estándar de ROS 2 que se utiliza para ejecutar un nodo específico que se encuentra alojado dentro de un paquete determinado.
*   **`rosapi`**: Es el paquete que contiene la lógica para exponer los parámetros y el grafo comunicacional de ROS de manera estandarizada y fácilmente consumible para clientes web.
*   **`rosapi_node`**: Es el ejecutable instanciado dentro del entorno de ROS.

**¿Para qué sirve?**
Al ejecutarse, este nodo levanta una serie de **Servicios ROS** (como `/rosapi/topics`, `/rosapi/services`, entre otros). Un cliente externo (tu frontend o un script proxy) puede llamar a estos servicios para consultar el mapa en tiempo real del sistema. Por ejemplo, permite a una UI web mostrar un menú desplegable con todos los tópicos seleccionables en el momento, sin necesidad de conectarse a ciegas.

---

## 2. Foxglove Bridge (Transmisión Híbrida y Video en Alta Frecuencia)

Para enviar telemetría de alta densidad como flujos de video o millones de vértices por segundo (Nubes de Puntos) hacia interfaces como Foxglove Studio o el mismo navegador web, la serialización tradicional tipo JSON tiene una latencia enorme. Aquí entra `foxglove_bridge`, implementando un servidor de sockets con protocolo binario extremadamente rápido.

### Comando de ejecución:

```bash
ros2 run foxglove_bridge foxglove_bridge --ros-args -p port:=8765 -p topic_whitelist:="['/cmd_vel', '/g1_robot/pointcloud', '/g1_robot/camera_head/depth/color/points', '/g1_robot/camera_head/rgb/image_raw']"
```

### Explicación Técnica Detallada:

*   **`ros2 run foxglove_bridge foxglove_bridge`**: Lanza el nodo puente desarrollado por Foxglove, que creará y expondrá el servidor WebSocket especial con serialización nativa (casi idéntico a MCAP) evitando retrasos computacionales de decodificación.

*   **`--ros-args`**: Parámetro reservado del CLI de ROS 2 que indica que todos los argumentos a su derecha deben pasarse directamente al núcleo del nodo para sobrescribir su configuración interna, en lugar de pasárselo a la línea de comandos principal.

*   **`-p port:=8765`**:
    *   **`-p`**: Abreviatura de parameter (también se puede usar `--param`).
    *   **`port:=8765`**: Modifica el puerto de escucha por defecto (normalmente 8765 de todos modos) asegurando que el servidor WebSocket quede amarrado al puerto TCP 8765 de la máquina Host. Los clientes externos se conectarán mediante una URL de tipo `ws://IP_HOST:8765`.

*   **`-p topic_whitelist:="..."`**:
    *   Este parámetro crítico es responsable del **filtro y optimización** de la red. En un entorno de simulación hay cientos de tópicos (TF locales, cinemática de las físicas, relojes simulados). Transferir todo eso colapsaría la red. Esta lista blanca (`whitelist`) establece una directriz estricta para que el puente de WebSockets solo escuche y despache la información de los tópicos que explícitamente se le indiquen en el arreglo.

**Detalle Técnico de los Tópicos Permitidos (Whitelist):**

1.  **`'/cmd_vel'`**: Tópico de interfaz de comandos Twist; permite que el cliente remoto (la interfaz web) inyecte vectores de velocidad diferencial a la base para comandar movimiento en el espacio de simulación.
2.  **`'/g1_robot/pointcloud'`**: Traspasa directamente la nube de puntos bruta del mundo simulado en Isaac Sim (generalmente de telémetros o sensores LiDAR directos), lo cual permite una reconstrucción y renderizado del ambiente local en la ventana de control web.
3.  **`'/g1_robot/camera_head/depth/color/points'`**: Nube de puntos híbrida y colmada construida superponiendo las salidas RGB (Color) en cada vértice mapeado en profundidad del lente estéreo de la cámara en la cabeza del robot, útil para mapeos fotorrealistas SLAM.
4.  **`'/g1_robot/camera_head/rgb/image_raw'`**: **(Visualización de Video / Cámara)** Al incluir este tópico, el nodo envía fotogramas codificados en tiempo real. Esta es la responsable directa de "mostrar la cámara" en la interfaz remota. Transfiere directamente la señal óptica frontal simulada de la cabeza del robot humanoide G1 para fines de monitoreo de primera persona (FPV - First Person View).
