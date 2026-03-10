# Dockerfile para G1 Control Center (Backend + Frontend)

# Usamos una imagen base oficial de Python ligera
FROM python:3.12-slim

# Evitamos que Python genere archivos .pyc y obligamos a que el output sea en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Creamos el directorio de trabajo en el contenedor
WORKDIR /app

# Instalamos dependencias del sistema requeridas para algunas librerías si fuera necesario 
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos el archivo de requerimientos y lo instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente de la aplicación (backend y frontend integrados)
COPY backend/ ./backend/

# Exponemos el puerto por el que FastAPI estará escuchando (5000 en tu configuración local)
EXPOSE 5000

# Cambiamos al subdirectorio backend para ejecutar main.py correctamente
WORKDIR /app/backend

# Comando para ejecutar la aplicación con Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
