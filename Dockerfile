# Usamos una imagen oficial de Python como base
FROM python:3.10-slim

# Evita que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Asegura que la salida de Python se muestre en la consola
ENV PYTHONUNBUFFERED 1

# Instala dependencias del sistema para la base de datos
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
     postgresql-client \
  && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install -r requirements.txt

# Copia el resto del código del proyecto al contenedor
COPY . .