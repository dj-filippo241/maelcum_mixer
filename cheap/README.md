# CHEAP — versione economica del maelcum mixer

Data di nascita: 2026-10-22 (richiesta di Filippo, dopo il budget di
`docs/09-budget.md`: 6.500-13.000 € IVA inclusa per il setup completo).

Progetto parallelo. Obiettivo: lo stesso mixer, con il costo più basso che
Filippo accetta. Il progetto principale (`docs/`, `sim/`, `SPECIFICA.md`)
NON si modifica da qui: CHEAP legge e copia, non scrive fuori da `cheap/`.

## Regole

1. Le regole del `CLAUDE.md` del progetto valgono anche qui (metodo,
   simulazioni, [BLOCCATO]/[PROVVISORIO]/[APERTO]/[SUPERATO]).
2. Ogni risparmio è un'opzione finché Filippo non la sceglie: suono,
   pannello e moduli restano suoi.
3. Le scelte CHEAP stanno in `cheap/01-decisioni-cheap.md`, numerate C1,
   C2… (non entrano nelle 130 decisioni del progetto principale).
4. Simulazioni CHEAP in `cheap/sim/`, con le librerie condivise di
   `sim/lib/` (`.include ../../sim/lib/...`).
5. Il budget CHEAP si calcola dalle stesse quantità del budget principale,
   con le opzioni scelte applicate.

## File

```
cheap/README.md                questo file
cheap/00-opzioni.md            le leve di risparmio, con risparmio e perdita
cheap/01-decisioni-cheap.md    le scelte di Filippo
```
