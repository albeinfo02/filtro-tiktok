// Logica della roulette "Che baffo sei?" (senza grafica: testabile con node --test).
//
// Fasi:  "pronto" -> "gira" (veloce, ~10 cambi al secondo)
//        -> "rallenta" (ogni cambio dura di più) -> "fermo" (baffo scelto).
// Il passaggio a "rallenta" avviene dopo `durataGiroMs` oppure al tocco.
// Un tocco quando è "fermo" fa ripartire tutto.

export function creaRoulette({
  quanti,
  durataGiroMs = 3000,
  intervalloVeloceMs = 100,
  passiRallentamento = 9,
  crescita = 1.35,
  rng = Math.random,
} = {}) {
  if (!(quanti >= 2)) throw new Error("servono almeno 2 baffi");

  let fase = "pronto";
  let indice = 0;
  let inizioGiro = 0;
  let prossimoCambio = 0;
  let intervallo = intervalloVeloceMs;
  let passiRimasti = 0;
  let scelto = -1;

  // un indice casuale diverso da quello attuale (niente "doppioni" visibili)
  const altro = () => {
    const n = Math.floor(rng() * (quanti - 1));
    return n >= indice ? n + 1 : n;
  };

  function avvia(ora) {
    fase = "gira";
    inizioGiro = ora;
    intervallo = intervalloVeloceMs;
    prossimoCambio = ora + intervallo;
    indice = altro();
    scelto = -1;
  }

  function rallenta(ora) {
    fase = "rallenta";
    passiRimasti = passiRallentamento;
    scelto = Math.floor(rng() * quanti);
    prossimoCambio = Math.min(prossimoCambio, ora + intervallo);
  }

  function aggiorna(ora) {
    if (fase === "gira" && ora - inizioGiro >= durataGiroMs) rallenta(ora);
    while ((fase === "gira" || fase === "rallenta") && ora >= prossimoCambio) {
      if (fase === "rallenta") {
        passiRimasti--;
        if (passiRimasti <= 0) {
          indice = scelto;
          fase = "fermo";
          break;
        }
        intervallo *= crescita;
        // all'ultimo passo prima dello stop evita di mostrare già il vincitore
        indice = altro();
        if (passiRimasti === 1 && indice === scelto) indice = (scelto + 1) % quanti;
      } else {
        indice = altro();
      }
      prossimoCambio += intervallo;
    }
    return stato();
  }

  function tocca(ora) {
    if (fase === "pronto" || fase === "fermo") avvia(ora);
    else if (fase === "gira") rallenta(ora);
    return stato();
  }

  function stato() {
    return { fase, indice, scelto };
  }

  return { avvia, aggiorna, tocca, stato };
}
