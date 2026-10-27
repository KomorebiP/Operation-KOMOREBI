# Block 27 proof guide — cubical refinement and curvature-controlled defects

## 1. Purpose

Block 26 subdivided one oriented edge and proved exact two-half-step/coarse-step compatibility.  It also showed that two directional corner transports agree exactly only when their plaquette holonomy is trivial.  Block 27 resolves the corresponding local three-dimensional cell problem instead of assuming the three one-axis embeddings glue automatically.

The block constructs one explicit `2 × 2 × 2` cubical cell with eight vertices and twelve oriented `U(1)` edges.  It proves the exact flat sector and retains the nonflat discrepancy as a gauge-invariant curvature term.

## 2. Cell geometry and gauge field

A child vertex is a Boolean triple `(x,y,z)`.  `CubeLinks` stores the four positively oriented edges in each axis direction:

- `edgeX y z`
- `edgeY x z`
- `edgeZ x y`.

A vertex gauge `g : CubeVertex → Circle` acts on every oriented link by target multiplication and source inverse multiplication.  The source and target gauge factors telescope along paths.

## 3. Face paths and plaquettes

For each of the six faces, the module defines the two two-edge paths around the face and their ratio.  For example,

`Ω_xy(z) = pathXY(z) / pathYX(z)`.

Lean proves:

`Ω_xy(z) = 1 ↔ pathXY(z) = pathYX(z)`,

and analogously for the `xz` and `yz` faces.  All six plaquettes are exactly gauge invariant.

## 4. Six corner paths

The six permutations of the three positive directions are represented explicitly:

`XYZ`, `XZY`, `YXZ`, `YZX`, `ZXY`, `ZYX`.

Every adjacent permutation is related by one face holonomy.  Representative identities are

`pathXYZ = Ω_xy(0) * pathYXZ`,

`pathXYZ = Ω_yz(1) * pathXZY`.

This gives an exact algebraic description of how local curvature obstructs path-independent interpolation.

## 5. Cubical Bianchi identity

Two sequences of adjacent transpositions carry `XYZ` to `ZYX`.  Cancelling their common terminal path proves

`Ω_yz(1) Ω_xz(0) Ω_xy(1)
 = Ω_xy(0) Ω_xz(1) Ω_yz(0)`.

This is the abelian discrete cube Bianchi identity in the chosen orientation.  A derived theorem shows that five flat faces force the sixth.

## 6. Flat sector

`CubeLinks.Flat` states that all six face plaquettes equal one.  Under this hypothesis Lean proves that all six origin-to-opposite-corner transports coincide.  Flatness is also preserved by arbitrary vertex gauges.

The conclusion is local to one cell.  It is not yet an inter-cell gluing theorem or a global trivialization theorem.

## 7. Gauge-covariant interpolation and Hilbert measure

A reference path is selected from the origin to each of the eight vertices.  The interpolation is

`I_L ψ(v) = referencePhase_L(v) • ψ`.

It obeys exact gauge covariance.  Since the same spinor is transported unitarily to eight vertices, raw counting measure would multiply its Hilbert weight by eight.  The cell inner product therefore carries the one-eighth child-cell measure, and Lean proves

`cubeIP (I_L ψ) (I_L φ) = ip ψ φ`.

The construction is lifted pointwise to a finite family of coarse sites, where it remains gauge covariant and Hilbert isometric.

## 8. Exact nonflat defect

For two path phases `p` and `q`, define

`D(p,q;ψ) = p•ψ - q•ψ`.

Whenever `p = Ω q`, Lean proves

`D(p,q;ψ) = q • ((Ω - 1) ψ)`.

It also proves the exact Hilbert identity

`⟨D,D⟩ = conjugate(Ω-1) (Ω-1) ⟨ψ,ψ⟩`.

Each adjacent corner-path pair receives a specialized theorem with its corresponding face plaquette.  For the fixed nonzero basis spinor, zero defect is equivalent to trivial holonomy.

## 9. Concrete nonflat witness

`nonflatCube` has lower `xy` plaquette `-1`.  Its `XYZ` and `YXZ` path phases are `-1` and `1`, and their transported basis-spinor defect is proved nonzero.  This prevents a false universal path-independence interpretation.

## 10. Main declarations

- `CubeLinks.plaquetteXY_gauge_invariant`
- `CubeLinks.plaquetteXZ_gauge_invariant`
- `CubeLinks.plaquetteYZ_gauge_invariant`
- `CubeLinks.pathXYZ_eq_xy0_mul_pathYXZ`
- `CubeLinks.pathXYZ_eq_yz1_mul_pathXZY`
- `CubeLinks.cube_bianchi`
- `CubeLinks.Flat.all_corner_paths`
- `CubeLinks.Flat.xy1_of_other_five`
- `CubeLinks.embed_gauge_covariant`
- `CubeLinks.embed_cubeIP_isometry`
- `CubeLinks.pathDefect_eq_curvature_transport`
- `CubeLinks.pathDefect_ip_eq_curvature_weight`
- `CubeLinks.all_adjacent_defects_zero`
- `cellEmbed_gauge_covariant`
- `cellEmbed_isometry`
- `nonflatCube_defect_nonzero`

## 11. Formal boundary

Block 27 proves a local cubical flatness theorem and exact plaquette-controlled path defects.  It does not yet construct the full fine/coarse `M-X-Y-Z-Y-X-M` intertwining, prove an operator-norm bound from curvature, glue neighboring cells into one refined lattice, establish scale decay or summability, or prove a continuum Dirac/gauge limit.
