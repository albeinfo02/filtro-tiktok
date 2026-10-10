// Anteprima web dell'effetto "Che baffo sei?".
// Tracciamento del viso con MediaPipe Face Landmarker, disegno su canvas 9:16.
import { FaceLandmarker, FilesetResolver } from
  "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/vision_bundle.mjs";
import { creaRoulette } from "./roulette.js";

// l'elenco dei baffi sta in baffi.json (lo stesso usato da tools/prepara_asset.py)
let BAFFI = [];
// Devono coincidere con tools/prepara_asset.py
const TELA = 1024, ANCORA = { x: 512, y: 300 }, LARGHEZZA_BASE = 600;
// quanto è largo un baffo "standard" rispetto alla bocca
const BAFFO_SU_BOCCA = 1.35;

// Punti del Face Mesh (468 punti) usati
const P = { sottoNaso: 2, labbroSup: 0, angoloSx: 61, angoloDx: 291, occhioSx: 33, occhioDx: 263 };

const $ = (id) => document.getElementById(id);
const tela = $("tela"), ctx = tela.getContext("2d");
const W = tela.width, H = tela.height;
const video = document.createElement("video");
video.playsInline = true; video.muted = true;

const stato = (t) => { $("stato").textContent = t; };

function carica(src) {
  return new Promise((ok, ko) => {
    const im = new Image();
    im.onload = () => ok(im);
    im.onerror = () => ko(new Error("immagine mancante: " + src));
    im.src = src;
  });
}

const immagini = {};
async function caricaImmagini() {
  BAFFI = (await (await fetch("../baffi.json")).json()).map((b) => b.id);
  const gruppi = ["baffi_nero", "baffi_bordo_bianco", "nomi_bordo_bianco"];
  await Promise.all(gruppi.map(async (g) => {
    immagini[g] = await Promise.all(BAFFI.map((b) => carica(`../asset/${g}/${b}.png`)));
  }));
}

let landmarker = null;
async function caricaTracker() {
  const fileset = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm");
  landmarker = await FaceLandmarker.createFromOptions(fileset, {
    baseOptions: {
      modelAssetPath: "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
      delegate: "CPU",
    },
    runningMode: "VIDEO",
    numFaces: 1,
  });
}

let roulette = null;
function nuovaRoulette() {
  roulette = creaRoulette({ quanti: BAFFI.length, durataGiroMs: Number($("optDurata").value) * 1000 });
}

// --- geometria: il video è "cover" su 9:16 e specchiato come una camera frontale
let ritaglio = { sx: 0, sy: 0, sw: 1, sh: 1 };
function calcolaRitaglio() {
  const vw = video.videoWidth, vh = video.videoHeight;
  const r = W / H;
  if (vw / vh > r) ritaglio = { sw: vh * r, sh: vh, sx: (vw - vh * r) / 2, sy: 0 };
  else ritaglio = { sw: vw, sh: vw / r, sx: 0, sy: (vh - vw / r) / 2 };
}
function inTela(p) {
  const x = (p.x * video.videoWidth - ritaglio.sx) / ritaglio.sw * W;
  const y = (p.y * video.videoHeight - ritaglio.sy) / ritaglio.sh * H;
  return { x: W - x, y }; // specchio
}

// posa smussata per evitare tremolii
let posa = null;
function aggiornaPosa(lm) {
  const q = (i) => inTela(lm[i]);
  const naso = q(P.sottoNaso), labbro = q(P.labbroSup);
  const a = q(P.angoloSx), b = q(P.angoloDx), oa = q(P.occhioSx), ob = q(P.occhioDx);
  const nuova = {
    x: naso.x + (labbro.x - naso.x) * 0.25,
    y: naso.y + (labbro.y - naso.y) * 0.25,
    ang: Math.atan2(ob.y - oa.y, ob.x - oa.x),
    bocca: Math.hypot(b.x - a.x, b.y - a.y),
  };
  // con lo specchio l'ordine degli occhi si inverte: normalizza l'angolo
  if (nuova.ang > Math.PI / 2) nuova.ang -= Math.PI;
  if (nuova.ang < -Math.PI / 2) nuova.ang += Math.PI;
  if (!posa) { posa = nuova; return; }
  const k = 0.5;
  for (const c of Object.keys(nuova)) posa[c] += (nuova[c] - posa[c]) * k;
}

