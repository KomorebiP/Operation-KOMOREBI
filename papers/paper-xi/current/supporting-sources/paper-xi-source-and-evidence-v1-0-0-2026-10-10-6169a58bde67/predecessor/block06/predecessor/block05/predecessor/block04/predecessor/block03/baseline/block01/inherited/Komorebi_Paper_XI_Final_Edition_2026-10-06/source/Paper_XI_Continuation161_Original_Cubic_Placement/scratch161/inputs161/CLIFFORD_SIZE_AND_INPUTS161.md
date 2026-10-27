# Clifford size bounds and the exact original arithmetic inputs

Ordinary proofs and a focused input audit, Block161. No new Lean run is
claimed. The two-cubic fixture remains realized by Block157; nothing below
reopens it. The purpose is to determine exactly which size bound a common
arithmetic construction may use, without silently strengthening H1.

## 1. What is actually supplied

The original paper is pinned in `PINS_INPUTS161.json`. Its Definitions9.1,
11.1 and15.1 and Theorems15.4 and16.2 are the controlling passages.

| Input | Exact supplied object | Data not supplied by that clause |
| --- | --- | --- |
| One-break Clifford datum,9.1 | Finite `N` normal in `G`; elementary abelian `A=G/N`; irreducible complex representations `Pi` and `rho`; invariant isomorphism class of `rho`; `Pi` restricts isotypically to `rho` | A second independent break acting on the same multiplicity space |
| Whole type,10 | An actual maximal simple character `theta` for a general linear group over the original local field, its actual groups `H1 <= J1 <= J`, its whole quotient, and the canonical beta extension as an external standard input | A coordinate embedding of a separately supplied type into a new common parameter field |
| Bridge,11.1 | An equivariant symplectic isometry from the Galois envelope to that whole type quotient, a common central character, and the stated dyadic extension data | A residue cuspidal factor, common defining sequence, or embeddings between different type fields |
| Break decomposition,15.1 | A finite orthogonal direct sum of finite symplectic packets, preserved by the declared stabilizer | A displayed action of the total envelope on a fixed Galois representation, or a nested Clifford tower recovering it |
| Break assembly,15.4 | The literal tensor product of the supplied finite bridges, including the stated phase and holonomy conditions | An actual arithmetic common type |

Section10 writes `GL_n(K)` for one type. When this definition is used
breakwise, the paper supplies actual corresponding type targets but gives
no equation relating their parameter-field degrees, orders, or ambient
ranks to each other. Nor does Definition15.1 contain a numerical equation
relating the newly displayed tensor carrier to the dimension of a fixed
original Weil representation. This is a statement about the displayed
definitions, not a denial of intended Galois structure.

The inherited Lean interface is more explicit about its boundary.
`FiniteBreakAssembly.Data` contains central extensions, group lifts,
irreducible actions and central characters. It contains no local field,
matrix rank, arithmetic simple character, or common source representation.
`ConditionalAtomicComparison.source` takes an `allowed` subtype of finite
diagrams and an independently supplied `Realization` on it. The
`Realization.exists_atom` field is not constructed there.
`ActualSourceCandidate111` instead starts with an actual field embedding
`(m -> E) ~= (n -> F)`, actual `D,theta,kappa`, the residue representation,
and the whole quotient/lattice dictionary. It constructs an arithmetic
candidate from these inputs. There is no finite-diagram argument that
constructs the inputs.

Consequently neither interface contains a hidden theorem that puts
arbitrary supplied type fields into the nested unramified coordinates of
Block160. Field ramification and prescribed full characters remain real
data. A new common host using the full scalar-pushout maps must declare and
prove those maps, as Block157 did, rather than assert those field embeddings.

## 2. The radical does not weaken the one-break degree equality

**Lemma1 (irreducible projective degree).** Let `A` be a finite abelian
group and let `T_a` be a nonzero finite-dimensional irreducible complex
projective representation with scalar multiplier `c`. Put

\[
b(a,b)=c(a,b)c(b,a)^{-1},\qquad R=\operatorname{rad}(b).
\]

Then

\[
\boxed{(\dim M)^2=|A/R|.}                                      \tag{1}
\]

In particular, for an elementary abelian p-group, if
`dim_Fp(A/R)=2r`, then `dim M=p^r` even when `R` is nonzero.

