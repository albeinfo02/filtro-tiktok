import { test } from "node:test";
import assert from "node:assert/strict";
import { creaRoulette } from "../web/roulette.js";

function simula(r, daMs, aMs, passo = 16) {
  const visti = [];
  for (let t = daMs; t <= aMs; t += passo) visti.push({ t, ...r.aggiorna(t) });
  return visti;
}

test("gira veloce (~10 al secondo) senza ripetere due volte di fila", () => {
  const r = creaRoulette({ quanti: 19, durataGiroMs: 10_000 });
  r.avvia(0);
  const v = simula(r, 0, 2000);
  const cambi = v.filter((s, i) => i && s.indice !== v[i - 1].indice).length;
  assert.ok(cambi >= 18 && cambi <= 21, `cambi in 2s: ${cambi}`);
  for (let i = 1; i < v.length; i++) assert.equal(v[i].fase, "gira");
});

test("dopo la durata rallenta e si ferma sul baffo scelto", () => {
  const r = creaRoulette({ quanti: 19, durataGiroMs: 3000 });
  r.avvia(0);
  const v = simula(r, 0, 15_000);
  const fine = v.at(-1);
  assert.equal(fine.fase, "fermo");
  assert.equal(fine.indice, fine.scelto);
  const primoFermo = v.find((s) => s.fase === "fermo");
  assert.ok(primoFermo.t > 3000 && primoFermo.t < 8000, `fermo a ${primoFermo.t}ms`);
  // una volta fermo non cambia più
  assert.ok(v.filter((s) => s.t >= primoFermo.t).every((s) => s.indice === fine.indice));
});

test("il tocco durante il giro fa partire subito il rallentamento", () => {
  const r = creaRoulette({ quanti: 19, durataGiroMs: 60_000 });
  r.avvia(0);
  simula(r, 0, 500);
  assert.equal(r.tocca(500).fase, "rallenta");
  const v = simula(r, 500, 8000);
  assert.equal(v.at(-1).fase, "fermo");
});

test("un tocco a roulette ferma la fa ripartire", () => {
  const r = creaRoulette({ quanti: 5, durataGiroMs: 100 });
  r.avvia(0);
  simula(r, 0, 10_000);
  assert.equal(r.stato().fase, "fermo");
  assert.equal(r.tocca(10_001).fase, "gira");
});

test("tutti i baffi possono uscire", () => {
  const usciti = new Set();
  for (let k = 0; k < 400; k++) {
    const r = creaRoulette({ quanti: 19, durataGiroMs: 200 });
    r.avvia(0);
    simula(r, 0, 6000, 50);
    usciti.add(r.stato().indice);
  }
  assert.equal(usciti.size, 19);
});
