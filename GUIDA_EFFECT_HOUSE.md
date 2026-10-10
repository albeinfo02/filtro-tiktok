# Guida: effetto TikTok "CHE BAFFO SEI?" con Effect House

Guida semplice, passo passo, per costruire l'effetto della canzone **I BAFFI** (ALBE.x).

---

## 1. Si può ancora fare? Sì

Effect House (il programma di TikTok per creare effetti) è attivo e aggiornato.
L'ultima versione nelle note di rilascio è la **5.14, del 26 agosto 2026**.
Gli effetti si inviano in revisione direttamente da dentro il programma.

**Cosa ti serve**
- Un **Mac** (va bene il tuo) con Effect House installato: lo scarichi da `effecthouse.tiktok.com`.
- Il tuo **account TikTok** (@damnwhosalbe): ci accedi da dentro Effect House.
- L'**iPhone** con TikTok, per provare l'effetto dal vivo (anteprima mobile).

**Limiti tecnici** (dalla checklist ufficiale)
| Cosa | Limite | I nostri file |
|---|---|---|
| Peso totale dell'effetto | max 8 MB | ~3 MB (baffi + nomi) ✅ |
| Peso di ogni immagine | max 1 MB | max 92 KB ✅ |
| Risoluzione immagini | max 1024×1024 | 1024×1024 e 1024×256 ✅ |
| Icona | PNG 162×162 (zona sicura centrale 144×144) | `asset/icona/icona_162.png` ✅ |

**Tempi di revisione**: di solito entro **1 giorno lavorativo**, a volte 2–3 giorni.
Se ti chiedono modifiche le fai e lo rimandi. Puoi aggiornare un effetto pubblicato
fino a **5 volte nei primi 6 mesi**.

> ⚠️ I nomi dei menu di Effect House cambiano un po' da una versione all'altra.
> Se un nome qui sotto non torna, cerca la voce più simile: la logica resta la stessa.

---

## 2. I file pronti (cartella `asset/`)

| Cartella | Cosa c'è |
|---|---|
| `baffi_nero/` | 31 baffi, PNG trasparenti 1024×1024, **già allineati**: il punto sotto il naso è sempre nello stesso posto (x 512, y 300). Basta cambiare immagine e il baffo resta al posto giusto. |
| `baffi_bordo_bianco/` | Gli stessi baffi con un bordino bianco, per chi ha la barba o la pelle scura (il nero si vede comunque). **Consiglio di usare questi.** |
| `nomi_nero/`, `nomi_bordo_bianco/` | Il nome di ogni baffo, PNG 1024×256, tutti centrati uguali. |
| `icona/` | Icona dell'effetto (162×162 per Effect House, 1024 grande per altri usi). |
| `foglio_controllo.png` | Tutti i baffi su un naso e una bocca finti, per controllare a colpo d'occhio. |

I baffi **01–19** sono i tuoi disegni originali, ripuliti dalle macchioline e messi
alla stessa scala. I **20–31** sono nuovi, disegnati nello stesso stile:
gabbiano, detective, farfalla, camionista, cattivo dei cartoni, onda, scopa,
spaghetto, corna, nuvola, zigzag, col pennarello.
Se vuoi ridisegnarne qualcuno a mano, guarda il paragrafo 6.

---

## 3. Costruire l'effetto, passo passo

### 3.1 Nuovo progetto
1. Apri Effect House → **New Project** → progetto vuoto (Blank).
2. Trascina dentro **Assets** le cartelle `asset/baffi_bordo_bianco` e `asset/nomi_bordo_bianco`.
   Diventano **Textures**.

### 3.2 Attaccare il baffo alla faccia
Hai due possibilità. Comincia dalla **A**, che è più semplice.

**A) Head Tracker + immagine (consigliata)**
1. Nella **Hierarchy**: **+ → Face Effects / Tracking → Head Tracker** (o "Face Tracker").
2. Dentro l'Head Tracker aggiungi **+ → 2D → Image** (o uno "Screen Image / Plane"
   con material Unlit trasparente).
3. Come Texture scegli `01_manubrio`.
4. Sposta l'immagine sul labbro superiore guardando l'anteprima con la faccia di prova.
   Siccome **tutti i PNG sono già allineati**, lo fai **una volta sola** e vale per tutti i 31 baffi.
   - Il centro della tela (512, 512) sta un po' **sotto** il punto del naso (512, 300).
     Quindi sposta l'immagine verso il basso finché il punto sotto il naso
     coincide con lo spazio tra naso e labbro.
   - La larghezza giusta: il baffo "a manubrio" deve uscire un po' oltre gli angoli della bocca.
