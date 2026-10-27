# RISULTATI — subsonica del phono a 18 Hz (dec. 138, 2026-10-27)

Netlist: `sim/cdj/phono-sub18.cir` (subsonica 18 Hz) e
`sim/cdj/phono-sub13-ref.cir` (stesso circuito con la subsonica a 13 Hz di
prima, riferimento). Base: `phono-sub100-fix.cir`, Cload 200 pF.

Modifica: Sallen-Key HP 2 poli Q 0,707 unity, C uguali 100n.
Rs1 86,6k → **61,9k**, Rs2 174k → **124k** (E96): f0 13,0 → **18,2 Hz**.

| Frequenza | 13 Hz (dB) | 18 Hz (dB) | Differenza |
|---|---|---|---|
| 10 Hz (warp) | 55,70 | 50,77 | **−4,94 dB** |
| 20 Hz | 60,45 | 58,89 | −1,56 dB |
| 30 Hz | 60,35 | 59,95 | −0,40 dB |
| 37 Hz (fondo VENU360) | 59,90 | 59,72 | −0,18 dB |
| 40 Hz | 59,68 | 59,54 | −0,13 dB |
| 50 Hz | 58,88 | 58,83 | −0,06 dB |
| 100 Hz e sopra | — | — | < 0,004 dB |

Fase della sola subsonica (nodo s2) a 40 Hz: 27,1° → 39,0° (+12°).

Lettura:
- Requisito della subsonica (phono-stage §1: −1 dB max a 30-40 Hz rispetto
  alla RIAA ideale): a 30 Hz l'errore passa da −0,24 a circa −0,64 dB. PASS.
- Warp a 10 Hz attenuato di 4,9 dB in più: il margine prima del clip dello
  stadio 2 sale di circa 1,8× (stima: ~25 mV → ~44 mV di warp puliti, da
  confermare con la `.tran` di `phono-riaa-overload.cir`).
- Costo: +12° di rotazione di fase a 40 Hz, solo sull'ingresso phono.
