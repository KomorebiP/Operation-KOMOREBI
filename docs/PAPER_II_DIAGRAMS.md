# Paper II: figure and atlas descriptions

These reading aids describe the 13 chapter figures, including their arrows, axes, scales and matrix entries. They retain the assumptions and example scope of the manuscript.

[Read the chapters](https://komorebip.github.io/Operation-KOMOREBI/read/paper-ii/index.html) · [Accessibility and reading options](ACCESSIBILITY.md)

<a id="figure-1-nested-dyadic-residue-addresses"></a>
<h2 id="figure-01" tabindex="-1">Figure 1: Nested dyadic residue addresses</h2>

Three horizontal levels contain residues modulo 2, 4 and 8. At the top, residue 0 branches to 0 and 2 modulo 4, while residue 1 branches to 1 and 3. Each middle node r branches to r and r+4 modulo 8. The bottom display order is 0, 4, 2, 6, 1, 5, 3, 7, which keeps siblings adjacent. Lines express exact parent membership; they do not average or interpolate coefficient values.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-ii/refinement-and-residue-coordinates.html#L209)

<a id="figure-2-two-coordinates-for-a-residue-modulo-24"></a>
<h2 id="figure-02" tabindex="-1">Figure 2: Two coordinates for a residue modulo 24</h2>

Rows are residues modulo 3, from 0 to 2; columns are residues modulo 8, from 0 to 7. The cell contains the unique residue modulo 24 having both addresses. All 24 addresses occur once.

<table>
<caption>Figure 2: Two coordinates for a residue modulo 24</caption>
<thead><tr><th scope="col">Residue mod 3 / residue mod 8</th><th scope="col">0</th><th scope="col">1</th><th scope="col">2</th><th scope="col">3</th><th scope="col">4</th><th scope="col">5</th><th scope="col">6</th><th scope="col">7</th></tr></thead>
<tbody>
<tr><th scope="row">0</th><td>0</td><td>9</td><td>18</td><td>3</td><td>12</td><td>21</td><td>6</td><td>15</td></tr>
<tr><th scope="row">1</th><td>16</td><td>1</td><td>10</td><td>19</td><td>4</td><td>13</td><td>22</td><td>7</td></tr>
<tr><th scope="row">2</th><td>8</td><td>17</td><td>2</td><td>11</td><td>20</td><td>5</td><td>14</td><td>23</td></tr>
</tbody>
</table>

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-ii/refinement-and-residue-coordinates.html#L536)

<a id="figure-3-exact-refinement-incidence"></a>
<h2 id="figure-03" tabindex="-1">Figure 3: Exact refinement incidence</h2>

Rows are coarse residues modulo 4 and columns are fine residues modulo 12. An entry is 1 exactly when the column address reduces to the row address modulo 4; all other entries are 0. The nonzero columns are listed below. Every column has one parent and every row has three children. Applied to complete packet vectors, these rows specify exact regrouping.

<table>
<caption>Figure 3: Exact refinement incidence</caption>
<thead><tr><th scope="col">Coarse residue mod 4</th><th scope="col">Fine residues mod 12 with entry 1</th></tr></thead>
<tbody>
<tr><th scope="row">0</th><td>0, 4, 8</td></tr>
<tr><th scope="row">1</th><td>1, 5, 9</td></tr>
<tr><th scope="row">2</th><td>2, 6, 10</td></tr>
<tr><th scope="row">3</th><td>3, 7, 11</td></tr>
</tbody>
</table>

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-ii/refinement-and-residue-coordinates.html#L276)

<a id="figure-4-weighted-transfer-graph"></a>
<h2 id="figure-04" tabindex="-1">Figure 4: Weighted transfer graph</h2>

Read each arrow from source to target. The table lists all six directed edges; each has multiplicity one. The weight is filtration gain, separate from the number of edges traversed. The walk-count example begins at packet 0 and ends at packet 2.

<table>
<caption>Figure 4: Weighted transfer graph</caption>
<thead><tr><th scope="col">Source</th><th scope="col">Target</th><th scope="col">Filtration weight</th></tr></thead>
<tbody>
<tr><th scope="row">0</th><td>0</td><td>2</td></tr>
<tr><th scope="row">0</th><td>1</td><td>1</td></tr>
<tr><th scope="row">1</th><td>1</td><td>3</td></tr>
<tr><th scope="row">1</th><td>2</td><td>2</td></tr>
<tr><th scope="row">2</th><td>0</td><td>1</td></tr>
<tr><th scope="row">2</th><td>2</td><td>4</td></tr>
</tbody>
</table>

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-ii/weighted-transfer.html#L265)

<a id="figure-5-counts-of-weighted-walks"></a>
<h2 id="figure-05" tabindex="-1">Figure 5: Counts of weighted walks</h2>

The horizontal axis is total walk weight, from 0 through 36. The vertical axis is the number of directed walks, including loops and repeated visits. Its symmetric logarithmic scale is logarithmic above 1 and retains zero. These are exact integer counts for Figure 4, transcribed below. They count walks, not the signed value of an operator sum.

<table>
<caption>Figure 5: Counts of weighted walks</caption>
<thead><tr><th scope="col">Total weight</th><th scope="col">Exact walk count</th></tr></thead>
<tbody>
<tr><th scope="row">0</th><td>0</td></tr>
<tr><th scope="row">1</th><td>0</td></tr>
<tr><th scope="row">2</th><td>0</td></tr>
<tr><th scope="row">3</th><td>1</td></tr>
<tr><th scope="row">4</th><td>0</td></tr>
<tr><th scope="row">5</th><td>1</td></tr>
<tr><th scope="row">6</th><td>1</td></tr>
<tr><th scope="row">7</th><td>3</td></tr>
<tr><th scope="row">8</th><td>1</td></tr>
<tr><th scope="row">9</th><td>5</td></tr>
<tr><th scope="row">10</th><td>4</td></tr>
<tr><th scope="row">11</th><td>10</td></tr>
<tr><th scope="row">12</th><td>7</td></tr>
<tr><th scope="row">13</th><td>19</td></tr>
<tr><th scope="row">14</th><td>17</td></tr>
<tr><th scope="row">15</th><td>37</td></tr>
<tr><th scope="row">16</th><td>34</td></tr>
<tr><th scope="row">17</th><td>72</td></tr>
<tr><th scope="row">18</th><td>74</td></tr>
<tr><th scope="row">19</th><td>141</td></tr>
<tr><th scope="row">20</th><td>151</td></tr>
<tr><th scope="row">21</th><td>278</td></tr>
<tr><th scope="row">22</th><td>316</td></tr>
<tr><th scope="row">23</th><td>548</td></tr>
<tr><th scope="row">24</th><td>646</td></tr>
<tr><th scope="row">25</th><td>1088</td></tr>
<tr><th scope="row">26</th><td>1328</td></tr>
<tr><th scope="row">27</th><td>2159</td></tr>
<tr><th scope="row">28</th><td>2707</td></tr>
<tr><th scope="row">29</th><td>4304</td></tr>
<tr><th scope="row">30</th><td>5518</td></tr>
<tr><th scope="row">31</th><td>8583</td></tr>
<tr><th scope="row">32</th><td>11209</td></tr>
<tr><th scope="row">33</th><td>17161</td></tr>
<tr><th scope="row">34</th><td>22746</td></tr>
<tr><th scope="row">35</th><td>34335</td></tr>
<tr><th scope="row">36</th><td>46079</td></tr>
</tbody>
</table>

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-ii/weighted-transfer.html#L572)

<a id="figure-6-finite-filtration-cutoff"></a>
<h2 id="figure-06" tabindex="-1">Figure 6: Finite filtration cutoff</h2>

The horizontal axis is precision L, from 1 through 12. The vertical axis is the largest integer word weight below L. The plotted points are (1,0), (2,1), and successive pairs through (12,11). The step line represents the support cutoff L−1. It does not count how many walks survive; algebraic relations can make additional terms zero.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-ii/weighted-transfer.html#L360)

<a id="figure-7-rational-sign-projectors"></a>
<h2 id="figure-07" tabindex="-1">Figure 7: Rational sign projectors</h2>

For the integral involution A with rows (1,1) and (0,−1), the left matrix is E₊=(I+A)/2 and the right is E₋=(I−A)/2. Their exact entries are given below. Each is idempotent, their products in either order vanish, and their sum is I. Both have denominator weight one at the prime 2 on the specified standard lattice.

<table>
<caption>Figure 7: Rational sign projectors</caption>
<thead><tr><th scope="col">Projector</th><th scope="col">Row</th><th scope="col">Column 0</th><th scope="col">Column 1</th></tr></thead>
<tbody>
<tr><th scope="row">E₊</th><td>0</td><td>1</td><td>1/2</td></tr>
<tr><th scope="row">E₊</th><td>1</td><td>0</td><td>0</td></tr>
<tr><th scope="row">E₋</th><td>0</td><td>0</td><td>-1/2</td></tr>
<tr><th scope="row">E₋</th><td>1</td><td>0</td><td>1</td></tr>
</tbody>
</table>

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-ii/integral-separation.html#L638)

<a id="figure-8-the-prime-two-and-denominator-weight"></a>
<h2 id="figure-08" tabindex="-1">Figure 8: The prime two and denominator weight</h2>

The horizontal axis lists the coefficient primes 2, 3, 5, 7 and 11. The vertical axis is the denominator weight vₚ(2) of each sign projector in Figure 7. The only positive bar has height 1 at prime 2. The four labeled points at odd primes have height 0 because 2 is a unit there.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-ii/integral-separation.html#L674)

<a id="figure-9-propagation-of-a-refinement-defect"></a>
<h2 id="figure-09" tabindex="-1">Figure 9: Propagation of a refinement defect</h2>

The horizontal axis is operator power n, from 1 through 12. The vertical axis is spectral norm on a logarithmic scale. Circles trace the measured defect and squares trace its telescoping bound. They agree at the first power, about 0.03, then separate: the measured error decreases while the bound grows. The delivered model uses three coarse coordinates with values 0.4, 0.8 and 1.3, three fine children each, averaging by one third, and a 0.09 perturbation in the first fine diagonal entry. The bound is valid but loose in this example.

<table>
<caption>Figure 9: Propagation of a refinement defect</caption>
<thead><tr><th scope="col">Power</th><th scope="col">Measured defect</th><th scope="col">Telescoping bound</th></tr></thead>
<tbody>
<tr><th scope="row">1</th><td>0.03</td><td>0.03</td></tr>
<tr><th scope="row">2</th><td>0.0267</td><td>0.078</td></tr>
<tr><th scope="row">3</th><td>0.017883</td><td>0.1521</td></tr>
<tr><th scope="row">4</th><td>0.0106827</td><td>0.26364</td></tr>
<tr><th scope="row">5</th><td>0.00600251</td><td>0.428415</td></tr>
<tr><th scope="row">6</th><td>0.00324843</td><td>0.668327</td></tr>
<tr><th scope="row">7</th><td>0.00171461</td><td>1.01363</td></tr>
<tr><th scope="row">8</th><td>0.000889311</td><td>1.50596</td></tr>
<tr><th scope="row">9</th><td>0.000455423</td><td>2.20247</td></tr>
<tr><th scope="row">10</th><td>0.000231022</td><td>3.18135</td></tr>
<tr><th scope="row">11</th><td>0.000116346</td><td>4.54933</td></tr>
<tr><th scope="row">12</th><td>5.8268e-05</td><td>6.45178</td></tr>
</tbody>
</table>

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-ii/refinement-defects.html#L139)

<a id="figure-10-sparse-stencil-transfer-blocks"></a>
<h2 id="figure-10" tabindex="-1">Figure 10: Sparse stencil transfer blocks</h2>

Rows select output packets i and columns select input packets j, both numbered 0 through 5. Each cell is a Frobenius norm for the 48-coordinate stencil resolved modulo 6. The color scale measures norm from zero upward; the numeric entries, rounded to two decimal places, are transcribed below. Zeros outside the diagonal and adjacent phases express exact absent transfers. Norms describe block size and do not preserve the signs or full action of the blocks.

<table>
<caption>Figure 10: Sparse stencil transfer blocks</caption>
<thead><tr><th scope="col">Output / input</th><th scope="col">0</th><th scope="col">1</th><th scope="col">2</th><th scope="col">3</th><th scope="col">4</th><th scope="col">5</th></tr></thead>
<tbody>
<tr><th scope="row">0</th><td>5.66</td><td>2.83</td><td>0</td><td>0</td><td>0</td><td>1.92</td></tr>
<tr><th scope="row">1</th><td>2.04</td><td>5.66</td><td>2.83</td><td>0</td><td>0</td><td>0</td></tr>
<tr><th scope="row">2</th><td>0</td><td>2.04</td><td>5.66</td><td>2.83</td><td>0</td><td>0</td></tr>
<tr><th scope="row">3</th><td>0</td><td>0</td><td>2.04</td><td>5.66</td><td>2.83</td><td>0</td></tr>
<tr><th scope="row">4</th><td>0</td><td>0</td><td>0</td><td>2.04</td><td>5.66</td><td>2.83</td></tr>
<tr><th scope="row">5</th><td>2.65</td><td>0</td><td>0</td><td>0</td><td>2.04</td><td>5.66</td></tr>
</tbody>
</table>

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-ii/models-and-algorithms.html#L29)

<a id="figure-11-nested-polyphase-samples"></a>
<h2 id="figure-11" tabindex="-1">Figure 11: Nested polyphase samples</h2>

Four panels use horizontal real reflection coordinate Re Γ and vertical imaginary coordinate Im Γ, with ticks −1, 0 and 1 and an outer unit circle. At N=2,4,8,16 the samples are Γₖ=0.72 exp(2πik/N), for k=0 through N−1. Thus the new order inserts midpoints in angular position while retaining every old sample. The dashed circle is the sample radius 0.72; the outer circle is radius 1. Marked additions at each refinement are also distinguished by their interleaving positions. These are Smith impedance-chart samples, distinct from Smith normal form.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-ii/models-and-algorithms.html#L71)

<a id="figure-12-symmetric-refinement-weight-in-the-reflection-disk"></a>
<h2 id="figure-12" tabindex="-1">Figure 12: Symmetric refinement weight in the reflection disk</h2>

The horizontal axis is Re Γ and the vertical axis is Im Γ. Color records log₁₀ w(Γ), with ticks 0.5, 1, 2 and 3, where w(Γ)=|1−Γ|⁻²+|1+Γ|⁻². The 300-by-300 sampling grid spans −0.98 to 0.98 in each coordinate and displays only points with |Γ|<0.985. Larger values cluster near Γ=−1 and Γ=1. The field is symmetric about both coordinate axes. The singular boundary points themselves are outside the displayed sample.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-ii/models-and-algorithms.html#L88)

<a id="figure-13-distinct-proof-branches"></a>
<h2 id="figure-13" tabindex="-1">Figure 13: Distinct proof branches</h2>

Each row is read from its input, through the middle construction, to its conclusion. The rows below preserve all eight routes. They do not form one chain: the unsigned walk series is independent of operator inversion, and the Smith and Bézout branches use their supplied arithmetic data.

<table>
<caption>Figure 13: Distinct proof branches</caption>
<thead><tr><th scope="col">Inputs</th><th scope="col">Construction</th><th scope="col">Conclusions</th></tr></thead>
<tbody>
<tr><th scope="row">Complete packet axioms</th><td>Coordinate coherence</td><td>Naturality and refined transfer blocks</td></tr>
<tr><th scope="row">Residue selectors and finite Fourier table</th><td>Finite Fourier formulas</td><td>Spectral residue projectors</td></tr>
<tr><th scope="row">Residue selectors and coprime moduli</th><td>Dyadic and odd CRT</td><td>Concrete refinement families</td></tr>
<tr><th scope="row">Quotient, filtration and weight certificates</th><td>Pruned finite inverse</td><td>Precision cutoff</td></tr>
<tr><th scope="row">Finite graph with positive edge weights</th><td>Walk enumeration and first-edge recurrence</td><td>Determinant rationality and recurrence</td></tr>
<tr><th scope="row">Evaluated Bézout data and lattice action</th><td>Integral separation</td><td>Upward closure and precision delay</td></tr>
<tr><th scope="row">Supplied Smith data and coordinate fibres</th><td>Finite Smith product</td><td>Solvability and fibre cardinality</td></tr>
<tr><th scope="row">A typed one-step defect</th><td>Telescoping powers</td><td>Polynomial actions and resolvents</td></tr>
</tbody>
</table>

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-ii/models-and-algorithms.html#L277)

## Visual atlas

The following descriptions cover all 24 atlas pages. The two orientation and evidence pages contain tables rather than drawings. [Open the original visual guide PDF](../papers/paper-ii/current/papers/Paper_II_Visual_Guide_Final.pdf).

<a id="atlas-page-1-three-kinds-of-resolution"></a>
<h3 id="atlas-01" tabindex="-1">Atlas page 1: Three kinds of resolution</h3>

Three side-by-side routes distinguish a finer coefficient address, a deeper arithmetic cutoff, and clearing a spectral denominator. The address route retains all coefficients. The cutoff route retains only words below the requested filtration depth. The denominator route controls the extra input precision needed for an integral output difference. Finer addresses alone do not imply either of the other improvements.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L3)

