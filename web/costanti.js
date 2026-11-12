// Misure condivise fra pagina, motore e Worker del 5-way.
export const B = 128;      // campioni per blocco
export const LAT = 6;      // blocchi di ritardo del 5-way nel Worker (6 x 128 = 16 ms a 48 kHz)
export const ANELLO = 32;  // blocchi nell'anello condiviso