**Proof.** Every `T_r`, for `r` in `R`, commutes with every projective
generator, hence is scalar by Schur's lemma. Choose a section
`s:A/R -> A` with `s(0)=0`. The operators `S_q=T_{s(q)}` multiply
projectively: the difference between `s(q)+s(q')` and `s(q+q')` belongs
to `R` and therefore acts by a scalar. All original `T_a` are scalar
multiples of these operators, so the resulting projective representation
on `A/R` remains irreducible. Its commutator is the induced nondegenerate
pairing. The nondegenerate twisted-algebra theorem8.3 of the original
paper gives (1). Notice that the original cocycle itself was not claimed
to descend literally: its quotient multiplier includes the scalar values
of the radical and the chosen section. This avoids losing central data.

**Corollary2 (the actual one-break Clifford bound).** For Definition9.1,

\[
\boxed{\dim\Pi=\dim\rho\;p^r,\qquad
       p^r\mid\dim\Pi,\qquad r=\tfrac12\dim_{\mathbf F_p}V_\rho.}
                                                                  \tag{2}
\]

**Proof.** The isotypic evaluation isomorphism is
`X ~= W tensor M_rho`. Proposition9.2 proves irreducibility of the
projective multiplicity action. Apply Lemma1 and take dimensions.
Thus nondegeneracy of the pairing on `A` itself is unnecessary for this
bound. The nondegenerate quotient is the correct object.

If this `Pi` is the original n-dimensional source, (2) gives `p^r | n`.
If it is only an identified constituent or subspace of that source, its
embedding supplies `p^r <= n`; divisibility needs the additional actual
dimension identity, for example the Clifford restriction identity below.
The abstract word "envelope" alone does not supply either identification.

## 3. Several independent factors on one carrier

**Lemma3 (projective module divisibility).** For a finite abelian `A` and
any nonzero finite-dimensional projective representation `T` with fixed
multiplier `c`, let `D=sqrt(|A/rad(b)|)`. Then

\[
\boxed{D\mid\dim M.}                                           \tag{3}
\]

**Proof.** Complete reducibility is elementary here. For any invariant
subspace `U` and any linear projection `P` onto it, average

\[
P_0=|A|^{-1}\sum_{a\in A}T_a P T_a^{-1}.
\]

Conjugation by the `T_a` is an honest action, because scalar multipliers
cancel. Thus `P_0` commutes with every `T_a`. Its image lies in `U` and
its restriction to `U` is the identity, so it is an equivariant
projection. Induction on dimension decomposes `M` into irreducible
projective modules with the same multiplier. Lemma1 gives degree `D`
for each constituent, proving (3).

**Corollary4 (a genuine common envelope bounds the tensor degree).**
Suppose finite elementary abelian groups `A_i` have projective actions on
one common nonzero carrier `M`, with the specified multipliers `c_i`, and
the operators of distinct factors commute. Write
`dim_Fp(A_i/rad(b_i))=2r_i`. Then

\[
\boxed{p^{\sum_i r_i}\mid\dim M.}                               \tag{4}
\]

**Proof.** Multiply the factor operators in a fixed order to obtain a
projective action of `product_i A_i`. Its scalar multiplier is the product
of the `c_i`, since cross operators commute. Its commutator radical is
the product of the individual radicals. Lemma3 gives (4).

The same conclusion holds when a supplied total central-product
Heisenberg representation acts on `M` with the stated nontrivial common
central character. This is exactly the action whose irreducible degree
is the product of the break degrees. If `M` is a subspace of an
n-dimensional Galois representation, the product is at most `n`. If
`M` is its full carrier, the product divides `n`.

This is stronger than bounding every break separately. The individual
bounds cannot be multiplied without independence on a common carrier.
For example, the degree-p Weyl representation of a symplectic plane can
be used twice on the same p-dimensional space. Each copy has degree p,
but their mutual operators do not commute, and degree p squared does
not divide p. Merely labelling the two copies as different packets and
forming an external orthogonal sum supplies no common action.

## 4. An actual ramification/Clifford tower also gives the product bound

**Lemma5 (nested Clifford product, including orbit factors).** Let

\[
G_0\triangleleft G_1\triangleleft\cdots\triangleleft G_s
\]

be finite groups with each successive quotient elementary abelian of
characteristic p. Choose an irreducible complex representation `rho_s`
of `G_s`, and recursively choose a constituent `rho_{i-1}` of
`rho_i|G_{i-1}`. Let `I_i` be its inertia group in `G_i`, let
`t_i=[G_i:I_i]`, and let `V_i` be the nondegenerate commutator quotient of
the projective multiplicity action on its isotypic component. Put
`dim_Fp V_i=2r_i`. Then

