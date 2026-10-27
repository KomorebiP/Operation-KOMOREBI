# Independent audit of the radix transport and actual coefficient bridges

Audit date: 2026-10-05. Reviewer: independent subagent `radix_review`.
No author file was edited. No Lean build was run. Primary proof sources were
read locally; no conclusion rests on an archive title or a claims ledger.

**Normalized target.** For every ordinary integer T>=0 for which
r=(17659+2^18 T)2^640-161 has true terminal161, prove
Phi_r(2^(2r-25)) != 0. Universal residual simplicity additionally requires
the other Euler address families in TARGET.md.

**Primary verdict: incomplete, with the smallest missing implication.** The
actual Bernoulli unit vector has not been excluded from simultaneous value
and derivative contact. The two audited notes do not claim to supply that
implication. Their exact radix transformations, deformation theorem, and
coefficient/lattice gate results pass this audit in the stated scopes.
No substantive mathematical error was found in those claims.

## 1. Claim cards and dependency graph

The radix claims concern integral restricted power-series units U_m,
integer slopes C>=1, and radix B=2^C. Their finite block identities hold for
C>=1; the infinite Tate-algebra tail assertion is used only for C>=2, and
the actual Euler tower has C>=4. The source A is the inherited restricted
integral unit with A=1 mod2 and A'=0 mod2. The actual normalized chart and
complete coefficient certificate are inherited from the immutable base.

The bridge claims concern the prescribed rational coefficients of
(z/sinh z)^2, ordinary coefficient-index sections, and the explicitly
defined spatial sections of rational or meromorphic transforms. They do
not equate these different section operations.

Dependencies reconstructed independently:

- Actual row formula -> integral odd-factor unit -> strict intrablock
  divisibility -> exact block-unit identity -> affine rescaling and its
  derivative scale -> forced joint-zero equations.
- Inherited actual chart certificate and source integrality -> a uniform
  critical-point contraction -> a unique odd deformation parameter ->
  exact double contact after changing only beta_r.
- Prescribed beta and the complex meromorphic generating function ->
  infinitely many poles of the canonical dyadic mask -> failure of the
  direct rational-mask hypothesis.
- Rationality, nonzero coefficients, and exponential real decay -> no
  finite rational digit representation -> infinite section rank over Q
  and Q_2.
- Actual finite prefix -> its residue 1/16 meromorphic section -> occupied
  distinct eigenmodes -> eigenvalue 1/4 -> no finite spanning stable
  Z_2-lattice for r>=3.
- Full spatial rational transform -> exact periodic coefficient lattice
  -> Smith invariants -> a valid reduction-size formula, without a scalar
  nonvanishing conclusion.

The leaves are elementary internal arguments, the inherited complete local
Euler certificate, and the retrieved primary bridge statements. The huge
actual Bernoulli index was not independently recomputed in this audit.
The inherited coefficient certificate was used only in its declared
complete 94-bit range; its role is explicit rather than hidden in the
bounded checker.

## 2. Obligation matrix

