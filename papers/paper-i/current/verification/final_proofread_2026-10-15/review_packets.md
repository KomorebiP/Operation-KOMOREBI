# Paper I conservative proofreading: packets, blocks, and graphs

Scope: every line (1–1156) of `editable/traditional/03_packets_and_graphs.tex`, with the main preamble, coefficient conventions, notation map, and Running Example R3 checked as context. Review-only mode; the manuscript was not edited. No proof was reconstructed or replaced.

## High-confidence findings

### 1. Universal mapping property omits linearity of the input maps

Locations: lines 150 and 154, `cor:packet-universal-property`.

The conclusion promises a linear extension for every family of maps. The displayed Hom formulation and the proof require linear input maps. There is no global convention in the coefficient section declaring every displayed arrow to be linear.

Exact minimal replacements:

* Line 150: `Every family \(f_\alpha:X_\alpha\to Y\)` → `Every family of linear maps \(f_\alpha:X_\alpha\to Y\)`.
* Line 154: `Every family \(g_\alpha:Y\to X_\alpha\)` → `Every family of linear maps \(g_\alpha:Y\to X_\alpha\)`.

Classification: mathematical-token changes (explicit hypotheses). The intended qualifier is forced by the adjacent Hom identities and linear extension conclusion. Report separately if applied.

For consistency, line 482's recap can receive the same qualifier:

`Their universal property assembles arbitrary packetwise maps uniquely.` → `Their universal property assembles arbitrary packetwise linear maps uniquely.`

### 2. Blockwise intertwining theorem omits linearity of U

Location: line 625, `thm:block-intertwining`.

Exact minimal replacement:

`and let \(U:X\to Y\).  Define` → `and let \(U:X\to Y\) be linear.  Define`.

The proof distributes U across the finite packet sum and the converse uses exact operator reconstruction for `UT-SU`. Both require linearity. Classification: mathematical-token change (explicit hypothesis), uniquely indicated by the immediate argument. If policy treats omitted hypotheses as beyond typographical repair, leave unchanged and record this as an unresolved issue instead.

### 3. Triangular example title reverses the declared block orientation

Location: line 783.

Exact minimal replacement:

`\begin{microexample}[title={Upper triangular support}]` → `\begin{microexample}[title={Lower triangular support}]`.

Line 784 permits transfers from a lower source index to a higher target index. Since the chapter writes blocks as `T_{\beta\alpha}`, with target beta as row and source alpha as column, these are lower triangular blocks. No formulas or arguments need to change. Classification: mathematical terminology correction; no symbolic token changes.

### 4. Full block algebra proof calls arbitrary maps linear without stating linearity

Location: line 692, `thm:block-algebra` proof.

Exact minimal replacement:

`Given arbitrary maps $B_{\beta\alpha}:X_\alpha\to X_\beta$, define` → `Given arbitrary linear maps $B_{\beta\alpha}:X_\alpha\to X_\beta$, define`.

The codomain of the theorem is already a product of Hom spaces, so this makes its existing quantification explicit rather than strengthening the theorem. Classification: mathematical-token qualifier, uniquely forced by that codomain and line 698's linear-operator conclusion.

## Lower-priority local ambiguities to leave unchanged without a broader decision

* Lines 714–719: the active contributions are written as a set, then summed. Distinct source indices can give identical contributions, so a literal set discards multiplicity. The proof at line 730 unambiguously means an indexed family. If clarified, replace line 716's `\bigl\{` with `\bigl(` and line 718's `\bigr\}` with `\bigr)`. This is a mathematical notation edit; report explicitly if applied. The proof already supplies the intended meaning.
* Line 477 lists both pointwise and strong convergence among convergence modes said not to be interchangeable. In the usual operator topology language, strong convergence is pointwise norm convergence. Removing `Pointwise, ` would avoid this terminological ambiguity, but the sentence as a statement that the whole list is not interchangeable is not literally false.
* Line 1149's mixed-seed microexample gives `\psrank=2` before specifying one-dimensional packets in the next sentence. Its intended example is clear from the immediately preceding boundary. For standalone clarity, move the one-dimensional qualification into the first sentence. This is exposition, not a forced correction, so no replacement is required.
* Line 6's roadmap does not exactly follow the printed order: support is defined before finite reconstruction, while the universal property precedes tensor products and duality. Purely navigational; no mathematical defect.

## Validation and outcome

* All 1156 lines reviewed.
* Automated local check found no unclosed/mismatched LaTeX environments and no missing targets for the chapter's `ref`, `cref`, `eqref`, or `pageref` references in the included chapter sources.
* The custom macros used in the chapter are defined in the main preamble.
* Running Example R3's oblique projectors agree with the tensor example's reference.
* No manuscript edits made and no compiler run performed by this reviewer; build/render verification belongs to the parent task.
* No additional objective grammar or punctuation corrections found. The issues above do not amount to a full mathematical proof audit.
