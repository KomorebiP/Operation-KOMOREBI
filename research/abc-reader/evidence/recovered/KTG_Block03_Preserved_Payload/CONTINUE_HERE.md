# Continue Here — Block 04

Treat this archive as the sole authoritative predecessor for the next
Komorebi × IUT transport-geometry block.

## Restore first

Read completely:

- `START_HERE.md`
- `BLOCK_03_FORMAL_REPORT.md`
- `PROJECT_STATUS.md`
- `notes/IUT_312_FIELD_TO_SOURCE_MAP.md`
- `notes/IUT_312_OPEN_OBLIGATIONS.md`
- `notes/AUDIT_IUT_III_COROLLARY_3_12.md`
- every file under `formalization/lean/KTG/`
- `verification/block03_final/verification.json`
- `verification/BLOCK_03_DEVELOPMENT_FAILURES.md`

Run:

```bash
cd formalization/lean
lake build
cd ../..
python verification/verify_block03.py --clean
```

Do not extend the theory until the clean verification reproduces.

## Preserved proof boundary

Do not claim that IUT III Corollary 3.12 is false, proved, disproved, repaired,
or refuted. Block 03 verifies a typed source-faithful interface and finite
logical models. It does not instantiate the actual IUT objects or supply an IUT
inhabitant of `SourceWitnessTheorem`.

Do not treat the finite countermodel as an IUT counterexample. Its theorem is
that the encoded pre-witness fields are not sufficient by logic alone.

## Block 04 objective

Move from source mapping to the first genuine IUT instantiation layer. Do not
add another abstract scalar theorem.

### Required sequence

1. **Instantiate the source object shell.**
   Introduce concrete records for the Step (xi-c) output package, fixed q-pilot,
   prime-strip, determinant-line object, and log-volume datum. Preserve context
   tags and do not identify these records definitionally.

2. **Construct the IPL/SHE/APT data from cited source interfaces.**
   Each constructor must name the exact IUT definition or result used. When the
   source supplies only prose or an algorithmic assertion, record that as an
   explicit hypothesis rather than as a proved Lean theorem.

3. **Separate the three strongest obstruction subtheorems.**
   Attempt concrete Lean statements for:
   - Ind1/Ind2 quotient invariance of the measured object
   - Ind3 one-sided upper semi-compatibility
   - unit-multiple absorption by the holomorphic hull

4. **Instantiate the normalization skeleton.**
   Give concrete symbolic parameters for determinant power, summand weights,
   structure-sheaf correction, and procession averaging. Prove the grade
   equation independently of the witness theorem.

5. **Decompose O5.**
   Replace the single open `SourceWitnessTheorem` with the smallest source-level
   lemmas that would imply it. At minimum distinguish:
   - construction of a candidate q-pilot representative
   - membership of that representative in the output hull
   - invariance of its measurement under the permitted indeterminacies
   - orientation of the final one-sided order

6. **Attempt the cheapest decisive theorem.**
   Prove one nontrivial O5 sublemma from the cited source chain, or produce a
   formal countermodel to an overstrong proposed sublemma. Do not count an
   assumption, renamed conclusion, or source paraphrase as closure.

## Completion criterion

Block 04 is successful only if at least one O1–O5 obligation changes from
“typed/source located” to an actual compiler-checked source instantiation or a
sharper formally proved impossibility boundary.

## One-line continuation prompt

> Open `Komorebi_IUT_KTG_Block03_Checked_v0.3.0_2026-09-17.zip` as the sole authoritative predecessor. Reproduce `verification/verify_block03.py --clean` before editing. Preserve the boundary that IUT III Corollary 3.12 is neither proved nor disproved and that the finite countermodel is not an IUT counterexample. Instantiate the first concrete Step (xi) source-object and normalization layer, decompose `SourceWitnessTheorem` into candidate construction, hull membership, measurement invariance, and order-orientation sublemmas, and close at least one source-backed sublemma or formally refute an overstrong candidate without assuming the desired containment.
