# Komorebi Cross-Radix Rigidity — certified continuation v0.8.0

v0.8.0 closes the active shell–jet / minimal invariant-hull block on top of certified v0.7.0.

## New theorem hierarchy

For a bounded quasi-polynomial tail profile `P`:

`ProfileOrbitHull(P) ⊆ ShellJetEnvelope(ProfileOrbitHull(P)) ⊆ InvariantShellJetEnvelope(ProfileOrbitHull(P)) ⊆ DegreeBoundedProfile(T,d)`.

The first object is the **absolute minimal positive-affine-invariant linear orbit hull**. The second is the smallest raw shell/jet coordinate mask containing it. The third is the smallest shell/jet coordinate mask that is itself positive-affine invariant.

For the full eventual sequence, `OrbitCommonHull N T d P` retains the transient prefix and uses the absolute minimal tail orbit hull. Under `BellDownstreamInterface a`, every positive affine/radix section lies in this one hull, and the hull is minimal under the explicit full-prefix-retention convention.

The dimension chain is

`finrank OrbitCommonHull ≤ N + finrank ProfileOrbitHull ≤ N + active shell/jet coordinate count ≤ N + T*(d+1)`.

The exact invariant shell/jet mask also has a finite exact coordinate-count formula through `allowedFreqJetFinset`.

## Integrity

- v0.7 frozen ZIP retained under `frozen_v0_7/`
- all 31 v0.7 source files are byte-identical
- 36 total Lean source modules
- 259 theorem/lemma declarations
- 140 definitions/abbreviations/structures
- 39 new v0.8 theorem/lemma declarations
- 20 new v0.8 definitions/abbreviations/structures
- no `sorry`, `admit`, or custom `axiom` in `src/`
- strict gate: `-DwarningAsError=true`
- representative load-bearing axiom audit: only `propext`, `Classical.choice`, `Quot.sound`

Bell remains external and the naive base-independent integral normal form remains rejected.
