# RR8 claim ledger

All results below have the scopes and hypotheses in the linked proofs.
Independent task review is disclosed mathematical review, not a formal
proof certificate. ABC remains open.

| Claim | Result | Evidence and review |
| --- | --- | --- |
| TG1 | All integer-translated norm tests on R x product Z_p recover exactly diagonal Z, without a common-zero axiom | [Proof](routes/translation_gluing/PROOF_NOTE.md), [isolated review](reviews/translation_gluing_review.md) |
| TG2 | Gaussian-translated tests over Q(i) recover diagonal Z[i] | Same proof and isolated review |
| TG3 | An explicit finite observer family recovers requested digits at supplied real budget B | Same proof and isolated review; exact unbounded precision is not claimed |
| FO1 | Each fixed finite translation profile, even with finitely many digit observers, misses a non-diagonal perturbation | [Proof](routes/finite_observers/PROOF_NOTE.md), [isolated review](reviews/finite_observers_review.md); entire norm objects may still be countably many |
| FS1 | Primitive S-supported positive additive triples biject S-unit solutions and are finite, with the stated ESS count | [Proof](routes/fixed_support/PROOF_NOTE.md), [source](routes/fixed_support/SOURCE_RECORD.md), [isolated review](routes/fixed_support/INDEPENDENT_REVIEW.md); external theorem imported |
| FS2 | The {2,3} sector consists of four triples up to swapping, seven ordered triples, maximal c=9 and stabilization modulo 24 | Same elementary proof and isolated review; no finite-search cutoff |
| SY1 | Known log c < K R^(1/3)(log R)^3 supplies an effective conductor budget | [Exact conversion and finite diagram](routes/fixed_support/EFFECTIVE_GLOBAL_BUDGET.md), same isolated review; source theorem imported, numerical K not instantiated |
| SY2 | At that budget, a two-object Set diagram with protected zero residue defect realizes all intended triples of radical <=T | Same exact conversion and review; bounded ordinary integer raw source is explicit |
| RP1 | Supported modulus M plus absolute defect <M forces exact addition | [Proof](routes/radical_precision/PROOF_NOTE.md), [isolated review](reviews/radical_precision_review.md); subsidiary consequence corrected to 0<a,b<=c |
| RP2 | For each N>=4, unbounded raw triples (4^u,9^v,25^w) with radical30 pass mod30^N but have c>a+b | Same universal CRT proof and isolated review; these are not ABC counterexamples |
| RP3 | Unrestricted residue-preserving sup-norm repair costs M ceil(abs(d/M)/3) | Same proof/review; positivity, primitivity and support need not survive correction |
| EH1 | B(T), maximal exact height at radical<=T, is finite, B(T)>T/4 for T>=4, and ABC iff log B(T)/log T tends to1 | [Proof](RADICAL_HEIGHT_ENVELOPE.md), [isolated review](reviews/radical_envelope_review.md); equivalence is not a proof of ABC |
| ABC | Every-epsilon sharp radical-height growth | Open |
| IUT | Actual source-specific numerical witness or disputed comparison | Open; no IUT theorem proved or disproved here |

The original positivity error and counterexample are retained in
[routine correction record](routes/radical_precision/REVIEW_FIX.md)
and its preserved original proof snapshot. No new Lean compilation or
load-bearing finite computation supports these claims. Historical novelty
was not asserted or searched.

