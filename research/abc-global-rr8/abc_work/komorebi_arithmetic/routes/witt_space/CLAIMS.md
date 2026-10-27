# Local arithmetic claims and their boundaries

This route starts from the current Komorebi Space definitions of a view
functor, protected partial section and compatibility differential, together
with Block03's local Teichmuller carry formulas. PROOF_NOTE.md constructs the
new incidence diagrams and proves the following statements.

| ID | Exact result | Scope |
| --- | --- | --- |
| W1 | t_N:k->R_N is the unique normalized multiplicative residue section, and its reductions commute | Every prime p and N>=1; t_0 is only the zero-tail notation |
| W2 | C_N takes values in R_(N-1), is a normalized symmetric cocycle, and reduces naturally | All primes and precisions; C_1 is zero |
| W3 | The protected carry quotient injects into the actual Komorebi protected-obstruction quotient for the declared finite additive diagram | The raw graph, fibers, restrictions and protected seed are fixed explicitly |
| W4 | That additive extension problem is empty at N>=2, while the carry-and-multiplication Set-valued diagram has one exact normalized realization | The nonzero carry is retained; multiplication corrections are not treated as an additive subgroup |
| W5 | Both operation tables and obstruction classes form coherent precision towers | Naturality is proved for the actual finite diagrams and quotient maps |
| W6 | Teichmuller digit coordinates k^N reconstruct every element of R_N, and their inverse-limit ring is Z_p | Local p-adic arithmetic, with explicit addition and multiplication recursions |
| W7 | Uniform radical-controlled archimedean height cost | Open; neither local existence nor an inverse limit proves it |

W1 and the carry formulas have classical arithmetic content already present
in the predecessor. This checkpoint supplies the actual finite view-system
construction, its protected obstruction injection and the precision-natural
realization theorem. No priority claim over classical Teichmuller or Witt
arithmetic is made.

No new Lean execution or finite mathematical experiment is asserted. Earlier
Block03 receipts have a different scope and do not verify these new diagrams.
The focused independent review records the exact raw proof revision it checks.
