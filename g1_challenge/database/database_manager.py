import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path='g1_telemetry.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Inicializa la base de datos y crea la tabla si no existe."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts DATETIME DEFAULT CURRENT_TIMESTAMP,
                x REAL,
                y REAL,
                theta REAL
            )
        ''')
        conn.commit()
        conn.close()

    def insert_telemetry(self, x, y, theta):
        """Inserta un nuevo registro de telemetría."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            ts = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO logs (ts, x, y, theta) VALUES (?, ?, ?, ?)",
                (ts, x, y, theta)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error insertando en DB: {e}")

    def get_latest_logs(self, limit=10):
        """Recupera los últimos N registros."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,))
        logs = cursor.fetchall()
        conn.close()
        return logs

if __name__ == '__main__':
    # Prueba rápida
    db = DatabaseManager('g1_telemetry.db')
    db.insert_telemetry(1.0, 2.0, 0.5)
    print("Últimos logs:", db.get_latest_logs())
