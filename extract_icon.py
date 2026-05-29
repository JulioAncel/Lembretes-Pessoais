"""Extrai a peninha azul do tk86t.dll e salva como icon.ico."""
import ctypes, ctypes.wintypes as wt
from PIL import Image
import os, sys

BASE   = os.path.dirname(os.path.abspath(__file__))
PY_DIR = os.path.dirname(sys.executable)
TK_DLL = os.path.join(PY_DIR, "DLLs", "tk86t.dll")

def hicon_to_pil(hicon, size):
    hdc_screen = ctypes.windll.user32.GetDC(None)
    hdc = ctypes.windll.gdi32.CreateCompatibleDC(hdc_screen)

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG),
            ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
            ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", wt.LONG),
            ("biYPelsPerMeter", wt.LONG), ("biClrUsed", wt.DWORD), ("biClrImportant", wt.DWORD),
        ]

    bih = BITMAPINFOHEADER()
    bih.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bih.biWidth = size; bih.biHeight = -size
    bih.biPlanes = 1;   bih.biBitCount = 32; bih.biCompression = 0

    pbits = ctypes.c_void_p()
    hbm = ctypes.windll.gdi32.CreateDIBSection(hdc, ctypes.byref(bih), 0, ctypes.byref(pbits), None, 0)
    old = ctypes.windll.gdi32.SelectObject(hdc, hbm)
    ctypes.windll.user32.DrawIconEx(hdc, 0, 0, hicon, size, size, 0, None, 3)

    buf = (ctypes.c_byte * (size * size * 4))()
    ctypes.windll.gdi32.GetBitmapBits(hbm, size * size * 4, buf)
    ctypes.windll.gdi32.SelectObject(hdc, old)
    ctypes.windll.gdi32.DeleteObject(hbm)
    ctypes.windll.gdi32.DeleteDC(hdc)
    ctypes.windll.user32.ReleaseDC(None, hdc_screen)

    arr = bytearray(buf)
    for i in range(0, len(arr), 4):
        arr[i], arr[i+2] = arr[i+2], arr[i]
    return Image.frombytes("RGBA", (size, size), bytes(arr))


large = (ctypes.c_size_t * 1)()
small = (ctypes.c_size_t * 1)()

# Extrai ambos os ícones do tk86t.dll e salva separado para ver qual é a peninha
n = ctypes.windll.shell32.ExtractIconExW(TK_DLL, -1, None, None, 0)
print(f"Total de ícones em tk86t.dll: {n}")

saved = []
for idx in range(n):
    large[0] = 0
    ctypes.windll.shell32.ExtractIconExW(TK_DLL, idx, large, small, 1)
    if large[0]:
        img = hicon_to_pil(large[0], 256)
        path = os.path.join(BASE, f"icon_preview_{idx}.png")
        img.save(path)
        saved.append((idx, large[0], path))
        print(f"  Ícone {idx} salvo em: {path}")
        ctypes.windll.user32.DestroyIcon(large[0])

if saved:
    # Usa o primeiro como icon.ico com múltiplos tamanhos
    # (pode trocar o índice depois de ver os previews)
    for idx, _, _ in saved:
        large[0] = 0
        ctypes.windll.shell32.ExtractIconExW(TK_DLL, idx, large, small, 1)
        if large[0]:
            sizes  = [16, 32, 48, 64, 128, 256]
            images = [hicon_to_pil(large[0], s) for s in sizes]
            ctypes.windll.user32.DestroyIcon(large[0])
            out = os.path.join(BASE, f"icon_tk_{idx}.ico")
            images[0].save(out, format="ICO", sizes=[(s,s) for s in sizes], append_images=images[1:])
            print(f"  ICO {idx} salvo: {out}")

print("\nAbra os arquivos icon_preview_0.png e icon_preview_1.png para ver qual é a peninha.")
