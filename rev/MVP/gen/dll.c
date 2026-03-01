#include <windows.h>

const char* get_flag(void)
{
    return "clctf{MVP_r1gHts_pr073tEd_w1Th_c3rT1F1c4735}";
}

__declspec(dllexport)
const char* get_mvp(void)
{
    return "Censurado. © 2026 Caliphal Labs - Todos los derechos reservados.";
}

BOOL WINAPI DllMain(
    HINSTANCE hinstDLL,
    DWORD fdwReason,
    LPVOID lpvReserved)
{
    return TRUE;
}