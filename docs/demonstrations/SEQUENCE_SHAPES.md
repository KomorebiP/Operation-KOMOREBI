# Komorebi sequence shapes

[Run the sequence experiments](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#sequence-growth) · [All worked examples](../HAND_WORKED_EXAMPLES.md) · [Sequence API](https://KomorebiP.github.io/Operation-KOMOREBI/math/sequences_oeis.html)

These experiments use the reciprocal families in Paper IV and the factorial
weights in the Special Functions sequence atlas. The code runs the published
Komorebi Math package. Each plot has an exact CSV export, editable parameters,
and routes back to its mathematical sources.

For a complete combinatorial hand derivation, follow
[Stirling, Bell and Fubini numbers through exact transfer](STIRLING_BELL_FUBINI.md).
It connects the factorial-weighted Stirling charts below to an invertible
triangular transformation, a reciprocal generating function, residue-packet
identities, and an explicit information-loss witness.

For the corresponding reciprocal-family approach to Euler numbers, read
[Euler numbers through packets, polynomials, and residuals](EULER_PACKETS.md).
That derivation reconstructs secant numbers through the quartic family,
explains failed coarsening and exact repair, and carries the signed Euler
data into polyphase difference coordinates.

## Reciprocal growth

[Run reciprocal growth](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#sequence-growth)

The library uses the convention

```math
D_N(t)=\sum_{q\geq0}\frac{(-1)^q t^{Nq}}{(Nq)!},\qquad
D_N(t)^{-r}=\sum_{n\geq0}A_N^{[r]}(n)\frac{t^{Nn}}{(Nn)!}.
```

These are Paper IV's coefficients $P_{N,n}(r)$. The library calls them
`reciprocal_coefficients(N, count, power=r)`. Index $n$ is compressed.
The corresponding degree in $t$ is $Nn$.

The first graph compares $\log_{10} A_N^{[r]}(n)$ with
$\log_{10}((Nn)!)$. The second graph shows
$\log_{10}(A_N^{[r]}(n)/(Nn)!)$. Dividing by the factorial reveals the
remaining coefficient scale. Similar-looking curves over a finite window
do not establish asymptotic equivalence.

At $N=2,r=1$, $D_2(t)=\cos t$. The reciprocal gives the secant numbers
[OEIS A000364](https://oeis.org/A000364), indexed from zero. In particular,
$A_2^{[1]}(2)=5$ contributes $5t^4/4!$. Its normalized value is $5/24$,
not $5/2!$. At the default $N=4,r=1$, the first five values are
$1,1,69,33661,60376809$.

The preset supports integer $2\leq N\leq8$, $1\leq r\leq3$ and at most
16 terms beginning at $n=0$. Try changing $N$ from four to two or $r$ from
one to two. Exact integer and rational values are preserved in
`reciprocal-growth-exact.csv`. Floating-point logarithms are used only for
the plotted heights. The plot-data CSV contains those heights, while the
separate exact CSV contains the original mathematical values.

## Reciprocal landscape

[Compare the reciprocal families](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#sequence-landscape)

Start with the 2D chart. Each line has its own label, point shape and color.
Use the series checkboxes to compare fewer families. A vertical value of
minus ten means $10^{-10}$. Each fall of one unit means a normalized value
ten times smaller. The Enlarge plot button gives the chart more space.

The separate 3D view uses the same data. Its axes are compressed index $n$, integer spacing $N$, and
$\log_{10}(A_N^{[r]}(n)/(Nn)!)$. The default has 112 exact coefficient
samples: seven spacings $N=2,\ldots,8$ and sixteen indices $n=0,\ldots,15$.
The reciprocal power $r$ is fixed for each run and can be changed in the editor.

Each row is a discrete sequence. Lines connect neighboring samples to help
the eye. There is no interpolated surface between integer $N$ values.
Rotate the view or use the front and top buttons. The data table offers the
same plotted coordinates, and `reciprocal-landscape-exact.csv` retains every
integer coefficient and rational normalization. Comparing equal $n$ across
different $N$ compares different ordinary degrees $Nn$.

## Factorial weights

[Run factorial weights](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#factorial-weights)

The Special Functions sequence atlas, lesson S08, uses

```math
F_n=\sum_{k=0}^{n}k!S(n,k),\qquad
\sum_{n\geq0}F_n\frac{t^n}{n!}=\frac{1}{2-e^t}.
```

Here $S(n,k)$ counts partitions of an $n$-element set into $k$ nonempty
blocks. The factorial $k!$ orders those blocks. The row sum is a Fubini
number, also called an ordered Bell number, [OEIS A000670](https://oeis.org/A000670).
This is a known sequence presented through Komorebi's transform framework.

For $n=5$, the Stirling row is $0,1,15,25,10,1$. Weighting it by $k!$
gives $0,1,30,150,240,120$. The ordinary sum is 52, and the weighted sum
is 541. The first plot compares these contributions as ordinary counts.
Blue bars show unordered partitions and striped orange bars show ordered
partitions. The two totals are printed above the chart.

The next figure is a 2D map of $\log_{10}(1+\text{contribution})$.
Each square is an integer pair $(n,k)$. A column shows all contributions
for one set size $n$. The white triangle where $k>n$ is outside the domain,
not a set of zero entries. Brighter squares have larger contributions.

The final 3D view shows the nonzero contributions over
$0\leq k\leq n\leq18$ on the same logarithmic scale as the map.
The added one handles zero values in the map. To recover a row sum,
add the exact CSV values rather than the plotted logarithms. The 3D view
omits zero contributions. The export includes all 190 triangular positions,
including zeros. `last` can be reduced from 18, and `row` selects a row
between zero and `last`.

## Papers, proofs, Lean and code

| Experiment | Reading and written proofs | Formal coverage | Code and hand calculation |
|---|---|---|---|
| Reciprocal growth and landscape | [Paper IV](../works/paper-iv.md#read), [reciprocal family definition and proofs](../../papers/paper-iv/current/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/traditional/Paper_IV_Traditional_Final.tex#L918) | [Paper IV Lean coverage](../works/paper-iv.md#lean) | [Sequence API](https://KomorebiP.github.io/Operation-KOMOREBI/math/sequences_oeis.html), [cyclic reciprocal hand calculation](../examples/16_CYCLIC_RECIPROCALS.md), [Paper IV code](../works/paper-iv.md#code) |
| Factorial weights | [Special Functions](../works/monographs-special-functions.md#read), [sequence atlas lessons S07 and S08](../../monographs/special-functions/expanded_visual/chapters_sequences.tex) | [Special Functions Lean coverage](../works/monographs-special-functions.md#lean) | [Original sequence figure code](../../monographs/special-functions/expanded_visual/figures_sequences.py), [library worked examples](https://KomorebiP.github.io/Operation-KOMOREBI/math/WORKED_EXAMPLES.html#exact-sequence-families-and-offline-oeis-comparisons) |

The playground displays each preset's complete code and provides its Python
download. The [preset sources](../../tools/sequence_presets.py) and
[finite comparison tests](../../tools/test_sequence_python.py) are maintained
with the site. The [source record](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/python-playground.json)
identifies the library revision and downloadable code checksums.

## What was checked

An independent ordinary rational-series inversion is compared with the
library's integer recurrence for $N=2,\ldots,8$, $r=0,\ldots,3$ and
$n=0,\ldots,15$: 448 coefficients. The power-zero row is an additional
boundary control. The test also rejects replacing the degree factorial by
the compressed-index factorial in the secant example.

All 190 factorial-weighted Stirling contributions through $n=18$ are
compared with the inclusion-exclusion formula for labelled surjections.
All 19 row sums are compared with the library's Fubini recurrence. Tests
check each preset's printed output and exact export. Browser checks exercise
the graphs with the site's pinned Python and library versions.

These are finite implementation checks. They do not prove the full families,
certify an asymptotic law, run Lean, establish new OEIS entries, or change
the recorded proof status. The linked sources retain their existing scope.

[Back to the experiments](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#sequence-growth) · [Paper IV claims](../CLAIM_LINKS.md#paper-iv) · [Special Functions evidence](../works/monographs-special-functions.md#evidence)
