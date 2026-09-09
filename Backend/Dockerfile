# Imagen base Python
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para cache)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar TODO el backend (modelos, rutas, services, utils, app.py, etc.)
COPY . .

# Exponer puerto Flask
EXPOSE 5000

# Comando para levantar el backend
CMD ["python", "app.py"]