<a id="atlas-page-2-an-atlas-of-the-refinement-layer"></a>
<h3 id="atlas-02" tabindex="-1">Atlas page 2: An atlas of the refinement layer</h3>

This orientation page is a table of objects and their roles, rather than a geometric plot. It distinguishes residue selectors, analysis and synthesis, coordinate changes, transfer blocks, filtration weights, graph adjacency, rational projectors, Smith weights and an intertwining defect. In particular, an unsigned graph count and an ordered signed operator sum answer different questions. Smith normal form and the nonlinear Smith impedance chart also have different roles.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L20)

<a id="atlas-page-3-follow-one-coefficient-through-the-tower"></a>
<h3 id="atlas-03" tabindex="-1">Atlas page 3: Follow one coefficient through the tower</h3>

Three rails contain all sixteen coefficient addresses, grouped modulo 2, 4 and 8. Heavier dividers mark packet boundaries. Follow address 6 from the even packet to residue 2 modulo 4 and then residue 6 modulo 8. Each level retains the same sixteen independent coefficients. The relations P₂,₀=P₄,₀+P₄,₂ and P₄,₂=P₈,₂+P₈,₆ describe exact parent membership.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L44)

<a id="atlas-page-4-regrouping-is-not-averaging"></a>
<h3 id="atlas-04" tabindex="-1">Atlas page 4: Regrouping is not averaging</h3>

