# CHE BAFFO SEI? — effetto TikTok per "I BAFFI" (ALBE.x)

Roulette di baffi disegnati a pennello sul labbro superiore. Si ferma su un baffo
a caso (dopo qualche secondo o con un tocco) e mostra "SEI: BAFFO A …".

- **[GUIDA_EFFECT_HOUSE.md](GUIDA_EFFECT_HOUSE.md)**: verifica di Effect House (ottobre 2026) e guida passo passo.
- `asset/`: file pronti per Effect House (31 baffi allineati, versione con bordino bianco, nomi, icona).
- `web/`: anteprima con webcam che fa lo stesso effetto (MediaPipe), con registrazione e canzone di prova.
- `baffi.json`: l'elenco dei baffi. Per aggiungerne uno basta una riga più il PNG (vedi guida §6).
- `originali/`: disegni originali (01–19) e baffi generati nello stesso stile (20–31).
- `tools/`: script che preparano gli asset (`prepara_asset.py`) e disegnano i baffi nuovi (`genera_baffi_nuovi.py`).

```
python3 tools/prepara_asset.py      # rigenera asset/ (serve Pillow + numpy)
python3 -m http.server 8000         # poi apri http://localhost:8000/web/
npm test                            # test della logica della roulette
```
