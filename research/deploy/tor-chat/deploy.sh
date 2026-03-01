#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}[*] Iniciando despliegue de infraestructura LOUDEN GROUP...${NC}"

# 1. Limpieza total
echo -e "${BLUE}[*] Limpiando contenedores antiguos...${NC}"
docker compose down --remove-orphans > /dev/null 2>&1

# 2. Configuración de permisos
# IMPORTANTE: Si la carpeta no existe, la creamos. Si existe, le damos permisos
# para que el 'build context' no falle, y luego se los devolveremos a Tor.
echo -e "${BLUE}[*] Ajustando permisos de volúmenes...${NC}"
mkdir -p tor_data
sudo chmod -R 755 tor_data  # Permiso temporal para el Build Context

# 3. Construcción y levantamiento
echo -e "${BLUE}[*] Construyendo imágenes y levantando servicios...${NC}"
docker compose up --build -d

# 4. Devolver permisos a Tor (UID 100 en Alpine)
echo -e "${BLUE}[*] Asegurando privacidad de llaves Tor...${NC}"
sudo chown -R 100:100 tor_data
sudo chmod -R 700 tor_data

# 5. Espera de la URL
echo -e "${BLUE}[*] Esperando generación de dirección .onion...${NC}"
MAX_RETRIES=40
COUNT=0
ONION_URL=""

while [ $COUNT -lt $MAX_RETRIES ]; do
    # Usamos sudo cat porque Kali no tendrá permiso de lectura directo
    if [ -f "tor_data/hostname" ]; then
        ONION_URL=$(sudo cat tor_data/hostname)
        break
    fi
    echo -ne "    Buscando llaves... ($((COUNT+1))/$MAX_RETRIES)\r"
    sleep 2
    COUNT=$((COUNT+1))
done

echo -e "\n"

if [ -z "$ONION_URL" ]; then
    echo -e "${RED}[!] Error: No se pudo obtener la URL .onion.${NC}"
    docker logs loudentor
else
    echo -e "${GREEN}[+] ¡INFRAESTRUCTURA LISTA!${NC}"
    echo -e "${GREEN}[+] URL:${NC} http://$ONION_URL"
fi

docker exec loudentor cat /var/lib/tor/hidden_service/hostname
