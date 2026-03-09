# Fase 2: Capa de Persistencia (Scripts de Datos)

## Objetivo Principal
Asegurar que los datos de telemetría del robot G1 no solo se visualicen, sino que se almacenen de forma permanente. El foco del Día 2 fue la creación de una **capa de persistencia robusta** usando SQLite y la optimización de la frecuencia de escritura.

## 📁 Estructura del Módulo de Datos
Se creó un módulo independiente para manejar la base de datos, siguiendo principios de modularidad:
- **`database/database_manager.py`**: Contiene la clase `DatabaseManager` que centraliza todas las operaciones de SQL.
- **`database/g1_telemetry.db`**: Archivo de base de datos generado automáticamente.

---

## 🐍 Detalle de Programación

### 1. La Clase `DatabaseManager`
Esta clase desacopla la lógica de ROS de la lógica de almacenamiento.
*   **Inicialización Segura**: Al instanciar la clase, el método `_init_db` verifica la existencia de la tabla `logs` y la crea si es necesario.
*   **Inserción de Telemetría**: El método `insert_telemetry(x, y, theta)` gestiona la conexión, inserta los datos y asegura el `commit` de la transacción.
    ```python
    def insert_telemetry(self, x, y, theta):
        # Abre conexión, inserta x, y, yaw y timestamp, cierra conexión.
    ```

### 2. Lógica de "Throttling" (Muestreo a 2Hz)
Para evitar saturar el disco con los 100Hz de datos que envía Isaac Sim, la lógica de guardado se integró en el bucle principal de `odom_subscriber.py` de la siguiente manera:

1.  El **Callback** de ROS actualiza una variable global `robot_log_data` a la máxima velocidad posible (100Hz).
2.  Un **Bucle `while` independiente** consulta esa variable y llama a `db.insert_telemetry` exactamente cada **0.5 segundos**.
    ```python
    while client.is_connected:
        x, y, yaw = robot_log_data['x'], robot_log_data['y'], robot_log_data['yaw']
        db.insert_telemetry(x, y, yaw)
        time.sleep(0.5) # Control de frecuencia (2Hz)
    ```

---

## 🛠️ Verificación de Datos
El éxito de este día se valida comprobando que el archivo `.db` crece en tamaño y contiene registros válidos:
1.  **Ejecución**: El script `odom_subscriber.py` ahora muestra en consola: `Log guardado: X=..., Y=...`.
2.  **Consulta SQL**: Verificación mediante terminal para asegurar que los timestamps y coordenadas son correctos.
    ```bash
    sqlite3 database/g1_telemetry.db "SELECT * FROM logs LIMIT 5;"
    ```

---
[< Anterior: Fase 1 (Scripts Python)](FASE_1.md) | [Volver al índice general](../README.md)
