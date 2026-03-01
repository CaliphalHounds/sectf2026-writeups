
questions = [
    ("¿Cuál es el nombre del usuario? (1/12)", "nofts"),
    ("¿Cuál fue la primera búsqueda que hizo en internet? (2/12)", "niftski"),
    ("¿Cuál fue el primer archivo que descargó? Introduce el nombre completo del archivo, sin la ruta. (3/12)", "Nestopia140bin.zip"),
    ("¿Cuándo fue la primera vez que ejecutó el emulador? Formato: YYYY-MM-DD HH:MM:SS GMT (4/12)", "2026-02-24 00:44:16 GMT"),
    ("¿Qué versión del emulador utiliza? Por ejemplo, si la versión es 2.34.1, la respuesta es 2.34.1. (5/12)", "1.40"),
    ("El usuario hizo una captura de pantalla desde el emulador mientras jugaba. ¿Cuál es el mensaje que muestra la pantalla? (6/12)", "GAME OVER"),
    ("Llegó un momento en el que se frustró y siguió buscando ayuda por internet. En ese momento, ¿qué binario descargó? Introduce el nombre completo del archivo, sin la ruta. (7/12)", "installer.exe"),
    ("Tras ese momento de frustración descargó una aplicación. ¿Cuál fue? (8/12)", "Discord"),
    ("Parece que el nombre del usuario del sistema fue un error... ¿cuál es el nombre real que quería poner el usuario? Pista: Busca el nombre de usuario de Discord (9/12)", "noftski"),
    ("¿En cuántos servidores de Discord estaba noftski? (10/12)", "2"),
    ("¿Cuáles son los IDs de los servidores de Discord? Introdúcelos de menor a mayor, con una coma en medio. Por ejemplo: id1,id2 (11/12)", "599131748143464459,1475665918297374916"),
    ("Uno de los servidores tiene bastantes miembros... ¿cuál es su nombre? (12/12)", "Super Mario Speedrunning (8-bit)"),
]

for question, answer in questions:
        print(question)
        user_answer = input("> ")
        if user_answer.strip().lower() == answer.lower():
            print("¡Correcto!\n")
        else:
            print("¡Incorrecto!")
            exit()

print("¡Felicidades!")
print("clctf{n0ftsk1_15_4_n1fTsk1_w4Nn4_B3}")
