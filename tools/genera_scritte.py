"""Scritte dell'effetto realistico ("CHE BAFFO SEI?", "SEI:", nomi) senza bordo da adesivo.

Uso:  python3 tools/genera_scritte.py
Scrive asset/scritte/<stile>/ con  titolo.png, sei.png, nome_00.png ... (ordine di realistici.json)
Stili:
  bianco  lettere bianche a pennello con un'ombra morbida (stile scritte di TikTok)
  nero    lettere nere a pennello con un alone chiaro sfumato (si legge anche su sfondi scuri)
I nomi usano le scritte a mano originali quando ci sono.
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from genera_baffi_nuovi import disegna_nome  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "asset" / "scritte"
SRC_NOMI = [ROOT / "originali" / "nomi_png", ROOT / "originali" / "nomi_generati"]


def alfa_testo(im):
    a = im.getchannel("A")
    return a.crop(a.getbbox())


def stile(alfa, nome_stile, W, H, pad=0.08):
    """Mette la scritta (solo canale alfa) su una tela W x H nello stile scelto."""
    s = min(W * (1 - 2 * pad) / alfa.width, H * (1 - 2 * pad) / alfa.height)
    alfa = alfa.resize((max(1, round(alfa.width * s)), max(1, round(alfa.height * s))), Image.LANCZOS)
    a = Image.new("L", (W, H), 0)
    a.paste(alfa, ((W - alfa.width) // 2, (H - alfa.height) // 2))
    r = max(2, H // 40)
    if nome_stile == "bianco":
        ombra = ImageChops.offset(a, r // 2, r).filter(ImageFilter.GaussianBlur(r * 1.6))
        ombra = ombra.point(lambda v: int(v * 0.75))
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        out.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), (0, 0, 0)).split(), ombra)))
        out.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), (255, 255, 255)).split(), a)))
    else:
        alone = a.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(r * 2.2))
        alone = alone.point(lambda v: int(min(255, v * 1.4) * 0.7))
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        out.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), (255, 255, 255)).split(), alone)))
        out.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), (17, 17, 17)).split(), a)))
    return out


def nome_sorgente(id_):
    for c in SRC_NOMI:
        if (c / f"{id_}.png").exists():
            return Image.open(c / f"{id_}.png").convert("RGBA")
    raise SystemExit(f"manca il nome di {id_}")


if __name__ == "__main__":
    elenco = json.loads((ROOT / "asset" / "realistici" / "realistici.json").read_text(encoding="utf-8"))
    titolo = alfa_testo(disegna_nome("CHE BAFFO SEI?", 7, passo=150))
    sei = alfa_testo(disegna_nome("SEI:", 8, passo=150))
    for st in ("bianco", "nero"):
        d = OUT / st
        d.mkdir(parents=True, exist_ok=True)
        stile(titolo, st, 1024, 192).save(d / "titolo.png", optimize=True)
        stile(sei, st, 512, 192).save(d / "sei.png", optimize=True)
        for i, b in enumerate(elenco):
            stile(alfa_testo(nome_sorgente(b["id"])), st, 1024, 256).save(d / f"nome_{i:02d}.png", optimize=True)
        print("stile", st, "ok")
