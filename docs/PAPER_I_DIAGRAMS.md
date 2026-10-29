# Paper I: figure and atlas descriptions

These descriptions explain the information carried by Paper I’s ten chapter
figures and twenty-two visual-atlas plates. They identify the arrows, axes,
matrix entries and comparisons without relying on colour. They are reading
aids for the retained manuscript, with its hypotheses and proof scope.

[Read Paper I](https://komorebip.github.io/Operation-KOMOREBI/read/paper-i/index.html)
· [Accessibility and reading options](ACCESSIBILITY.md)

<a id="figure-1-from-seeds-to-a-realization"></a>
<h2 id="figure-01" tabindex="-1">Figure 1: from seeds to a realization</h2>

Six boxes form a directed sequence. Across the top row, read **Choose seeds**
(generators in the object), then **Address them** (indices for the seeds), then
**Apply operators** (words in the fixed algebra). An arrow descends to **Record
relations** (kernel and quotient data). The lower row runs from right to left:
**Form the hull** (span or closure), then **Reconstruct** (a realization map).
A separate box below gives an optional packet view: project to expose blocks
when projectors are available. This is a guide to the presentation data, rather
than a claim that every object comes with all these choices automatically.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-i/foundations-and-seed-rank.html#L203)

<a id="figure-2-transfer-blocks-of-a-sampled-operator"></a>
<h2 id="figure-02" tabindex="-1">Figure 2: transfer blocks of a sampled operator</h2>

This three-by-three heatmap gives the Frobenius norm of each block of a sampled
operator. Rows are **output** packets and columns are **input** packets. Select
input packet j, apply the operator, then select output packet i. The packet
dimensions are 5, 6 and 7. Numbers are rounded to one decimal place; darker
cells indicate larger norms.

| Output packet | Input 1 | Input 2 | Input 3 |
| --- | ---: | ---: | ---: |
| 1 | 5.0 | 5.0 | 8.1 |
| 2 | 5.7 | 6.2 | 6.0 |
| 3 | 5.7 | 6.3 | 7.3 |

Diagonal blocks act within a packet. Off-diagonal blocks transfer between
different packets. A norm gives the size of a block; it does not retain the
block’s signs or its complete linear action.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-i/packets-and-transfer-graphs.html#L900)

<a id="figure-3-one-seed-can-span-the-space-or-stall"></a>
<h2 id="figure-03" tabindex="-1">Figure 3: one seed can span the space or stall</h2>

The horizontal axis counts Krylov vectors, from 1 through 8. The vertical axis
is the dimension of their span in an eight-dimensional space. The vectors are
the fixed seed v followed by Tv, T squared v, and subsequent powers.
The cyclic companion operator has ranks **1, 2, 3, 4, 5, 6, 7, 8**. The operator
with two equal Jordan blocks has ranks **1, 2, 3, 4, 4, 4, 4, 4**. The curves
coincide through the fourth vector; one then rises to the full dimension while
the other remains at four. The repeated blocks cannot be separated by this
single polynomial orbit.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-i/foundations-and-seed-rank.html#L1013)

<a id="figure-4-semisimple-multiplicity-and-seed-rank"></a>
<h2 id="figure-04" tabindex="-1">Figure 4: semisimple multiplicity and seed rank</h2>

The horizontal axis is multiplicity m, from 1 to 24. The vertical axis is the
simple-module dimension d, from 1 to 8. Every cell displays, by shading, the
least integer greater than or equal to m divided by d. The legend ranges from
one to twenty-four seeds. Along a row, the required count increases by one
whenever the multiplicity exceeds another multiple of d. Highlighted examples
are d = 8, m = 8: one seed; d = 4, m = 12: three seeds; d = 2, m = 16: eight
seeds; and d = 1, m = 24: twenty-four seeds. This is the displayed split simple
block formula under the manuscript’s semisimple hypotheses.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-i/foundations-and-seed-rank.html#L867)

<a id="figure-5-one-seed-for-path-adjacency"></a>
<h2 id="figure-05" tabindex="-1">Figure 5: one seed for path adjacency</h2>

A six-vertex path illustrates a seed at its first endpoint. Beneath it, a plot
has number of vertices on the horizontal axis and adjacency seed rank on the
vertical axis. Every plotted path size from **2 through 20** has rank **1**,
so all points lie on a horizontal line. Repeated application of the adjacency
operator to an endpoint reaches a new furthest vertex at each step. The
finite plot illustrates the manuscript’s general endpoint argument; the
plotted cases alone are not its proof.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-i/worked-models.html#L359)

<a id="figure-6-two-seeds-for-cycle-adjacency"></a>
<h2 id="figure-06" tabindex="-1">Figure 6: two seeds for cycle adjacency</h2>

A six-vertex cycle accompanies a plot of cycle sizes **3 through 20**. The
horizontal axis is number of vertices; the vertical axis is adjacency seed
rank. Every plotted point has rank **2**. The annotation identifies a largest
eigenspace of dimension two, which a single adjacency-polynomial orbit cannot
span. Read this with the complex-field hypotheses in the accompanying cycle
result. The figure concerns the undirected adjacency operator, not a directed
cyclic shift.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-i/worked-models.html#L402)

<a id="figure-7-periodic-shift-through-six-residue-packets"></a>
<h2 id="figure-07" tabindex="-1">Figure 7: periodic shift through six residue packets</h2>

The left panel is a six-by-six support matrix for a periodic shift on
twenty-four coordinates. Both axes are numbered 0 through 5; columns are input
packets and rows are output packets. The only ones are at output/input pairs
**(1,0), (2,1), (3,2), (4,3), (5,4), (0,5)**. All other entries are zero. A one
means a nonzero block, rather than a numerical value for the whole block.
The right panel draws the same routing as the directed cycle
**0 → 1 → 2 → 3 → 4 → 5 → 0**. This finite periodic model is distinct from the
infinite bilateral shift, whose phase-boundary block retains an address shift;
see atlas plate 19 below.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-i/worked-models.html#L241)

<a id="figure-8-multiplication-by-y-exchanges-two-packets"></a>
<h2 id="figure-08" tabindex="-1">Figure 8: multiplication by y exchanges two packets</h2>

The coordinate algebra is described by the relation **y squared = x cubed − x**.
Its two coefficient lanes are the even packet k[x] and the odd packet yk[x].
The transfer matrix has first row **0, x cubed − x** and second row **1, 0**;
columns are inputs and rows are outputs. A directed arrow from even to odd has
weight one. The return arrow from odd to even has weight x cubed − x. There
are no within-packet arrows for one application of multiplication by y.
Two applications multiply each packet by x cubed − x, matching the relation.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-i/worked-models.html#L130)

<a id="figure-9-projector-products-after-a-change-of-basis"></a>
<h2 id="figure-09" tabindex="-1">Figure 9: projector products after a change of basis</h2>

This numerical heatmap records Frobenius norms of products of transported
projectors Q_i Q_j. There are three four-dimensional packets in a
twelve-dimensional space. Diagonal entries are **12.16, 16.02 and 17.31**.
The off-diagonal entries, by output row, are:

- Row 1: column 2 is 1.5 × 10⁻¹⁴; column 3 is 2.2 × 10⁻¹⁴.
- Row 2: column 1 is 1.2 × 10⁻¹⁴; column 3 is 2.3 × 10⁻¹⁴.
- Row 3: column 1 is 1.5 × 10⁻¹⁴; column 2 is 1.7 × 10⁻¹⁴.

The displayed exact identities are Q_i = U P_i U inverse, Q_i squared = Q_i,
and Q_i Q_j = zero for different indices. A nonorthogonal change of coordinates
can give large projector norms. The tiny off-diagonal numerical values are
roundoff in this illustration, rather than nonzero terms in the exact identity.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-i/transport-and-realization.html#L369)

<a id="figure-10-two-proof-families-meet-in-the-worked-models"></a>
<h2 id="figure-10" tabindex="-1">Figure 10: two proof families meet in the worked models</h2>

Two left-to-right chains converge on one **Worked realizations** box. The
generator chain is **Fixed operator grammar → Hulls and presentations →
Generator counts and bounds**. The packet chain is **Finite projector system
→ Analysis and synthesis → Blocks and transport**. Each final box points to
the shared worked-realization box. Three formulas below identify coordinate
transport of projectors, an intertwining relation, and a block obtained by
selecting input and output packets around an operator. This is a structural
overview of the arguments, not an exhaustive dependency graph of Lean
declarations.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-i/worked-models.html#L454)

## Visual atlas: twenty-two plates

The original atlas occupies **PDF pages 83–104**, labelled **75–96** in the
printed manuscript. The descriptions below follow its plate order. Page links
open the original PDF at the corresponding page. The atlas’s surrounding
explanations and hypotheses remain part of the reading.

<a id="plate-1-what-can-one-seed-actually-do"></a>
<h2 id="atlas-01" tabindex="-1">Plate 1: what can one seed actually do?</h2>

Four rows compare minimum seed counts for the same six-dimensional rational
space. Scalar multiples of the identity require **6** seeds. Polynomials in
two equal nilpotent chains require **2**. Adding the two chain projectors to
that grammar lowers the count to **1**. The full six-by-six matrix algebra
also requires **1**. Filled squares count seeds; they do not measure runtime.
The point of the comparison is that the admissible algebra changes while the
ambient space stays fixed.

[Original plate 1](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=83)

<a id="plate-2-an-atlas-of-the-objects"></a>
<h2 id="atlas-02" tabindex="-1">Plate 2: an atlas of the objects</h2>

A three-column table pairs each symbol with its role and a concrete example.
The space X supplies possible target vectors; S supplies seeds; the fixed
algebra supplies allowed operations; and the hull is their invariant linear
span. Projectors extract packet spaces, while a transfer block specifies an
input packet, an operator and an output packet. A word quotient records seed
relations as a module. An invertible U changes coordinates; an intertwiner
need not be invertible. A topology specifies which limits are allowed.
The reading order for P_beta T P_alpha is right to left: extract alpha,
apply T, then extract beta.

[Original plate 2](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=84)

<a id="plate-3-two-chains-can-stay-linked"></a>
<h2 id="atlas-03" tabindex="-1">Plate 3: two chains can stay linked</h2>

Two horizontal three-vertex chains run from e_0 to e_1 to e_2 to zero, and from
f_0 to f_1 to f_2 to zero. Vertical dotted pairings join corresponding positions.
They mean equal coefficients, not additional permitted arrows. Starting from
e_0 + f_0 gives e_1 + f_1, then e_2 + f_2, then zero. Thus the orbit spans three
directions. Allowing the chain projectors would separate the two heads and
produce all six directions, but that is a larger operator grammar.

[Original plate 3](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=85)

<a id="plate-4-a-quotient-proves-two-seeds-are-necessary"></a>
<h2 id="atlas-04" tabindex="-1">Plate 4: a quotient proves two seeds are necessary</h2>

A two-by-six matrix has its only nonzero entries in the first row’s e_0 column
and the second row’s f_0 column. Both entries are one. It keeps the two chain
heads and forgets the advanced positions. The induced action on this
two-dimensional quotient is scalar, so one seed’s image remains on a line.
The quotient therefore supplies a lower bound of two seeds. The two separate
chain heads attain that bound in the original space.

[Original plate 4](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=86)

<a id="plate-5-relations-identify-words-not-just-outputs"></a>
<h2 id="atlas-05" tabindex="-1">Plate 5: relations identify words, not just outputs</h2>

Three two-by-two matrices show C = E_12, B = E_21 and their product
CB = E_11. C has a one only in its upper-right cell, B only in its lower-left
cell, and CB only in its upper-left cell. C kills the first basis vector;
CB sends that vector to itself. Multiplying a seed-annihilating relation on
the right can therefore destroy it. The presentation quotient is a quotient
of left modules; a seed annihilator is not automatically a two-sided ideal.

[Original plate 5](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=87)

<a id="plate-6-a-reached-type-can-still-hide-a-direction"></a>
<h2 id="atlas-06" tabindex="-1">Plate 6: a reached type can still hide a direction</h2>

Five slots are grouped as two directions in U and three in V. In the first
row, a seed supported at U fills both U slots and only the first two V slots:
the generated dimension is **4**. Adding the missing V direction fills all
five slots. A third row shows that one mixed seed also fills all five when
vertex projectors are admissible. Reaching a vertex type, filling its space,
and minimizing the unrestricted number of seeds are different questions.

[Original plate 6](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=88)

<a id="plate-7-exact-does-not-mean-orthogonal"></a>
<h2 id="atlas-07" tabindex="-1">Plate 7: exact does not mean orthogonal</h2>

In a coordinate plane, one packet lies on the horizontal axis and the other
on the diagonal line. The vector x = (3,2) is the sum of Px = (1,0) and
Qx = (2,2); dashed sides complete their parallelogram. The packet directions
are not perpendicular. The squared norm of x is **13**, whereas the sum of
the two component squared norms is **9**. The picture illustrates exact
algebraic reconstruction without an energy-preserving orthogonal splitting.

[Original plate 7](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=89)

<a id="plate-8-a-transfer-block-has-an-input-and-an-output"></a>
<h2 id="atlas-08" tabindex="-1">Plate 8: a transfer block has an input and an output</h2>

Two three-by-three matrices show an operator and its square. The rows of T
are **(1,2,0), (0,1,3), (4,0,1)**. The rows of T squared are
**(1,4,6), (12,1,6), (8,8,1)**. Columns identify inputs and rows identify outputs.
The square sums products over intermediate packets. For example, entry (1,2)
is 1 times 2 plus 2 times 1, giving 4. Entry (1,3) is 2 times 3, giving 6.
These are actual signed coefficients, not a matrix of norms or a support graph.

[Original plate 8](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=90)

<a id="plate-9-two-visible-routes-can-cancel-exactly"></a>
<h2 id="atlas-09" tabindex="-1">Plate 9: two visible routes can cancel exactly</h2>

A diamond graph starts at e_1, branches to e_2 and e_3, then rejoins at e_4.
The first two arrows have weight +1. The e_2-to-e_4 arrow has weight +1,
while the e_3-to-e_4 arrow has weight −1. The two length-two contributions
cancel. The neighbouring Krylov matrix has columns e_1, e_2 + e_3 and zero,
so its rank is two. Every graph vertex is reachable, but the single-operator
hull does not span the four-dimensional space. Inserting a packet projector
between steps would change the allowed grammar.

[Original plate 9](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=91)

<a id="plate-10-which-zero-patterns-survive-multiplication"></a>
<h2 id="atlas-10" tabindex="-1">Plate 10: which zero patterns survive multiplication?</h2>

Three matrices compare an allowed support pattern, an offending product and
the transitive closure. The first allows the diagonal, 1-to-2 and 2-to-3, but
omits 1-to-3. Multiplying E_32 by E_21 produces E_31, outside that pattern.
Adding the missing position gives the lower-triangular support pattern.
Here a one means “allowed position,” not a fixed coefficient. For the universal
supported algebra on nonzero packet spaces, diagonal positions supply the
identity and transitive closure supplies all compositions.

[Original plate 10](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=92)

<a id="plate-11-move-the-packets-with-the-coordinates"></a>
<h2 id="atlas-11" tabindex="-1">Plate 11: move the packets with the coordinates</h2>

The top row shows T = diag(1,2), the shear with rows (1,1) and (0,1), and the
conjugated operator with rows (1,1) and (0,2). The transformed matrix gains an
off-diagonal entry. Beneath it, the transported projectors have rows
**(1,−1), (0,0)** and **(0,1), (0,1)**. Relative to these oblique packets the
cross-packet blocks are still zero. The packet maps must move with the
coordinates; a change in ordinary matrix sparsity alone does not describe a
change in packet routing.

[Original plate 11](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=93)

<a id="plate-12-shared-control-and-independent-control-differ"></a>
<h2 id="atlas-12" tabindex="-1">Plate 12: shared control and independent control differ</h2>

Both panels start from the mixed seed (1,1). Shared scalar action reaches only
the diagonal line, represented by points (a,a). Independent coordinate action
reaches the whole plane, represented by (a,b); the shading is only a finite
window of that plane. The corresponding seed counts are two for shared scalars
and one for independent scalars. In the independent direct-sum formula,
component seed lists can occupy the same positions, so the count is their
maximum rather than their sum.

[Original plate 12](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=94)

<a id="plate-13-how-much-row-space-can-one-seed-supply"></a>
<h2 id="atlas-13" tabindex="-1">Plate 13: how much row space can one seed supply?</h2>

Three two-by-five seed matrices cover columns 1 and 2, then 3 and 4, then 5.
Their cumulative orbit dimensions under left multiplication by two-by-two
matrices are **4, 8 and 10**. One seed has at most two independent row-space
directions, while the multiplicity space has dimension five. Three seeds are
therefore needed in this model. The displayed target matrix has rows
(1,2,3,4,5) and (6,7,8,9,10); its successive column pairs determine coefficients
that synthesize it from the three fixed seeds.

[Original plate 13](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=95)

<a id="plate-14-distinct-labels-let-one-polynomial-separate-chains"></a>
<h2 id="atlas-14" tabindex="-1">Plate 14: distinct labels let one polynomial separate chains</h2>

Two six-by-six Krylov matrices compare equal and distinct primary labels.
Two equal nilpotent three-chains give rank **3** for the mixed seed. Replacing
the second operator block by two times the identity plus the nilpotent block
gives determinant **512**, hence full rank six. This changes the operator,
not just its coordinates. The plate supplies a polynomial that is zero modulo
t cubed and one modulo (t−2) cubed; it separates the two chain heads using
operations already in the polynomial grammar.

[Original plate 14](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=96)

<a id="plate-15-walk-counts-make-an-endpoint-cyclic"></a>
<h2 id="atlas-15" tabindex="-1">Plate 15: walk counts make an endpoint cyclic</h2>

A five-vertex path marks vertex 1 as the seed. Under it, the five Krylov columns
count walks of lengths 0 through 4. The matrix rows are **(1,0,1,0,2)**,
**(0,1,0,2,0)**, **(0,0,1,0,3)**, **(0,0,0,1,0)** and **(0,0,0,0,1)**.
Every diagonal entry is one, and every entry below the diagonal is zero.
A vertex cannot be reached sooner than its distance from the endpoint, and
there is one shortest path. This is the unit-triangular structure used by the
general endpoint proof.

[Original plate 15](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=97)

<a id="plate-16-closing-a-path-changes-the-seed-obstruction"></a>
<h2 id="atlas-16" tabindex="-1">Plate 16: closing a path changes the seed obstruction</h2>

A six-vertex cycle highlights adjacent vertices 0 and 1 as a generating pair.
A bar chart gives eigenvalue multiplicities: **−2 has 1, −1 has 2, 1 has 2,
and 2 has 1**. These are exact dimensions, not estimated spectral peaks. A
single vertex seed spans four dimensions; the adjacent pair spans all six.
The plate’s two-row scalar quotient certifies why one arbitrary seed cannot
suffice, and the adjacency recurrence constructs the remaining vertices from
the pair.

[Original plate 16](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=98)

<a id="plate-17-a-relation-becomes-a-packet-product-rule"></a>
<h2 id="atlas-17" tabindex="-1">Plate 17: a relation becomes a packet product rule</h2>

Two infinite coefficient lanes are shown through degree four. The top lane is
**1, x, x squared, x cubed, x to the fourth, …**. The lower lane is
**y, xy, x squared y, x cubed y, x to the fourth y, …**. Higher powers of y are
rewritten using y squared = x cubed − x; they are not discarded. Each element
has the form a(x) + yb(x). Multiplication by y swaps the lanes, with the return
transfer weighted by x cubed − x. The diagram is about normal forms and
multiplication, not the genus or smoothness of a drawn algebraic curve.

[Original plate 17](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=99)

<a id="plate-18-density-is-not-finite-generation-of-each-vector"></a>
<h2 id="atlas-18" tabindex="-1">Plate 18: density is not finite generation of each vector</h2>

A stem plot shows the sequence x[n] = 2 to the power −|n|. It peaks at one at
zero and halves at each step away from zero in either direction. The shaded
window contains indices −3 through 3. Outside every finite window, entries
remain nonzero; the picture is not periodic wraparound. Truncating to indices
−N through N gives squared error two-thirds times 4 to the power −N. The
displayed errors for N = 1, 3 and 5 are **1/6, 1/96 and 1/1536**. Shifted impulses
give finite-support approximants whose norm limit is the infinite sequence.

[Original plate 18](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=100)

<a id="plate-19-residue-packets-retain-an-address-carry"></a>
<h2 id="atlas-19" tabindex="-1">Plate 19: residue packets retain an address carry</h2>

Three rows divide a window of integer addresses into residue classes modulo
three. Row 0 contains −6, −3, 0, 3 and 6; row 1 contains −5, −2, 1 and 4; row 2
contains −4, −1, 2 and 5. Each address belongs to exactly one row. Under one
shift, packet 0 moves to packet 1, packet 1 to packet 2, and packet 2 to packet
0 with a shift of the coarse address. In formulas, the new packet 0 at k uses
the old packet 2 at k−1. Replacing that boundary shift by a scalar would lose
information about the infinite sequence, even if the phase graph looked the same.

[Original plate 19](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=101)

<a id="plate-20-stop-when-the-subspace-stops-growing"></a>
<h2 id="atlas-20" tabindex="-1">Plate 20: stop when the subspace stops growing</h2>

The horizontal axis counts hull-expansion iterations; the vertical axis is
subspace dimension. Both curves start at dimension one for the same mixed
seed. The dashed curve allows only the nilpotent operator and plateaus at
dimension **3**. The solid curve also allows the chain projectors and reaches
dimension **6**. Repeated plateau values indicate the stop. Equality of
consecutive subspaces certifies invariance only after images under the whole
declared generating family have been included. The dimensions are exact,
rather than results of a numerical rank tolerance.

[Original plate 20](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=102)

<a id="plate-21-tensor-products-require-every-cross-term"></a>
<h2 id="atlas-21" tabindex="-1">Plate 21: tensor products require every cross term</h2>

A two-by-two coefficient rectangle expands the tensor product of
2e_1 + 3e_2 with 5f_1 + 7f_2. Rows correspond to e_1 and e_2; columns correspond
to f_1 and f_2. The first row is **10, 14**, and the second is **15, 21**.
All four basis tensors occur. Keeping only the diagonal entries would omit
both cross terms, 14 and 15. The full rectangular family gives the stated
product upper bound on algebraic tensor seed rank. It is not a universal
equality or a theorem about completed topological tensor products.

[Original plate 21](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=103)

<a id="plate-22-what-the-pictures-certify"></a>
<h2 id="atlas-22" tabindex="-1">Plate 22: what the pictures certify</h2>

A three-column table connects seven topics to their mathematical content and
the hypotheses that must remain attached. Presentations require a fixed
grammar. Finite packets require idempotence, annihilation and completeness;
orthogonality is additional. Semisimple counts require the specified
decomposition data. Primary and graph counts retain their field and
multiplicity conventions. Path and cycle proofs are distinct from finite
tests. Coordinate normal forms do not by themselves establish smooth
projective geometry. Completion requires its topology and boundedness
hypotheses. The accompanying text distinguishes written proofs, formal
contracts and executable records.

[Original plate 22](../papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf#page=104)

## Sources and coverage

Descriptions were checked against all ten rendered chapter figures, the
twenty-two rendered atlas plates, their captions and the retained atlas source.
They do not replace the manuscript’s arguments or add a mathematical review.
The existing PDF remains the reference for the original visual layout.

[Atlas source](../papers/paper-i/current/editable/traditional/visual_atlas.tex)
· [Paper I overview](works/paper-i.md)
