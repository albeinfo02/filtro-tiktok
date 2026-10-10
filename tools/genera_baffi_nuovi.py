"""Disegna baffi NUOVI nello stile "inchiostro a pennello" e i loro nomi.

Uso:  python3 tools/genera_baffi_nuovi.py
Scrive in originali/baffi_generati/ e originali/nomi_generati/.
Dopo, lancia tools/prepara_asset.py come per gli altri.

Ogni baffo è descritto da "pennellate": liste di punti (x, y, spessore) in
unità relative (x: 0 = centro sotto il naso, 1 ≈ mezza bocca; y: verso il
basso). Le pennellate con simmetria vengono specchiate a sinistra.
Se ridisegni un baffo a mano, metti il PNG in originali/baffi_png/ con lo
stesso nome: ha la precedenza su questo generato.
"""

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepara_asset import pennello  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_B = ROOT / "originali" / "baffi_generati"
OUT_N = ROOT / "originali" / "nomi_generati"
U = 600                    # pixel per unità (disegno a 2x, poi si dimezza)
CW, CH = 2400, 1800
CX, CY = CW // 2, 600
INCHIOSTRO = (17, 17, 17, 255)


def catmull(pts, passi=60):
    """Curva morbida che passa per i punti (x, y, w)."""
    if len(pts) < 2:
        return pts
    p = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for s in range(passi):
            t = s / passi
            t2, t3 = t * t, t * t * t
            out.append(tuple(
                0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                       + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3)
                for k in range(3)))
    out.append(pts[-1])
    return out


def pennellata(d, pts, specchia=True):
    for x, y, w in catmull(pts):
        r = max(w, 0.004) * U / 2
        for sx in ((1, -1) if specchia else (1,)):
            px, py = CX + sx * x * U, CY + y * U
            d.ellipse([px - r, py - r, px + r, py + r], fill=255)


def spirale(cx, cy, r0, giri, w0, w1, verso=1, inizio=math.pi / 2):
    pts = []
    n = 24
    for i in range(n + 1):
        t = i / n
        a = inizio + verso * t * giri * 2 * math.pi
        r = r0 * (1 - 0.75 * t)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a), w0 + (w1 - w0) * t))
    return pts


# ---------------------------------------------------------------- i baffi
def gabbiano(d, rng):
    pennellata(d, [(0, 0.0, 0.09), (0.2, 0.1, 0.13), (0.45, 0.08, 0.11), (0.7, -0.04, 0.06), (0.88, -0.16, 0.015)])


def da_detective(d, rng):
    pennellata(d, [(0, 0.02, 0.07), (0.3, 0.06, 0.065), (0.58, 0.04, 0.04),
                   (0.72, -0.04, 0.025), (0.76, -0.16, 0.012), (0.73, -0.2, 0.004)])


def a_farfalla(d, rng):
    pennellata(d, [(0, 0.06, 0.07), (0.1, 0.02, 0.16), (0.22, 0.04, 0.22), (0.33, 0.08, 0.14), (0.38, 0.1, 0.05)])


def da_camionista(d, rng):
    pennellata(d, [(0, 0.04, 0.22), (0.3, 0.07, 0.26), (0.58, 0.16, 0.2), (0.72, 0.3, 0.09)])
    for i in range(16):  # ciuffi che scendono sul labbro
        x = -0.7 + 1.4 * i / 15 + rng.uniform(-0.03, 0.03)
        y0 = 0.14 + 0.18 * (abs(x) / 0.7) ** 2
        pennellata(d, [(x, y0, 0.05), (x + rng.uniform(-0.03, 0.03), y0 + rng.uniform(0.07, 0.12), 0.012)], False)


def da_cattivo(d, rng):
    pennellata(d, [(0, 0.02, 0.06), (0.35, 0.06, 0.055), (0.62, 0.02, 0.04), (0.74, -0.06, 0.03)])
    pennellata(d, spirale(0.66, -0.12, 0.13, 1.3, 0.03, 0.012, verso=1, inizio=-math.pi / 6))


def a_onda(d, rng):
    pts = [(x / 20 * 0.85, 0.05 + 0.055 * math.sin(x / 20 * 0.85 * 13), 0.09 - 0.06 * x / 20) for x in range(21)]
    pennellata(d, pts)


def a_scopa(d, rng):
    pennellata(d, [(0, 0.0, 0.11), (0.25, 0.01, 0.12), (0.45, 0.03, 0.1)])
    for i in range(19):  # setole
        x = -0.48 + 0.96 * i / 18 + rng.uniform(-0.015, 0.015)
        pennellata(d, [(x, 0.03, 0.035), (x + rng.uniform(-0.02, 0.02), 0.22 + rng.uniform(-0.03, 0.03), 0.018)], False)


def a_spaghetto(d, rng):
    pennellata(d, [(0, 0.02, 0.09), (0.14, 0.04, 0.08), (0.26, 0.08, 0.05)])
    pennellata(d, [(0.26, 0.08, 0.04), (0.33, 0.25, 0.03), (0.24, 0.42, 0.028),
                   (0.34, 0.6, 0.024), (0.25, 0.78, 0.02), (0.31, 0.9, 0.01)])


def a_corna(d, rng):
    pennellata(d, [(0, 0.02, 0.1), (0.22, 0.05, 0.12), (0.38, 0.0, 0.09), (0.46, -0.16, 0.06), (0.47, -0.3, 0.035), (0.44, -0.4, 0.01)])


