# Block 13 validation record

## Exact bridge-synthesis verifier

Command:

```powershell
python .\verify_block13_bridge_synthesis.py
```

Recorded result:

```json
{
  "passed": true,
  "checks": 154209,
  "failures": 0,
  "periodic_objects": 583
}
```

The suite checks the frozen bridge matrix, exact unit-periodic replay, cross-chart invariant comparison, triangle coherence, the fixed-Euler-basis and prime-uniform multiplicative overlap, directional information-loss records, completeness gates, and finite Cech holonomy models.

## Exact global-invariant verifier

Command:

```powershell
python .\verify_block13_global_invariants.py
```

Recorded result:

```json
{
  "bridges": 24,
  "checks": 119453,
  "clusters": 7,
  "failures": 0,
  "passed": true
}
```

The suite checks weighted q-ary coefficient formulas, marked fixed-point identities, selected algebraic and first-order holonomic charts, packet synthesis and address-carry equations, exact parameter recovery, comparison paths, and component-tag separation.

## Combined count ledger

| Record | Exact assertions | Failures |
|---|---:|---:|
| Bridge-synthesis suite | 154,209 | 0 |
| Weighted q-ary and federated-invariant suite | 119,453 | 0 |
| All Block 13 assertions executed | 273,662 | 0 |
| Regression and authentication assertions already counted in Blocks 03-12 | 39,846 | 0 |
| **New nonduplicative Block 13 assertions** | **233,816** | **0** |
| **Cumulative unique block assertions** | **2,272,676** | **0** |
| Cumulative executed assertions including Block 13 replay | 2,312,522 | 0 |

The assertion totals are implementation and regression records. They are not counts of independent theorems.

## LaTeX and PDF validation

- final PDF pages: 211
- page size: US letter, with declared landscape tables
- outline entries: 173
- unresolved references: 0
- undefined control sequences: 0
- multiply defined labels: 0
- overfull boxes: 0
- underfull boxes: 0
- fonts embedded: yes
- encryption: none
- interactive forms or JavaScript: none
- final pages rendered and inspected: 211
- source manifest: 265 entries passed
- source ZIP integrity: PASS
- clean source replay: PASS
- same-renderer replay comparison: 211 of 211 pages pixel-identical at 96 dpi

The final PDF was also preflighted successfully with PyMuPDF and contains no form fields or attachments.

## Replay note

The normal replay authenticates frozen Blocks 03-10, recomputes Blocks 11-13, regenerates the recent figures and LaTeX tables, and compiles the manuscript. A clean replay from an isolated source copy completed successfully. The rebuilt PDF can differ byte-for-byte because TeX records build time metadata, so the publication comparison is made at rendered-page level.

## Claim boundary

The exact computation supports the declared finite bridge matrix, the five connected normalized components, the printed comparison identities, the marked Fuss-Catalan overlap, the selected directional loss records, and the finite invariant-descent theorem. It is not evidence for an unrestricted equivalence among the broad strata or for independent peer validation of the manuscript-level proofs.