function disegnaBaffo(img) {
  const s = (posa.bocca * BAFFO_SU_BOCCA) / LARGHEZZA_BASE;
  ctx.save();
  ctx.translate(posa.x, posa.y);
  ctx.rotate(posa.ang);
  ctx.scale(s, s);
  ctx.drawImage(img, -ANCORA.x, -ANCORA.y, TELA, TELA);
  ctx.restore();
}

function scritta(testo, y, size) {
  ctx.save();
  ctx.font = `900 ${size}px system-ui, -apple-system, sans-serif`;
  ctx.textAlign = "center"; ctx.textBaseline = "middle";
  ctx.lineWidth = size / 5; ctx.lineJoin = "round"; ctx.strokeStyle = "#fff";
  ctx.strokeText(testo, W / 2, y);
  ctx.fillStyle = "#111"; ctx.fillText(testo, W / 2, y);
  ctx.restore();
}

function disegnaNome(img, fermo) {
  const nw = W * 0.86, nh = nw / 4;
  const y = H * 0.80;
  if (fermo) {
    const pulsa = 1 + 0.04 * Math.sin(performance.now() / 120);
    scritta("SEI:", y - nh * 0.55, 64);
    ctx.save();
    ctx.translate(W / 2, y + nh * 0.25);
    ctx.scale(pulsa, pulsa);
    ctx.drawImage(img, -nw / 2, -nh / 2, nw, nh);
    ctx.restore();
  } else {
    ctx.drawImage(img, (W - nw) / 2, y - nh / 2 + nh * 0.25, nw, nh);
  }
}

function disegnaPunti(lm) {
  ctx.fillStyle = "#0f0";
  for (const i of Object.values(P)) {
    const p = inTela(lm[i]);
    ctx.fillRect(p.x - 4, p.y - 4, 8, 8);
  }
}

let ultimoTs = -1, ultimiPunti = null, perso = 0;
function ciclo() {
  requestAnimationFrame(ciclo);
  if (video.readyState < 2) return;
  const ora = performance.now();

  ctx.save();
  ctx.translate(W, 0); ctx.scale(-1, 1);
  ctx.drawImage(video, ritaglio.sx, ritaglio.sy, ritaglio.sw, ritaglio.sh, 0, 0, W, H);
  ctx.restore();

  if (landmarker && video.currentTime !== ultimoTs) {
    ultimoTs = video.currentTime;
    const res = landmarker.detectForVideo(video, ora);
    if (res.faceLandmarks.length) { ultimiPunti = res.faceLandmarks[0]; aggiornaPosa(ultimiPunti); perso = 0; }
    else if (++perso > 10) { ultimiPunti = null; posa = null; }
  }

  const st = roulette.aggiorna(ora);
  const bordo = $("optBordo").checked;
  if (posa) {
    if (st.fase !== "pronto") disegnaBaffo(immagini[bordo ? "baffi_bordo_bianco" : "baffi_nero"][st.indice]);
    if ($("optDebug").checked && ultimiPunti) disegnaPunti(ultimiPunti);
  } else {
    scritta("Inquadra la faccia", H * 0.12, 54);
  }
  if (st.fase === "pronto") scritta("TOCCA PER GIRARE", H * 0.86, 56);
  else disegnaNome(immagini.nomi_bordo_bianco[st.indice], st.fase === "fermo"); // sempre leggibile
  scritta("CHE BAFFO SEI?", H * 0.06, 50);

  if (st.fase !== faseAudio) gestisciAudio(st.fase);
}