For x=(1,2,3,4), four coordinate-supported packets regroup into (1,0,3,0) and (0,2,0,4). These two full vectors still determine x. The separate scalar-summary map sends four numbers to two sums, (x₀+x₂,x₁+x₃), and loses information: (1,0,−1,0) lies in its kernel. Thus the picture compares different stored objects, rather than two equally invertible ways of compressing four scalars.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L70)

<a id="atlas-page-5-the-operator-changes-coordinates-too"></a>
<h3 id="atlas-05" tabindex="-1">Atlas page 5: The operator changes coordinates too</h3>

The panels show actual eight-by-eight integer matrices for T=I+2S+S² on a periodic eight-coordinate carrier. Here S sends eⱼ to eⱼ₊₁ modulo 8. Dots denote zeros and heavy dividers mark packet blocks. At levels 2 and 4 the block sizes are four and two. Reordering by the permutation R_N gives T̂_N=R_NTR_N⁻¹ and J₄,₂=R₄R₂⁻¹, so J₄,₂T̂₂=T̂₄J₄,₂. This fully specifies the plotted entries without treating their norms as the operator.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L102)

<a id="atlas-page-6-selectors-survive-without-division"></a>
<h3 id="atlas-06" tabindex="-1">Atlas page 6: Selectors survive without division</h3>

