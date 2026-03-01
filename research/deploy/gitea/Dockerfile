FROM gitea/gitea:latest

# Configuración de Servidor
ENV GITEA__server__HTTP_PORT=34698
ENV GITEA__server__DOMAIN=challs.caliphallabs.com
ENV GITEA__server__ROOT_URL=http://challs.caliphallabs.com:34698/
ENV GITEA__security__INSTALL_LOCK=true

# Configuración de Visibilidad (Abierto para CTF)
ENV GITEA__service__REQUIRE_SIGNIN_VIEW=false
ENV GITEA__repository__DEFAULT_PRIVATE=public
ENV GITEA__repository__ENABLE_PUSH_CREATE_USER=true
ENV GITEA__service__DISABLE_REGISTRATION=true

RUN apk add --no-cache git netcat-openbsd curl

RUN mkdir -p /tmp/ransomware-project
COPY files/ransomware-project /tmp/ransomware-project

COPY entry_point.sh /usr/local/bin/entry_point.sh
RUN chmod +x /usr/local/bin/entry_point.sh

EXPOSE 34698

ENTRYPOINT ["/usr/local/bin/entry_point.sh"]