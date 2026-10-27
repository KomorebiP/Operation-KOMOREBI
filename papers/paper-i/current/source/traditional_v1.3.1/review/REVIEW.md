# Paper I: journal review and verification report

**Edition reviewed:** v1.3.0  
**Upstream:** v1.2.1 manuscript, Lean component v1.0.1, Python companion v1.1.1  
**Delivered components:** journal manuscript v1.3.0, Lean component v1.0.2, Python companion v1.1.2  
**Review status:** substantive editorial and mathematical review with fresh scoped formal checks. This is not independent peer review.

## Executive finding

The registered formal contract is retained and passes fresh checks. The
journal edition corrects errors in exposition and in the computational
companion without changing any existing Lean theorem statement or proof
body. It is ready to replace the Paper I placeholder at the explicitly
stated scope. It should not be presented as a proof of the excluded
classification inputs, a verified eigensolver, or a novelty certification.

The review found real defects despite the upstream build and test records.
In particular, the original 18-test Python suite passed here before the two
new counterexamples were added. A passing finite test suite was therefore
not evidence that the implementation handled every documented case.

## 1. Mathematical corrections

### 1.1 Dense realization, Theorem 8.5: repair the range argument

The statement assumes an intertwining surjection and bounded operators P
and Q. Its original reverse-inclusion proof treated an arbitrary y in the
range of Q as though Qy = y. That step requires Q to be idempotent, a
hypothesis absent from the stated theorem and unnecessary for its truth.

The repaired argument writes y = Qz, lifts z = Phi(x) by surjectivity, and
uses the intertwining equation to obtain y = Q Phi(x) = Phi(Px). Thus
Phi(range P) = range Q without adding idempotence. The existing formal
`map_packetRange_eq` already has this stronger, arbitrary-operator scope.
This is a prose-proof correction, not a new Lean theorem.

### 1.2 Dense range is not the same requirement as surjectivity

The original boundary stated that surjectivity was indispensable to both
conclusions. That is too strong. For the density conclusion, continuity
sends the closure of the source hull into the closure of its image. If Phi
has dense range, the target hull is dense. Exact range equality generally
requires the stronger surjectivity hypothesis used in the theorem.

The corrected boundary and map row 29 now distinguish these conclusions.
The general dense-range variation is explained mathematically; this edition
does not add a new Lean declaration for that variation. The registered
surjective theorem remains unchanged and checked.

### 1.3 Companion matrices: cyclicity does not supply every certificate

The original companion example said that every companion matrix supplied
one primary block at eigenvalue zero. A general characteristic polynomial
need not be a power of t and need not split over the coefficient field.

The revised example proves companion cyclicity directly from the Krylov
basis. It reserves the single block at zero for the nilpotent companion
used in the finite experiment. Cyclicity over the ground field is preserved;
an unwarranted assertion about a split primary certificate is removed.

### 1.4 Make the graph argument inspectable

The cycle section now gives the actual upper/lower bound mechanism. Adjacent
coordinate vectors generate by the adjacency recurrence. Over C, a pair of
primitive-root Fourier functionals gives a surjective two-dimensional
scalar quotient, ruling out one seed. The endpoint Krylov proof for paths
and the all-size complex-cycle formal statements remain separate from the
sampled graph plots. No all-size theorem is inferred from the plot.

### 1.5 Other scope and notation repairs

The completion clause states the nontrivially normed scalar field. The
operator-family hull is defined by finite words rather than silently
requiring an operator algebra. Pairwise annihilation of idempotents is not
called Hilbert orthogonality. The source-component remark is limited to
packet-supported seed families and nonzero counted components. The
repeated-block example requires a positive block size. A representation,
not the grammar itself, is identified with a module over a path algebra
with relations. Singleton-hull notation is made explicit.

No definition, theorem, proposition, corollary, example, construction,
remark, or boundary was dropped to obtain the checked status. All 69
numbered main-text environments and existing result labels are preserved;
that count includes non-theorem environments.

## 2. Computational companion corrections

### 2.1 Floating division corrupted an exact integer formula

The old implementation used `ceil(m / d)`. For d = 1 and
m = 2**53 + 1, conversion through binary floating point returned
9007199254740992 instead of 9007199254740993.

The implementation now uses `(m + d - 1) // d`, with exact integer
validation. It rejects fractional counts and booleans, supports arbitrary
Python integers, and retains zero multiplicities. Regressions include the
53-bit boundary, a 401-digit multiplicity, NumPy integer inputs, and invalid
input shapes and signs.

### 2.2 Complex symmetry did not justify the spectral shortcut

The former symmetric-adjacency shortcut accepted the complex symmetric
matrix A = [[i, 1], [1, -i]]. This nonzero matrix has A**2 = 0. Its
algebraic eigenvalue multiplicity is two, while its minimum cyclic seed
number is one. Complex symmetry alone does not imply diagonalizability.

The shortcut now requires entries that SymPy can establish are real, as
well as symmetry. The general single-operator routine remains available
for the nilpotent example. This aligns the shortcut with its use on real
undirected graph adjacency matrices. Symbolic eigensolver correctness is
not formally verified by this release.

### 2.3 Evidence generation no longer asserts unrelated checks

The old `run_all.py` wrote a verification record containing predetermined
pass labels for stages it did not execute. The journal generator records
only its examples and figure outputs. Tests, Lean checks, and PDF review
have separate commands and observed process records. The final Python
runner requires actual zero exit codes and checks the expected test count.