Rows show a finite coefficient sequence over the field with two elements and the results of its even and odd zero-one masks. Each coefficient is retained in exactly one output row; adding the rows reconstructs the input. The masks select exponent addresses directly. They do not divide by two, so they remain valid when the usual even/odd averaging formula is unavailable in characteristic two.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L132)

<a id="atlas-page-7-a-fourier-certificate-you-can-inspect"></a>
<h3 id="atlas-07" tabindex="-1">Atlas page 7: A Fourier certificate you can inspect</h3>

The left three-by-three table is 3 on the diagonal and 0 elsewhere, with arithmetic modulo 7. Multiplication by 5, the inverse of 3, gives the identity table on the right. The labels use ω=2 and ω⁻¹=4, with row and column residues 0,1,2. The lower counterexample instead works in the product ring F₃×F₃: ω=(−1,1) has order two, but the normalized nontrivial sum is (0,1), not zero. Order alone does not supply the required orthogonality in that ring.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L155)

<a id="atlas-page-8-one-address-two-independent-residues"></a>
<h3 id="atlas-08" tabindex="-1">Atlas page 8: One address, two independent residues</h3>

The grid has columns a modulo 4 and rows b modulo 3. Each cell contains n=9a+4b modulo 12. Its rows, in column order 0,1,2,3, are (0,9,6,3), (4,1,10,7), and (8,5,2,11). The marked cell is a=3,b=1, giving n=7. Every combined residue appears once. A separate incompatible pair, n=0 modulo 4 and n=1 modulo 6, shows why the coprime rectangle needs its hypothesis.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L176)

