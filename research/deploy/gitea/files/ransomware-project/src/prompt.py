import os
import shutil

def copy_prompt_image(destination_path="."):
    source = os.path.join("assets", "pwned.png")
    
    destination = os.path.join(destination_path, "prompt.png")

    try:
        if os.path.exists(source):
            shutil.copy2(source, destination)
            print(f"[+] Nota Ransom copiada en {destination_path}")
        else:
            print(f"[-] Error: Imagen '{source}' no encontrada. Asegúrate de que exista la carpeta assets/.")
            
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    copy_prompt_image()