def a_nuvola(d, rng):
    for i in range(7):
        t = i / 6
        x = 0.62 * t
        y = 0.05 + 0.1 * t * t
        r = 0.16 - 0.07 * t
        pennellata(d, [(x, y, r), (x + 0.01, y + 0.01, r)])
    pennellata(d, [(0, 0.08, 0.16), (0.5, 0.12, 0.1)])


def a_zigzag(d, rng):
    pts = []
    for i in range(9):
        x = 0.8 * i / 8
        pts.append((x, 0.03 + (0.09 if i % 2 else 0.0) + 0.05 * (x / 0.8) ** 2, 0.08 - 0.05 * i / 8))
    # niente curva morbida: segmenti dritti
    for a, b in zip(pts, pts[1:]):
        pennellata(d, [a, b])


def col_pennarello(d, rng):
    # scarabocchio avanti-indietro dentro la sagoma di un baffo
    pts = []
    for i in range(27):
        t = i / 26
        x = -0.72 + 1.44 * t
        alto = -0.01 + 0.06 * (abs(x) / 0.72) ** 2
        basso = 0.24 - 0.14 * (abs(x) / 0.72) ** 1.5
        y = alto if i % 2 == 0 else basso
        pts.append((x + rng.uniform(-0.02, 0.02), y + rng.uniform(-0.015, 0.015), 0.03))
    for a, b in zip(pts, pts[1:]):
        pennellata(d, [a, b], specchia=False)


NUOVI = {
    "20_a_gabbiano": (gabbiano, "A GABBIANO"),
    "21_da_detective": (da_detective, "DA DETECTIVE"),
    "22_a_farfalla": (a_farfalla, "A FARFALLA"),
    "23_da_camionista": (da_camionista, "DA CAMIONISTA"),
    "24_da_cattivo_dei_cartoni": (da_cattivo, "DA CATTIVO DEI CARTONI"),
    "25_a_onda": (a_onda, "A ONDA"),
    "26_a_scopa": (a_scopa, "A SCOPA"),
    "27_a_spaghetto": (a_spaghetto, "A SPAGHETTO"),
    "28_a_corna": (a_corna, "A CORNA"),
    "29_a_nuvola": (a_nuvola, "A NUVOLA"),
    "30_a_zigzag": (a_zigzag, "A ZIGZAG"),
    "31_col_pennarello": (col_pennarello, "COL PENNARELLO"),
}


def disegna_baffo(fn, seed):
    m = Image.new("L", (CW, CH), 0)
    fn(ImageDraw.Draw(m), random.Random(seed))
    m = pennello(m, ampiezza=7, seed=seed)
    m = m.crop(m.getbbox())
    m = m.resize((m.width // 2, m.height // 2), Image.LANCZOS)
    pad = 22  # stesso margine degli originali
    im = Image.new("RGBA", (m.width + 2 * pad, m.height + 2 * pad), (17, 17, 17, 0))
    alfa = Image.new("L", im.size, 0)
    alfa.paste(m, (pad, pad))
    im.putalpha(alfa)
    return im


def font(size):
    for p in ("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def disegna_nome(testo, seed):
    """Lettere maiuscole storte e irregolari, come scritte a pennello."""
    rng = random.Random(seed)
    righe = [testo]
    if len(testo) > 14:  # va a capo come i nomi originali lunghi
        parole = testo.split()
        meta = max(range(1, len(parole)), key=lambda k: -abs(len(" ".join(parole[:k])) - len(testo) / 2))
        righe = [" ".join(parole[:meta]), " ".join(parole[meta:])]
    S, passo = 220, 190
    W = max(len(r) for r in righe) * passo + 200
    H = len(righe) * 260 + 120
    m = Image.new("L", (W, H), 0)
    for ri, riga in enumerate(righe):
        x0 = (W - len(riga) * passo) / 2
        for i, ch in enumerate(riga):
            if ch == " ":
                continue
            s = int(S * rng.uniform(0.9, 1.08))
            lettera = Image.new("L", (s * 2, s * 2), 0)
            ImageDraw.Draw(lettera).text((s, s), ch, font=font(s), fill=255, anchor="mm")
            lettera = lettera.rotate(rng.uniform(-7, 7), resample=Image.BICUBIC)
            cx = x0 + i * passo + passo / 2 + rng.uniform(-8, 8)
            cy = 60 + ri * 260 + 130 + rng.uniform(-14, 14)
            m.paste(255, (int(cx - s), int(cy - s)), lettera)
    m = pennello(m, ampiezza=6, seed=seed)
    m = m.crop(m.getbbox())
    m = m.resize((m.width // 2, m.height // 2), Image.LANCZOS)
    im = Image.new("RGBA", (m.width + 40, m.height + 40), (17, 17, 17, 0))
    alfa = Image.new("L", im.size, 0)
    alfa.paste(m, (20, 20))
    im.putalpha(alfa)
    return im


if __name__ == "__main__":
    OUT_B.mkdir(parents=True, exist_ok=True)
    OUT_N.mkdir(parents=True, exist_ok=True)
    for k, (nome_file, (fn, testo)) in enumerate(NUOVI.items()):
        disegna_baffo(fn, 100 + k).save(OUT_B / f"{nome_file}.png", optimize=True)
        disegna_nome(testo, 200 + k).save(OUT_N / f"{nome_file}.png", optimize=True)
        print("generato", nome_file)