\[
\boxed{
\dim\rho_s=\dim\rho_0\prod_{i=1}^s t_i\,p^{r_i}.
}                                                               \tag{5}
\]

**Proof.** The distinct `G_{i-1}`-isotypic components of `rho_i` are
permuted transitively by `G_i`: otherwise the sum of an orbit would be a
proper invariant subspace. They have equal dimensions and their number
is `t_i`. Let `X_i` be the component belonging to `rho_{i-1}`. It is an
irreducible `I_i`-representation. Indeed, an `I_i`-invariant proper
subspace of `X_i` and all its translates would have a direct sum that
is a nonzero proper `G_i`-invariant subspace of the original carrier.
The quotient `I_i/G_{i-1}` is elementary abelian as a subgroup of
`G_i/G_{i-1}`. Corollary2 applies to this actual Clifford datum, giving
`dim X_i=(dim rho_{i-1})p^{r_i}`. Multiplying by `t_i` and iterating
proves (5).

The isotypic tower is the special case `t_i=1`. Thus a supplied genuine
Clifford tower proves the full product bound without assuming the tensor
factors already commute on one common presentation. This is a useful
constructive way to extract the bound from actual finite source data.
To apply it to an already supplied break diagram, each of that diagram's
packets must be identified with its indicated tower envelope. An unrelated
refinement of the group chain does not certify the given break factors.

The elementary abelian requirement has not been suppressed. For a
general nonabelian quotient, projective operators need not have scalar
commutators, and a symplectic radical quotient need not exist. One must
provide actual abelian stages or a different argument. Nor do arbitrary
successive ramification quotients automatically give the required
isotypic datum: the inertia-group passage above is what handles that
issue once those groups and constituents are supplied.

## 5. Consequence for a large arithmetic carrier at unchanged rank

Suppose either Corollary4 or Lemma5 has established for the original
rank n that

\[
D=p^R\le n,\qquad
R=\tfrac12\sum_i\dim_{\mathbf F_p}V_i.
\]

Let the residue field of the original local field have cardinality
`q=p^f`. The one-step unramified maximal-field construction of Block160,
with field degree n, residue rank one and even positive critical depth,
has whole quotient dimension `n(n-1)` over `F_q`. Its half-dimension
over `F_p` is

\[
R_{\mathrm{host}}=\frac{f n(n-1)}2.
\]

For n at least2,

\[
p^R\le n\le2^{n-1}\le p^{f n(n-1)/2},
\qquad R\le R_{\mathrm{host}}.                                \tag{6}
\]

The middle elementary inequality follows by induction from `n<=2^(n-1)`.
At n=1 the original bound forces R=0. Therefore such genuine Galois
data always fit *dimensionally* into an isotropic reduction of this
actual fixed-rank host: in a symplectic basis of its F_p-space, choose
an isotropic subspace of dimension `R_host-R`; the reduction then has
dimension `2R`.

This is a dimension construction, not a new whole-quotient equality.
It does not require the isotropic subspace to be stable under a supplied
native stabilizer. Block159 handles recovery when it is not invariant,
but native equivariant source placement still needs its own proof.
It also does not put the original type fields into this unramified field,
or retain their full characters by literal restriction. Retaining them
through full scalar-pushout group maps is a different, explicit operation.

## 6. Exact conclusion for the original allowed class

There are now two proved ways to obtain the useful product bound:
an actual common projective action, or an actual successive Clifford
tower. The supplied one-break datum alone gives the exact individual
bound even with a radical. The literal original finite assembly interface
does not supply either multi-break certificate, so the product bound
must not be asserted for every value of that bare interface.

The construction can use (6) for genuine source data for which one of
these certificates is extracted. It cannot use the bound as a substitute
for extracting that certificate, nor define the original allowed class
to consist only of already certified data. No new H5 assumption, LLC
construction, or extra factor test is introduced here.

## Review and provenance

The ordinary proofs above use elementary complex representation theory
and original Theorem8.3. The original paper and retained interfaces were
read directly. The claims about actual unramified host size invoke the
specific proved Block160 construction and its exact parity formula.
No external theorem was looked up, no numerical experiment was used,
and no Lean compilation was attempted.

Self-review checked the radical scalar step, the projective quotient
multiplier, the averaging projection, the non-isotypic inertia-group
passage, the independence needed for tensor bounds, and the distinction
between arithmetic rank and Heisenberg degree. Final proofreading covered
this new file only. No inherited source was edited.
