# 🛠️ Guía de Scripts de Monitoreo y Diagnóstico

Este documento detalla los scripts disponibles en el paquete `g1_monitor` para interactuar con el robot G1 en Isaac Sim mediante el Rosbridge.

---

## 🛰️ Scripts de Operación Principal

Estos scripts forman el núcleo de la telemetría y el control del robot.

### 1. `odom_subscriber.py`
- **Propósito**: Suscribirse al tópico de odometría (`/odom`) y persistir los datos en SQLite.
- **Uso**: `python odom_subscriber.py`
- **Características**: Implementa "throttling" de 2Hz para evitar saturar la base de datos.

### 2. `cmd_vel_publisher.py`
- **Propósito**: Enviar comandos de velocidad al robot mediante el tópico `/cmd_vel`.
- **Uso**: `python cmd_vel_publisher.py`
- **Mensaje**: Envía un `geometry_msgs/Twist` con velocidades lineales y angulares.

### 3. `lidar_subscriber.py`
- **Propósito**: Monitorear la recepción de datos de la nube de puntos LiDAR.
- **Uso**: `python lidar_subscriber.py`
- **Métricas**: Muestra la frecuencia (Hz) y el número total de puntos recibidos de `/g1_robot/pointcloud`.

---

## 🔍 Scripts de Diagnóstico y Depuración

Herramientas creadas para solucionar problemas de comunicación y configuración.

### 4. `check_heartbeat.py`
- **Propósito**: Verificar si el simulador está enviando señales de tiempo.
- **Lógica**: Escucha el tópico `/clock`. Si no hay mensajes, Isaac Sim podría estar en pausa.

### 5. `verify_subscriber.py`
- **Propósito**: Actuar como suscriptor de prueba para comandos de velocidad.
- **Uso**: Sirve para confirmar si los mensajes publicados en `/cmd_vel` están llegando realmente al bridge.

### 6. `list_topics.py` / `list_topics_with_types.py`
- **Propósito**: Listar los tópicos activos en el Rosbridge.
- **Nota**: Requiere que el servicio `rosapi` esté activo en el servidor.

### 7. `check_odom_variants.py`
- **Propósito**: Escanear múltiples nombres de tópicos posibles para la odometría.
- **Contexto**: Útil cuando no estamos seguros de bajo qué nombre Isaac Sim está publicando la pose.

### 8. `inspect_tf.py`
- **Propósito**: Inspeccionar el árbol de transformaciones (`/tf`).
- **Uso**: Muestra las relaciones padre-hijo (ej. `odom` -> `base_link`) detectadas en la simulación.

### 9. `monitor_activity.py`
- **Propósito**: Reportar el contador de mensajes en tópicos críticos (`/tf`, `/cmd_vel`) durante un intervalo de 10 segundos.

---

## 🚦 Recomendaciones de Depuración

Si el robot no se mueve o no recibes datos:
1. Ejecuta `check_heartbeat.py` para ver si la simulación está corriendo (PLAY).
2. Usa `monitor_activity.py` para ver si hay tráfico en `/tf`.
3. Si el script principal no recibe odometría, usa `check_odom_variants.py` para ver si el nombre del tópico ha cambiado.
