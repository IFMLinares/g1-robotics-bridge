from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import roslibpy
import uvicorn
import os
import sys

# Ajuste de path (ya no se usa db pero lo mantenemos por si se usa en otro lado)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, "../../")))

app = FastAPI(title="G1 Humanoid Control Center")

# Configuración de estáticos y plantillas
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Data Storage in Memory
robot_telemetry: dict[str, float] = {
    "x": 0.0,
    "y": 0.0,
    "theta": 0.0
}

# Clase Bridge según planificación
class G1Bridge:
    def __init__(self, host='192.168.3.122', port=9090):
        self.client = roslibpy.Ros(host=host, port=port)
        self.cmd_vel_topic = roslibpy.Topic(self.client, '/cmd_vel', 'geometry_msgs/msg/Twist')
        self.tf_topic = roslibpy.Topic(self.client, '/tf', 'tf2_msgs/msg/TFMessage')
        self.status = "Disconnected"

    def connect(self):
        self.client.on('error', self._on_error)
        self.client.on('close', self._on_close)
        self.client.run()
        self.status = "Connected"
        self.tf_topic.subscribe(self._on_tf_message)

    def _on_tf_message(self, message):
        import math
        # tf publish arrays of transforms
        transforms = message.get("transforms", [])
        for tf in transforms:
            # Look for the transform from odom to base_link or world to base_link
            # Common names are 'odom' -> 'base_link' or 'world' -> 'pelvis' (for G1)
            child_frame = tf.get("child_frame_id", "")
            
            # Update telemetry if this is the main body log
            if "pelvis" in child_frame or "base_link" in child_frame or "torso" in child_frame:
                translation = tf.get("transform", {}).get("translation", {})
                robot_telemetry["x"] = translation.get("x", 0.0)
                robot_telemetry["y"] = translation.get("y", 0.0)
                
                rotation = tf.get("transform", {}).get("rotation", {})
                qz = rotation.get("z", 0.0)
                qw = rotation.get("w", 1.0)
                yaw = math.atan2(2.0 * (qw * qz), 1.0 - 2.0 * (qz * qz))
                robot_telemetry["theta"] = yaw

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
    try:
        bridge.connect()
        print("G1Bridge iniciado y conectado.")
    except Exception as e:
        print(f"Error iniciando G1Bridge: {e}. El dashboard funcionará sin conexión backend-to-ROS.")

@app.on_event("shutdown")
async def shutdown_event():
    bridge.close()

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/telemetry")
async def get_telemetry():
    """Obtiene los últimos datos de Odometría."""
    return {
        "status": bridge.status,
        "x": round(robot_telemetry["x"], 2),
        "y": round(robot_telemetry["y"], 2),
        "theta": round(robot_telemetry["theta"], 2)
    }

@app.post("/api/move")
async def move_robot(linear_x: float = 0.0, linear_y: float = 0.0, angular_z: float = 0.0):
    """
    Control fluido: recibe magnitudes directas para soportar diagonales.
    """
    twist = {
        'linear': {'x': float(linear_x), 'y': float(linear_y), 'z': 0.0},
        'angular': {'x': 0.0, 'y': 0.0, 'z': float(angular_z)}
    }
    
    success = bridge.publish_cmd(twist)
    return {"status": "success" if success else "error", "values": {"x": linear_x, "y": linear_y, "z": angular_z}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
