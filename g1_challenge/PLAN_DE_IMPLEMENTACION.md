# Reto Técnico: Integración G1 Humanoid (NVIDIA Isaac Sim)

Este documento centraliza la planeación para la prueba técnica de 5 días. 

## 1. Estructura del Proyecto
```text
g1_challenge/
├── ros2_ws/                 # Workspace de ROS 2 (Humble/Iron)
│   └── src/
│       └── g1_monitor/      # Paquete de telemetría y lógica ROS
├── backend/                 # Servidor FastAPI (Python 3.10+)
│   ├── app/
│   │   ├── main.py          # Entrypoint de la API
│   │   ├── ros_bridge.py    # Lógica de comunicación rclpy
│   │   ├── static/          # CSS/JS para la interfaz web
│   │   └── templates/       # index.html (Dashboard básico)
│   └── requirements.txt
├── database/                # SQLite (g1_telemetry.db)
├── docker/                  # Dockerfile y docker-compose.yml
├── foxglove/                # Layouts (.json) para monitoreo
└── README.md                # Guía de entrega final
```

## 2. Cronograma de Objetivos

## 2. Cronograma Técnico Detallado (Pasos a seguir)

### Día 1: Inmersión en ROS 2 (Suscripción)
- **Tarea**: Crear paquete `g1_monitor` y nodo `odom_subscriber.py`.
- **Lógica**: Suscribirse a `/odom` (`nav_msgs/msg/Odometry`).
- **Verificación**: `ros2 topic echo /odom` desde la PC cliente debe mostrar datos del Isaac Sim.
- **Entregable**: Terminal imprimiendo `Pose: x=1.2, y=-0.5, yaw=0.1`.

### Día 2: Capa de Datos (SQLite)
- **Tarea**: `database_manager.py`.
- **Esquema**: `CREATE TABLE logs (id INTEGER PRIMARY KEY, ts DATETIME, x REAL, y REAL, theta REAL)`.
- **Optimización**: No guardar cada mensaje. Usar un timer de 2Hz (cada 0.5s) para insertar en BD.
- **Entregable**: Consulta `SELECT * FROM logs LIMIT 10;` exitosa.

### Día 3: Backend & Web UI (FastAPI)
- **Tarea**: Servidor FastAPI en `backend/app/main.py`.
- **Interfaz Web**: `templates/index.html` con:
  - **Panel de Estado**: Muestra posición actual (vía WebSocket o Long Polling).
  - **Joystick/Botones**: Botones WASD que envían `fetch('/api/v1/robot/move', {method: 'POST', body: ...})`.
- **Bridge**: Clase `ROSBridge` en hilo separado manejando el publicador `/cmd_vel` (`geometry_msgs/msg/Twist`).

### Día 4: Visualización HMI & Docker
- **Tarea**: Integrar `rosbridge_suite`.
- **Foxglove**: Crear un layout que se conecte al WebSocket de tu PC y muestre la posición del G1 en un gráfico.
- **Empaquetado**: `Dockerfile` instalando `rclpy` y `fastapi`.
- **Entregable**: `docker-compose up` levanta API + Web + DB.

### Día 5: Pulido y Defensa
- **Refactor**: Limpiar código, añadir docstrings.
- **Doc**: README con "Guía rápida de 3 pasos para correr todo".
- **Defensa**: Mostrar el robot moviéndose desde la página web y los datos guardándose en la BD.

## 3. Consideraciones Técnicas Avanzadas

### 3.1 Networking (Multi-PC Setup)
Dado que Isaac Sim corre en otra PC de la red:
- **ROS_DOMAIN_ID**: Ambas máquinas deben compartir el mismo ID (ej. `export ROS_DOMAIN_ID=30`).
- **Subnet**: Deben estar en el mismo segmento de red (ej. 192.168.1.x).
- **RMW Implementation**: Se recomienda usar `rmw_cyclonedds_cpp` si hay problemas de descubrimiento.

### 3.2 Elección del Backend: ¿FastAPI o DRF?
| Característica | FastAPI (Recomendado) | Django Rest Framework (DRF) |
| :--- | :--- | :--- |
| **Rendimiento** | Extremadamente alto (Async nativo). | Moderado (Síncrono por defecto). |
| **Peso** | Muy ligero, ideal para microservicios. | Pesado (incluye ORM, Auth, Admin). |
| **Curva** | Muy rápida para APIs simples. | Media (tienes que configurar modelos/apps). |
| **Integración ROS** | Excelente para bucles asíncronos. | Requiere manejo extra para hilos. |

**Veredicto**: Si ya sabes usar DRF, podrías terminar más rápido la parte de la API. Sin embargo, en robótica se valora mucho el **asincronismo y la ligereza**. FastAPI te hará ver más como un "especialista en integración" que como un "desarrollador web generalista".

### 3.4 Tipos de Mensajes ROS 2
- **/odom**: Se usa `nav_msgs/msg/Odometry`. De aquí extraeremos `pose.pose.position.x`, `y` y `pose.pose.orientation`.
- **/cmd_vel**: Se usa `geometry_msgs/msg/Twist`. Controlaremos `linear.x` (avanzar/retroceder) y `angular.z` (girar).

### 3.5 Gestión de Frecuencia y BD
Isaac Sim puede publicar a altas frecuencias (100Hz+). Escribir cada mensaje individual en SQLite puede causar cuellos de botella. 
- **Estrategia**: Implementar un "Throttling" (Muestreo). Guardar en la base de datos solo cada N mensajes o cada 0.5 segundos para mantener el rendimiento sin perder la trayectoria.

### 3.6 Manejo de Errores y Robustez
- **Timeout de Conexión**: Si no se reciben mensajes de `/odom` en 5 segundos, el sistema debe alertar en la terminal.
- **Heartbeat**: La API debe verificar si el nodo de ROS está "vivo" antes de intentar publicar un comando.

## 4. Arquitectura del Puente (Bridge)
Para comunicar la API con ROS 2 de forma segura:
1. **Thread Separado**: El nodo de ROS 2 correrá en un hilo (`threading.Thread`) independiente de FastAPI (Uvicorn).
2. **Estado Global**: Usaremos una clase `G1Bridge` que herede de `Node` y actúe como punto de acceso único para la API.

### 3.7 Simplicidad Tecnológica (No Redis)
Para este reto de 5 días, **NO es necesario usar Redis** ni sistemas de mensajería complejos adicionales.
- **Por qué**: ROS 2 ya es un middleware de mensajería extremadamente potente y eficiente. Usar Redis añadiría una capa de complejidad innecesaria (Overkill) para una integración de este nivel.
- **Comunicación Web**: Para el Dashboard de FastAPI del Día 3, usaremos simples peticiones `fetch` (HTTP POST) para los comandos y, opcionalmente, un WebSocket ligero nativo de FastAPI para la telemetría en vivo.

### 3.8 El rol de WebSockets y Foxglove
Los WebSockets solo entrarán en juego de dos formas muy sencillas:
1. **Día 3**: Opcional en FastAPI si queremos ver los números moverse en vivo sin refrescar.
2. **Día 4**: A través de `rosbridge_suite`. Este paquete ya hace todo el trabajo pesado de convertir mensajes de ROS 2 a WebSockets para que Foxglove los entienda. Tú no tienes que programar los sockets manualmente.
