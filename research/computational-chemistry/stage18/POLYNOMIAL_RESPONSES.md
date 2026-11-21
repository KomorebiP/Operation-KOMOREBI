# Tighter response bounds from the same saved values

The precision planner can fail because its between-sample enclosure is too wide, even when its sampled responses are accurate. This study changes that enclosure while keeping every Hamiltonian action, source vector and saved response value fixed.

At broadening 0.1 Hartree, the existing 64-action, 41-energy curve now has a maximum local-polynomial radius below 0.000499 per Hartree across the complete interval. The previously unsupported budget of 0.001 per Hartree is therefore met without another Hamiltonian action or endpoint response solve. The 128-action curve improves from a linear radius about 0.007565 to below 0.000215 per Hartree. The narrow 0.01-Hartree, 512-action curve improves from about 0.09735 to below 0.04855 using the same 166 saved energies.

These are conditional bounds for the same finite H10-derived target and supplied source/reference. They do not establish physical source, basis-set, ground-reference or experimental accuracy. A polynomial full-grid alternative uses every saved energy in its curve. It is not a minimum-node plan under the separate Stage 17 linear-bound optimization.

## Exact interpolation implication

Let H be a finite Hermitian matrix, b a fixed complex vector and eta>0. Define

    R(E)=((E+i eta)I-H)^(-1),    g(E)=b*R(E)b,
    S(E)=-Im g(E)>=0.

The star denotes conjugate transpose. Let a<c, h=c-a and E=a+t h with 0<=t<=1. Choose m distinct real interpolation nodes a_j, where m is 2, 3 or 4. The node set must contain a and c and have no node inside (a,c). Set

    x_j=(a_j-a)/h,
    L_j(t)=product over k!=j of (t-x_k)/(x_j-x_k),
    P(t)=product over j of (t-x_j).

Suppose valid disks are supplied at the nodes: |g(a_j)-c_j|<=r_j with r_j>=0. Write U_j=-Im(c_j)+r_j, which must be nonnegative. Then

    |g(a+t h)-sum_j L_j(t)c_j|
      <= sum_j |L_j(t)|r_j + C_m |P(t)|,                     (1)
    C_m=(h/eta)^m min over i<j of sqrt(U_i U_j).

A rational upper enclosure of C_m may replace it. Negative Lagrange weights require absolute values in the endpoint-error term.

## Proof of the resolvent identity and bound

For a real eigenvalue lambda of H, multiply the scalar interpolation error by

    (E+i eta-lambda) product_j(a_j+i eta-lambda).

The resulting polynomial in E has degree at most m and vanishes at every a_j. It is therefore a constant times product_j(E-a_j). At E=lambda-i eta its value is product_j(a_j+i eta-lambda), whereas product_j(E-a_j) has value (-1)^m times that same nonzero product. The constant is (-1)^m. Applying this scalar identity in an orthonormal eigenbasis gives

    R(E)-sum_j L_j(t)R(a_j)
      = (-1)^m h^m P(t) R(E) product_j R(a_j).                (2)

All resolvents commute because they are functions of one H. The spectral expansion gives

    ||R(E)||<=1/eta,
    ||R(a_j)b||^2=||R(a_j)*b||^2=S(a_j)/eta.

In the matrix product in (2), place any chosen R(a_i) next to the left source and any other R(a_j) next to the right source. There are m-1 remaining resolvents. Cauchy-Schwarz and the operator-norm bound give

    |b*R(E) product_j R(a_j)b|
      <= sqrt(S(a_i)S(a_j))/eta^m
      <= sqrt(U_i U_j)/eta^m.

Minimize over distinct pairs, multiply by h^m|P(t)| and add the propagated endpoint-center errors. This proves (1). Zero source and zero upper strengths are included. Hermiticity is essential to the spectral-strength argument; the algebraic identity alone does not supply the norm estimate for a nonnormal operator.

For m=2, (1) is precisely the previous linear-center enclosure. For m=3 its center is quadratic, and for m=4 its center is cubic. Endpoint recovery is exact: at an interpolation node the center equals its supplied center and the radius equals its supplied radius.

## A polynomial radius on each cell

There are no interpolation nodes in the open cell. Consequently every L_j and P has a constant sign there, determined at t=1/2. Their absolute values on [0,1] are therefore polynomials, with the endpoint values supplied by continuity. The right side of (1) is a nonnegative polynomial of degree at most m.

For a polynomial p(t)=sum_l a_l t^l of degree at most n, its Bernstein representation has coefficients

    beta_k=sum over l<=k of a_l binomial(k,l)/binomial(n,l),
    p(t)=sum_k beta_k binomial(n,k)t^k(1-t)^(n-k).

