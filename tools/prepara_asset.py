"""Prepara gli asset per l'effetto "Che baffo sei?" partendo da originali/.

Uso:  python3 tools/prepara_asset.py

Cosa fa:
  1. pulisce i baffi dalle macchioline isolate;
  2. li porta tutti su una tela 1024x1024 con lo STESSO punto d'aggancio
     (centro del labbro superiore) e una scala coerente tra loro;
  3. crea la versione con bordino bianco (per barbe / pelle scura);
  4. ritaglia i nomi su una tela uniforme 1024x256 (anche con bordo bianco);
  5. genera l'icona dell'effetto (162x162, specifiche Effect House);
  6. genera un foglio di controllo con tutti i baffi allineati.
"""

import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
# i disegni a mano hanno la precedenza su quelli generati con lo stesso nome
SRC_BAFFI = [ROOT / "originali" / "baffi_png", ROOT / "originali" / "baffi_generati"]
SRC_NOMI = [ROOT / "originali" / "nomi_png", ROOT / "originali" / "nomi_generati"]
OUT = ROOT / "asset"

TELA = 1024
# punto della tela dove cade il centro del labbro superiore (sotto il naso)
ANCORA = (512, 300)
# larghezza "standard" di un baffo sulla tela; ogni tipo ha un moltiplicatore
LARGHEZZA_BASE = 600
# l'elenco dei baffi (nome e scala di ognuno) sta in baffi.json
CATALOGO = json.loads((ROOT / "baffi.json").read_text(encoding="utf-8"))
BORDO_PX = 14  # spessore del bordino bianco sulla tela 1024


def componenti(mask):
    """Etichetta le componenti connesse (8-vicini) di una maschera booleana."""
    h, w = mask.shape
    lab = np.zeros((h, w), dtype=np.int32)
    comps = []
    for y, x in zip(*np.nonzero(mask)):
        if lab[y, x]:
            continue
        n = len(comps) + 1
        lab[y, x] = n
        q = deque([(y, x)])
        pts = []
        while q:
            cy, cx = q.popleft()
            pts.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n
                        q.append((ny, nx))
        ys, xs = zip(*pts)
        comps.append((len(pts), min(ys), min(xs), max(ys), max(xs)))
    return lab, comps


def pulisci(im):
    """Toglie le macchioline lontane dal disegno principale."""
    a = np.array(im.getchannel("A"))
    mask = a > 32
    lab, comps = componenti(mask)
    grande = max(c[0] for c in comps)
    # il "corpo" del disegno: componenti almeno al 10% della più grande
    corpo = [c for c in comps if c[0] >= grande * 0.10]
    y0 = min(c[1] for c in corpo); x0 = min(c[2] for c in corpo)
    y1 = max(c[3] for c in corpo); x1 = max(c[4] for c in corpo)
    m = int(0.12 * max(x1 - x0, y1 - y0))
    tieni = np.zeros(len(comps) + 1, dtype=bool)
    for i, c in enumerate(comps, start=1):
        dentro = c[1] >= y0 - m and c[3] <= y1 + m and c[2] >= x0 - m and c[4] <= x1 + m
        tieni[i] = c[0] >= grande * 0.10 or dentro
    pulita = np.array(im)
    via = ~tieni[lab] & (a > 0)
    # anche i pixel semitrasparenti attorno alle macchie (alpha <= 32)
    via |= (a <= 32) & (a > 0) & ~np.array(Image.fromarray((tieni[lab] * 255).astype(np.uint8))
                                           .filter(ImageFilter.MaxFilter(5))).astype(bool)
    pulita[via, 3] = 0
    out = Image.fromarray(pulita, "RGBA")
    return out.crop(out.getchannel("A").getbbox())


def punto_labbro(im):
    """Coordinate (x, y) del centro del labbro superiore nell'immagine ritagliata:
    il pixel più in alto nella fascia centrale (10%) del disegno."""
    a = np.array(im.getchannel("A")) > 32
    w = a.shape[1]
    fascia = a[:, int(w * 0.45): int(w * 0.55) + 1]
    righe = np.nonzero(fascia.any(axis=1))[0]
    y = int(righe[0]) if len(righe) else 0
    return w / 2, y


