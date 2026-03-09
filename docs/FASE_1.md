# Fase 1: Inmersión en ROS 2 (Scripts de Python)

## Objetivo Principal
Entender la estructura de comunicación de ROS 2 y desarrollar los primeros scripts en Python para interactuar con el robot G1 EDU. El enfoque de este día fue la **suscripción de datos** y la **validación de conectividad**.

## Arquitectura de los Scripts
Para el desarrollo se utilizó **`roslibpy`**, una librería que permite comunicarse con ROS 2 vía WebSockets (Rosbridge). Esto permite que los scripts de Python corran en cualquier entorno (Windows, macOS, Linux) sin necesidad de una instalación completa de ROS 2 Humble.

---

## 🐍 Detalle de Programación (Scripts del Día 1)

### 1. `odom_subscriber.py` (El Suscriptor Core)
Este es el nodo principal encargado de recibir la telemetría del robot.

*   **Conversión de Coordenadas**: El robot entrega su orientación en Cuaterniones. Se implementó la función `quaternion_to_yaw` para convertir estos datos en un ángulo de rotación (Yaw) comprensible para humanos.
    ```python
    def quaternion_to_yaw(q):
        # Convierte x, y, z, w a ángulo Yaw usando atan2
        ...
    ```
*   **Gestión de Tópicos**: Se suscribe al tópico `/odom` con el tipo de mensaje `nav_msgs/Odometry`.
*   **Flujo de Datos**:
    1. Se conecta al `host` (IP del servidor Isaac Sim) y puerto `9090`.
    2. Define un `callback` que extrae la posición (X, Y) y la orientación.
    3. Imprime los datos formateados en la terminal para monitoreo en vivo.

### 2. `cmd_vel_publisher.py` (Validación de Movimiento)
Utilizado para verificar que el puente también permite enviar comandos al robot.
*   **Tópico**: `/cmd_vel`
*   **Tipo de Mensaje**: `geometry_msgs/Twist`
*   **Lógica**: Crea mensajes con velocidad lineal (`linear.x`) y angular (`angular.z`) para comandar el movimiento del humanoide G1.

---

## ⚠️ Bloqueos y Soluciones (Reporte de Avance)

Siguiendo los requerimientos del reto técnico, se documenta el principal bloqueo encontrado durante el Día 1:

### Bloqueo: Error `Service /rosapi/topics does not exist`
Al intentar listar los tópicos desde la laptop cliente usando `list_topics.py`, se obtuvo un error indicando que el servicio de la API de ROS no estaba disponible.

*   **Causa**: El nodo `rosbridge_server` se inició sin el componente `rosapi`, el cual es responsable de exponer servicios como el listado de tópicos y nodos a través del WebSocket.
*   **Solución Aplicada**: 
    1.  Verificar que Rosbridge se lance usando el archivo de configuración completo: `ros2 launch rosbridge_server rosbridge_websocket_launch.xml`.
    2.  Como alternativa de depuración rápida, utilizar `ros2 topic list` directamente en la terminal del host para confirmar la disponibilidad de los tópicos antes de intentar consumirlos vía script.

---

## 🛠️ Verificación y Hitos
1.  **Conexión Exitosa**: Al ejecutar `python3 odom_subscriber.py`, el terminal muestra `¡Conectado!`.
2.  **Lectura en Tiempo Real**: Visualización de las coordenadas X e Y cambiando en la terminal mientras el robot se mueve en Isaac Sim.
3.  **Hito Logrado**: Código fuente inicial cargado con una estructura que separa la lógica de ROS de la futura lógica de base de datos.

---
[Volver al índice general](../README.md) | [Siguiente > Fase 2 (Almacenamiento SQLite)](FASE_2.md)
