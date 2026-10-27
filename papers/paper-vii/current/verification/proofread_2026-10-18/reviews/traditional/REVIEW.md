# Paper VII traditional mathematical parts: full proofreading review

Reviewer: `traditional_proofread` subagent. Mode: review only.

Baseline: `/workspace/scratch/be33f0b6c391/paper7_work/source/Komorebi_Paper_VII_Monograph_2026-10-09`.

## Coverage and result

I read all nine `editable/traditional/parts/*.tex` files completely, totaling 5,123 source lines. The reading included the prose, declarations, displayed mathematics, proof bodies, captions, and citation and reference syntax. I also read the main preamble and opening conventions needed to interpret these parts. All nine source hashes match the baseline's `current_source_records.json`. Exact paths, line counts and hashes are in `coverage.json`.

No manuscript file was modified by this reviewer. No forced sign, coefficient, index, domain or other mathematical-token typo was identified. No obvious spelling or grammar error meriting a routine edit was found. The material findings are scope and meaning clarifications below, ordered by risk. They need explicit editorial handling rather than silent changes to protected mathematics.

This is conservative mathematical proofreading, including local consistency. It is not an independent proof audit, a new Lean build, bibliography source verification, or a review of the historical archives. The parent handles the documented build and PDF inspection.

## Findings

### TR-01: carry the positive row dimension into the several-seed equivalence

- File: `editable/traditional/parts/03_supplement_03.tex`, lines 14–27, especially line 17.
- Current opening: `For seeds $C_1,\ldots,C_k$, generation means the concrete statement`.
- The following equivalence, generation if and only if the stacked matrix has rank `m`, needs `d>0`. The preceding paragraph states this only conditionally for the one-seed equivalence and explicitly says that the nonempty-row assumption is essential. If the next subsection is read without that condition, `d=0,m>0` is a counterexample: the zero-row matrix space has only its zero element and is generated trivially, but the stacked rank is zero rather than `m`.
- Proposed exact opening: `Assume $d>0$. For seeds $C_1,\ldots,C_k$, generation means the concrete statement`.
- Classification: mathematical-token addition, an explicit hypothesis/scope clarification. It is not a uniquely forced isolated typographical correction. Confirm the corresponding formal theorem's nonempty row hypothesis before applying. The direct-sum subsection already requires `d_i>0`.
- No new proof is proposed or needed for the intended positive-row branch.

### TR-02: the approximate KL defect does not bound arbitrary error-image nonorthogonality

- File: `editable/traditional/parts/02_strengthened.tex`, line 1441, following lines 1431–1452.
- Current text: `Thus \(\varepsilon_{\rm KL}\) controls both state dependence of error overlaps and nonorthogonality of nominal syndrome images.`
- The displayed estimate controls deviation from the selected scalar overlaps `c_ab`. It does not by itself bound nonorthogonality of the original error images. For example, `E_1=E_2=I` on a nonzero code gives zero KL defect while the two error images coincide. The valid estimate and its proof do not need alteration.
- Proposed exact replacement: `Thus \(\varepsilon_{\rm KL}\) controls the deviation of error overlaps from their scalar code form.`
- Classification: meaning-calibration of an explanatory conclusion. No mathematical symbol or displayed formula changes, but the prose narrows an overbroad interpretation. Record it as an explicit mathematical meaning correction, not as spelling or typography.

### TR-03: identify the quantity proved to converge at a heat trace boundary

- File: `editable/traditional/parts/02_strengthened.tex`, lines 2509–2526, specifically line 2522.
- Current ending: `in trace norm and the limiting heat trace is nonzero, then the spectral dimensions converge at that time.`
- The theorem allows unbounded operators and assumes trace class heat and heat-moment operators at one fixed time. The proof directly establishes convergence of the moment ratios `2t Tr(L exp(-tL))/Tr(exp(-tL))`. The earlier finite definition also identifies this ratio with a logarithmic derivative. At a trace class boundary, the heat trace need not be finite on a two-sided time neighborhood, so that two-sided derivative interpretation requires more than the stated fixed-time assumptions.
- Proposed exact ending: `in trace norm and the limiting heat trace is nonzero, then the spectral dimensions defined by the heat-moment ratio converge at that time.`
- Classification: explicit definition-scope calibration of the conclusion. No displayed formula changes. If a literal two-sided logarithmic derivative is intended instead, the required neighborhood assumption is a substantive matter outside proofreading and should be reviewed separately.
- The ratio convergence itself follows exactly by the existing proof.