| Obligation | Status | Decisive reason |
|---|---|---|
| Half-index binomial factor and row slope 4 | Passed | Separating even and odd factors gives exactly the displayed binomial quotient and an integral odd-factor unit. |
| Analytic unit grouping, including the initial partial block | Passed | Every ratio before the next radix boundary contains at least one factor2 in the Tate algebra. |
| Affine quotient D_(a,q) | Passed | The q factors indexed by a+Bj give B^q(Y)_q; all remaining factors have valuation<C, and their scalar valuation cancels the factorial quotient. |
| Successive radix 16 and cumulative 2^68 | Passed | The new slope is CB; starting at 4 gives 64 and next radix 2^64. |
| Derivative after a nonaligned cut | Passed | Differentiation in Y contributes B P'(a+BY); the prefix forcing remains in both equations. |
| Two-coefficient exact double-contact construction | Passed | The source jet determinant is odd, the correction is strictly smaller than each original coefficient, and the curvature valuation remains 149. |
| One-coefficient deformation and normalization | Passed | A contraction determines c(u); the critical value is 1+u mod2 coefficientwise; changing beta_r changes the natural normalization by one common unit. |
| Nonrational canonical mask for every actual fixed cutoff | Passed | Its numerator has infinitely many negative-real double poles where its denominator is analytic. Denominator zeros cannot remove those poles. |
| Infinite rational and Q_2 section rank | Passed | Finite rational digit matrices give a polynomial denominator bound, incompatible with nonzero exponential decay. Finite rational evaluation minors preserve rank under field extension. |
| Spatial raw-lattice basis and Smith invariants | Passed | The four rational functions are independent, period 12 detects every coordinate, and all determinantal divisors were recomputed. |
| Stable integral lattice for the actual prefix | Passed as a nonexistence result for r>=3 | The actual orbit contains t^2 and zero section acts on it by 1/4; such an eigenvalue cannot occur in an integral matrix. |
| Bridge source applicability | Passed in the stated limited scope | The retrieved theorems concern compiler work, a chosen representation, or finite section lattices, rather than contact of the Euler moment function with its actual prefix. |
| Actual stationary nonvanishing | Not addressed by these new positive results | No Bernoulli-specific invariant excluding the joint contact has been obtained. |
| Higher-address coverage | Out of scope | The immediate focused chart does not cover the universal target. |

## 3. Critical reconstructions

### Radix units and derivative forcing

For the affine quotient, v2((Bq)!)=(B-1)q+v2(q!). Removing the q factors
B(Y-j) leaves total scalar valuation (B-C-1)q. The remaining factors are
2^v times an odd constant plus a coefficient divisible by 2^(C-v), with
v<C. Thus D_(a,q) is a polynomial unit reducing coefficientwise to 1.
This proves the exact analytic lift and justifies retaining the units;
it does not identify the new units with those at a smaller Euler cutoff.

For a partial initial block, differentiating
T_r(a+BY)=P(a+BY)+T_new(Y) gives
B T_r'(a+BY)=B P'(a+BY)+T_new'(Y). A double zero therefore yields exactly
the two forced equations printed in the note. Discarding P or its
derivative would be invalid. The note does neither.

### One changed coefficient is enough in the enlarged dyadic family

At T=0 the inherited congruence gives K'/2=Z mod2 and K''/2=1 mod2.
For L(Z)=A(10202+2^15 Z), L=1 mod2 and L'/2 is divisible by 2^15.
The equation K'(Z)/2+uL'(Z)/2=0 is Z+2R(Z,u)=0 with R integral and
restricted. Iteration is a strict 2-adic contraction in Z_2<u>, so c(u)
exists uniquely and is 0 mod 2. Consequently
Psi(u)=K(c(u))+uL(c(u))=1+u mod2 coefficientwise. The same contraction
argument gives its unique zero u_star, which is odd. Curvature divided
by 2 stays odd, so the resulting zero has order exactly 2.

The fixed-normalization q=0 coefficient is 2^154. Multiplication of beta_r
by 1+2^24 u_star therefore adds exactly 2^178 u_star A to G. With the
modified kernel's own denominator beta_tilde_r, every residual term is
then multiplied by the common unit (1+2^24 u_star)^(-1). Multiplicity and
all coefficient valuations are unchanged. All other beta coefficients,
including the entire prefix, remain exactly fixed. This is an exact
dyadic deformation theorem, not a Bernoulli or rational counterexample.

### Coefficient-rank gate

Finite rational section rank allows a basis consisting of actual
rational sections and rational digit matrices. A length-ell digit word
has denominator dividing C D^(ell+1). Therefore a nonzero coefficient
cannot have absolute value smaller than a fixed inverse power of n+1.
Taking sqrt(8)<R<pi in the Cauchy bound gives exponential decay both for
beta_m and for every fixed-r gamma_(r,q). Their nonvanishing is part of
the exact beta valuation theorem. This contradiction applies to every
fixed radix k>=2, since its word length is also O(log n).

