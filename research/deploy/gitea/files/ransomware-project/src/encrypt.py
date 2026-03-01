import os
import struct
from cryptography.fernet import Fernet

def generate_key():
    key = Fernet.generate_key()
    with open("key.txt", "wb") as key_file:
        key_file.write(key)
    return key

def encrypt_folder(folder_name, output_file):
    if not os.path.exists(folder_name):
        print(f"Error: Carpeta '{folder_name}' no encontrada.")
        return

    key = generate_key()
    cipher = Fernet(key)

    print(f"Cifrando carpeta: {folder_name}...")

    with open(output_file, "wb") as f_out:
        for root, dirs, files in os.walk(folder_name):
            for file in files:
                path = os.path.join(root, file)
                with open(path, "rb") as f_in:

                    file_content = f_in.read()
                    
                    header = f"FILE_NAME:{file}CONTENT:".encode()
                    footer = b"END_FILE"
                    payload = header + file_content + footer
                    
                    encrypted_block = cipher.encrypt(payload)
                    
                    f_out.write(struct.pack(">I", len(encrypted_block)))
                    f_out.write(encrypted_block)
                    
                    print(f" [+] Archivo cifrado: {file}")

    print(f"\nCarpeta cifrada en '{output_file}'")
    print("Key utilizada guardada en 'key.txt'.")

if __name__ == "__main__":
    encrypt_folder("medical-files", "files.enc")