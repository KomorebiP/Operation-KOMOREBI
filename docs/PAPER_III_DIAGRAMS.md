# Paper III: figure and atlas descriptions

These reading aids describe the 6 chapter figures, including their arrows, axes, scales and matrix entries. They retain the assumptions and example scope of the manuscript.

[Read the chapters](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iii/index.html) · [Accessibility and reading options](ACCESSIBILITY.md)

<a id="figure-1-typed-edge-words-and-directed-walks"></a>
<h2 id="figure-01" tabindex="-1">Figure 1: Typed edge words and directed walks</h2>

The left panel follows P₀→P₁→P₂→P₃ through edges e₁, e₂, e₃. The written operator product is Lₑ₃Lₑ₂Lₑ₁ because the rightmost factor acts first. Its only possible endpoint block is output 3, input 0. On the right, e maps Pᵢ to Pⱼ and f maps Pℓ to Pₖ, with j≠ℓ. Their intermediate types do not match, so L_f L_e=0. Rows are targets and columns are sources.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iii/finite-coordinates.html#L156)

<a id="figure-2-coordinate-transport-and-chosen-connection"></a>
<h2 id="figure-02" tabindex="-1">Figure 2: Coordinate transport and chosen connection</h2>

Both triangles traverse a→b→c→a. On the left, exact analysis and synthesis define J; the loop product Jₐ←c J_c←b J_b←a is identity by cancellation of coordinate maps. On the right, the independently chosen connection Γ has holonomy H=Γₐ←c Γ_c←b Γ_b←a. A gauge change at the base sends H to GₐHGₐ⁻¹. The matching arrow shapes do not identify these two kinds of transport.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iii/connections-and-obstructions.html#L88)

<a id="figure-3-holonomy-obstruction-blocks"></a>
<h2 id="figure-03" tabindex="-1">Figure 3: Holonomy obstruction blocks</h2>

The grid has output packet μ on the rows and input packet ν on the columns, each from 0 to 3. Its cell is Ob^{μν}=Πμ(H−id)Πν. The highlighted row 1, column 3 is a conditional mixing witness: if this map is nonzero, some input in packet 3 produces a nonzero obstruction in packet 1. The shading assigns no numerical block value. Completeness gives Ob=Σμ,ν Ob^{μν}; the total obstruction vanishes exactly when all these blocks vanish.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iii/connections-and-obstructions.html#L540)

<a id="figure-4-two-exact-packet-hessians"></a>
<h2 id="figure-04" tabindex="-1">Figure 4: Two exact packet Hessians</h2>

The first derivative at the origin is identity. Each two-by-two grid lists ordered input slots x and y along both rows and columns. The first output retains both mixed Hessian entries; the second has only the repeated x-input entry. The tables below give every entry. Consequently D²F(0)[h,k]=(hₓkᵧ+hᵧkₓ,2hₓkₓ), and one half of D²F(0)[h,h] is (hₓhᵧ,hₓ²). The factor one half and both mixed slots are retained. All higher jets vanish for this degree-two model.

<table>
<caption>Figure 4: Two exact packet Hessians</caption>
<thead><tr><th scope="col">Output</th><th scope="col">First input slot</th><th scope="col">Second slot x</th><th scope="col">Second slot y</th></tr></thead>
<tbody>
<tr><th scope="row">1</th><td>x</td><td>0</td><td>1</td></tr>
<tr><th scope="row">1</th><td>y</td><td>1</td><td>0</td></tr>
<tr><th scope="row">2</th><td>x</td><td>2</td><td>0</td></tr>
<tr><th scope="row">2</th><td>y</td><td>0</td><td>0</td></tr>
</tbody>
</table>

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iii/nonlinear-coordinates.html#L250)

<a id="figure-5-correctable-defect-and-cokernel-residual"></a>
<h2 id="figure-05" tabindex="-1">Figure 5: Correctable defect and cokernel residual</h2>