An initial attempt failed during metadata collection because the optional
`wheel` package was absent. That failure is retained. Metadata collection
now records an absent optional package as null rather than inventing a
version or blocking numerical output. No wheel-build claim is made.

### 2.4 Final computational result

All 33 companion tests pass with warnings treated as errors. The new
finite experiment JSON agrees with the upstream values; differences are
limited to manuscript version, companion version, and Python interpreter
metadata. The table retains the measured transported-projector residual
1.851317738057773e-15. This is a numerical residual, not exact equality.

## 3. Fresh formal verification

The checked environment is Linux x86-64, Lean 4.34.0-rc2, with Mathlib pinned
to aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine dependency repository
revisions were matched against the release manifest and restored cache.
The restored runtime archive's SHA-256 was checked before extraction.

The final run compiled all 20 local modules into an initially empty local
object directory, using one worker and warning-fatal elaboration. It then
resolved all 84 distinct targets in the 35-row contract, printed their full
types and transitive axioms, reran the fail-closed namespace audit, and
executed two deliberate invalid-proof controls.

The namespace audit covered 1,126 entries, including definitions and
generated helpers. Only `propext`, `Classical.choice`, and `Quot.sound` were
permitted. No source `sorry`, `admit`, new axiom declaration, unsafe
definition, native-decide trust shortcut, or forbidden declaration injection
was accepted by the recorded source-policy check. Both negative controls
failed for their intended reasons, not because of missing imports.

### What changed to make the build practical

The first attempt retained the upstream blanket `import Mathlib`. It
stalled under the available memory limit and was deliberately interrupted.
That run did not finish and is not counted as a successful check.

The focused-import development initially lacked several dependencies.
Those runs failed during elaboration. The missing imports were added until
all modules compiled. A subsequent report parser rejected ordinary
universe-annotated axiom names; the output was changed to print axiom names
without universe annotations, while retaining universe information on type
signatures. The final run passed both the direct reports and the independent
Lean-side namespace gate. Failed attempts remain under
`verification/development` rather than being overwritten.

Eight existing import lines are the only changes to the nineteen original
Lean source files. The added twentieth file contains imports only. An
explicit source comparison verifies preservation of all existing statements
and proof bodies. The map's row-29 explanatory exclusion was corrected; the
mapped target list is unchanged.

### What this does not establish

This is not a fresh rebuild of Mathlib or the compiler. Matching cached
imports remain trusted inputs. It does not establish consistency of Lean's
foundations, formal equivalence between the English text and Lean syntax,
independent priority, or the correctness of an unverified Python eigensolver.
The previous 8,883-job aggregate build is an archived result, not this run's
count. The 84 mapped targets and 1,126 namespace entries are not independent
theorem counts.

## 4. Classical and certificate boundaries retained

The semisimple formula consumes split algebra and compatible module
equivalences. Primary and graph formulas consume the stated generators,
polynomial projectors, scalar quotients, eigenbases, and spectrum data.
Jordan, Wedderburn, and the spectral theorem are not reconstructed here.
The algorithm section proves mathematical specifications, including a
noncomputable spectral quantity, not extracted software or complexity bounds.

The quadratic coordinate algebra and its operator identities are checked in
the same development but are outside the 35-row completion denominator.
Projective smoothness, genus, and the geometric discriminant identification
remain classical inputs. No such statement is silently included in the
formal coverage count.

## 5. Journal editing and production

The abstract and introduction now lead with the mathematical problem: an
acting algebra, its module generators, and a finite projector resolution.
The contribution is distinguished from the classical minimum-generator
invariant. The free-presentation and cyclicity proofs are explicit. The
conclusion summarizes the constructions rather than making program-level
promises. The long claim ledger was moved to an appendix without changing
its identifiers.

Typography follows the modern journal identity: restrained teal metadata,
a readable serif text face, sans-serif headings, consistent theorem
styling, controlled heading breaks, and section-contained figures. The
byline is only Komorebi P. No personal name or invented affiliation is added.
The source uses vector figure PDFs; PNG companions are retained for previews.

Figure captions distinguish numerical evidence from exact statements. The
former linear 'dependency' picture has been replaced by the two argument
families described in the text. The figure is explicitly a structural
overview, not a generated complete Lean dependency graph. Matrix indices
and discrete graph sizes now have integer ticks; binary support legends
use zero and one.

Bibliographic metadata was checked against publisher/project records.
Unverified pinpoint page/chapter citations were removed instead of being
presented as confirmed. References to Lean 4 and the mathlib publication
were added. This was not a systematic literature search or a rereading of
all cited books. Metadata checks do not by themselves validate every use of
a reference.

The final PDF's production results are recorded separately under
`verification/pdf_final` and `verification/pdf_visual_review.json`.
The final 39-page article was rendered at 200 DPI. All pages were visually
reviewed; full-size checks included the formalization and claim-ledger tables.
The three-pass build has no warnings, overfull boxes, or unresolved references.
All PDF font entries are embedded. These checks are not a PDF/UA, PDF/A, or
printer-specific press certification.

Source patches, the claim map, original snapshot, and hash comparisons are
included so this review can itself be inspected.

## 6. Release decision

Release the corrected Paper I as the journal's scoped foundational article,
with this supplement attached to its source package. No registered row
remains marked partial in the delivered map. The excluded existence inputs
remain excluded; future extensions need their own statements and evidence.
An external referee may still find issues. This review and successful
compiler run are not substitutes for independent mathematical scrutiny.
