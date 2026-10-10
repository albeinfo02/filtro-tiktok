"""Icona dell'effetto con il personaggio centrale della copertina di "I Baffi".

Uso:  python3 tools/genera_icona_copertina.py
Legge originali/copertina/copertina_i_baffi.png, isola il personaggio centrale
(solo l'inchiostro suo, senza i pezzi delle facce vicine) e scrive in asset/icona/:
  copertina_giallo_162.png / _1024   personaggio su sfondo giallo, viso color carta
  copertina_carta_162.png  / _1024   personaggio su sfondo carta, come la copertina
  copertina_bianco_162.png / _1024   personaggio su sfondo bianco puro
  copertina_domanda_162.png / _1024  come il giallo, con un "?" a pennello
"""

import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepara_asset import font, pennello  # noqa: E402
from genera_baffi_nuovi import disegna_nome  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "originali" / "copertina" / "copertina_i_baffi.png"
OUT = ROOT / "asset" / "icona"
RITAGLIO = (640, 560, 1300, 1220)        # zona del personaggio centrale (copertina 2000x2000)
GIALLO, CARTA, INCHIOSTRO = (255, 210, 63), (243, 240, 232), (17, 17, 17)


def componenti(mask):
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32)
    info = []
    for y, x in zip(*np.nonzero(mask)):
        if lab[y, x]:
            continue
        n = len(info) + 1
        lab[y, x] = n
        q, pts = deque([(y, x)]), 0
        y0 = y1 = y
        x0 = x1 = x
        while q:
            cy, cx = q.popleft()
            pts += 1
            y0, y1, x0, x1 = min(y0, cy), max(y1, cy), min(x0, cx), max(x1, cx)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n
                        q.append((ny, nx))
        info.append((pts, y0, x0, y1, x1))
    return lab, info


def personaggio():
    """Restituisce (inchiostro, interno): maschere del tratto e del viso da riempire."""
    im = Image.open(SRC).convert("L").crop(RITAGLIO)
    ink = np.array(im) < 110
    lab, info = componenti(ink)
    h, w = ink.shape
    # il personaggio è la componente grande più vicina al centro
    centro = lab[h // 2 - 40: h // 2 + 40, w // 2 - 40: w // 2 + 40]
    vals, cnt = np.unique(centro[centro > 0], return_counts=True)
    princ = int(vals[np.argmax(cnt)]) if len(vals) else int(np.argmax([i[0] for i in info]) + 1)
    _, Y0, X0, Y1, X1 = info[princ - 1]
    tieni = np.zeros(len(info) + 1, bool)
    for n, (_, y0, x0, y1, x1) in enumerate(info, start=1):
        tieni[n] = n == princ or (y0 >= Y0 and x0 >= X0 and y1 <= Y1 and x1 <= X1)
    inchiostro = tieni[lab]
    # interno del viso = ciò che non è raggiungibile dal bordo senza attraversare l'inchiostro
    chiuso = np.array(Image.fromarray(inchiostro.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(7))) > 0
    fuori = np.zeros_like(chiuso)
    q = deque((y, x) for y in range(h) for x in (0, w - 1)) + deque((y, x) for x in range(w) for y in (0, h - 1))
    for y, x in q:
        fuori[y, x] = not chiuso[y, x]
    q = deque((y, x) for y, x in zip(*np.nonzero(fuori)))
    while q:
        cy, cx = q.popleft()
        for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
            if 0 <= ny < h and 0 <= nx < w and not fuori[ny, nx] and not chiuso[ny, nx]:
                fuori[ny, nx] = True
                q.append((ny, nx))
    # l'anello tra il fuori e il tratto (lasciato dalla chiusura) non è viso: niente alone chiaro
    fuori = np.array(Image.fromarray(fuori.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(9))) > 0
    interno = ~fuori & ~inchiostro
    ys, xs = np.nonzero(inchiostro)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    return inchiostro, interno, box


def componi(inchiostro, interno, box, sfondo, G=1024, margine=0.12, viso=CARTA, dx=0.0):
    x0, y0, x1, y1 = box
    lato = max(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    sel = (int(cx - lato / 2), int(cy - lato / 2), int(cx + lato / 2), int(cy + lato / 2))
    dim = int(G * (1 - 2 * margine))

    def mappa(m):
        img = Image.fromarray(m.astype(np.uint8) * 255).crop(sel)
        return img.resize((dim, dim), Image.LANCZOS)

    tela = Image.new("RGB", (G, G), sfondo)
    off = ((G - dim) // 2 + int(G * dx), (G - dim) // 2 + int(G * 0.03))
    tela.paste(viso, off, mappa(interno))
    tela.paste(INCHIOSTRO, off, mappa(inchiostro))
    return tela


def riga(testo, seed):
    """Scritta a pennello su una riga sola (disegna_nome andrebbe a capo con i testi lunghi)."""
    pezzi = []
    for k, parola in enumerate(testo.split()):
        a = disegna_nome(parola, seed + k, passo=150).getchannel("A")
        pezzi.append(a.crop(a.getbbox()))
    h = max(p.height for p in pezzi)
    spazio = h // 2
    out = Image.new("L", (sum(p.width for p in pezzi) + spazio * (len(pezzi) - 1), h), 0)
    x = 0
    for p in pezzi:
        out.paste(p, (x, h - p.height))
        x += p.width + spazio
    return out


def salva(im, nome):
    im.save(OUT / f"{nome}_1024.png", optimize=True)
    im.resize((162, 162), Image.LANCZOS).save(OUT / f"{nome}_162.png", optimize=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    ink, dentro, box = personaggio()
    salva(componi(ink, dentro, box, GIALLO), "copertina_giallo")
    salva(componi(ink, dentro, box, CARTA), "copertina_carta")
    salva(componi(ink, dentro, box, (255, 255, 255), viso=(255, 255, 255)), "copertina_bianco")
    for nome, sfondo, viso in (("copertina_domanda", GIALLO, CARTA),
                               ("copertina_bianco_domanda", (255, 255, 255), (255, 255, 255))):
        # personaggio un po' più piccolo e spostato a sinistra, "?" in alto a destra senza toccare i capelli
        im = componi(ink, dentro, box, sfondo, margine=0.17, viso=viso, dx=-0.05)
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).text((im.width * 0.8, im.height * 0.2), "?", font=font(240), fill=255, anchor="mm")
        im.paste(INCHIOSTRO, mask=pennello(m, ampiezza=6, seed=3))
        salva(im, nome)
    # bianca con "?" e la scritta del ritornello sotto
    im = componi(ink, dentro, box, (255, 255, 255), margine=0.25, viso=(255, 255, 255), dx=-0.05)
    im = im.transform(im.size, Image.AFFINE, (1, 0, 0, 0, 1, 150), fillcolor=(255, 255, 255))   # personaggio più in alto
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).text((im.width * 0.8, im.height * 0.14), "?", font=font(220), fill=255, anchor="mm")
    im.paste(INCHIOSTRO, mask=pennello(m, ampiezza=6, seed=3))
    for testo, y in (("HO FATTO CRESCERE", 0.74), ("I BAFFI", 0.87)):
        t = riga(testo, 40 + len(testo))
        s_ = min(im.width * 0.86 / t.width, im.height * 0.11 / t.height)
        t = t.resize((int(t.width * s_), int(t.height * s_)), Image.LANCZOS)
        im.paste(INCHIOSTRO, (int((im.width - t.width) / 2), int(im.height * y - t.height / 2)), t)
    salva(im, "copertina_bianco_scritta")
    print("icone ok")