// --- canzone (opzionale): parte quando gira la roulette, per provare i tempi
const audioEl = new Audio();
let audioCtx = null, audioDest = null, faseAudio = "pronto";
$("fileAudio").addEventListener("change", (e) => {
  const f = e.target.files[0];
  if (!f) return;
  audioEl.src = URL.createObjectURL(f);
  if (!audioCtx) {
    audioCtx = new AudioContext();
    const sorgente = audioCtx.createMediaElementSource(audioEl);
    audioDest = audioCtx.createMediaStreamDestination();
    sorgente.connect(audioCtx.destination);
    sorgente.connect(audioDest);
  }
  stato("Canzone caricata: parte quando giri la roulette.");
});
function gestisciAudio(fase) {
  if (fase === "gira" && faseAudio !== "rallenta" && audioEl.src) {
    audioCtx.resume();
    audioEl.currentTime = Number($("optOffset").value) || 0;
    audioEl.play();
  }
  faseAudio = fase;
}

// --- registrazione del canvas (video 9:16, con la canzone se caricata)
let recorder = null, pezzi = [];
function tipoVideo() {
  for (const t of ["video/mp4;codecs=avc1", "video/mp4", "video/webm;codecs=vp9", "video/webm"])
    if (window.MediaRecorder && MediaRecorder.isTypeSupported(t)) return t;
  return "";
}
$("btnRec").addEventListener("click", () => {
  if (recorder) { recorder.stop(); return; }
  const stream = tela.captureStream(30);
  if (audioDest) audioDest.stream.getAudioTracks().forEach((t) => stream.addTrack(t));
  const tipo = tipoVideo();
  recorder = new MediaRecorder(stream, tipo ? { mimeType: tipo } : undefined);
  pezzi = [];
  recorder.ondataavailable = (e) => e.data.size && pezzi.push(e.data);
  recorder.onstop = () => {
    const tipo = recorder.mimeType.split(";")[0];
    const ext = tipo.includes("mp4") ? "mp4" : "webm";
    ultimoVideo = new File(pezzi, `che_baffo_sei.${ext}`, { type: tipo });
    $("btnCondividi").classList.remove("nascosto");
    stato("Video pronto! Tocca \"Condividi\" per mandarlo su TikTok o salvarlo.");
    recorder = null;
    $("btnRec").textContent = "● Registra"; $("btnRec").classList.remove("rec");
  };
  recorder.start();
  $("btnRec").textContent = "■ Stop"; $("btnRec").classList.add("rec");
});

// condividi (iPhone: foglio di condivisione -> TikTok / Salva video), altrimenti scarica
let ultimoVideo = null;
$("btnCondividi").addEventListener("click", async () => {
  if (!ultimoVideo) return;
  if (navigator.canShare && navigator.canShare({ files: [ultimoVideo] })) {
    try {
      await navigator.share({ files: [ultimoVideo], text: "Che baffo sei? 🥸 Suono: ALBE.x – I BAFFI" });
      return;
    } catch (e) {
      if (e.name === "AbortError") return;
    }
  }
  const a = document.createElement("a");
  a.href = URL.createObjectURL(ultimoVideo);
  a.download = ultimoVideo.name;
  a.click();
});

function tocco() {
  if (audioCtx) audioCtx.resume();
  if (roulette.stato().fase === "fermo") nuovaRoulette();
  roulette.tocca(performance.now());
}
tela.addEventListener("pointerdown", tocco);
$("btnGira").addEventListener("click", tocco);
$("optDurata").addEventListener("change", () => { if (roulette.stato().fase !== "gira") nuovaRoulette(); });

$("btnAvvia").addEventListener("click", async () => {
  $("btnAvvia").disabled = true;
  try {
    stato("Carico i baffi…");
    await caricaImmagini();
    stato("Apro la fotocamera…");
    video.srcObject = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false,
    });
    await video.play();
    calcolaRitaglio();
    video.addEventListener("resize", calcolaRitaglio);
    nuovaRoulette();
    $("avvio").classList.add("nascosto");
    $("comandi").classList.remove("nascosto");
    // le opzioni di prova si vedono solo aprendo la pagina con ?prova
    if (new URLSearchParams(location.search).has("prova")) $("opzioni").classList.remove("nascosto");
    else $("optBordo").checked = true;
    requestAnimationFrame(ciclo);
    stato("Carico il riconoscimento del viso…");
    await caricaTracker();
    stato("Pronto! Tocca lo schermo per girare la roulette.");
  } catch (err) {
    console.error(err);
    stato("Errore: " + err.message);
    $("btnAvvia").disabled = false;
  }
});
