# Block 32 — Finite reachable modules in intrinsic cyclic-factor coordinates

## Goal I / phase D
The input is the actual correlated reachable module produced in Block31, not the
ambient coordinate-ideal box. The target is a finite cyclic presentation, exact
transport of all digit operations, and a canonical module signature. The target
is NOT a canonical choice of basis or an observable/minimal machine.

## 1. Finite module presentation
Let p be prime and let V be a finite module over R=Z/p^r. Then p^r annihilates V.
The classical finite abelian group decomposition gives V as a finite direct sum
of cyclic groups Z/n_i with n_i>1. Annihilation of the i-th cyclic unit shows
n_i divides p^r. Consequently n_i=p^e_i with 1<=e_i<=r.

A chosen presentation P contains the finite factor index, exponents, their bounds,
and an actual additive equivalence

    f_P : V ≃+ product_i Z/(p^e_i).

The theorem `equiv_scalar` proves that its scalar action is reduction in each
factor: f_P(a*x)_i = red_(r,e_i)(a)*f_P(x)_i. Thus this is a module presentation,
not merely an equal-cardinality encoding. At r=0 its factor index is empty.

Let g_i=f_P^-1(e_i), where here e_i on the right denotes the coordinate unit vector.
The generator relation theorem is

    sum_i a_i*g_i=0  iff  p^(exponent_i) divides a_i for every integer a_i.

Every x has the exact generator expansion using its canonical coordinate residues.
Therefore the diagonal p-power relations are ALL integer relations among these
generators. The ambient cardinality is exactly p^(sum_i exponent_i).

The decomposition existence is an application of the checked mathlib finite
abelian group theorem; it is not claimed as a new structure theorem.

## 2. Why the signature is intrinsic
For k>=0 write V[p^k]={x : p^k*x=0}. On a cyclic factor Z/p^e this subgroup
contains exactly p^min(k,e) elements. Product and equivalence transport give

    ell_k(V) := log_p |V[p^k]| = sum_i min(k,e_i).

For k>=1,

    ell_k-ell_(k-1) = number of i with e_i>=k,

so

    mu_k(V) = (ell_k-ell_(k-1))-(ell_(k+1)-ell_k)

is exactly the number of factors with e_i=k. The Lean formulas use natural
subtraction; the proved count identities justify its nonnegative interpretation.
Zero exponents are excluded, so their multiplicity is zero.

Every chosen presentation therefore has the same exponent multiset. Sorting
it produces a unique list. Conversely, equality of the multisets supplies an
index matching by exponent and hence a coordinate isomorphism. Additive maps
of ZMod(p^r)-modules respect every scalar. Thus the signature classifies the
underlying ZMod(p^r)-module isomorphism type.

This is NOT a classification of the complete tuple (module, initial state,
digit maps, output functional). Module type alone does not determine a sequence.

## 3. Operator transport and mixed moduli
For an R-linear T define T^P=f_P*T*f_P^-1. Initial and output data are transported
by the same equivalence. Every ordered word commutes exactly with encoding and
decoding. For a second presentation Q, f_Q*f_P^-1 conjugates all transported maps.

The j,i matrix entry t_ji lies in Z/p^e_j and is obtained by applying T^P to the
i-th cyclic generator. It satisfies

    p^e_i * t_ji = 0,

or equivalently on canonical integer representatives,

    p^max(e_j-e_i,0) divides t_ji.val.

The source/destination orientation is fixed: destination rows, source columns.
The exact coordinate formula is

    (T^P x)_j = sum_i x_i.val * t_ji  in Z/p^e_j.

These are not arbitrary matrices over one field. Changing a source residue by
its modulus cannot change an output because of the displayed annihilator law.
The source theorem derives this from actual transported homomorphisms. It does
not assert a separately formalized constructor for every supplied admissible matrix.

## 4. Actual masks and coefficient outputs
For prime p, r>0, integer A,B, p not dividing B(0), and A(0)=B(0) in Z/p^r, the
inherited canonical F satisfies F(0)=1 and B(z)F(z)=A(z)F(z^p). We choose a
presentation of the exact Block31 reachable module and transport its actual
initial state, digit maps and output.

For every n, processing the least-significant-first digits of n in the presented
machine gives coeff_n(F). All word and coefficient equalities come from exact
coordinate conjugacy with Block31, not from comparisons of sampled outputs.
Positive-precision output reduction is preserved; no cross-precision identification
of state modules is made. The state count is unchanged from Block31.

## 5. Exact reference implementation
Let H Z^N be the integer preimage lattice of a residue submodule of (Z/p^r)^N,
so p^r Z^N is contained in H Z^N. Put K=H^-1*(p^r I). K is integral and

    M ≅ Z^N / K Z^N.

The reference requests a Smith proposal D=U K V. It verifies integral matrices,
unimodularity of U,V, diagonal positivity and the divisibility chain. Coordinates
of x are U H^-1 x modulo diag(D); inverse coordinates are H U^-1 y modulo p^r.
Diagonal factors equal to one are omitted. A transition matrix becomes

    U H^-1 T H U^-1,

with each destination row reduced by its own diagonal modulus. All source
annihilator constraints are independently checked before the presentation is used.

These finite computations provide certificate-checked examples and reference code.
They are not a Lean correctness proof of SymPy, not equality with Lean's classical
coordinate choice, and not an independently implemented kernel audit.

## 6. Restriction witnesses
Z/4 and (Z/2)^2 both have four elements but different signatures {2} and {1,1}.
Their 2-torsion counts are 2 and 4 respectively; no additive isomorphism exists.

On (Z/5)^2, T(x0,x1)=(x1,0) has the same module signature after swapping
coordinates, yet the entry at destination0/source1 changes from1 to0. The two
matrices are conjugate, not literally equal. The module signature never selected
one of them.

A proposed map Z/2 -> Z/4 taking1 to1 fails its source relation: 2*1≠0 mod4.
The value2 is permitted, since 2*2=0 mod4. Negative controls expose these exact
contradictions rather than accepting arbitrary compilation failures.
