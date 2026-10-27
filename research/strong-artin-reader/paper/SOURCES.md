# Strong Artin reader edition: source register

Edition 1.0, 8 October 2026. Author: Komorebi P.

## The retained mathematical spine

The primary project manuscript is `PSC_Strong_Artin_Residual_Realization(1).tex`, with its companion bibliography and authenticated `PSC_Strong_Artin_Residual_Realization_Package(1)` archive. Its title is *Finite Trace Alphabets, Residual Realization, and the Strong Artin Gate*. The package includes its proof audit, deep audit, source audit, original verifiers, figure sources, and earlier baseline evidence.

The revised `body.tex` retains all 78 original theorem, proposition, lemma, and corollary groups: 29 theorems, 8 propositions, 4 lemmas, and 37 corollaries. The proofs have been retained or replaced by a more precise complete argument where the current audit found a scope or reasoning issue. This is not a short summary substituted for the longer project source. Two explicit conjecture statements, a new introduction, current literature boundaries, and additional worked calculations have been added.

The retained groups cover cyclic extension and descent torsors, exterior coefficient rotation, determinant selection, algebraic central blindness, stable epsilon comparisons, total induction blindness, stable and moving subgroup types, multiplicity spectra and Fourier tests, exact global label intersection, local Artin descent, finite Satake alphabets, separating coefficient primes, residual image bounds, conditional lifting and attachment, quotient prime collapse and congruence, semisimple l-adic rigidity, realization routes, finite separators, and positive saturation for Artin holomorphy. The positive cone method is a separate analytic sufficient criterion. It does not imply automorphic existence.

## Corrections to the earlier presentation

The reader text now separates weak unramified attachment from all local attachment. The remaining checks include exceptional finite places and every archimedean place. A lower weak attachment suffices for the fixed finite Satake alphabet outside one declared exceptional set. It does not establish finite local parameters at an excluded place.

The local Fourier obstruction tests matching zero supports as well as nonzero ratios. The arbitrary coefficient field in quotient-prime collapse is handled through full characteristic polynomials and modular Brauer–Nesbitt, without silently assuming a splitting field. The finite image trace theorem is proved for any subgroup with finite trace alphabet under the stated semisimplicity and characteristic conditions. Its characteristic zero case gives the direct l-adic rigidity proof.

The large residual recovery theorem fixes its separation field, bounded cyclotomic alphabet, and bad rational primes before any residual realization or ordinary lift is chosen. It does not need the unknown lift's matrix entries in its separation field. The global semisimplicity, finite ramification, and continuity hypotheses on the l-adic representation are explicit. Continuity of a realized complex pseudocharacter is proved by trace coordinates, followed by the no-small-subgroups proof of finite image.

These corrections are mathematical editorial work reviewed independently. They are not claimed to have been newly encoded and replayed in Lean in this edition.

## Later formal developments

The recovered final checkpoint is `Strong_Artin_Lean_v0.38.0_Effective_Matrix_Hensel_Checked`. Its `PROOF.md`, `RESEARCH_BOUNDARY.md`, `SELF_REVIEW.md`, and `CONTINUE_HERE.md` define the actual local lifting boundary. The archive retains its parents and the earlier cyclic cohomology, obstruction, syzygy, and compatible tower work.

`formal_appendix.tex` supplies a detailed mathematical exposition of these mechanisms. The exact arithmetic comparisons remain inputs. The matrix Hensel theorem assumes an integral coefficient operator B with B D_A = D_A B = p^s I, verifies both identities on matrix units, and requires m > s. Its target congruence is B vec(U − A^d) = 0 modulo p^(m+s). It does not classify a derivative singular over Q_p, all shallow resonant prefixes, or arbitrary simultaneous local prescriptions.

The formal evidence register is `evidence/LEAN_COVERAGE.md`. It distinguishes source authentication, historical compiler replay, current source-level checks, and proof inputs. Current toolchain recovery was blocked by HTTP 403 before any compiler invocation. Therefore no fresh Lean replay is asserted by this reader edition. Historical verification is retained with its source hashes.

## External mathematical inputs

The exact external leaf contracts and authenticated source hashes are recorded in `evidence/LITERATURE_CHECK.md`, `evidence/LITERATURE_SOURCE_MANIFEST.json`, and `evidence/ADDITIONAL_LITERATURE_LEAVES.md`. Fifteen primary works were checked in this edition. The printed bibliography has 29 entries, including inherited background references. The latter are not all newly authenticated simply because they appear in the bibliography.

Arthur–Clozel and Clozel–Rajan supply the prime cyclic cuspidal descent and automorphic induction inputs. Invariant unitary cuspidal descent, cuspidal base change, free character action, and a full Galois conjugacy orbit for induction are the relevant hypotheses. No assertion that cyclic base change alone proves general solvable Strong Artin is made.

The Harris–Taylor author preprint supplies local twisting, cyclic prime base change, and induction compatibility in Lemma 12.7. Its numbering differs from the published book. Deligne–Henniart's Theorem 4.6 supplies the high-ramification epsilon ratio. The ratio is used directly, avoiding an unspecified determinant evaluation element and its sign convention.

Chenevier's checked arXiv:0809.0415v2 provides the characteristic zero determinant/pseudocharacter correspondence and semisimple realization, together with the modular full-characteristic-polynomial uniqueness interface. Theorem numbering in the reader refers expressly to that preprint. Algebraic realization alone is not cited as a usual-topology continuity theorem.

Kim–Yamauchi's checked theorem is conditional on its five inputs. It is an adjacent construction method, not a source of arbitrary residual realization existence. BLGGT's regular lifting theorem does not cover repeated all-zero weights at rank greater than one. Calegari–Geraghty demonstrates a special nonregular range, which is not the unrestricted weight-zero target.

Scholze's residual theorem requires actual cohomological occurrence and its precise q_v normalization and field/theorem conditions. Goldring's main theorem, with Shin's appendix, has its unitary datum, holomorphic limit, coefficient-prime, and density-one split-prime normalization hypotheses. The corresponding reader corollaries require an explicit comparison with the exact project polynomial alphabet. Gee–Kassaei and Dimitrov–Wiese are used as precise rank-two weight-one examples, not arbitrary-rank construction theorems.

Wang's September 2026 preprint statements are checked in their specific generalized octahedral three-dimensional and primitive solvable six-dimensional sectors. The full proof was not independently audited here. Neither a broad priority claim nor a claim that those particular sectors are untouched is made.

## Exact figures and computations

The five paper figures reuse the native vector matplotlib figures from `visual/figures/`. They illustrate exact finite torsor, coefficient, alignment, trace-coordinate, and matrix tower models. They are not generated illustrations. Their provenance and bounded calculations are recorded by the visual computation report and manifest.

`worked_appendix.tex` gives full derivations of the prime cyclic Clifford alternatives, ordered multiplicity alignment, coefficient stabilizers, the rank-three determinant failure, an incompatible infinity model, trace encodings, and the necessity of semisimplicity and the residual characteristic restriction. Its incompatible examples are finite algebraic controls, not arithmetic counterexamples to Strong Artin.