Expanding the right side verifies the identity. The Bernstein basis functions are nonnegative on [0,1] and sum to one, so min beta_k<=p(t)<=max beta_k. The implementation applies exact midpoint subdivision twice, covering four subcells, and takes the largest upper control value. The two-node case instead uses the sharp quadratic maximum already proved in Stage 17.

The coefficient C_m and final uniform radius are rounded upward to 18 decimal places. All polynomial operations and comparisons use exact fractions. On each cell the implementation considers every contiguous stencil of size 2, 3 or 4 containing both cell endpoints and chooses the one with the smallest declared uniform radius, with deterministic ties. The two-node option is always retained, so the selected bound never exceeds the previous published linear bound. This selection is not a general optimum over every interpolation method or node grid.

For the model comparison, form the polynomial difference between the full and reduced imaginary centers and add their radius polynomials. Bernstein lower and upper bounds on the difference minus/plus that sum give a signed interval valid throughout the cell. A signed interval crossing zero does not certify model separation. Each model keeps its own fixed operator and source.

## Conservative curves in the plot

The plotted center has degree at most three and is represented by native cubic Bezier segments. A band edge can have degree four because it adds or subtracts the radius polynomial. It is enclosed, rather than silently replaced by a chord.

For a quartic with Bernstein controls beta_0,...,beta_4, take the cubic Hermite controls

    H0=beta_0,
    H1=beta_0+(4/3)(beta_1-beta_0),
    H2=beta_4-(4/3)(beta_4-beta_3),
    H3=beta_4.

Elevate this cubic to degree four and subtract its controls from the quartic controls. The first two and last two differences are zero; write e2 for the middle difference. Thus

    p(u)-H(u)=6 e2 u^2(1-u)^2,
    |p(u)-H(u)|<=(3/8)|e2|,    0<=u<=1.

Adding this exact constant padding to an upper cubic, and subtracting it from a lower cubic, encloses the corresponding band edge throughout the subcell. Lower-degree edges are elevated exactly and need no padding. The implementation uses the same four subcells. Drawing padding does not alter the reported analytic response radius. SVG coordinates and short labels are approximate; downloadable fractions retain the numerical certificates.

## Results and finite audits

All 1,005 cells across the 22 existing cache curves were processed. The study considered 11,708 full/reduced stencil candidates. At eta=0.1 the 64-action complete-grid bound is 0.000498604890418071 per Hartree, below the requested 0.001. The 128-action bound is 0.000214294047656491 per Hartree. At eta=0.01 the 512-action bound is 0.048542980339147052 per Hartree, using its unchanged 166-node grid.

The pure quadratic option at eta=0.1 does not reach the same 0.001 target on the available grids; the four-value option resolves it. A local mixture of degrees is used where appropriate, including one quadratic cell in the 512-action narrow curve. These comparisons concern conservative bounds, not measured physical errors or optimized wall time.

The separate exact audit checks 480 matrix identities, 480 response-disk inclusions, 480 uniform point inclusions, 80 comparisons with the previous linear formula and 39,168 display-envelope inclusions. It includes complex Hermitian matrices, complex sources, boundary stencils and perturbed endpoint centers. A zero-source Hermitian example shows why signed propagation of endpoint radii is invalid: an outer Lagrange weight is negative while its endpoint disk error has positive radius. Three invalid stencil patterns are rejected. These are deterministic finite checks; the analytic arguments establish the general implication under the named hypotheses.

The review is project self-review, without independent expert or proof-assistant verification. No novelty claim is made. The endpoint enclosures retain the original binary64 primitive-operation assumptions; no new Hamiltonian action or endpoint response solve is performed here.

## Replay

Saved-byte provenance can be checked with Python's standard library:

```text
python -B research/computational-chemistry/stage18/verify_stage18.py
```

Fresh calculations use new output directories:

```text
python -B research/computational-chemistry/stage18/polynomial_study.py --output fresh-polynomial-study
python -B research/computational-chemistry/stage18/audit_polynomial.py --output fresh-polynomial-audit
```

The study uses only the standard library. The exact audit additionally uses SymPy. Recorded versions were Python 3.12.14 and SymPy 1.14.0. The recorded study took about 6.1 seconds, and the exact audit about 151.6 seconds, on this Windows environment. The provenance runner applied respective 300- and 180-second wall caps and a 1 MiB log cap to each run; the manual commands above do not impose those caps. These postprocessing timings are not an optimized chemistry-solver benchmark.

The replay also includes the exact-fraction JavaScript polynomial checker, its shared rational arithmetic, both required data fixtures and its Node test. From the extracted replay root, run `node tools/test_chemistry_polynomial.mjs`. This checks all saved cell bounds, endpoint recovery, the two newly qualifying targets, malformed-certificate rejection and drawing construction. It does not repeat the symbolic matrix audit or validate the endpoint arithmetic model on hardware.
