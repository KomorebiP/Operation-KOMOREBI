# Komorebi Cross-Radix Rigidity Lean v0.5.0

Durable Lean checkpoint closing the physical Reynolds/DFT/affine-decoder/lcm-intersection layer above certified v0.4.0.

## New checked results

- exact 0/1 Fourier width masks on `ZMod T`;
- DFT-conjugated Reynolds projectors with idempotence and commutation;
- exact lcm composition and range-intersection laws;
- finite-family lcm product/intersection laws;
- literal cyclic subgroup Reynolds averaging and proof of equality with the DFT projector;
- exact character-annihilator and finite character-sum formulas;
- raw positive-radix reduction through `gcd(T,m)`, including two-radix and finite-list lcm laws;
- reversible affine polynomial substitution for positive radix;
- explicit projector-factorized affine decoder satisfying `AB=P`, `ABA=A`, `BAB=B`;
- DFT primitive shells agreeing with the persisted divisor/Möbius shells and pairwise orthogonal as operators.

## Verification

The six new substantive modules and the v0.5 axiom-audit module were recompiled from a separate clean Lake root with the pinned package cache and `-DwarningAsError=true`. The four load-bearing v0.4 dependency modules used by this layer were also recompiled there. The final placeholder scan finds no `sorry`, `admit`, or custom `axiom` declaration. Representative `#print axioms` outputs contain only `propext`, `Classical.choice`, and `Quot.sound`.

See `AUDIT.json`, `logs/STRICT_COMPILE_ALL.log`, and `logs/CrossRadixV05AxiomAudit.log`.

## Boundaries

Bell generalized Cobham remains explicitly external. The old naive base-independent integral normal form is still false and is not revived here. The affine decoder applies to the explicit saved projector-factorized normal form. The exact rank/nullity law is **not** part of v0.5.0 and remains the next proof target.
