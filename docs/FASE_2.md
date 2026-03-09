# Fase 2: Capa de Persistencia (SQLite)

## Objetivo Principal
Proporcionar una memoria a corto o mediano plazo para el sistema de control del G1, persistiendo su posición y trayectoria a lo largo de los días de simulación de manera ultra-ligera, robusta y con dependencias mínimas.

## Justificación Tecnológica (La "Navaja de Ockham")

En la integración robótica de telemetría a escala pequeña o de depuración veloz (un solo robot en 5 días de reto), la adición de una cola Redis o una base de datos Time-Series (como InfluxDB) puede resultar en una carga (Overkill) innecesaria de dependencias en un dispositivo de baja potencia como una Raspberry Pi, Jetson Nano o portátil secundaria. 

Por ello, se optó por **SQLite3**:
1. No requiere un servidor daemon en background.
2. Un único archivo (`.db`) fácil de empaquetar, compartir y examinar.
3. Lo suficientemente veloz para escrituras en batches si se maneja correctamente en un hilo. 

## Diseño del Módulo de Datos
La arquitectura delega el manejo a la clase `database/database_manager.py`.

### El Riesgo del Cuello de Botella (Throttling)
La naturaleza de los tópicos ROS como `/odom` es que están dictaminados por el ciclo de reloj interno de la física de Isaac Sim (a menudo 100Hz o más, es decir, 100 mensajes Odometry por segundo).

**Problema:** Si el nodo ROS intenta hacer 100 inserciones SQLite individuales síncronas por segundo (`INSERT INTO ...`), bloquearía el hilo de lectura del WebSocket o causaría un bloqueo `database is locked` en SQLite rápidamente, interrumpiendo fluidamente la lectura en el servidor FastAPI.

**Solución Implementada:** Un mecanismo de *Throttling* interno.
- Solo se permite almacenar la última posición si ha pasado una variable "t" (ej. **0.5 segundos**) desde la última escritura válida.
- Frecuencia efectiva de guardado: **2 Hz** (2 registros por segundo).
- Esto es suficientemente fluido para dibujar una línea de trayectoria en un mapa 2D sin sobrecargar el disco local.

### Esquema y Tipado de SQLite

Se estableció una sola tabla estructural llamada `logs` diseñada para agilidad:

```sql
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts DATETIME DEFAULT CURRENT_TIMESTAMP,
    x REAL NOT NULL,
    y REAL NOT NULL,
    theta REAL NOT NULL
)
```

- `ts`: Se delega a SQLite (`CURRENT_TIMESTAMP`) la marca temporal, desvinculando la sincronización de reloj del Isaac Sim (donde las cabeceras `header.stamp` podrían estar en tiempo simulado `sim_time` causando problemas de coherencia en el frontend).
- `theta`: Corresponde al valor Yaw procesado (en radianes o grados) extraído del cuaternión en la Fase 1, no a un cuaternión crudo completo, reduciendo columnas de datos inútiles para la interfaz en 2D.

## Verificación de Integridad

Una vez que el manejador está acoplado al nodo ROS receptor (asegurado por un bloque `try-except` para prevenir que una falla en la Base de Datos tire o detenga la suscripción de ROS), se valida:

1. Levantar el cliente `python3 odom_subscriber.py`.
2. Mover el robot en Isaac Sim.
3. En otra terminal, interrogar al archivo en crudo mediante la CLI local de bash:
   ```bash
   sqlite3 database/g1_telemetry.db "SELECT * FROM logs ORDER BY id DESC LIMIT 5;"
   ```
   *Debe generar las últimas coordenadas almacenadas progresivamente.*

---
[< Anterior: Fase 1 (Suscripción ROS 2)](FASE_1.md) | [Volver al índice general](../README.md)
