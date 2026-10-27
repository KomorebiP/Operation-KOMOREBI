# Continue with Block 52

Open `Komorebi_Beal_Block51_Monodromy_Depth_v5.1.0.zip` as the latest
combined checkpoint. It contains the full recovered Block 49 bundle and
the later Block 50 extension checkpoint, with both original archives.
Do not discard Block 50 merely because it was a small checkpoint.

Read completely before editing:

- README.md
- work51/REPORT.md
- work51/PROOF_BOUNDARY.md
- work51/VERIFICATION.md
- work51/TARGET_CONTRACT.md
- work51/notes/LOCAL_DEPTH_THEOREM.md
- work51/notes/ARITHMETIC_SUPPORT.md
- work51/notes/BLOCK50_FRESH_REVIEW.md
- work50/notes/extension_geometry.md
- work50/verification/extgeo_checkpoint.json
- work49/notes/extension_route.md
- work49/notes/extension_selmer_sharpness.md

Run `python verify.py --replay-predecessors` from the extracted root.
The runner executes in temporary copies and does not modify frozen files.
Its default report is written outside the package, next to its directory.
Do not treat a timeout as a pass or a mathematical contradiction.

## Preserve

The new equality is n=t+2s, 0<=s<=v_7(Q-1), not n<=t+h.
The actual global n comes from the complete stable-lattice segment in
one Frobenius-at-three eigenbasis. It is not a freely chosen modulus.
Only actual ramification of the opposite class forces equality with
v_7(N_21). At variable q|C, t=1+v_7(v_q(C)), on the natural lattice.
The two-depth conclusion n in {1,3} requires both ordinary eligible
multiplicities and Q not congruent to 1 modulo 49 for every eligible place.
These conditions are not automatic. Keep the higher diagonal obstruction
and all source-dependent hypotheses visible.

## Primary next target

Obtain a representation-specific restriction on the global n or on the
relative toric-line angles that appear in the exact local equality.
A useful bounded first objective is to calculate the natural Kummer
coordinates and the higher diagonal character in compatible global bases,
then test their coupling in the n=1 and n=3 ordinary regime. Do not invent
coefficient ratios by normalizing independently at distinct places.

For n=1, delta vanishes and every ramified eligible place must have
natural alpha(F)=0. Determine whether the actual Kummer class can satisfy
all those residue constraints. Nonempty residue possibilities are not
geometric solutions and cannot be discarded as unlikely.

For n=3 in the ordinary h=1 regime, every ramified eligible place has
nonzero local cup and a nonliftable diagonal character. Determine whether
the actual family imposes a global incompatibility, rather than assuming
all diagonal characters lift. The old q=1504231 ray family survives only
with the exact local multiplicity cost from equation (23); it is still
not a realized Frey example.

Parallel geometric direction: use additional structure of the particular
Frey family, not principal polarization or RM alone. Those survive the
lattice moves. A useful result would be an explicit period-angle relation,
a computed compatible Kummer coefficient, or a proved obstruction to an
actual endpoint character. A no-go theorem or exact surviving exceptional
family is also a valid outcome if all boundaries are preserved.

The CM congruence/cover branch and higher Hilbert levels remain separate.
Do not declare progress on them merely because the reducible branch was
refined. Do not claim full Beal from a result about this one signature.
