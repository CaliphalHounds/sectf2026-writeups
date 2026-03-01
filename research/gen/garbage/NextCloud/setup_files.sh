#!/bin/bash

echo "[*] Copiando archivos a la cuenta de Louden..."
# Crear el directorio del usuario si no existe y copiar
docker exec -u www-data -it $(docker ps -qf "name=app") mkdir -p /var/www/html/data/Louden/files/
docker exec -u root -it $(docker ps -qf "name=app") cp -r /tmp/files_to_upload/. /var/www/html/data/Louden/files/

echo "[*] Indexando archivos en Nextcloud..."
# Escanear los archivos para que aparezcan en la interfaz web
docker exec -u www-data -it $(docker ps -qf "name=app") php occ files:scan Louden

echo "[+] Proceso completado. Accede en http://localhost:8080"