In the coordinate plane, L(a,b)=(a,0), so its image is the horizontal axis. The diagonal arrow is d=(2,3), the horizontal arrow is (2,0), and the vertical arrow is (0,3); dashed guides join them. Choosing u=(−2,0) removes the horizontal component and leaves d+Lu=(0,3). The functional ℓ(x,y)=y vanishes on the image of L but takes value 3 on d. Thus Lu=−d has no solution in this example. The drawing uses the standard Euclidean splitting and the displayed quotient identification.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iii/nonlinear-coordinates.html#L943)

<a id="figure-6-a-rotating-line-and-its-complement"></a>
<h2 id="figure-06" tabindex="-1">Figure 6: A rotating line and its complement</h2>

Solid lines show the rank-one packet P(θ)=uθuθᵀ with uθ=(cos θ,sin θ). Dashed lines show Q(θ)=I−P(θ). The marked motion runs counterclockwise from θ=0 to π/3. The continuous generator has rows (0,−1) and (1,0), so U(θ)=R(θ). For a step δ with |δ|<π/2, the comparison S=cos δ R(δ) has polar factor R(δ). The mesh table below lists the three products. Their exact equality is special to this circular model; the general theorem concerns convergence for broader paths.

<table>
<caption>Figure 6: A rotating line and its complement</caption>
<thead><tr><th scope="col">Steps</th><th scope="col">Each increment</th><th scope="col">Ordered product</th></tr></thead>
<tbody>
<tr><th scope="row">2</th><td>π/6</td><td>R(π/3)</td></tr>
<tr><th scope="row">4</th><td>π/12</td><td>R(π/3)</td></tr>
<tr><th scope="row">8</th><td>π/24</td><td>R(π/3)</td></tr>
</tbody>
</table>

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iii/correction-and-transport.html#L1048)

## Visual atlas

The following descriptions cover all 24 atlas pages. The two orientation and evidence pages contain tables rather than drawings. [Open the original visual guide PDF](../papers/paper-iii/current/publication/Paper_III_Visual_Guide_v1.0.0.pdf).

<a id="atlas-page-1-three-objects-three-different-questions"></a>
<h3 id="atlas-01" tabindex="-1">Atlas page 1: Three objects, three different questions</h3>

Three panels distinguish a typed matrix transfer, coordinates of one ambient vector in different frames, and a chosen loop transport that can be a shear. A typed product can vanish when adjacent packets do not match. Canonical coordinate changes cancel on a loop. A separately chosen connection can instead have nonidentity holonomy. Similar-looking arrows do not make these three maps the same object.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L1)

<a id="atlas-page-2-an-atlas-of-the-objects"></a>
<h3 id="atlas-02" tabindex="-1">Atlas page 2: An atlas of the objects</h3>

The orientation table identifies objects by their source, target and role. In particular, a discrepancy between two routes from C_a to C_c is not yet an endomorphism of C_a. Turning it into a holonomy obstruction at the base requires the specified inverse return transport. The table also distinguishes packet blocks, input labels in a tree, and the chosen semantics of operation symbols.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L17)

<a id="atlas-page-3-read-the-product-in-execution-order"></a>
<h3 id="atlas-03" tabindex="-1">Atlas page 3: Read the product in execution order</h3>

The grids use target rows and source columns numbered 0,1,2. The first edge 0→1 has matrix 2E₁₀ and the second edge 1→2 has matrix 3E₂₁. Executing them in that order gives the written product L_f L_e=6E₂₀. Reversing the order breaks the intermediate type and gives zero. The first product sends (x₀,x₁,x₂) to (0,0,6x₀).

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L44)

<a id="atlas-page-4-all-sixteen-words-only-five-walks"></a>
<h3 id="atlas-04" tabindex="-1">Atlas page 4: All sixteen words, only five walks</h3>

