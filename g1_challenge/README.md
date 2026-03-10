# G1 Control Center Dashboard - Isaac Sim Bridge

Este proyecto proporciona un puente de comunicación y un **Dashboard de Control Premium** desarrollado con FastAPI y HTML/JS vanilla (con WebSockets) para operar al robot humanoide **Unitree G1** simulado dentro de **NVIDIA Isaac Sim**.

## 🚀 Características Principales

1. **Backend FastAPI**: Servidor Python ligero que expone una base de rutas `/api` y envía comandos de movimiento.
2. **Dashboard Web Interactivo**: Una interfaz gráfica enriquecida, rápida, y con un diseño estético oscuro/futurista.
3. **Control de Movimiento en Tiempo Real**: Translación `X` e `Y` a través de D-PAD o teclado (WASD, Q/E) publicadas al tópico `/cmd_vel` de ROS 2.
4. **Telemetría y Estado Cíclico**: Capacidad de conectarse para leer odometría direccional a través de la red `/tf` y el flujo de cámara del robot.

---

## 🛠 Instalación y Ejecución

El ecosistema entero se puede ejecutar de dos maneras diferentes, a preferencia del entorno (con o sin Docker). 
*Nota: este repositorio ejecuta el Cliente Web / API, asumiendo que el Robot y el Bridge ya existen en una topología de simulación con Rosbridge activado (puerto 9090).*

### Opción 1: Ejecutar usando Docker (Recomendado)
El proyecto incluye un `Dockerfile` y un `docker-compose.yml` listos para levantar todo en un abrir y cerrar de ojos, ideal para aislar el entorno.

1. Instala Docker y Docker Compose en tu máquina.
2. Sitúate en el nivel donde está el build (`/g1_challenge`).
3. Construye y levanta el contenedor en segundo plano:
   ```bash
   docker-compose up -d --build
   ```
4. Abre tu navegador de preferencia y visita: **`http://localhost:5000`**
5. (Opcional) Para apagar y limpiar los contenedores:
   ```bash
   docker-compose down
   ```

### Opción 2: Ejecución Nativa desde Consola
Para escenarios de desarrollo donde quieras depurar el backend de FastAPI en vivo o probar scripts manualmente:

1. Asegúrate de tener Python 3.12+ (o similar) y crea un entorno virtual en la raíz del proyecto:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Instala las dependencias declaradas en `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. Levanta el servidor usando el módulo Uvicorn, configurándolo para el puerto 5000:
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 5000
   ```
4. Navega a `http://localhost:5000` en tu navegador local para abrir el panel de control.

---

## ⚠️ Limitaciones Conocidas y Soporte de ROS 2 QoS (Isaac Sim)

Durante la validación de telemetría y video con los visores web de este dashboard, se identificó un conflicto de conectividad común asociado al protocolo interno QoS (Quality of Service) emitido por **Isaac Sim**.

* **Diagnóstico del Emisor:** Sensores masivos como cámaras (`/camera/color/image_raw`) y odometría de alta frecuencia (`/tf` / `/odom`) en Isaac Sim son forzados a emitir datos bajo perfiles QoS estilo **"Best Effort"**. Esto previene colapsar la física del Engine de USD.
* **El Problema del Bridge:** Librerías estándar como `rosbridge_server` (websocket `9090`), `roslib.js` o `roslibpy` están típicamente diseñadas para suscribirse siempre bajo el modelo de fiabilidad **"Reliable"**. 
* **El Efecto Crossover:** Por diseño intrínseco de ROS 2 DDS, un publicador "Best Effort" rechazará subscripciones que piden un canal "Reliable". Los nodos muestran estar conectados, pero **se descartan silenciosamente los mensajes completos**, simulando un entorno de 0 bits de recepción por segundo. Se experimentaron códigos *HTTP 400 Bad Request* iterativos intentando interceptar el canal binario alterno sin puentes de transcodificación intermedios.
* **Comandos Funcionales:** En cambio, el control de movimientos de traslación emitido explícitamente desde este Dashboard hacia el simulador vía POST (`/cmd_vel`) **SÍ opera en tiempo real al 100%**, la suscripción a este tópico bidireccional no incurre en un cuello de botella de QoS.
* **Workaround Sugerido para Video:** Si las visualizaciones puras del `image_raw` o PointClouds masivos son críticas, la herramienta nativa en C++ recomendada por el momento es utilizar las fuentes puras de **Foxglove Studio** conectándose al Foxglove WebSocket Extension bridge (puerto `8765`), dado que este sistema negocia perfiles restrictivos de Quality of Service sin necesitar refactorizar el Action Graph del Omniverse de NVIDIA.