5. Prova a girare la testa nell'anteprima: il baffo deve seguirla.

**B) Face Mask / Face Sticker (si deforma con la bocca)**
Se nella tua versione c'è il componente **Face Mask** (texture sul viso), il baffo si piega
quando apri la bocca. In questo caso devi disegnare i baffi sul template UV del viso
di Effect House, quindi lo sconsiglio come primo tentativo.

### 3.3 La scritta del nome
1. Nella Hierarchy aggiungi **+ → 2D → Screen Image**, **non** dentro l'Head Tracker,
   così resta fissa sullo schermo.
2. Mettila nella parte bassa dello schermo, sopra la zona dei pulsanti di TikTok
   (circa al 75–80% dell'altezza).
3. Come Texture usa `01_manubrio` della cartella **nomi**.
4. (Facoltativo) Aggiungi un'altra Screen Image o un **Text** con scritto **"SEI:"**,
   da mostrare solo quando la roulette si ferma.

### 3.4 La roulette (Visual Scripting)
Apri il pannello **Visual Scripting** (o "Graph").

**Variabili** (pannello Variables):
- `indice`: Number, il baffo mostrato adesso;
- `fermo`: Boolean, vale `false` all'inizio;
- `intervallo`: Number, `0.1`, cioè 10 cambi al secondo.

**Logica**:

```
[Start] ───────────────► fermo = false, intervallo = 0.1
                          │
[Timer/Delay: intervallo] ┴──► se fermo == false:
                                  indice = Random(0 … 30)   (intero; 31 baffi)
                                  Baffo.texture = Lista_baffi[indice]
                                  Nome.texture  = Lista_nomi[indice]
                                  ripeti il Timer

[Dopo 3 secondi]  oppure  [Screen Tap] ──► RALLENTA:
      ripeti 8–9 volte:  intervallo = intervallo × 1.35   (0.10 → 0.13 → 0.18 … ~1 s)
      all'ultimo giro:   fermo = true
                         mostra "SEI:"  (Visible = true)
                         piccolo "pop" della scritta (Tween Scale 1 → 1.15 → 1)
```

**Come si fa in pratica con i nodi:**
1. **Lista delle immagini**: crea una variabile di tipo **Texture Array** (o "List of
   Texture") e trascinaci dentro i 31 baffi **in ordine**. Fai lo stesso per i 31 nomi.
   Così `indice` sceglie insieme il baffo e il suo nome.
2. **Numero casuale**: nodo **Random** (min 0, max 30) seguito da **Floor** (o "Round"),
   per avere un numero intero.
3. **Cambiare immagine**: nodo **Set Texture** / **Set Image Texture** sull'immagine
   del baffo e su quella del nome, con **Get Item / Array Get** (lista, `indice`).
4. **Ripetere**: nodo **Delay** collegato a sé stesso (loop), con durata = `intervallo`.
   Oppure un **Timer** con "Repeat".
5. **Fermare**: nodo **Screen Tap** + un **Delay** di 3 s dopo lo Start.
   Tutti e due vanno a un nodo **Gate / Do Once**, così il rallentamento parte una
   volta sola. Il rallentamento è un **For Loop** (8 giri) con un Delay che cresce,
   oppure 8 Delay in fila: 0.13, 0.18, 0.24, 0.33, 0.44, 0.60, 0.81, 1.1 s.
6. **Ripartire** (facoltativo): un altro Screen Tap quando `fermo == true` rimette
   `fermo = false` e `intervallo = 0.1` e riparte.

> 💡 **Il trucco del ritmo**: nel tuo pezzo (da 0:01.4) "tagliarli" arriva a un
> momento preciso. Misura con il cronometro dopo quanti secondi dall'inizio del suono
> arriva "tagliarli" (o il drop). Poi regola il "Delay 3 s" in modo che la roulette
> si **fermi proprio lì**: la durata del rallentamento è circa 3,8 s.
> Con l'anteprima web (paragrafo 5) puoi provarlo subito con la canzone vera.

### 3.5 Provare sull'iPhone
In Effect House premi **Preview on mobile / Send to TikTok** e inquadri il QR con
l'iPhone: l'effetto si apre su TikTok, solo per te. Controlla tre cose:
- che il baffo stia bene **con la bocca aperta e chiusa**;
- che si veda anche con **poca luce**;
- che il nome non finisca sotto i pulsanti di TikTok.

### 3.6 Icona, nome, invio
1. **Publish / Submit**.
2. **Nome effetto**: `CHE BAFFO SEI?`. Nella descrizione metti come usarlo, per esempio:
   "Scopri che baffo sei 👨🏻 tocca lo schermo per fermare la roulette. Suono: ALBE.x – I BAFFI".
3. **Icona**: `asset/icona/icona_162.png`.
4. **Video demo** (dice "facoltativo", ma **mettilo sempre**: senza video a volte lo
   rifiutano per "problema tecnico"): 10–15 secondi di te che usi l'effetto.
5. Invia. Arriva una notifica quando è approvato (di solito entro 1 giorno).

### 3.7 La canzone
Non importare un file mp3, perché la musica caricata da fuori viene rifiutata per il copyright.
Usa invece il pannello **Timeline → TikTok Sounds** e cerca "ALBE.x I BAFFI": è la libreria
ufficiale di TikTok, quindi il suono è già autorizzato e parte insieme all'effetto.
In più:
- pubblica **tu per primo** 3–4 video con l'effetto;
- nella descrizione dell'effetto scrivi "suono: ALBE.x – I BAFFI".

---

## 4. Attenzione alla revisione

- **"Fu Manchu"**: è il nome vero di quel tipo di baffo, ma viene da un personaggio
  nato come stereotipo razzista. Le regole di TikTok rifiutano gli effetti con
  stereotipi razziali, quindi la revisione potrebbe bloccarlo. Se vuoi stare tranquillo
  cambia il nome, per esempio "A FERRO LUNGO" o "DA MAGO CATTIVO", oppure togli il baffo 05.
- Niente loghi di altri marchi e niente persone famose riconoscibili nell'icona.
- Il testo nell'icona è meglio evitarlo, ed è per questo che l'icona ha solo "?" e il baffo.

---

## 5. Anteprima web (per provare tutto subito, senza Effect House)

Nella cartella `web/` c'è una pagina che fa **esattamente l'effetto** con la webcam:
roulette a 10 cambi al secondo, rallentamento, stop al tocco o dopo X secondi,
nome "SEI: …", bordino bianco attivabile, registrazione del video.
Puoi anche **caricare la canzone** e scegliere da che secondo parte (di default 1,4 s):
parte insieme alla roulette, così senti se lo stop cade su "tagliarli".

Per aprirla dal Mac, nel Terminale:
```
cd filtro-tiktok
python3 -m http.server 8000
```
Poi apri nel browser `http://localhost:8000/web/`.
Per aprirla dall'iPhone serve un indirizzo https: la soluzione più semplice è
GitHub Pages sul repository. Te lo posso configurare se vuoi.

Se Effect House un giorno non andasse più, questa pagina è già un piano B:
la gente registra il video sul sito e lo carica su TikTok con il tuo suono.

---

## 6. Aggiungere altri baffi (sempre di più)

1. Disegna il baffo a pennello su sfondo trasparente (PNG). Il lato del labbro va
   in alto, al centro. La scala non conta, la sistemi dopo.
2. Mettilo in `originali/baffi_png/32_nome_baffo.png` e il nome scritto a mano in
   `originali/nomi_png/32_nome_baffo.png`.
3. Aggiungi una riga in `baffi.json`:
   `{"id": "32_nome_baffo", "nome": "NOME BAFFO", "scala": 1.0, "disegno": "originale"}`
   (`scala` 1.0 = larghezza normale; 0.5 = piccolo; 1.3 = largo).
4. Lancia `python3 tools/prepara_asset.py`: rifà tutti i PNG allineati, i bordi bianchi
   e il foglio di controllo. L'anteprima web lo prende in automatico.
5. In Effect House aggiungi le 2 nuove texture in fondo alle due liste e porta il
   `Random` a max = (numero di baffi − 1).

Puoi anche ridisegnare a mano uno dei baffi nuovi (20–31). Mettilo in
`originali/baffi_png/` **con lo stesso nome**: ha la precedenza su quello generato.
