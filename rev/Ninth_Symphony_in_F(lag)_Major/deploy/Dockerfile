FROM --platform=$BUILDPLATFORM gcc:13-bookworm AS build

WORKDIR /build
COPY vm.c .

RUN gcc -O2 -Wall vm.c -o ninth_symphony && strip --strip-all ninth_symphony

FROM debian:bookworm-slim

RUN apt update && apt install socat -y

WORKDIR /

COPY --from=build /build/ninth_symphony /ninth_symphony
COPY flag.txt /flag.txt

RUN useradd -m ctf
USER ctf

EXPOSE 5000

CMD ["socat", "TCP-LISTEN:5000,fork,reuseaddr", "EXEC:stdbuf -o0 /ninth_symphony,stderr"]
