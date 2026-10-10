"""Baffi "realistici" disegnati pelo per pelo (niente AI).

Uso:  python3 tools/genera_baffi_realistici.py
Legge le sagome già allineate in asset/baffi_nero/ e scrive in asset/realistici/:
  <colore>/<id>.png           baffo completo (tela 512x512, stesso aggancio dei disegnati)
  <colore>/<id>_crescita_N.png  fasi di crescita (0 = primo accenno ... ultima = completo)

Ogni pelo nasce dentro la sagoma, segue la "piega" del baffo (verso l'esterno
e un po' verso il basso), è leggermente curvo e ha un colore che varia di poco.
Sotto i peli c'è un velo morbido che dà densità senza coprire la pelle.
"""

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "asset" / "baffi_nero"
OUT = ROOT / "asset" / "realistici"

LATO = 512          # tela finale (metà della tela dei disegnati: stesso aggancio in proporzione)
SS = 4              # si disegna a 4x e poi si riduce: peli sottili e morbidi
G = LATO * SS

# baffi che hanno senso in versione "vera" (gli altri sono troppo cartoon)
SCELTI = [
    "01_manubrio", "02_alla_dali", "03_tricheco", "04_ferro_di_cavallo", "06_spazzolino",
    "07_a_matita", "08_chevron", "09_imperiale", "10_inglese", "11_a_pennello", "12_a_lampada",
    "13_baffo_e_pizzetto", "14_peluria", "16_moschettiere", "17_da_carabiniere",
    "18_da_pizzaiolo", "19_da_zio_al_matrimonio",
]
COLORI = {
    "scuro": ((22, 15, 10), (88, 62, 42)),
    "castano": ((52, 34, 20), (140, 100, 64)),
}
FASI = [0.25, 0.5, 0.75, 1.0]   # lunghezza dei peli in ogni fase di crescita


def sagoma(id_):
    """Maschera della sagoma a G x G, ammorbidita (via le sbavature da pennello)."""
    a = Image.open(SRC / f"{id_}.png").getchannel("A").resize((G, G), Image.BILINEAR)
    a = a.filter(ImageFilter.GaussianBlur(SS * 3)).point(lambda v: 255 if v > 110 else 0)
    return np.array(a) > 0


def campo_direzioni(m):
    """Direzione dei peli: lungo la forma (perpendicolare al gradiente), verso l'esterno e in giù."""
    sm = np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(SS * 10)),
                  dtype=np.float32)
    gy, gx = np.gradient(sm)
    tx, ty = -gy, gx                          # tangente alla forma
    cx = G / 2
    xs = np.arange(G)[None, :] - cx
    # verso: x verso l'esterno; se il tratto è verticale, verso il basso
    segno = np.where(np.abs(tx) > np.abs(ty) * 0.3, np.sign(tx * xs + 1e-6), np.sign(ty + 1e-6))
    tx, ty = tx * segno, ty * segno
    n = np.hypot(tx, ty) + 1e-6
    tx, ty = tx / n, ty / n
    # i peli veri cadono un po' verso il basso e si aprono dal centro
    apri = np.clip(xs / (G * 0.25), -1, 1)
    dx = tx * 0.75 + apri * 0.35
    dy = ty * 0.75 + 0.55
    n = np.hypot(dx, dy) + 1e-6
    return dx / n, dy / n