Passing from Q_2 back to Q is justified: choose a finite invertible
evaluation minor of a rational basis of sections. Every other rational
section has rational coordinates obtained from this minor. There is no
unstated embedding of Q_2 into the real numbers.

### Meromorphic spatial-state lattice

The spatial extension uses the p-adic logarithm branch satisfying
log(zeta*y)=log(y) for 2-power torsion zeta. The root-of-unity filter then
gives C_b[y^j t^k]=2^(-k)y^((j-b)/2)t^k in its stated parity class. This
is an algebraic meromorphic continuation; no measure interpretation of
the prefix states is assumed.

Residue 1 modulo 16 isolates j=1 from {+-1,+-3,+-9}; its coefficient at
each t^(2n-2) is the nonzero value displayed in the bridge note. Further
zero sections produce a Vandermonde matrix in the distinct rational
eigenvalues 2^(2-2n). Thus every one of those modes lies in the actual
orbit span. For r>=3 the t^2 eigenline has eigenvalue 1/4. An integral
matrix has monic integral characteristic polynomial, so all eigenvalues
are integral over Z_2; 1/4 is not. This excludes every finite spanning
stable integral lattice for that transfer, not merely the chosen basis.
It does not exclude a depth-dependent rescaling with a new precision
ledger, or another representation.

## 4. Source and execution checks

The retrieved Block05 theorem is a Kummer carry identity for compiler
correction indices. Block12's displayed parameter envelope becomes
2P+2+d(d+1) at p=2,h=0. Neither statement places a bound on the precision
at which an Euler critical scalar must become nonzero.

Bridge01's negative-binomial correction formula was reconstructed from
BF=A F(y^p) and B^p=B(y^p)+pE_B. Bridge02's relevant criterion concerns
preservation of the literal one-layer formula. For the actual normalized
spatial mask, [y^2]E_B=-1, so that formula fails modulo 4 although an
exact spatial compiler exists. The note's semantic distinction is valid.

The Universal Lane manuscript explicitly assumes an integer-valued
sequence of finite rational section rank in its integral-lattice
section. Its typed obstruction comparison also explicitly requires a
map of the underlying correction data. The audit does not import an
unrestricted bridge from this source.

Both exact checkers were replayed without changing author files, using
a temporary output directory. The radix replay produced the same result
bytes as certified_run_reviewed/results.json (also identical to the
superseded final-named result). It repeated 21600 weight comparisons,
64 rational polynomial quotient checks, the 220-bit two-jet calculation,
and the 93-bit one-coefficient joint Hensel model. The bridge replay was
byte-identical to certified_run/results.json and recovered Smith
invariants (2,2,2,12), along with the documented beta, gamma, and prefix
checks. These bounded results support the formulas, not the universal
Euler theorem.

Current manifests were checked with artifact-root verification:

```
python3 audit_helpers/validate_manifest.py --root /workspace/scratch/fa86fc5a0e51 radix_closure/radix_descent/certified_run_reviewed/manifest.json
python3 audit_helpers/validate_manifest.py --root /workspace/scratch/fa86fc5a0e51 radix_closure/bridge_inventory/certified_run/manifest.json
```

Both passed. All 11 entries in bridge_inventory/SOURCE_PINS.json matched
their current files. The earlier radix certified_run_final manifest is
superseded by certified_run_reviewed after an additional independent
source-jet check; it should not be labeled the current computation.

## 5. Exact revisions reviewed

Paths below are relative to the project root. Full source paths are also
recorded in bridge_inventory/SOURCE_PINS.json.