The four edge labels are a:0→1 with coefficient 2, b:0→1 with coefficient −1, c:1→2 with coefficient 3, and d:2→0 with coefficient 1. Columns of the four-by-four board select the first executed edge and rows select the second. Only the chronological words ac, bc, cd, da and db survive; their coefficients are 6, −3, 3, 2 and −1. Crosses mark the other eleven type mismatches. Parallel a and b remain distinct before their contributions are added.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L69)

<a id="atlas-page-5-coefficients-need-not-commute"></a>
<h3 id="atlas-05" tabindex="-1">Atlas page 5: Coefficients need not commute</h3>

The two coefficient matrices are A with rows (1,1),(0,1), and B with rows (1,0),(1,1). The coefficient for traversing A then B is BA with rows (1,1),(1,2). Reversing it gives AB with rows (2,1),(1,1). On input (1,0), these produce (1,1) and (2,1), respectively. All entries are exact integers, so the difference does not rely on a numerical tolerance or on commutativity.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L86)

<a id="atlas-page-6-a-reachable-packet-can-receive-zero"></a>
<h3 id="atlas-06" tabindex="-1">Atlas page 6: A reachable packet can receive zero</h3>

Two directed routes connect packet 0 to packet 3 through packets 1 and 2. The dashed edge is an actual edge of coefficient −1. The two route contributions cancel, although the unsigned walk count is two. A visible path therefore supplies an upper bound on possible support; it does not guarantee a nonzero entry of the summed operator.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L112)

<a id="atlas-page-7-reachability-is-only-an-upper-bound"></a>
<h3 id="atlas-07" tabindex="-1">Atlas page 7: Reachability is only an upper bound</h3>

The orbit-column matrix begins with e₀, then e₁+e₂, followed by zeros. Its span consists exactly of (a,b,b,0,0), so the orbit hull has dimension two. Four coordinates are graph-reachable, while packet 4 is isolated. Packet 3 is absent because of cancellation, and the two reachable middle coordinates remain linked under powers of the single summed operator. Allowing individual edges would be a different generation problem.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L135)

<a id="atlas-page-8-paths-through-changing-packet-lists"></a>
<h3 id="atlas-08" tabindex="-1">Atlas page 8: Paths through changing packet lists</h3>

The packet-list sizes change as 2→3→2→1 under A, B and C. For each input, the lower board lists all six choices of intermediate indices and includes zero terms. The final row is CBA=(−4,6). The contributions for input 0 are 2,−4,0,0,−2,0; for input 1 they are 0,−2,12,0,−1,−3. These are ordered signed matrix contributions rather than probabilities or unsigned path counts.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L156)

<a id="atlas-page-9-one-vector-three-exact-frames"></a>
<h3 id="atlas-09" tabindex="-1">Atlas page 9: One vector, three exact frames</h3>

Three coordinate planes represent the same ambient vector (3,2). Their synthesis frames are F₀=I, F₁ with rows (1,1),(0,1), and F₂ with rows (2,0),(1,1). The coordinate arrows are (3,2), (1,2), and (3/2,1/2). Multiplying each by its frame recovers (3,2). The transport F_b⁻¹F_a cancels intermediate frames, so either route and every return loop are exact even though the frames need not preserve angles.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L179)

<a id="atlas-page-10-nonlinear-charts-still-cancel-exactly"></a>
<h3 id="atlas-10" tabindex="-1">Atlas page 10: Nonlinear charts still cancel exactly</h3>

A square-like coordinate grid is mapped by A(x,y)=(x,y+x²): horizontal lines become parabolas. The inverse is S(u,v)=(u,v−u²). For the operation F(x,y)=(x+y,xy), the correctly changed formula is AFS, rather than a reused copy of F. At input (1,2), both routes give new-chart output (3,11). The sampled boundaries visualize exact polynomial inverse and route identities.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L205)

<a id="atlas-page-11-reversibility-is-a-real-hypothesis"></a>
<h3 id="atlas-11" tabindex="-1">Atlas page 11: Reversibility is a real hypothesis</h3>

