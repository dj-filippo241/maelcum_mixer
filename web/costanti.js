// Misure condivise fra pagina, motore e Worker del 5-way.
export const B = 128;      // campioni per blocco
export const LAT = 6;      // blocchi di ritardo del 5-way nei Worker (6 x 128 = 16 ms a 48 kHz)
export const ANELLO = 32;  // blocchi nell'anello condiviso
export const NPAR = 32;    // caselle per le manopole del 5-way

// Memoria condivisa fra motore e i due Worker del 5-way (lato L e lato R):
//   ctl[0] blocchi scritti dal motore, ctl[1] fatti dal lato L, ctl[2] fatti dal lato R,
//   ctl[3] versione delle manopole (la pagina la alza dopo ogni scrittura in par)
//   par   manopole del 5-way, nell'ordine di dsp/indice.json
//   ringIn DJ BUS, ringOut uscita del 5-way: per blocco B campioni L poi B campioni R
const CTL = 32, PAR = NPAR * 8, RING = ANELLO * 2 * B * 4;
export const SAB_BYTE = CTL + PAR + 2 * RING;
export function viste(sab) {
  return {
    ctl: new Int32Array(sab, 0, 8),
    par: new Float64Array(sab, CTL, NPAR),
    ringIn: new Float32Array(sab, CTL + PAR, ANELLO * 2 * B),
    ringOut: new Float32Array(sab, CTL + PAR + RING, ANELLO * 2 * B),
  };
}
