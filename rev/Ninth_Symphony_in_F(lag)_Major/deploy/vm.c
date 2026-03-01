#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>


typedef struct {
    uint8_t regs[8];
    uint8_t memory[1024];
    uint16_t pc;
    uint8_t zf;
    uint8_t result;
} VM;


void vm_init(VM *vm) {
    memset(vm, 0, sizeof(VM));
    vm->result = 0;
}


static int vm_read_string(VM *vm, uint8_t addr, char *out, size_t max)
{
    size_t i = 0;

    while (i + 1 < max && addr < 1024) {
        uint8_t c = vm->memory[addr++];
        out[i++] = (char)c;
        if (c == 0)
            return 1;
    }

    out[i] = 0;
    return 0;
}


static void vm_syscall(VM *vm, uint8_t s, uint8_t a)
{
    switch (vm->regs[s]) {
        case 1: {
            char path[256];

            if (!vm_read_string(vm, vm->regs[a], path, sizeof(path)))
                break;

            FILE *f = fopen(path, "rb");

            memset(vm->memory, 0, sizeof(vm->memory));
            fread(vm->memory, 1, sizeof(vm->memory), f);
            fclose(f);
            break;
        }
        case 2: {
            putchar(vm->regs[a]);
            fflush(stdout);
            break;
        }
        default: break;
    }
}


void vm_run(VM *vm, const uint8_t *code, size_t size) {
    vm->pc = 0;
    while (vm->pc < size) {
        uint8_t op = code[vm->pc];
        switch (op) {
            case 0x00: return;
            case 0x01: {
                vm->pc++; uint8_t d = code[vm->pc++], v = code[vm->pc++];
                vm->regs[d] = v;
                break;
            }
            case 0x02: {
                vm->pc++; uint8_t d = code[vm->pc++], s = code[vm->pc++];
                vm->regs[d] += vm->regs[s];
                break;
            }
            case 0x03: {
                vm->pc++; uint8_t d = code[vm->pc++], s = code[vm->pc++];
                vm->regs[d] ^= vm->regs[s];
                break;
            }
            case 0x04: {
                vm->pc++; uint8_t a = code[vm->pc++], b = code[vm->pc++];
                vm->zf = (vm->regs[a] == vm->regs[b]);
                break;
            }
            case 0x05: {
                vm->pc++; uint8_t l = code[vm->pc++], h = code[vm->pc++];
                uint16_t t = (h << 8) | l;
                vm->pc = t;
                break;
            }
            case 0x06: {
                vm->pc++; uint8_t l = code[vm->pc++], h = code[vm->pc++];
                uint16_t t = (h << 8) | l;
                if (vm->zf) {
                    vm->pc = t;
                }
                break;
            }
            case 0x07: {
                vm->pc++; uint8_t l = code[vm->pc++], h = code[vm->pc++];
                uint16_t t = (h << 8) | l;
                if (!vm->zf) {
                    vm->pc = t;
                }
                break;
            }
            case 0x08: {
                vm->pc++; uint8_t d = code[vm->pc++], b = code[vm->pc++];
                uint16_t addr = vm->regs[b];
                vm->regs[d] = (addr < 1024) ? vm->memory[addr] : 0;
                break;
            }
            case 0x09: {
                vm->pc++; uint8_t r = code[vm->pc++];
                vm->result = vm->regs[r];
                break;
            }
            case 0x0A: {
                vm->pc++; uint8_t s = code[vm->pc++], b = code[vm->pc++];
                uint16_t addr = vm->regs[b];
                if (addr < 1024) vm->memory[addr] = vm->regs[s];
                break;
            }
            case 0x0B: {
                vm->pc++; uint8_t s = code[vm->pc++], a = code[vm->pc++];
                vm_syscall(vm, s, a);
                break;
            }
            default: return;
        }
    }
}


int calculate_arg(char n, char acc, char oct)
{
    int sem = 0;

    switch(n) {
        case 'A': sem = 0; break;
        case 'B': sem = 2; break;
        case 'C': sem = 3; break;
        case 'D': sem = 5; break;
        case 'E': sem = 7; break;
        case 'F': sem = 8; break;
        case 'G': sem = 10; break;
        default: return 0;
    }

    if(acc == '#') sem += 1;

    int oct_val = 0;
    if(oct >= '1' && oct <= '9')
        oct_val = oct - '1';
    else if(oct >= 'A' && oct <= 'C')
        oct_val = 9 + (oct - 'A');
    
    return oct_val * 12 + sem;
}


size_t translate_melody(char* melody, uint8_t *bytecode)
{
    size_t bytecode_len = 0;

    for (size_t i = 0; melody[i]; i += 9) {
        char op_n = melody[i];
        char op_acc = melody[i+1];

        switch (op_n) {
            case 'C':
                if (op_acc == '#')
                    bytecode[bytecode_len++] = 0x01;
                else
                    bytecode[bytecode_len++] = 0x00;
                break;

            case 'D':
                if (op_acc == '#')
                    bytecode[bytecode_len++] = 0x03;
                else
                    bytecode[bytecode_len++] = 0x02;
                break;

            case 'E':
                if (op_acc == '#')
                    bytecode[bytecode_len++] = 0x05;
                else
                    bytecode[bytecode_len++] = 0x04;
                break;

            case 'F':
                if (op_acc == '#')
                    bytecode[bytecode_len++] = 0x06;
                else
                    bytecode[bytecode_len++] = 0x05;
                break;

            case 'G':
                if (op_acc == '#')
                    bytecode[bytecode_len++] = 0x08;
                else
                    bytecode[bytecode_len++] = 0x07;
                break;

            case 'A':
                if (op_acc == '#')
                    bytecode[bytecode_len++] = 0x0A;
                else
                    bytecode[bytecode_len++] = 0x09;
                break;

            case 'B':
                if (op_acc == '#')
                    bytecode[bytecode_len++] = 0x00;
                else
                    bytecode[bytecode_len++] = 0x0B;
                break;
        }

        bytecode[bytecode_len++] = calculate_arg(melody[i+3], melody[i+4], melody[i+5]);
        bytecode[bytecode_len++] = calculate_arg(melody[i+6], melody[i+7], melody[i+8]);
    }

    return bytecode_len;
}


int main() {
    char melody[512*3];
    printf("Introduzca la melodía que desee reproducir: ");
    if (!fgets(melody, sizeof(melody), stdin)) return 1;
    melody[strcspn(melody, "\n")] = 0;

    uint8_t bytecode[512];
    size_t bytecode_len = translate_melody(melody, bytecode);

    VM vm;
    vm_init(&vm);
    vm_run(&vm, bytecode, bytecode_len);

    return 0;
}