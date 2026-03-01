FROM python:3.9-slim

WORKDIR /app

# Copiamos primero los requerimientos para aprovechar la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el contenido (app.py, static, files, etc.)
COPY . .

# Exponemos el puerto solicitado
EXPOSE 8821

# Ejecutamos con Gunicorn en el puerto 13942
# 'app:app' significa archivo app.py, instancia app
CMD ["gunicorn", "--bind", "0.0.0.0:8821", "app:app"]