<a id="atlas-page-9-which-words-can-survive-precision-five"></a>
<h3 id="atlas-09" tabindex="-1">Atlas page 9: Which words can survive precision five?</h3>

At precision 5 modulo 32, the ordered generators are a=2E₀₁ and b=4E₁₀, with weights 1 and 2. The nonzero retained signed contributions are I, −a, −b, ab=8E₀₀, ba=8E₁₁, and −aba=−16E₀₁. The first discarded nonzero word has weight at least 5. The rightmost matrix factor acts first. Equal weight does not make ab and ba equal, and some words below the cutoff still vanish because a²=b²=0.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L199)

<a id="atlas-page-10-an-inverse-computed-in-both-orders"></a>
<h3 id="atlas-10" tabindex="-1">Atlas page 10: An inverse computed in both orders</h3>

The matrix calculation takes T with rows (5,3),(4,1) and gives its inverse K modulo 32 with rows (9,5),(28,13). The integer products TK and KT have rows (129,64),(64,33) and (65,32),(192,97), respectively; both reduce to identity. The construction is K=SD⁻¹ with S rows (9,−18),(−4,9). Reversing these exterior factors would change the noncommutative formula.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L219)

<a id="atlas-page-11-the-residual-tells-you-when-to-stop"></a>
<h3 id="atlas-11" tabindex="-1">Atlas page 11: The residual tells you when to stop</h3>