| Artifact | SHA256 |
|---|---|
| radix_closure/TARGET.md | 0d5d3a7f131cac8baf80ccc5b51d06bc0698559bdb7097ad99cd3441d9da171f |
| radix_descent/RADIX_JET_TRANSPORT.md | f5f95150f8292c44c63ba88caafd4ad0dd280870a67266fc11aae75bb44c959f |
| radix_descent/check_radix_jets.py | a36a2b3cb1fda4f4589c687e89ce2ef6b7e147c6ec263788e78ee61206266271 |
| radix_descent/certified_run_reviewed/manifest.json | f7d616dcf122aaab9a2aee8008aff85fd96e34dd7a02e1969fb49d28076547bc |
| radix_descent/certified_run_reviewed/results.json | b9fc91f7d91a9823cff7e057a72b6b6ee5be404e34a2adf9c5c30503481cc25f |
| bridge_inventory/ACTUAL_COEFFICIENT_BRIDGE_AUDIT.md | 4325bdb8d9f038b3997407c7a95f5a8ef44322572b19e14d86655c5a17aaf6f7 |
| bridge_inventory/check_bridge_gates.py | 47a5613de59d4e8374a864b4f424f66d9c59ddfce4f5fdbab68f7f79a7b373b2 |
| bridge_inventory/certified_run/manifest.json | 112d2dc20c938665adca1f72636e0b2d6d338d91e6255de004acf0ee4e4ae08a |
| bridge_inventory/certified_run/results.json | c18aa9b883dea57aa7ba4dd0b7b9ef0ec25e9feeac48600d472c4cc68ccf97c5 |
| cartier_mask/EXACT_SPATIAL_COMPILER.md, sections 1-3 dependency | f6b120348c1c28df00c1bf6510397a9b3636c8c12cbc1927f6e3de69fed7c6e3 |
| shifted_obstruction/critical_arithmetic/inherited_coefficients.json | 709cc3a8fb2307697d5147305c5a617147a210712e2f6f06c10837efc77eac70 |
| shifted_obstruction/critical_arithmetic/LOCAL_ARITHMETIC_CERTIFICATE.md | c87a0a50f25e92c706e10977dfbeced1533612e48547b7d25f27ec818277b41d |
| Block05 THEOREM_NOTE.md | f69c92e09e894c1c2d1c551b2a8ca630d0a094007a9a087ebff84c8cfe3095f6 |
| Block05 RadixDescent.lean | 79d2ff08d59cc792a28a71ef41f23e4330658b85c8411a21e6d5be78fe0f0109 |
| Block12 RepresentativeBudgetClosedForm.lean | fc5d284e75fe09a2beeb4ce660f505b624fd69cafeb29868e06c426ede2dff6d |
| Block12 RepresentativeBudgetParameterEnvelope.lean | dbb94aee4e341f3818c71af515a43fc1057f4a4e3fbc607996295a94fbf5022e |
| Cartier Bridge01 THEOREM_NOTE.md | 1299c454f9e2e7973829723fb0a2fc307d37683d2659fdcdbe48df854c84276d |
| Cartier Bridge02 THEOREM_NOTE.md | 1ff17c5dd35521c2c84c1b4dc57ec5b4689cd2b4a3f564453a1ab57115fffdde |
| Universal Lane Block15 manuscript in v1.16 source | f66e87b0d4b0b90ae03b23b4f0c60ea50031facdc9e35646263006def49fbf6e |

All unprefixed route paths in this table are under radix_closure/.

## 6. Strongest safe conclusion and next discriminant

The complete radix valuation data cannot alone exclude a repeated zero:
an exact one-coefficient dyadic deformation preserves that data and the
whole lower prefix while producing double contact. The direct
rational-mask and finite section-lattice hypotheses fail for the actual
beta/gamma sequences. The actual meromorphic prefix cannot be inserted
unchanged into a bounded stable-lattice argument.

These are rigorous limits on specified proof mechanisms, not a claim
that every radix-assisted proof is impossible. A surviving proof must
use an identity distinguishing the actual Bernoulli coefficient vector
from the deformation and retain the prefix forcing. The cheapest
meaningful next audit is of such a proposed invariant at the coupled
value/derivative equations; extending a finite precision check alone
does not supply it. The evolving two-function moment recursion is not
reviewed by this report.

Self-review: the newly written report was conservatively proofread for notation, source locators, and prose. Routine spacing edits only; no mathematical-token changes. No unresolved local proofreading issue remains.
