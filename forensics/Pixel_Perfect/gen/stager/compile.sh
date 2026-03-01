pyinstaller --onefile --noconsole --icon=NONE stager.py

#x86_64-w64-mingw32-g++ loader.cpp -o installer.exe -municode -static -s -lwinhttp -lcrypt32 -lshell32 -lshlwapi