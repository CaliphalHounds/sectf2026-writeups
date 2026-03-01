#!/usr/bin/env bash

rm /entrypoint.sh
cd /app

flag='clctf{0tr0_n0nc3_r3us3_3n_3cd5a...}'
jwt_secret="$(head -c 64 /dev/urandom | base64 -w 0)"

FLAG="$flag" JWT_SECRET="$jwt_secret" ./secure-sign