The horizontal coordinate counts geometric-series terms N. The vertical coordinate is the minimum dyadic valuation of a nonzero residual entry. Since A²=8I, even residual powers have valuation 3k at N=2k and odd powers have 3k+1 at N=2k+1. The dashed requested level is 5. Three terms leave valuation 4 and fail, while four leave valuation 6 and suffice. The generic minimum-weight estimate gives the more conservative cutoff of five terms.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L249)

<a id="atlas-page-12-walks-are-not-simple-paths"></a>
<h3 id="atlas-12" tabindex="-1">Atlas page 12: Walks are not simple paths</h3>

The directed multigraph has a weight-one loop at 0, two distinct weight-two edges a and b from 0 to 1, and a weight-one return edge from 1 to 0. At total weight 5 there are six walks from 0 to 1: two with three initial loops and one forward edge, and four with a forward edge, return, and another forward edge. Words here list chronological traversals from left to right, unlike written matrix products. Parallel labels and repeated visits count separately.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L273)

<a id="atlas-page-13-a-finite-graph-produces-its-denominator"></a>
<h3 id="atlas-13" tabindex="-1">Atlas page 13: A finite graph produces its denominator</h3>

The graph from V12 gives Q(t)=1−t−2t³ and numerator 2t² for its 0-to-1 walk series. The initial coefficients are a₀=a₁=0 and a₂=2; the recurrence is aₙ=aₙ₋₁+2aₙ₋₃ for n≥3. The plot shows the resulting integer counts by total weight. This is a formal power-series identity with its numerator and initial exception retained, rather than an analytic convergence claim at a selected value of t.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L298)

