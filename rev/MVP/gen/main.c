#include <windows.h>
#include <imagehlp.h>
#include <bcrypt.h>
#include <stdio.h>

#pragma comment(lib, "imagehlp.lib")
#pragma comment(lib, "bcrypt.lib")


static BYTE key[32] = {
    0x63,0x61,0x6c,0x69,0x70,0x68,0x61,0x6c,
    0x5f,0x6c,0x61,0x62,0x73,0x21,0x21,0x21,
    0x21,0x21,0x21,0x21,0x21,0x21,0x21,0x21,
    0x21,0x21,0x21,0x21,0x21,0x21,0x21,0x21
};

static BYTE iv[16] = {
    0x6d,0x76,0x70,0x6d,0x76,0x70,0x6d,0x76,
    0x70,0x6d,0x76,0x70,0x6d,0x76,0x70,0x6d
};

int main()
{
    char path[MAX_PATH];
    GetModuleFileNameA(NULL, path, MAX_PATH);

    HANDLE hFile = CreateFileA(
        path,
        GENERIC_READ,
        FILE_SHARE_READ,
        NULL,
        OPEN_EXISTING,
        0,
        NULL);

    DWORD certCount = 0;

    ImageEnumerateCertificates(
        hFile,
        CERT_SECTION_TYPE_ANY,
        &certCount,
        NULL,
        0); 

    if (certCount == 0){
        printf("No certificates!\n");
        return 0;
    }

    DWORD size = 0;

    ImageGetCertificateData(
        hFile,
        0,
        NULL,
        &size);

    BYTE* buffer = (BYTE*)malloc(size);

    ImageGetCertificateData(
        hFile,
        0,
        (LPWIN_CERTIFICATE)buffer,
        &size);

    WIN_CERTIFICATE* cert = (WIN_CERTIFICATE*)buffer;

    BYTE *enc = ((BYTE*)cert) + 1456;
    DWORD enc_size = cert->dwLength - 1456;

    BCRYPT_ALG_HANDLE hAlg = NULL;
    BCRYPT_KEY_HANDLE hKey = NULL;

    DWORD objLen = 0, cb = 0;

    BCryptOpenAlgorithmProvider(
        &hAlg,
        BCRYPT_AES_ALGORITHM,
        NULL,
        0);

    BCryptSetProperty(
        hAlg,
        BCRYPT_CHAINING_MODE,
        (PUCHAR)BCRYPT_CHAIN_MODE_CBC,
        sizeof(BCRYPT_CHAIN_MODE_CBC),
        0);

    BCryptGetProperty(
        hAlg,
        BCRYPT_OBJECT_LENGTH,
        (PUCHAR)&objLen,
        sizeof(objLen),
        &cb,
        0);

    BYTE *keyObj = (BYTE*)malloc(objLen);

    BCryptGenerateSymmetricKey(
        hAlg,
        &hKey,
        keyObj,
        objLen,
        (PUCHAR)key,
        sizeof(key),
        0);

    DWORD plainSize = 0;

    BCryptDecrypt(
        hKey,
        enc,
        enc_size,
        NULL,
        iv,
        16,
        NULL,
        0,
        &plainSize,
        BCRYPT_BLOCK_PADDING);

    BYTE *plain = (BYTE*)malloc(plainSize);

    BCryptDecrypt(
        hKey,
        enc,
        enc_size,
        NULL,
        iv,
        16,
        plain,
        plainSize,
        &plainSize,
        BCRYPT_BLOCK_PADDING);
    
    char tmpPath[MAX_PATH];
    char dllPath[MAX_PATH];

    GetTempPathA(MAX_PATH, tmpPath);
    GetTempFileNameA(tmpPath, "mvp", 0, dllPath);

    HANDLE hOut = CreateFileA(
        dllPath,
        GENERIC_WRITE,
        0,
        NULL,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    DWORD written = 0;
    WriteFile(hOut, plain, plainSize, &written, NULL);
    CloseHandle(hOut);

    HMODULE hMod = LoadLibraryA(dllPath);

    typedef char* (*get_mvp_t)(void);

    get_mvp_t get_mvp = (get_mvp_t)GetProcAddress(hMod, "get_mvp");
    printf(get_mvp());

    FreeLibrary(hMod);
    DeleteFileA(dllPath);

    return 0;
}