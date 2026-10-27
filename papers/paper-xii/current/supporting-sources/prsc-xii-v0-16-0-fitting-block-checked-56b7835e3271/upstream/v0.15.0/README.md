# Paper XII: fifteenth checked Lean block

**Komorebi P. · v0.15.0 · 9 September 2026**

Added **26 checked theorem declarations**. Paper XII now has
**546**, excluding **81 unchanged reused Paper X theorem declarations**.

Revised **Claim 12.6** assembles actual ordinary or perfect derived patched
carriers, support-preserving comparison to a Hecke carrier, actual nonzero
Hecke eigenvectors, conditional representation isomorphisms, and propagation
through both existing compatible families with the same polynomial spine.
Its original statement remains partial.

The comparison hypothesis is the genuine inverse-image inclusion of prime
supports. The revised statement supplies a compatible Hecke point over the
same coefficient field. This is necessary: full-support preservation under
Q -> Q[X]/(X^2+1) does not produce a Q-valued point. Ordinary fibers are actual
tensor modules; derived fibers use actual cohomology and the finite projective
model's integer interval. The declared realization input applies to the
produced eigenvector. The system input supplies the produced automorphic
object together with one attached family, its distinguished member identity,
common-spine evidence and member semisimplifications. Propagation compares
that family with the given source family.

Residual occupancy, represented-deformation existence, classicality and
attached representations, Frobenius density, semisimplification existence
and general algebraic Brauer–Nesbitt remain named external inputs. Their
arithmetic interpretation is application provenance. They are not proved by
support transport, and the release does not construct missing companions.

Revised manuscript: **43 / 49 complete, 1 partial, 5 unchecked**.
Original wording: **35 complete, 8 partial, 6 unchecked**.
The eight explicit amendments are **6.12, 9.4, 9.5, 9.6, 10.5, 12.2, 12.4 and 12.6**.
Original partial claims are **7.1, 9.4, 9.5, 9.6, 10.5, 12.2, 12.4 and 12.6**;
the revised partial claim is **7.1**, intrinsic Fitting-ideal transport.
Remaining revised unchecked claims are **3.1, 3.3, 6.3, 6.4 and 6.5**.
All other claim coverage is preserved.

All **71 modules** and **934
declaration axiom audits** passed with warnings as errors. Both invalid
controls were rejected. Counts: 546 theorem declarations,
214 definitions, 11 structures,
32 abbreviations and 7 named
instances in 64 own modules. All **68 prior
production sources remain byte-identical**. The transitive axiom audit
permits only propext, Classical.choice and Quot.sound.

```bash
bash Run-Portable.sh /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 checks/validate_package.py
```

Lean 4.34.0-rc2 and the pinned Mathlib cache are required separately. The
updated PDF, editable LaTeX, bibliography and 18 original vector figures are
in paper/. All 106 original labels and every original statement/proof record
are preserved. REVISION_CHANGES_v0.15.0.json records the exact sequential TeX
update; MANUSCRIPT_CHANGES.json records cumulative changes. Independent
reviews and failed development attempts are retained. Declaration counts
include supporting lemmas and are not a new census of the twelve-paper corpus.
