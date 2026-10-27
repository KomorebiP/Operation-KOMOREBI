# Komorebi: cut comparison, one-sided ideals, and unrestricted restored circuits

Date: 2026-09-21. Status: written derivations with exact finite checks and self-review. Not Lean-verified. No proof of P versus NP and no claim of publication novelty.

## 0. Target contract and lineage

The original target is P versus NP. A sufficient stronger endpoint is a superpolynomial unrestricted Boolean-circuit lower bound for an NP-complete language, with input length measured in encoded bits. We do not substitute a linear bound or a special circuit model for that target.

Authoritative predecessor: `Komorebi_PNP_Restoration_Transport_Block_2026-09-21.zip`, SHA256 `8af5cebdfca147f9643b936f1921267d644d0d7e59e79891241b8eaf54a86cde`. Its 25 sealed files are checked before and after the continuation. An extracted copy is retained under `predecessor/`.

The circuit basis is classical NOT, CNOT, and three-distinct-wire Toffoli. Logical inputs and arbitrarily many initialized-zero ancillas may be used as workspace. The designated target may be used as a control. The circuit must implement, for every x and both values of y,

    (x,0^a,y) -> (x,0^a,y XOR f(x)).

Borrowed bits may additionally be allowed if restored uniformly; fixing their initial values reduces to the stated model. This is not a theorem about quantum circuits, relative-phase gates, measurement, un-restored garbage, or stronger gates. S denotes total gates, T only Toffolis. XOR and NOT are free when counting multiplicative complexity. Boolean degree is unique multilinear ANF degree over F2.

The predecessor proved the standard constant-factor comparison with ordinary circuits, protected-output normalization, a protected-output lower bound 2 deg(f)-3, and a general midpoint identity with a decoder-degree term. This continuation replaces the decoder in the scalar decision with a direct comparison and derives an unrestricted bound using one-sided immunity.

## 1. Exact cut comparison: the answer is inequality of two states

Split any restored circuit as C=Q composed with P, at an arbitrary gate boundary. Put R=Q inverse. Suppress restored ancillas in the initial-state notation. Define

    A(x)=P(x,0),   D(x)=P(x,1)+P(x,0),
    B(x)=R(x,0).

The predecessor's exact identity is

    A+B=f D.                                                  (1)

For completeness, C(x,y)=(x,y+f(x)) implies P(x,y)=R(x,y+f(x)). For f(x)=0 the two prefixes agree at both target values. For f(x)=1, the two values are exchanged. This proves (1), and equality of the forward and reverse difference vectors.

P is a permutation, so P(x,0) and P(x,1) differ. Consequently D(x) is never the zero vector. Set H_i=A_i+B_i. Equation (1) gives

    H_i(x) <= f(x),
    OR_i H_i(x) = f(x).                                       (2)

Thus

    f(x)=1 iff P(x,0) != Q^{-1}(x,0).                         (3)

This comparison uses no unit-certificate decoder, determinant, polynomial expansion, or choice of coordinates depending on the answer. Evaluating the supplied P and Q inverse uses S reversible gates simulated as Boolean operations, then at most one XOR per relevant register and an OR tree. Only touched registers can differ, so unused ancillas cause no hidden cost. With the n logical registers, target, and at most three new register names per gate, the overhead is O(n+S).

This is not an algorithm for SAT from its verifier: it assumes an implementing decision circuit C was supplied. It says that reconstructing the answer from an actual circuit cut is cheap.

## 2. A linear shared transport certificate, without polynomial expansion

The original unit-certificate formulation can also be made constructive. Evaluate a prefix simultaneously from u_0=(x,0) and v_0=(x,1), with the same restored boundary registers. Let u_j,v_j be the two states before gate j and delta_j=v_j+u_j.

For a Toffoli a,b -> t,

    delta'_t = delta_t + v_b delta_a + u_a delta_b,            (4)

and all other delta coordinates are unchanged. Indeed

    v_a v_b + u_a u_b
      = v_b(v_a+u_a)+u_a(v_b+u_b).

This is an exact two-point identity. It is not the ordinary differential chain rule in the quotient x_i^2=x_i; the latter is not valid without care.

Equation (4) is multiplication by an elementary matrix

    M=I+e_t(v_b e_a^T+u_a e_b^T).

The controls differ from the target, so M^2=I. CNOT has the corresponding single-entry transvection; NOT has M=I.

Start a covector lambda=e_y^T, so lambda delta_0=1. At each gate transport lambda to lambda M^{-1}. For Toffoli this is

    lambda'_a=lambda_a+lambda_t v_b,
    lambda'_b=lambda_b+lambda_t u_a,

