# Fase 1: Inmersión en ROS 2 (Suscripción y Mapeo)

## Objetivo Principal
Establecer la comunicación bidireccional básica con el robot G1 en Isaac Sim a través de **ROS 2**. Esto implica obtener datos de posicionamiento en tiempo real (Odometría) y asegurar capacidades para enviar comandos de movimiento, actuando como la base para el dashboard web posterior.

## Análisis de la Arquitectura de Comunicación
Debido a que el Isaac Sim se ejecuta en una máquina distinta a la PC de desarrollo web, se optó por dos estrategias de integración, priorizando la ligereza del cliente final:

1. **Vía WebSocket (`roslibpy`) [Elegida para Laptops]**: Se ejecuta el paquete `rosbridge_suite` en la máquina anfitriona (servidor Isaac Sim). El desarrollo del cliente (la PC que monitorea) se hace consumiendo un socket en el puerto `9090`. Esto libra a la laptop de requerir Ubuntu local o una instalación full de `ros-humble-desktop`, facilitando que cualquier SO interactúe.
2. **Vía ROS 2 Nativo (`rclpy`) [Para el Entorno Producción Docker]**: Usando el mismo `ROS_DOMAIN_ID` en ambas máquinas (o contenedores) de la red local, para tener rendimiento en crudo (utilizando el middleware DDS nativo como `rmw_cyclonedds_cpp` si hay problemas de enrutamiento UDP).

## Implementación Técnica y Tópicos

La inmersión se centró en dos tópicos cruciales estandarizados por ROS para robótica móvil y humanoide básica:

### 1. Lectura de Posición: Tópico `/odom` 
Este tópico nos indica dónde cree el robot que está basándose en sus sensores (cinemática o IMU del simulador).
- **Tipo de Mensaje**: `nav_msgs/msg/Odometry`
- **Script**: `odom_subscriber.py`
- **Procesamiento de Datos (Mapeo)**:
  - El mensaje anida mucha información. Extraemos las coordenadas cartesianas desde `pose.pose.position.x` y `pose.pose.position.y` para dibujar el mapa 2D futuro.
  - La rotación llega en un Cuaternión (`pose.pose.orientation`), requiriendo matemáticas (decuaternización) si se desea usar un simple Yaw (ángulo de vista) en el dashboard web.

### 2. Control G1: Tópico `/cmd_vel`
Este tópico espera comandos de velocidad (Velocity Commands).
- **Tipo de Mensaje**: `geometry_msgs/msg/Twist`
- **Script (Prueba)**: `cmd_vel_publisher.py`
- **Estructura de Envío**:
  - `linear.x`: Controla el avance o retroceso (Ej. 1.0 m/s hacia adelante).
  - `angular.z`: Controla el giro sobre su propio eje vertical (Yaw) (Ej. 0.5 rad/s rotando a la izquierda).

## Verificación de Integración (Troubleshooting)

Para confirmar el éxito de esta fase de inmersión sin necesidad de tener scripts corriendo, se deben hacer los siguientes pasos:

1. **Chequeo de Ecosistema**:
   En la PC Anfitriona, con la simulación G1 activa:
   ```bash
   ros2 topic list
   ```
   Debe mostrar explícitamente `/odom` y `/cmd_vel` en la lista. Si no aparecen, los Action Graphs de Omniverse/Isaac Sim no están exportando los "puertos ROS 2" hacia afuera.

2. **Dumping de Telemetría (El Entregable)**:
   Si el cliente corre Ubuntu/ROS nativo:
   ```bash
   ros2 topic echo /odom
   ```
   *Debe imprimir en terminal sin parar bloques YAML que incluyan `Pose: x=... y=...`*

3. **Prueba en Cliente Ligero**:
   Corriendo el script `odom_subscriber.py` modificado con la IP del servidor, la terminal deberá escupir de forma parseada los números (`[INFO]: x: 1.25, y: -0.4, yaw: 11]`).

---
[Volver al índice general](../README.md) | [Siguiente > Fase 2 (Almacenamiento SQLite)](FASE_2.md)