<a id="atlas-page-14-separate-before-dividing"></a>
<h3 id="atlas-14" tabindex="-1">Atlas page 14: Separate before dividing</h3>

The normalization route begins with the integral involution A having rows (1,1),(0,−1). Set F=A−I and G=A+I. The evaluated identities −F+G=2I and FG=0 give the numerator N=G, which satisfies N²=2N. Dividing by 2 gives E₊ with rows (1,1/2),(0,0). This rational idempotent need not act integrally on the selected lattice. An inflated denominator certificate may give a valid but nonminimal clearing bound.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L321)

<a id="atlas-page-15-where-the-dyadic-digit-is-lost"></a>
<h3 id="atlas-15" tabindex="-1">Atlas page 15: Where the dyadic digit is lost</h3>

In the ordinary integer coordinate plane, the eigenvectors (1,0) and (−1,2) generate the index-two sublattice with even second coordinate. Filled dots belong to that sublattice and hollow integer dots occupy the other coset. The separate hollow point (1/2,0) is the image of an integral vector under E₊. This is a lattice illustration, not a drawing of the topology of the dyadic field. Localizing at an odd prime makes 2 invertible but does not change the ordinary integer index.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L349)

<a id="atlas-page-16-one-extra-digit-is-genuinely-necessary"></a>
<h3 id="atlas-16" tabindex="-1">Atlas page 16: One extra digit is genuinely necessary</h3>

For requested output agreement modulo 8, compare input differences (0,8) and (0,16). The projector E₊(x,y)=(x+y/2,0) sends them to (4,0) and (8,0). Thus input agreement modulo 8 alone fails, while agreement modulo 16 suffices. The two routes show an exact loss of one dyadic digit for differences on the specified lattice; they do not assert that the projector itself has integral entries.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L370)

<a id="atlas-page-17-see-every-smith-fiber-modulo-eight"></a>
<h3 id="atlas-17" tabindex="-1">Atlas page 17: See every Smith fiber modulo eight</h3>

Both square grids use residues 0 through 7 on their two axes. The map is (x,y)↦(2x,4y) modulo 8. The left grid contains all 64 inputs. The right has eight attainable targets: first coordinate 0,2,4,6 and second coordinate 0 or 4. Each has eight preimages. For target (2,4), x is 1 or 5 and y is 1,3,5 or 7. Every other target has an empty fibre.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L400)

<a id="atlas-page-18-transport-the-whole-solution-fiber"></a>
<h3 id="atlas-18" tabindex="-1">Atlas page 18: Transport the whole solution fiber</h3>