def profondita(m):
    """0.7 sul bordo alto della sagoma (sotto il naso) fino a 1 sul bordo basso (sul labbro), colonna per colonna."""
    h, w = m.shape
    yy = np.arange(h)[:, None].astype(np.float32)
    ha = m.any(axis=0)
    top = np.where(ha, m.argmax(axis=0), 0).astype(np.float32)
    bot = np.where(ha, h - 1 - m[::-1].argmax(axis=0), 1).astype(np.float32)
    spess = np.maximum(bot - top, 1)
    t = np.clip((yy - top) / spess, 0, 1)
    f = 0.7 + 0.3 * (t * t * (3 - 2 * t))
    # sfuma anche fuori dalla sagoma (punte dei peli)
    f = np.where(yy > bot, 1.0, f)
    return np.array(Image.fromarray((f * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(SS * 3)),
                    dtype=np.float32) / 255


def disegna(id_, colore, fase, seed):
    rng = np.random.default_rng(seed)
    m = sagoma(id_)
    dx, dy = campo_direzioni(m)
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        raise SystemExit(f"{id_}: sagoma vuota")
    area = len(xs)
    peluria = id_ == "14_peluria"
    n_peli = int(area / (SS * SS) * (0.42 if not peluria else 0.9) * (0.45 + 0.55 * fase))
    lungo = SS * (9 + 15 * fase) * (0.5 if peluria else 1.0)

    alfa = Image.new("L", (G, G), 0)
    col = Image.new("RGB", (G, G), tuple(int(v * 0.8) for v in colore[0]))
    da, dc = ImageDraw.Draw(alfa), ImageDraw.Draw(col)
    scuro, chiaro = np.array(colore[0]), np.array(colore[1])
    idx = rng.integers(0, area, n_peli)
    for k in idx:
        x, y = float(xs[k]), float(ys[k])
        L = lungo * rng.uniform(0.6, 1.3)
        curva = rng.normal(0, 0.06)
        ang = math.atan2(dy[int(y), int(x)], dx[int(y), int(x)]) + rng.normal(0, 0.07)
        pts = [(x, y)]
        for _ in range(4):
            x += math.cos(ang) * L / 4
            y += math.sin(ang) * L / 4
            ang += curva
            pts.append((x, y))
        t = rng.random() ** 3   # quasi tutti scuri, qualche pelo più chiaro
        c = tuple(int(v) for v in scuro * (1 - t) + chiaro * t)
        a = int(rng.uniform(170, 245))
        w = int(SS * rng.uniform(0.35, 0.6)) or 1
        # radice più spessa, punta più sottile
        da.line(pts[:3], fill=a, width=w + 1)
        da.line(pts[2:], fill=int(a * 0.75), width=max(1, w - 1))
        dc.line(pts, fill=c, width=w + 1)

    # velo sotto i peli: densità alla radice, la pelle si intravede
    velo = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(SS * 4))
    velo = velo.point(lambda v: int(v * (0.7 + 0.3 * fase) * (0.5 if peluria else 1)))
    alfa = Image.fromarray(np.maximum(np.array(alfa), np.array(velo)))

    a = np.array(alfa, dtype=np.float32) / 255
    # più pieno nei toni medi (i peli sottili ridotti a 512 diventerebbero troppo trasparenti)
    alfa = Image.fromarray((255 * (a ** 0.5) * profondita(m)).astype(np.uint8))
    im = col.convert("RGBA")
    im.putalpha(alfa)
    return im.resize((LATO, LATO), Image.LANCZOS)


if __name__ == "__main__":
    nomi = {b["id"]: b["nome"] for b in json.loads((ROOT / "baffi.json").read_text(encoding="utf-8"))}
    elenco = []
    for nome_col, colore in COLORI.items():
        cartella = OUT / nome_col
        cartella.mkdir(parents=True, exist_ok=True)
        for i, id_ in enumerate(SCELTI):
            for f, fase in enumerate(FASI):
                im = disegna(id_, colore, fase, seed=1000 + i)
                im.save(cartella / f"{id_}_crescita_{f}.png", optimize=True)
            # l'ultima fase è il baffo completo
            (cartella / f"{id_}.png").write_bytes((cartella / f"{id_}_crescita_{len(FASI) - 1}.png").read_bytes())
            print(f"{nome_col:8s} {id_}")
    (OUT / "realistici.json").write_text(json.dumps(
        [{"id": i, "nome": nomi[i]} for i in SCELTI], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
