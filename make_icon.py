"""Gera icon.ico com ícone de sino para o app."""
from PIL import Image, ImageDraw
import math

def draw_bell(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size

    # Fundo azul arredondado
    r = max(4, s // 6)
    d.rounded_rectangle([2, 2, s-2, s-2], radius=r, fill=(35, 95, 195, 255))

    # Proporções do sino
    cx   = s * 0.50
    dome_top  = s * 0.14
    dome_r    = s * 0.28          # raio do domo
    body_bot  = s * 0.65          # base do corpo
    flare_bot = s * 0.72          # base da aba inferior
    flare_ex  = s * 0.06          # quanto a aba extravasa

    # Domo (semicírculo superior)
    d.pieslice(
        [cx - dome_r, dome_top, cx + dome_r, dome_top + dome_r * 2],
        start=180, end=0,
        fill=(255, 255, 255, 240)
    )

    # Corpo retangular abaixo do domo
    d.rectangle(
        [cx - dome_r, dome_top + dome_r, cx + dome_r, body_bot],
        fill=(255, 255, 255, 240)
    )

    # Aba inferior (mais larga)
    d.rounded_rectangle(
        [cx - dome_r - flare_ex, body_bot,
         cx + dome_r + flare_ex, flare_bot],
        radius=max(2, s // 30),
        fill=(255, 255, 255, 240)
    )

    # Batedor (círculo pequeno)
    cr = s * 0.065
    cy = flare_bot + cr * 1.1
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(255, 255, 255, 240))

    # Cabo no topo
    hx, hy = cx, dome_top
    hr = s * 0.055
    d.ellipse([hx - hr, hy - hr * 1.6, hx + hr, hy + hr * 0.3],
              outline=(255, 255, 255, 240), width=max(2, s // 28))

    return img


if __name__ == "__main__":
    sizes = [16, 32, 48, 64, 256]
    imgs = [draw_bell(s) for s in sizes]

    out = "C:/Users/Acer/Lembretes pessoais/icon.ico"
    imgs[0].save(
        out,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=imgs[1:]
    )
    print(f"Ícone salvo em {out}")