Two modular coordinate grids show the same eight-solution fibre before and after a shear. The diagonal system has D=diag(2,4), the original matrix M has rows (2,2),(0,4), and the change V has rows (1,−1),(0,1), with MV=D. The target is (2,4) modulo 8. Each diagonal solution y maps bijectively to x=Vy; for example (1,3) becomes (6,3). Lines and placement express a modular change of coordinates, not interpolation between residue points.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L427)

<a id="atlas-page-19-precision-exposes-directional-freedom"></a>
<h3 id="atlas-19" tabindex="-1">Atlas page 19: Precision exposes directional freedom</h3>

The horizontal axis is precision depth L=1 through 6. Each stacked bar has height W(L)=min(0,L)+min(1,L)+min(3,L), giving 2,3,4,4,4,4. The labels above the bars are the corresponding admissible fibre counts 4,8,16,16,16,16. The zero-weight direction adds no branching. These counts apply only after target admissibility is checked; a target failing a directional divisibility requirement has no solutions.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L452)

<a id="atlas-page-20-filter-first-or-split-first-same-output"></a>
<h3 id="atlas-20" tabindex="-1">Atlas page 20: Filter first or split first: same output</h3>

The input row is x=(1,2,3,4,5,6), zero outside this support, and the filter is (1,2,1). Exact convolution gives (1,4,8,12,16,20,17,6), including both tail entries. The two lower phase rows are even output (1,8,16,17) and odd output (4,12,20,6); interleaving them returns the full row. With phase delay w, the matrix has rows (1+w,2w),(2,1+w). The cross-phase delay records the shift across a phase boundary.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L480)

<a id="atlas-page-21-two-smith-constructions-different-roles"></a>
<h3 id="atlas-21" tabindex="-1">Atlas page 21: Two Smith constructions, different roles</h3>

Matching labels identify eight points in reflection coordinates Γ and impedance coordinates z=(1+Γ)/(1−Γ). The reflection samples are Γₖ=(1/2)exp(ikπ/4); the outer reflection circle has radius 1. Opposite samples correspond to the reciprocal impedance action z↦1/z. Labels 0 and 4 give 3 and 1/3, while label 2 gives (3+4i)/5. This nonlinear chart is distinct from the linear congruence construction called Smith normal form.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L505)

<a id="atlas-page-22-a-small-defect-can-grow-under-powers"></a>
<h3 id="atlas-22" tabindex="-1">Atlas page 22: A small defect can grow under powers</h3>

For power n, the paired bars compare actual defect and telescoping bound in induced infinity norm, both divided by ε=1/16. The actual height is 2ⁿ−1 and the upper-bound height is n2ⁿ⁻¹. The model uses the shear C with rows (1,ε),(0,1) and independently keeps T_f=T_c=diag(1,2). Exact coordinate invertibility does not make those independently selected operators intertwine; the defect can grow under iteration.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L525)

<a id="atlas-page-23-resolvents-amplify-errors-near-poles"></a>
<h3 id="atlas-23" tabindex="-1">Atlas page 23: Resolvents amplify errors near poles</h3>

Horizontal bar lengths are exact resolvent amplification factors after dividing out ε=1/16. The rows are separate rational samples z>2, not equally spaced values on a continuous z-axis. In displayed order the pairs are z=5/2: 4/3; 11/5: 25/6; 21/10: 100/11; 41/20: 400/21; and 201/100: 10000/101. The formula is 1/((z−1)(z−2)). Neither resolvent is defined at its poles 1 and 2.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L551)

<a id="atlas-page-24-read-the-certificates-with-the-pictures"></a>
<h3 id="atlas-24" tabindex="-1">Atlas page 24: Read the certificates with the pictures</h3>

This final page is an evidence table. It separates inherited formal results, exact finite examples, sampled displays, and the ordinary mathematical arguments. The graph, inverse, Smith, and separation pictures keep their own inputs and hypotheses. A successful finite example illustrates its stated mechanism; it does not enlarge the retained formal contract or supply a missing general structure theorem.

[Original plate explanation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/papers/paper-ii/current/editable/traditional/visual_atlas.tex#L577)