with the remaining coordinates unchanged. Therefore, at every cut,

    sum_i lambda_i D_i=1.                                    (5)

Evaluating both endpoint traces takes 2T Boolean multiplications. Transporting the covector takes 2T more. All cut covectors share the same straight-line computation, so the total multiplication count is at most 4T, not 4T independently for every cut. The XOR/NOT cost is O(S), and old outputs can be referenced for free in a DAG. This is an arithmetic-gate count; explicitly listing every coordinate at every cut may require a larger polynomial number of output references.

This constructs small shared decoder circuits from every short reversible circuit. Large ANF degree of the coefficients, large expanded monomial count, or summing the sizes of separately recomputed cut certificates is not a valid lower bound. The construction resembles reverse-mode algebraic differentiation, but the proof here is the explicit Boolean secant calculation.

There is an even simpler generic certificate when only D is supplied: lambda_i=product_{j<i}(1+D_j). Shared prefix products take O(w) operations for w coordinates. The reversible transport construction gives a sharper history-shared accounting over all cuts.

## 3. One-sided ideals give an unrestricted restoration lower bound

For a nonzero Boolean function f define

    alpha_1(f)=min { deg(h) : h != 0 and h(1+f)=0 }.

Equivalently, h is a nonzero Boolean polynomial supported only on f's positive inputs. This is the one-sided immunity/weak-representation degree of the positive support. It is an established algebraic notion, not a newly invented measure. Define alpha_0(f)=alpha_1(1+f) when the negative set is nonempty. Do not confuse max(alpha_0,alpha_1) below with the cryptographic convention taking their minimum.

### Theorem 3.1

For any nonconstant f, every restored NCT oracle, including output-active ones, satisfies

    T >= max{0, deg(f)-1, 2 alpha_1(f)-3, 2 alpha_0(f)-3}.      (6)

Proof. A circuit with t multiplications computes coordinate functions of degree at most t+1. One self-contained proof is to replace each AND output by a fresh formal Boolean variable, express each as a product of two affine forms in preceding variables, and substitute in reverse order. Starting from an affine output, each substitution raises total degree by at most one. Boolean multilinear reduction never increases degree. This admits sharing and cancellation.

Choose a cut with a=floor(T/2) preceding Toffolis and c=ceil(T/2) following Toffolis. The forward coordinates A_i have degree at most a+1; reverse coordinates B_i have degree at most c+1. Thus every H_i=A_i+B_i has degree at most ceil(T/2)+1.

By (2), every H_i lies in the positive-support ideal, and at least one H_i is nonzero when f is nonzero. Hence

    alpha_1(f) <= ceil(T/2)+1,

which gives T>=2 alpha_1(f)-3, with the integer rounding valid for both parities of T.

Appending an output NOT implements 1+f without changing T, proving the alpha_0 bound. The degree-minus-one bound applies directly to the original target coordinate. QED.

No passivity hypothesis, output-normalization overhead, or assumption that the suffix reverses the prefix occurs in this argument.

### Monotone specialization

If f is monotone and nonzero, then

    alpha_1(f)=min {|S|: f(1_S)=1}.                          (7)

More strongly, the Boolean ideal I_f={h:h(1+f)=0} has a monomial vector-space basis indexed by positive supports S. If S is a negative support, every T subset S is also negative. The coefficient of x^S in h is XOR_{T subset S} h(1_T)=0. Conversely, every monomial whose support S is positive vanishes on the negative inputs. This proves the basis assertion and (7).

Thus I_f can have exponentially many basis monomials, but its minimum nonzero degree has the simple value (7). The negative-side statement follows by flipping all input coordinates.

### Exact monomial calibration

For f=x_1...x_k, its only positive logical input is all ones, so alpha_1(f)=k. Therefore T>=2k-3 for arbitrary restored circuits. The product chain and its uncomputation use exactly 2k-3 Toffolis, with no other gates. Hence, for k>=2,

    min T = min total NCT gates = 2k-3.                       (8)

This closes the predecessor's protected-versus-active gap for this family. It is not a new claim that the 2k-3 multicontrol resource count was unknown: published constructions already describe that count as optimal. Our result is a derivation through the cut-comparison invariant, in the stated classical model. It does not apply to more powerful quantum operations or discarded workspace.

## 4. An NP-complete family with an unrestricted (2-o(1))N bound

For M=4^r, r>=2, put K=M-sqrt(M) and let J_M be K-CLIQUE on M labeled vertices. The actual input length is N=binom(M,2).