def bordo_bianco(im, r):
    a = np.array(im.getchannel("A")) > 32
    dil = np.zeros_like(a)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                dil |= np.roll(np.roll(a, dy, 0), dx, 1)
    sil = Image.fromarray((dil * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    base = Image.new("RGBA", im.size, (255, 255, 255, 0))
    base.putalpha(sil)
    base.alpha_composite(im)
    return base


def sorgente(cartelle, nome):
    for c in cartelle:
        if (c / f"{nome}.png").exists():
            return c / f"{nome}.png"
    raise SystemExit(f"manca il disegno di {nome} in " + ", ".join(str(c) for c in cartelle))


def prepara_baffi():
    out_n = OUT / "baffi_nero"; out_b = OUT / "baffi_bordo_bianco"
    out_n.mkdir(parents=True, exist_ok=True); out_b.mkdir(parents=True, exist_ok=True)
    risultati = []
    for voce in CATALOGO:
        nome = voce["id"]
        im = pulisci(Image.open(sorgente(SRC_BAFFI, nome)).convert("RGBA"))
        s = LARGHEZZA_BASE * voce["scala"] / im.width
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        lx, ly = punto_labbro(im)
        x, y = round(ANCORA[0] - lx), round(ANCORA[1] - ly)
        if x < BORDO_PX or y < BORDO_PX or x + im.width > TELA - BORDO_PX or y + im.height > TELA - BORDO_PX:
            raise SystemExit(f"{nome}: non entra nella tela ({x},{y},{im.size})")
        tela = Image.new("RGBA", (TELA, TELA), (0, 0, 0, 0))
        tela.alpha_composite(im, (x, y))
        tela.save(out_n / f"{nome}.png", optimize=True)
        bb = bordo_bianco(tela, BORDO_PX)
        bb.save(out_b / f"{nome}.png", optimize=True)
        risultati.append((nome, tela, bb))
        print(f"baffo  {nome:26s} ok")
    return risultati


def prepara_nomi():
    out_n = OUT / "nomi_nero"; out_b = OUT / "nomi_bordo_bianco"
    out_n.mkdir(parents=True, exist_ok=True); out_b.mkdir(parents=True, exist_ok=True)
    W, H, PAD = 1024, 256, 20
    for voce in CATALOGO:
        f = sorgente(SRC_NOMI, voce["id"])
        im = Image.open(f).convert("RGBA")
        im = im.crop(im.getchannel("A").getbbox())
        s = min((W - 2 * PAD) / im.width, (H - 2 * PAD) / im.height)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        tela = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        tela.alpha_composite(im, ((W - im.width) // 2, (H - im.height) // 2))
        tela.save(out_n / f.name, optimize=True)
        bordo_bianco(tela, 8).save(out_b / f.name, optimize=True)
        print(f"nome   {f.stem:26s} ok")


def font(size):
    for p in ("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def pennello(mask, ampiezza=9, seed=7):
    """Rende irregolare il bordo di una maschera (effetto inchiostro a mano)."""
    rng = np.random.default_rng(seed)
    h, w = mask.size[1], mask.size[0]
    campo = []
    for _ in range(2):
        n = Image.fromarray((rng.random((h // 32, w // 32)) * 255).astype(np.uint8))
        campo.append((np.array(n.resize((w, h), Image.BICUBIC), dtype=np.float32) / 255 - 0.5) * 2 * ampiezza)
    yy, xx = np.mgrid[0:h, 0:w]
    sy = np.clip(yy + campo[0], 0, h - 1).astype(int)
    sx = np.clip(xx + campo[1], 0, w - 1).astype(int)
    a = np.array(mask)[sy, sx]
    out = Image.fromarray(a).filter(ImageFilter.GaussianBlur(3))
    return out.point(lambda v: 255 if v > 128 else 0).filter(ImageFilter.GaussianBlur(0.8))


def prepara_icona():
    """Icona 162x162 (area utile centrale 144x144), più una versione grande 1024."""
    out = OUT / "icona"; out.mkdir(parents=True, exist_ok=True)
    G = 1024
    ic = Image.new("RGBA", (G, G), "#FFD23F")
    # punto interrogativo grande, con bordi "a pennello" come i baffi
    m = Image.new("L", (G, G), 0)
    ImageDraw.Draw(m).text((G / 2, G * 0.40), "?", font=font(560), fill=255, anchor="mm")
    ic.paste("#111111", mask=pennello(m))
    baffo = Image.open(OUT / "baffi_bordo_bianco" / "01_manubrio.png")
    baffo = baffo.crop(baffo.getchannel("A").getbbox())
    s = G * 0.80 / baffo.width
    baffo = baffo.resize((round(baffo.width * s), round(baffo.height * s)), Image.LANCZOS)
    ic.alpha_composite(baffo, ((G - baffo.width) // 2, int(G * 0.62)))
    ic.convert("RGB").save(out / "icona_1024.png", optimize=True)
    ic.convert("RGB").resize((162, 162), Image.LANCZOS).save(out / "icona_162.png", optimize=True)
    print("icona  ok")


def foglio_controllo(risultati):
    """Tutti i baffi su una faccia stilizzata, per controllare allineamento e scala."""
    c, cols = 256, 6
    rows = -(-len(risultati) // cols)
    sheet = Image.new("RGB", (c * cols, c * rows * 2), "#e9e4d8")
    d = ImageDraw.Draw(sheet)
    for i, (nome, nero, bb) in enumerate(risultati):
        for j, im in enumerate((nero, bb)):
            x = (i % cols) * c
            y = (i // cols) * c + j * c * rows
            bg = "#e9e4d8" if j == 0 else "#5b3a29"
            d.rectangle([x, y, x + c - 1, y + c - 1], fill=bg, outline="#999")
            ax, ay = x + ANCORA[0] * c // TELA, y + ANCORA[1] * c // TELA
            d.ellipse([ax - 22, ay - 30, ax + 22, ay - 8], outline="#c44", width=2)  # naso
            d.line([ax - 40, ay + 22, ax + 40, ay + 22], fill="#c44", width=3)       # bocca
            sheet.paste(im.resize((c, c), Image.LANCZOS), (x, y), im.resize((c, c), Image.LANCZOS))
            d.text((x + 4, y + c - 14), nome, fill="#c44")
    sheet.save(OUT / "foglio_controllo.png", optimize=True)
    print("foglio di controllo ok")


if __name__ == "__main__":
    ris = prepara_baffi()
    prepara_nomi()
    prepara_icona()
    foglio_controllo(ris)
