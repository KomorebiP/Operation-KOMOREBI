# Sources and normalization for the final push

Checked 26 September 2026. Primary-source verification for the Galois,
Chebotarev and filtered-module statements is recorded in
[arithmetic/NOTE.md](arithmetic/NOTE.md). The independent source checks for
Han's packet formula and the classical tau identities are in
[prior_audit/AUDIT.md](prior_audit/AUDIT.md). The polynomial-content theorem
uses the harmonic theta statement of the parent checkpoint, with its lattice
and character calculation reproduced in the new proof.

## Independent coefficient calculation

William Stein, *Modular Forms: A Computational Approach*, online chapter
[Modular Forms of Level 1](https://wstein.org/books/modform/modform/level_one.html).
The displayed text was read at Proposition 2.7, Definition 2.9 and equation
(3), Theorem 2.14, Corollary 2.15, and the weight-12 discussion preceding
Remark 2.36. This is an author-hosted primary exposition. No local source
copy was made and no historical novelty assessment is attached.

Stein normalizes E_k to have coefficient of q equal to 1. Our script uses
constant coefficient 1, denoted here F_k to avoid ambiguity:

F4=240 E4=1+240 sum sigma3(n)q^n,
F6=-504 E6=1-504 sum sigma5(n)q^n,
F8=480 E8=1+480 sum sigma7(n)q^n.

F4*F8-F6^2 is a weight-12 cusp form with first coefficient 1728. Since
S12 is one-dimensional and normalized Delta has first coefficient 1,

    Delta=(F4*F8-F6^2)/1728.

Consequently the exact coefficient formula implemented independently is

    1728*tau(n) = 240*sigma3(n)+480*sigma7(n)+1008*sigma5(n)
                  +115200*sum_(k=1)^(n-1) sigma3(k)*sigma7(n-k)
                  -254016*sum_(k=1)^(n-1) sigma5(k)*sigma5(n-k).

The code function tau_eisenstein calls the constant-normalized forms E4,E6,E8
in its docstring; this dictionary fixes that naming difference. The source
normalization was checked explicitly. The displayed formula and dimensional
argument are sufficient for the independent coefficient check.

## Search scope and unused retrievals

Discovery searched for tau congruences modulo 25/125, possible valuation
formulas involving p+1, and level-one Eisenstein identities. The resulting
valuation equalities were treated as proposed shortcuts and tested directly,
not attributed to any author. No literature claim that those false
equalities were established is made.

The MPIM preprint *Sums of two squares and the tau-function: Ramanujan's
trail* (2024-22) was inspected for context but supplies no necessary new
proof leaf. A Rutgers-hosted candidate PDF lee14b.pdf failed retrieval and
was not used. Search failure is neither a theorem nor a novelty statement.

All statements claimed as proofs use the detailed checked sources or the
internal proofs, not discovery snippets. None of the project's new-to-project
formulations is claimed to be a previously unknown theorem.
