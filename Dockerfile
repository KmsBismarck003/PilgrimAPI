FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de dependencias primero para optimizar la caché de Docker
COPY ./requirements.txt /app/requirements.txt

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de pilgrim dentro de /app/pilgrim para mantener 
# la estructura de módulos de Python (como se usa en run_pilgrim.py)
COPY . /app/pilgrim

# Configurar el PYTHONPATH para que Python reconozca los módulos desde /app
ENV PYTHONPATH=/app

# Exponer el puerto por defecto de Pilgrim
EXPOSE 8000

# Ejecutar el gateway
CMD ["uvicorn", "pilgrim.main:app", "--host", "0.0.0.0", "--port", "8000"]