Every smallest positive graph is exactly a K-clique, so

    alpha_1(J_M)=q=binom(K,2).

Theorem 3.1 gives

    T_st(J_M) >= 2q-3
               = (M-sqrt(M))(M-sqrt(M)-1)-3
               = 2N-2 M^(3/2)+M+sqrt(M)-3
               = (2-o(1))N.                                (9)

This applies to unrestricted restored classical NCT oracles, not merely output-passive ones. It is still linear, and is not a new best lower bound for ordinary fan-in-two Boolean circuits.

### Uniform NP-completeness reduction

Given CLIQUE(G,k) on v vertices, 2<=k<=v, let s be the smallest power of two at least max(v,4). Put M=s^2 and K=M-s. Add a=K-k mutually adjacent vertices, adjacent to all original vertices. Add b=s-v+k completely isolated vertices. Then v+a+b=M, both counts are nonnegative, and M=O(v^2).

The nonisolated core has clique number a+omega(G); an isolated vertex cannot be in a K-clique. Therefore the enlarged graph contains a K-clique iff G contains a k-clique. Trivial thresholds can be mapped to fixed yes/no examples. Membership in NP is witnessed by K vertices, whose edges can be checked in polynomial time.

The recognized language restricts to the stated square-power vertex lengths and rejects other encodings. The reduction's graph description has O(v^4) bits, a polynomial overhead.

For comparison with the preceding degree bound, all these thresholds exceed M/2 and M is a power of two. The predecessor's binary-tree symmetry proof gives deg(J_M)=N. Thus (9) exceeds the degree-only N-1 bound for the displayed family.

Examples (bounds, not circuit synthesis):

| M | K | input bits N | degree-only N-1 | new restored-Toffoli lower bound |
|---:|---:|---:|---:|---:|
|16|12|120|119|129|
|64|56|2016|2015|3077|
|256|240|32640|32639|57357|
|1024|992|523776|523775|983069|

## 5. Attempted exponential amplification: ideal dimension is not packet count

For CLIQUE, the degree-q part of I_f has basis

    m_K(G)=product_{e subset K, |e|=2} G_e,

indexed by K-vertex subsets. Its dimension is binom(M,K), superpolynomial in N for the family above. I tried to turn this dimension into a requirement for many separate safe discrepancy packets H_i.

That implication is false without charging generation cost.

### Theorem 5.1: low-degree semantic packet compression

Let an n-bit Boolean function be represented exactly as an OR of D predicates m_1,...,m_D. There exist at most n+1 parity combinations

    h_j = XOR_l c_{jl} m_l

such that

    h_j <= f for every j,
    OR_j h_j=f.                                               (10)

If the m_l have degree at most q, so do the h_j.

Proof. For any positive x, the vector m(x) is nonzero. Choose each row c_j independently and uniformly from F2^D. For fixed x, all n+1 parity combinations vanish with probability 2^{-(n+1)}. There are at most 2^n inputs, so the union bound makes the probability of missing any positive input at most 1/2. Some fixed row set covers them all. At a negative input all m_l vanish. QED.

For CLIQUE, choose its clique monomials m_K. There are therefore only N+1 degree-q safe packets needed in a semantic cover, despite the superpolynomial monomial-basis dimension.

The coefficients form (N+1)D bits and each displayed sum may contain D terms. The theorem supplies no polynomial-size circuit for evaluating them and no efficient deterministic construction. It is a counterexample to a packet-number lower-bound route, NOT a polynomial algorithm for CLIQUE.

### Exact four-vertex calibration

Let t_1,t_2,t_3,t_4 be the four triangle monomials on four vertices. The three packets

    h_1=t_1+t_3, h_2=t_2+t_3, h_3=t_4

satisfy TRIANGLE=h_1 OR h_2 OR h_3. If they all vanish, then t_4=0 and t_1=t_2=t_3. The all-one choice for the latter three forces the fourth triangle, a contradiction. Thus all four t_i vanish.

Three is minimal among parity-of-triangle covers. Exactly 12 of the 16 triangle incidence vectors are realizable; the four missing vectors are precisely those of weight three. A linear map to two bits has a kernel of dimension at least two. Two different weight-three vectors have a weight-two sum, which is realizable and nonzero. Thus such a kernel cannot avoid all realized positive vectors. The finite checker independently enumerates all 256 two-row coefficient matrices and all 64 graphs.

## 6. Exactly what remains

The original superpolynomial target is not reached. We have advanced the restoration inequality from a protected-output statement to an unrestricted statement with a one-sided-support parameter, and obtained a stronger linear coefficient for an explicit NP-complete family.

