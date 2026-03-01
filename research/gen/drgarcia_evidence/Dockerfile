# Usamos la imagen oficial de Debian (versión estable)
FROM debian:stable-slim

# Evitar prompts interactivos durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# 1. Actualizar el sistema e instalar sudo (opcional, por si lo necesitas)
RUN apt-get update && apt-get install -y \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# 2. Crear el usuario "drgarcia"
# -m crea automáticamente el directorio /home/drgarcia
# -s define el shell por defecto (bash)
RUN useradd -m -s /bin/bash drgarcia

# 3. (Opcional) Dar permisos de sudo al usuario sin contraseña
RUN echo "drgarcia ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# 4. Establecer el directorio de trabajo en el home del usuario
WORKDIR /home/drgarcia

# 5. Cambiar al usuario "drgarcia" para que el contenedor inicie con él
USER drgarcia

# Comando por defecto al arrancar el contenedor
CMD ["/bin/bash"]