Both rows use forward scalar transports 2, 3 and direct comparison 5. The first chooses return 1/6 and produces loop value 1, even though the forward cocycle discrepancy is 3·2−5=1. That return is not the inverse of 5. The reversible row instead returns by 1/5 and produces holonomy 6/5. Self-transport equal to identity and an inverse condition on reversed edges are separate assumptions.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L227)

<a id="atlas-page-12-measure-the-mismatch-at-its-base"></a>
<h3 id="atlas-12" tabindex="-1">Atlas page 12: Measure the mismatch at its base</h3>

The triangle compares a two-step multiplier 3·2=6 with the specified dashed direct multiplier 5. Returning by 1/5 changes their target discrepancy into the base obstruction 1/5, with holonomy 6/5. On input 5, the target outputs are 30 and 25; after return they are 6 and 5. The repeated-loop table records exact powers of 6/5, not an analytic convergence claim.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L247)

<a id="atlas-page-13-the-identity-can-hide-in-the-spectrum"></a>
<h3 id="atlas-13" tabindex="-1">Atlas page 13: The identity can hide in the spectrum</h3>

The dashed unit square and its solid sheared image are related by H with rows (1,1),(0,1). The vector e₁=(0,1) moves to (1,1), so its displacement is e₀. Although trace 2, determinant 1 and eigenvalues both 1 match the identity matrix, H−I=E₀₁ is nonzero. The explicit moved vector is the obstruction witness.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L268)

<a id="atlas-page-14-gauge-changes-the-picture-not-flatness"></a>
<h3 id="atlas-14" tabindex="-1">Atlas page 14: Gauge changes the picture, not flatness</h3>

The two parallelograms are exact images of a unit square before and after the gauge D=diag(2,1). Conjugation changes the upper-right shear entry from 1 to 2. The obstruction has Frobenius norm 1 in the first fixed coordinate basis and 2 in the second, while both obstructions have rank one and are nonzero. A nonorthogonal gauge can change this numerical size without changing whether the loop is identity.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L295)

<a id="atlas-page-15-flat-is-not-the-same-as-calibrated"></a>
<h3 id="atlas-15" tabindex="-1">Atlas page 15: Flat is not the same as calibrated</h3>

Three rulers have chosen scale factors g₀=1, g₁=2 and g₂=3; their marks are g_a times integers. Relative transport is the target scale divided by the source scale. Thus 0→1 multiplies by 2, 1→2 by 3/2, and 0→2 by 3. The products agree, so this connection is flat, although its edges differ from the original canonical identity transports. The rulers show supplied gauge factors rather than an intrinsic metric.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L323)

<a id="atlas-page-16-resolve-the-entire-obstruction"></a>
<h3 id="atlas-16" tabindex="-1">Atlas page 16: Resolve the entire obstruction</h3>

The three-by-three obstruction board uses output rows μ and input columns ν. For H=I+2E₀₁+3E₁₂, the only nonzero blocks of H−I are row 0, column 1 with coefficient 2 and row 1, column 2 with coefficient 3. On input (4,5,6), they contribute (10,0,0) and (0,18,0). Adding all nine embedded blocks reconstructs the full displacement. The basis inputs e₁ and e₂ separately witness the two nonzero transfers.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L350)

<a id="atlas-page-17-why-diagonal-checks-are-insufficient"></a>
<h3 id="atlas-17" tabindex="-1">Atlas page 17: Why diagonal checks are insufficient</h3>

For obstruction E₀₁, both diagonal blocks in the standard coordinate resolution are zero, but row 0, column 1 remains nonzero. Omitting the second packet would miss the same obstruction. A separate pair of oblique projectors still sums to identity and reconstructs every block exactly, even though the projectors are not symmetric in the Euclidean inner product. The test must cover both source and target packets of a complete resolution.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L372)

<a id="atlas-page-18-a-gauge-can-move-every-packet-label"></a>
<h3 id="atlas-18" tabindex="-1">Atlas page 18: A gauge can move every packet label</h3>

