# Stato del lavoro — effetto "CHE BAFFO SEI?" (ALBE.x – I BAFFI)

Riassunto per continuare il lavoro in una sessione sul Mac (con controllo del computer).

## Cosa c'è già
- **Effetto disegnato** (prima versione): asset in `per_effect_house/`, guida in `GUIDA_EFFECT_HOUSE.md`.
- **Sito web pubblico** con la stessa roulette: https://albeinfo02.github.io/filtro-tiktok/
  (`?realistico` per i baffi veri). Si pubblica da solo a ogni push su questo branch.
- **Effetto realistico** (quello su cui si lavora ora), progetto Effect House "chebaffo sei"
  aperto sul Mac:
  - Hierarchy: Face Binding → Head → **Baffo** (Image, Blend Mode Multiply, opacità 0.9),
    **GameManager** (script APJS `GameManager`: campi `baffi: Texture[]`, `nomi: Texture[]`,
    `durataGiro`, `intervalloVeloce`, `passiRallentamento`, `crescita`, `baffoImage: Image`,
    `nomeImage: Image`, `nomeTransform: ScreenTransform`, `sei: SceneObject`), Timeline con
    TikTok Sounds "ALBE.x I BAFFI", 2D Camera → Nome, Sei, Titolo.
  - Liste del GameManager: 17 baffi `baffo_00..16` e 17 nomi `nome_00..16` (ordine in
    `per_effect_house_realistico/ELENCO.txt`).
  - Titolo e "SEI:" sostituiti con lo stile bianco a pennello (`scritte_bianco.zip`);
    i nomi li sta ridisegnando Alberto a mano.

## Da fare (in ordine)
1. **Face Sticker al posto dell'immagine** "Baffo", perché il baffo si pieghi con le labbra:
   creare un Face Sticker "BaffoSticker" (texture `baffo_00`, Multiply, opacità ~0.85,
   tra naso e labbro) e modificare lo script GameManager in modo che cambi la texture dello
   sticker invece di `baffoImage`; poi nascondere "Baffo".
2. **Baffi v2** (meno neri, radi sotto il naso): `baffi_realistici_v2.zip` → per ogni
   `baffo_..` negli Assets "Replace asset" con il file con lo stesso nome.
3. Posizioni: Sei Position Y ≈ -120, Nome Position Y ≈ -215 (il nome sopra il bottone rosso).
4. Facoltativo: crescita del baffo con le texture `ombra_..` (ora inutilizzate: si possono cancellare).
5. Prova con "Preview in TikTok", video demo 10–15 s, Create icon (`icona_162.png`), Submit:
   nome "CHE BAFFO SEI?", descrizione "Che baffo ti cresce? 🥸 Tocca lo schermo per fermare
   la roulette! Suono: ALBE.x – I BAFFI". Login TikTok e invio finale li conferma Alberto.

## Rigenerare gli asset
`python3 tools/genera_baffi_realistici.py` (baffi veri), `python3 tools/genera_scritte.py`
(scritte), `python3 tools/prepara_asset.py` (baffi disegnati). Rispondere ad Alberto in
italiano, in modo semplice.
