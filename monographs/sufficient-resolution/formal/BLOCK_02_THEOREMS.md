# Block 02 — Exact discrete memory and finite closure certificates

**Komorebi P. | Sufficient Resolution v0.2.0 | 13 September 2026**

This guide describes the new checked statements. The general block dynamics and
closure theorems are over modules over a commutative ring. The polynomial and
canonical hidden-space layer is over a field. Only the dimension-controlled
corollaries assume a finite-dimensional hidden space. No orthogonality is assumed.

## The dynamical object

Let T(y,z) = (Ay+Bz, Gy+Dz), where y is visible and z hidden.
The formalization constructs the full linear operator T from A, B, G, D and
constructs actual trajectories by powers of T. Their recurrence is derived,
not assumed as an additional premise.

Set M_k = B D^k G and E_n = C T^n R, where C(y,z)=y and R(y)=(y,0).
Operator multiplication applies the right factor first. M_k is a return after
k hidden transitions and two boundary crossings; its first effect is at full
time k+2, not k or k+1.

## 1. Exact hidden elimination

`BlockDynamics.forced_recurrence_formula` proves the finite convolution formula
for a forced linear recurrence. `BlockDynamics.hidden_elimination` specializes it:

    z_n = D^n z_0 + sum_{j=0}^{n-1} D^(n-1-j) G y_j.

`BlockDynamics.discrete_memory_equation` then proves:

    y_(n+1) = A y_n + B D^n z_0
              + sum_{j=0}^{n-1} M_(n-1-j) y_j.

These formulas include n=0 (empty sum) and arbitrary initial hidden state z_0.
They are not continuous-time Volterra equations.

## 2. Prepared evolution and exact closure

With z_0=0, `BlockDynamics.prepared_recurrence` gives:

    E_(n+1) = A E_n + sum_{j=0}^{n-1} M_(n-1-j) E_j,
    E_0 = I, E_1 = A.

The following conditions are proved equivalent, with no finite dimension needed:

    E_n = A^n for every natural n;
    M_k = 0 for every natural k;
    E_(m+n) = E_m E_n for every m,n;
    the split-compression defects of all powers of T are zero.

Lean declarations:

- `prepared_powers_iff_memory_zero`
- `prepared_semigroup_iff_memory_zero`
- `power_defects_zero_iff_memory_zero`

Both directions are proved. The necessity proof isolates successive feedback
coefficients; it does not assume invariant lifted state or zero entry coupling.

## 3. Exact depth-to-delay identification

`prepared_prefix_iff_memory_prefix N` proves:

    E_n=A^n for all n <= N+1  iff  M_k=0 for all k<N.

`first_return_discrepancy k` proves, assuming M_j=0 for j<k:

    E_(k+2) - A^(k+2) = M_k.

`first_return_detected` concludes nonagreement at k+2 when M_k is nonzero.
Thus finite tests have an exact scope even before any dimension bound is known.

## 4. A genuinely finite all-depth certificate

For a supplied monic polynomial p with p(D)=0, `memory_zero_of_annihilator`
proves that M_k=0 for k<degree(p) implies M_k=0 for every k. Polynomial remainders
are constructed, with their degree bound, not inserted as an unproved span claim.

For finite-dimensional H, Mathlib's proved Cayley-Hamilton theorem supplies
p=charpoly(D), with degree d=finrank(H). Therefore:

    E_n=A^n for every n
      iff M_0=...=M_(d-1)=0
      iff E_n=A^n for every n<=d+1.

Lean declarations:

- `memory_zero_of_finrank_prefix`
- `memory_zero_iff_finrank_prefix`
- `prepared_powers_iff_finrank_memory`
- `prepared_powers_iff_finite_horizon`
- `nonclosure_has_finite_feedback_witness`

The hidden dimension may be zero. The visible space need not be finite-dimensional.
The finite test concerns equality of entire linear maps. Checking sampled vectors
or approximate floating-point agreement does not discharge its hypothesis.

## 5. Prepared-state closure is weaker than all-state closure

`all_state_closure_iff_B_zero` proves:

    y_n=A^n y_0 for all n,y_0,z_0  iff B=0.

This is stronger than requiring M_k=0 for all k. A hidden initial state can affect
the visible state even when visible inputs never return through the hidden space.

## 6. Canonical realization of an arbitrary split compression

Let c have C:X->Z and R:Z->X with C R=I. Define Q=I-RC and H=ker(C).
The new maps are:

    analysis(x) = (Cx,Qx) in Z x H;
    synthesis(y,z) = Ry+z.

Both inverse identities are proved. Given a fine operator T, the constructed
block system on Z x H is conjugate to T, including all powers. Its blocks are:

    A = C T R
    B = C T inclusion_H
    G = Q T R, with codomain H
    D = Q T inclusion_H, with codomain H.

`block_prepared_eq_coarse` identifies its prepared maps with the original C T^n R.
Consequently:

    C T^n R = (C T R)^n for all n
      iff the canonical feedback maps all vanish.

If ker(C) has dimension d, testing the full compressed maps through depth d+1
suffices. The certificate uses the actual discarded dimension, not the entire
fine-state dimension. These results do not require orthogonal C or R.

Lean declarations:

- `SplitCompression.block_synthesis_analysis`
- `SplitCompression.block_analysis_synthesis`
- `SplitCompression.block_step_eq`
- `SplitCompression.block_powers_eq`
- `SplitCompression.exact_powers_iff_canonical_memory_zero`
- `SplitCompression.exact_powers_iff_canonical_finite_memory`
- `SplitCompression.exact_powers_iff_canonical_finite_horizon`

## 7. Checked controls

The delayed rational three-cycle is instantiated as this four-block system.
Lean proves M_0=0, M_1=I, M_(n+2)=0, exact agreement through depth two, and exact
error I at depth three. Its full step is proved equal to the prior release's
`Examples.rotate`, so this is a bridge to the old counterexample, not a replacement.

A second rational system has A=I, D=I, B(z1,z2)=z1 and G(y)=(0,y).
Both B and G are nonzero, yet every M_k is zero. Prepared dynamics are exact at
every depth, while all-state closure fails. This tests both the stronger
all-state boundary and the fact that nonzero entry/return maps need not form
an active feedback path.

## Source inventory

| New module | Explicit theorem declarations |
|---|---:|
| DiscreteMemory | 15 |
| MemoryClosure | 14 |
| FiniteMemory | 6 |
| SplitMemory | 10 |
| MemoryExamples | 12 |
| **Added** | **57** |

The cumulative package has 125 explicit theorem declarations in 11 modules.
Counts include helpers and examples, not only principal mathematical claims.
