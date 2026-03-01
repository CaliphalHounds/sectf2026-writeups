#!/bin/bash

cleanup() {
    echo "[*] Deteniendo Gitea..."
    kill $GITEA_PID
    exit 0
}

trap cleanup SIGINT SIGTERM

/usr/bin/entrypoint &
GITEA_PID=$!

echo "[*] Esperando a que Gitea inicie en el puerto 34698..."
while ! nc -z localhost 34698; do 
  sleep 2
done

echo "[+] Gitea detectado. Iniciando configuración de Louden..."

# 1. Crear Usuario
su git -c "gitea admin user create --username Louden --password '23af2cb61920c' --email louden@proton.me --admin --must-change-password=false"

# 2. Habilitar Push to Create
su git -c "gitea admin config set repository.ENABLE_PUSH_CREATE_USER true"

echo "[*] Realizando push del proyecto..."
chown -R git:git /tmp/ransomware-project
su git -c "cd /tmp/ransomware-project && \
    git init && \
    git config --global user.email 'louden@proton.me' && \
    git config --global user.name 'Louden' && \
    git add . && \
    git commit -m 'Initial commit - Source code' && \
    git remote add origin http://localhost:34698/Louden/ransomware-hospital.git && \
    git push http://Louden:23af2cb61920c@localhost:34698/Louden/ransomware-hospital.git master"

# 3. Forzar visibilidad PÚBLICA (AHORA ANTES DEL WAIT)
echo "[*] Verificando repositorio y forzando visibilidad pública..."
sleep 2

# Intentar el parche hasta que Gitea haya procesado el nuevo repo
for i in {1..5}; do
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X 'PATCH' \
      'http://localhost:34698/api/v1/repos/Louden/ransomware-hospital' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -u Louden:23af2cb61920c \
      -d '{ "private": false, "visibility": "public" }')
    
    if [ "$RESPONSE" == "200" ]; then
        echo "[!] Repositorio convertido a PÚBLICO con éxito."
        break
    fi
    echo "[...] Reintentando visibilidad ($i/5)..."
    sleep 2
done

echo "[!] Configuración completada. Gitea operativo en: http://challs.caliphallabs.com:34698/"

# EL WAIT SIEMPRE AL FINAL
wait $GITEA_PID