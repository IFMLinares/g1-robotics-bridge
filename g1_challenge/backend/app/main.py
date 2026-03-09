from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import roslibpy
import uvicorn
import os
import sys

# Ajuste de path para importar DatabaseManager
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, "../../")))
from database.database_manager import DatabaseManager

app = FastAPI(title="G1 Humanoid Control Center")

# Configuración de estáticos y plantillas
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Configuración de Base de Datos
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "../../database/g1_telemetry.db"))
db = DatabaseManager(DB_PATH)

# Clase Bridge según planificación
class G1Bridge:
    def __init__(self, host='192.168.3.122', port=9090):
        self.client = roslibpy.Ros(host=host, port=port)
        self.cmd_vel_topic = roslibpy.Topic(self.client, '/cmd_vel', 'geometry_msgs/Twist')
        self.status = "Disconnected"

    def connect(self):
        self.client.on('error', self._on_error)
        self.client.on('close', self._on_close)
        self.client.run()
        self.status = "Connected"

    def _on_error(self, error):
        self.status = "Error"
        print(f"ROS Error: {error}")

    def _on_close(self, reason):
        self.status = "Disconnected"
        print(f"ROS Closed: {reason}")

    def publish_cmd(self, twist_msg):
        if self.client.is_connected:
            self.cmd_vel_topic.publish(roslibpy.Message(twist_msg))
            return True
        return False

    def close(self):
        self.client.terminate()

bridge = G1Bridge()

@app.on_event("startup")
async def startup_event():
    bridge.connect()
    print("G1Bridge iniciado y conectado.")

@app.on_event("shutdown")
async def shutdown_event():
    bridge.close()

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/telemetry")
async def get_telemetry():
    """Obtiene los últimos datos de la base de datos para el Dashboard."""
    latest_logs = db.get_latest_logs(limit=1)
    if latest_logs:
        log = latest_logs[0]
        return {
            "status": bridge.status,
            "ts": log[1],
            "x": round(log[2], 2),
            "y": round(log[3], 2),
            "theta": round(log[4], 2)
        }
    return {"status": bridge.status, "message": "No data in DB"}

@app.post("/api/move")
async def move_robot(direction: str):
    speed = 0.5
    turn = 1.0
    twist = {'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0}, 'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}}

    if direction == "forward": twist['linear']['x'] = speed
    elif direction == "backward": twist['linear']['x'] = -speed
    elif direction == "left": twist['angular']['z'] = turn
    elif direction == "right": twist['angular']['z'] = -turn
    
    success = bridge.publish_cmd(twist)
    return {"status": "success" if success else "error", "direction": direction}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
