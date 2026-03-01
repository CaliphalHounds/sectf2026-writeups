x86_64-w64-mingw32-g++ -o payload.exe payload.cpp -lws2_32 -static -static-libgcc -static-libstdc++ -O2

python3 Payload_To_PixelCode_video.py 

#x86_64-w64-mingw32-g++ Loader.cpp -o Loader.exe -municode -static -s -lwinhttp -lcrypt32 -lshell32 -lshlwapi