But alpha_1(f)<=n for every nonzero n-bit f: the indicator of any one accepting input has degree n. Replacing degree by the minimum circuit size of a single nonzero safe packet also cannot grow superpolynomially: the same point indicator has an O(n)-gate circuit. The difficulty must involve global coverage with shared computation.

Equation (10) defeats merely counting safe low-degree packets. Section 2 defeats inferring hardness from expanded reconstruction coefficients or summing independently recomputed cut decoders.

The remaining sufficient task is a superpolynomial lower bound on the SHARED generation of a complete discrepancy cover for an explicit NP function, with the paired forward/reverse circuit histories allowed. A short decision circuit gives a short such paired history by reversible simulation. Conversely, supplied histories are compared by (3) at linear overhead. This equivalence is an exact target reduction, not a lower bound and not an efficient synthesis algorithm from an NP verifier.

No claim that a circuit must construct every clique monomial, enumerate every witness, remain monotone, preserve preferred coordinates, or avoid dirty excursions has been used. Proving such an extra restriction without justification would invalidate the separation.

## 7. Computational contract and review

`python checks/run_all.py` verifies the inherited 25-file seal, replays both immediate-predecessor scientific checkers in controlled destinations, compares the substantive JSON results, and runs both new checkers. All arithmetic is exact. The manifest records commands, return codes, times, input/output hashes, source stability, and bounded subprocess limits.

New tests:
- All 276 Boolean functions on one through three inputs: one-sided immunity checked by GF2 kernel search and independently by enumeration of all 6,375 nonzero supported functions across these truth tables.
- All 168 monotone four-input functions: the minimum-support/ideal-degree identity.
- 306 specified restored circuits, including 20 output-active identity-loop variants, a uniform borrowed-bit cubic circuit, and monomial chains through ten inputs. All 13,969 gate cuts checked over full logical truth tables, with 263,607 covector coordinate checks. A separate scalar evaluator covers 4,240 input/target cases for the small canonical oracles. This is not an exhaustive circuit search.
- All 960 elementary three-wire gate/endpoint pairs: exact secant update.
- All 4,306 source graph/threshold pairs through five vertices: padding to 16- or 64-vertex targets, with independent exact maximum-clique evaluation of the actual resulting graph.
- Small CLIQUE ideals through four vertices: exact GF2 one-sided-degree computation.
- All 64 four-vertex graphs and all 256 two-row parity matrices: the three-packet example and its finite optimality.

The asymptotic lower bounds and random-hash existence statement are written proofs. The large numerical table only evaluates their closed-form consequences; it is not large-instance synthesis or exhaustive graph enumeration.

The proofs were self-reviewed, particularly for: XOR versus OR, arbitrary output use, degree rounding, the distinction between positive support and two-sided algebraic immunity, gate legality, unit-certificate sharing, actual encoding length, and nonuniform versus uniform assertions. The first combined replay runner failed because a required sibling module was absent from its isolated directory. Both unchanged predecessor modules are now copied and hashed; the failure is preserved and the full runner rerun. No Lean run, independent human review, or fresh-agent review occurred.

## 8. Bounded external-source check

The following primary sources were consulted for terminology and existing context. The derivations above are provided explicitly; a bounded search is not a novelty audit.

1. Mathias Soeken, *Determining the Multiplicative Complexity of Boolean Functions using SAT*, arXiv:2005.01778v1, Section III. Standard degree-minus-one bound and shared XOR-AND model. https://arxiv.org/html/2005.01778v1
2. Chris Beck and Yuan Li, *Represent MOD function by low degree polynomial with unbounded one-sided error*, arXiv:1304.0713v1. One-sided immunity/weak representation and ideals supported on a Boolean function. https://arxiv.org/html/1304.0713v1
3. Tanuj Khattar and Craig Gidney, *Rise of conditionally clean ancillae for efficient quantum circuit constructions*, arXiv:2407.17966v2. The 2n-3 multicontrol Toffoli count is already described as optimal. Our gate model and proof scope remain explicitly classical. https://arxiv.org/html/2407.17966v2
4. Joan Boyar and Magnus Gausdal Find, *Multiplicative Complexity of Vector Valued Boolean Functions*, arXiv:1407.6169v3. Context for shared multiplicative complexity and the limits of simple nonlinearity measures. No historical statement about the current circuit frontier is imported from this older article. https://arxiv.org/html/1407.6169v3

One PMC page returned a browser challenge; it was not used as a theorem dependency. The primary arXiv texts supplied the required definitions. No PDFs were needed for the load-bearing source check.