The first fixed-coordinate matrix is E₀₁, with one nonzero entry. With mixing gauge G having rows (1,0),(1,1), its conjugate has rows (−1,1),(−1,1), with four nonzero entries. Both have rank one. Thus individual labels in the fixed packet grid can change their zero status. Transporting the projectors as Q_i=GP_iG⁻¹ restores the corresponding block-by-block conjugacy relation.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L397)

<a id="atlas-page-19-an-obstruction-rejects-one-candidate"></a>
<h3 id="atlas-19" tabindex="-1">Atlas page 19: An obstruction rejects one candidate</h3>

The residual table uses candidate columns and two equation rows: x²−1 and x−1. At x=−1 the first residual is 0 but the second is −2; at x=1 both are 0. Shading marks a nonzero residual for that particular candidate. The example distinguishes an obstruction to one candidate from the stronger claim that every candidate is obstructed; x=1 is a counterexample to the latter claim.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L422)

<a id="atlas-page-20-a-tree-reads-its-named-leaves"></a>
<h3 id="atlas-20" tabindex="-1">Atlas page 20: A tree reads its named leaves</h3>

The rooted syntax tree evaluates (x²+3)−y. Child-to-parent arrows mean evaluation, and the two subtraction slots stay ordered. At x=2,y=5, the square node gives 4, addition gives 7, and the root gives 2. Only named input leaves x and y are read. This syntactic locality does not assert minimal semantic dependence: for example the tree x−x names x even though its value is always zero.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L447)

<a id="atlas-page-21-where-a-nonlinear-defect-can-enter"></a>
<h3 id="atlas-21" tabindex="-1">Atlas page 21: Where a nonlinear defect can enter</h3>

The solid parabola is 2x² and the dashed one is 4x², with horizontal input x and vertical output value. They compare transporting the output of f(x)=x² by multiplication by 2 with applying the same formula after transporting the input. Their route difference is −2x². Under a consistent coordinate change v=2x, the target formula is instead v²/2, which restores equality. A chosen incompatible rule, rather than nonlinearity alone, causes this defect.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L466)

<a id="atlas-page-22-mixed-terms-are-not-optional"></a>
<h3 id="atlas-22" tabindex="-1">Atlas page 22: Mixed terms are not optional</h3>

The rectangle has horizontal pieces of lengths 2 and 3 and vertical pieces 5 and 7, with separately scaled display units. Its four cell products are 10, 15, 14 and 21, totaling 60. Keeping only the matching-label cells 10 and 21 gives 31 and loses the mixed contributions 15 and 14. The nearby unary-square comparison similarly retains its mixed term 2ab. Distributive expansion needs the stated multilinearity and slot types.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L487)

<a id="atlas-page-23-from-loop-data-to-a-packet-witness"></a>
<h3 id="atlas-23" tabindex="-1">Atlas page 23: From loop data to a packet witness</h3>

The top calculation follows a reversible connection through A, then B, then inverse direct map C⁻¹ with C=I. Its holonomy has rows (1,1),(1,2), and the defect has rows (0,1),(1,1). The vector row starts at e₀=(1,0) and returns as (1,1), leaving displacement e₁. Thus output packet 1, input packet 0 supplies a concrete nonflatness witness. Replacing C by BA repairs these data by changing the connection; it is not a gauge transformation of the original nonflat one.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L506)

<a id="atlas-page-24-read-the-evidence-with-the-pictures"></a>
<h3 id="atlas-24" tabindex="-1">Atlas page 24: Read the evidence with the pictures</h3>

The evidence page separates finite worked examples, ordinary proofs in the traditional paper, and the inherited finite Lean contract. The 22 drawings illustrate exact finite mechanisms across the 24 pages. Input locality for syntax trees is narrower than a general nonlinear chain rule or analytic stability theorem. The evidence rows preserve these scopes rather than treating every diagram as a formal verification of every related claim.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-iii/current/manuscript/visual_atlas.tex#L528)
