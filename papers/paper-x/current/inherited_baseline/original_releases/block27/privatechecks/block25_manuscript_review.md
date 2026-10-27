# Independent review-only mathematical proofreading: Block 25 amendments

Proofread: all changed hunks of `source/Block25_Amendments.patch`, the resulting Block 25 text, and the surrounding theorem, definitions, macros, and notation needed to interpret those changes.

- Routine edits: none. Review-only mode; no manuscript or patch was changed.
- Mathematical-token changes: none.
- Unresolved objective issues in the reviewed changes: none.
- Validation: bounded lexical structure validation passed; the original Claim 9.1 theorem and proof are byte-for-byte unchanged as text. No TeX compiler or PDF rendering was run, so page layout and rendering are not certified.
- Coverage: changed Block 25 status passages, the new system/member and cofinite-overlap explanations, the complete finite cyclotomic arithmetic case, the finite-deletion example, and the corresponding current-boundary passage. This is not a fresh proofread of every historical section.

## Frozen inputs

- `source/Projector_Resolved_Seed_Calculus_X_Block25_Amended.tex`: SHA256 `eaf88f5f90ec10893b56499a438b07092ad22beb8e7942002bd0e2ad33be81ed`.
- `source/Block25_Amendments.patch`: SHA256 `df5a44df8f1e3ab1e8ece5920c1c663409a04539eb7dea9778d7f24c5cc035c0`.
- The unchanged Claim 9.1 theorem-through-proof text has SHA256 `6db3e6ea5ba2c0096666260e69eb8bad982b49cd83918f6c314212e3a8c0dc33`.

## Meaning and notation checks

The new system-isomorphism display explicitly uses memberwise representation equivalence. Its explanation uses the same coefficient embedding for common traces and retains the overlap of the two coefficient primes' good-place sets. The cofinite-coverage paragraph expressly requires every finite deletion. It does not infer robust coverage from density of the original samples.

The cyclotomic discussion fixes n>0 and L=Q(zeta_n). The automorphism sigma_p is defined only for primes p not dividing n. Its residue convention is explicitly arithmetic Frobenius, p-power action. The forbidden set B and numerical lower bound b are distinct and consistently used. The existence of a maximal prime P above the selected p is now justified by the frozen three-theorem wrapper, rather than left as a premise.

The wording “ramification index is one” exactly matches the production conclusion. Subsequent “unramifiedness” language refers to that standard number-field criterion. It does not assert that a separate Lean `Algebra.IsUnramifiedAt` instance was constructed, or confuse unramifiedness with complete splitting. The residue equation quantifies over every integral x and identifies the actual quotient O_L/P.

The finite Galois group Gal(L/Q) and the absolute Galois group are kept distinct. The text calls the result a complete restricted case and immediately retains the general absolute-Galois coverage gap. The “no coverage or character-continuity hypothesis is added” sentence is confined to the fixed cyclotomic specialization, where actual prime coverage is proved and the finite extension's Krull topology is discrete. It is not applied to arbitrary profinite groups.

The new status passages consistently retain seventeen checked claims and three partial claims, naming 9.1, 9.2, and 11.1 as partial. They do not promote the fixed cyclotomic result to full Claim 9.1 or claim Hodge–Tate/Weil–Deligne attachment. The phrase “arithmetic attachment” in the cyclotomic paragraph is locally specified by the actual prime, decomposition group, and residue action, with the separate Hodge–Tate/Weil–Deligne exclusions stated below.

The finite-deletion example uses the discrete group C2, removes sample index zero, and correctly explains why its surviving identity samples cannot distinguish the sign and trivial characters. The explanation does not claim this counterexample is itself an arithmetic Frobenius sample family.

Preamble macros used by the additions, including `\Q`, are defined. Displays, indices, subscript conventions, and prose punctuation are consistent. No new unresolved labels, references, or citations were introduced.

## Validation performed

The existing `checks/check_manuscript_structure.py` was executed with its output redirected to the private review record `privatechecks/block25_manuscript_structure_review.json`; the script file itself was not edited. It reported:

- 107 matched environments;
- 135 pairs of display-math delimiters;
- 203 pairs of parenthesized inline-math delimiters;
- 1,022 unescaped dollar delimiters;
- no brace, environment, delimiter, label/reference, or citation errors.

A direct extraction comparison confirmed that the original Claim 9.1 theorem and proof are unchanged from the frozen Block 24 manuscript. The new explanatory paragraphs follow that existing proof and preserve its current partial status. This review did not independently replay the patch application; the root release checks own that separate artifact-consistency gate.

## Review dependencies and evidence

The arithmetic meaning was checked against `CyclotomicPrimeCoverage.lean`, the new `CyclotomicFrobeniusPrimes.lean`, and the independently reviewed primary Mathlib sources. The broader system-separation theorem is being independently audited by another reviewer; this proofreading review does not replace that proof audit.

| Evidence | SHA256 |
|---|---|
| `source/Projector_Resolved_Seed_Calculus_X_Block25_Amended.tex` | `eaf88f5f90ec10893b56499a438b07092ad22beb8e7942002bd0e2ad33be81ed` |
| `source/Block25_Amendments.patch` | `df5a44df8f1e3ab1e8ece5920c1c663409a04539eb7dea9778d7f24c5cc035c0` |
| `checks/check_manuscript_structure.py` | `dbc3a6b8ea9a54f2f7bbe63e8e784752eab1c993db7d84a4ed0548a564807719` |
| `privatechecks/block25_manuscript_structure_review.json` | `29a35b5734d816d5edb13ca385e9adacfe73df85a6ba23112002ce348adb3240` |
| `lean/PaperX/CyclotomicPrimeCoverage.lean` | `497cb15ebc4b9c48206bcf1782758ef3f66c0c46c30a2168d6c169a9dcab6273` |
| `lean/PaperX/CyclotomicFrobeniusPrimes.lean` | `315bdb71a834a6024fa47e7dc41ebb64954b0279d1df0fea451b662d7c8231fe` |
| `CYCLOTOMIC_ARITHMETIC_REVIEW.md` | `2a26702d77feaa45e6fbda1867fb3c4477e814004222866d48caf6b5b490c521` |
| `CYCLOTOMIC_PRIME_EXISTENCE_REVIEW.md` | `4b06078995099af46de1dabf0f10586f14a4f6fad1a26682825b9918d4f47b9a` |