### TR-04: distinguish the cosmological constant from the volume coefficient

- Files: `editable/traditional/parts/01_finite_core.tex`, lines 1233–1239, and `editable/traditional/parts/02_strengthened.tex`, lines 2555–2571.
- Part I writes the four-dimensional Einstein term as `(R-2 Lambda)/(16 pi G)`. Part II writes the volume coefficient as `+Lambda`, separately from `R/(16 pi G)`.
- These can be different conventions, but the same symbol is not the same coefficient under both formulas. No sign or normalization replacement is uniquely forced, since the parts preserve separate source treatments and the second formula allows dimension `d`.
- Proposed prose note after the Part II display: `Here $\Lambda$ denotes the coefficient of the volume term. In the four-dimensional normalization of Part I, that coefficient is $-\Lambda_{\mathrm{cosm}}/(8\pi G)$, where $\Lambda_{\mathrm{cosm}}$ denotes the cosmological constant used there.`
- Classification: mathematical-token addition and convention translation. This is an editorial convention choice, not a typographical correction. It should be accepted or rephrased explicitly by the parent rather than silently inserted by a proofreader.

### TR-05: state the order used in the path interference sum

- File: `editable/traditional/parts/02_strengthened.tex`, lines 452–464.
- The interference formula sums over `gamma<gamma'` without declaring an order on the finite path set.
- Proposed addition after defining `Gamma_b`: `Fix any total order on \(\Gamma_b\).`
- Classification: mathematical data/notation clarification, not a changed interference formula. The result is independent of the chosen order, since it is only used to count each unordered pair once. No order was edited into the source by this reviewer.

### TR-06: define the partition mesh

- File: `editable/traditional/parts/02_strengthened.tex`, lines 798–837.
- The symbol `abs(pi)` appears in the error bound and proof without an explicit definition.
- Proposed sentence after the displayed partition: `Write \(\abs{\pi}=\max_{0\le j<n}(t_{j+1}-t_j)\) for its mesh.`
- Classification: mathematical-token addition defining already-used conventional notation. No estimate changes. The natural reading is already the partition mesh, so this is a minor clarity item.

## Metadata item sent to the parent

`01_finite_core.tex:1298` says the 19 original figures are retained from the recovered numerical companion. The package also carries repair provenance. Ensure the release wording does not imply byte-identical retained graphics if some were regenerated or repaired. This is outside the nine-part mathematical finding set and can be handled in the edition's provenance explanation.

The supplemental phrases such as “this release”, “new module”, “freshly compiled” and “outside this block” describe the historical formal block represented by that supplement. The main opening note already distinguishes the archived checkpoint from a fresh compilation. If the new edition revises that note, keep this provenance distinction explicit.

## Structural verification

`structural_checks.json` records:

- All 29 explicit reference commands in the nine parts resolve against the current main inputs.
- All 15 citation commands use keys in the supplied bibliography.
- No duplicate labels were found in the current input set examined.
- Environment nesting, braces, and explicit math delimiters passed static checks.
- An initial naive substring counter wrongly treated `\\[-2pt]` in Supplement 5 as a display opening. The counter was corrected to distinguish an optional row-break length from `\[`. The corrected result is clean. This was a diagnostic limitation, not a source error.
- The parent is responsible for compiling the current edition and checking its rendered pages.

## Per-file status

| Mathematical source | Full source lines read | Findings |
|---|---:|---|
| `01_finite_core.tex` | 1–1325 | TR-04 convention comparison, metadata note |
| `02_strengthened.tex` | 1–2619 | TR-02, TR-03, TR-04, TR-05, TR-06 |
| `03_supplement_01.tex` | 1–229 | No objective proofreading issue found |
| `03_supplement_02.tex` | 1–233 | No objective proofreading issue found |
| `03_supplement_03.tex` | 1–175 | TR-01 |
| `03_supplement_04.tex` | 1–137 | No objective proofreading issue found |
| `03_supplement_05.tex` | 1–212 | No objective proofreading issue found |
| `03_supplement_06.tex` | 1–148 | No objective proofreading issue found |
| `04_alternative_derivations.tex` | 1–45 | No objective proofreading issue found |

These statuses are bounded to the exact hashes in `coverage.json`. Edits made afterward need a changed-hunk self-review and refreshed source records.
