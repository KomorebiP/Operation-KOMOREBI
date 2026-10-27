# Komorebi: restoration transport, protected outputs, and an explicit CLIQUE endpoint

Date: 2026-09-21  
Status: written proofs and exact finite checks, self-reviewed. Not Lean-verified. No novelty or P-versus-NP resolution claim.

## 0. Target and source boundary

The original target remains P versus NP. A sufficient stronger target is a superpolynomial unrestricted Boolean circuit lower bound for an NP-complete language.

The immediate predecessor is `Komorebi_PNP_Stable_Dirty_Metric_Block_2026-09-21.zip`, SHA256
`9a27b285bb1970ddf9c2d77a8b6ea2ad84e41aa759a117ff487f10e2f8f451ad`.
Its mathematical model permits NOT, CNOT, and three-distinct-wire Toffoli gates, any number of initially zero ancillas, arbitrary intermediate use, and final restoration. For logical input x and target y the required map is

    (x,0^a,y) -> (x,0^a,y XOR f(x)).

One may additionally allow arbitrary borrowed bits z, provided correctness and restoration hold for every z. A lower bound with unlimited clean ancillas also applies to such implementations after specializing z to zero. No quantum gates, measurement, approximate implementation, or initialized answer advice are admitted.

Let S count all gates and T count only Toffoli gates. NOT and CNOT may be arbitrarily numerous when discussing T. Let d(f) be the degree of the unique multilinear algebraic normal form over F2. All degree comparisons below concern this Boolean degree, not real approximate degree.

The predecessor's circuit-size comparison is retained. Its test compiler had a model defect: repeated controls in a source gate AND(a,a) or OR(a,a) produced a generalized TOF(a,a,t), which is not a standard Toffoli. The repair is CNOT(a,t). This does not invalidate the written size upper bound. Details are in AUDIT.md.

## 1. Protected-output normalization

Call a circuit output-passive when its designated target y is never used as a control. It may be targeted by NOT, CNOT, or Toffoli. All other registers can be used and restored arbitrarily, including the original logical inputs.

### Theorem 1

If an arbitrary restored oracle circuit for f has S gates and T Toffolis, there is an output-passive restored oracle circuit with one additional clean bit, exactly 2S+1 gates, and exactly 2T Toffolis.

Proof. Introduce a fresh clean bit c. Run the original oracle with every occurrence of y renamed c. It maps c=0 to c=f(x), restoring all its other required registers. Apply CNOT(c,y). Run the renamed circuit in reverse. This restores c and every other workspace register; y now equals its original value XOR f(x). The actual y appears only in the copying CNOT. Every gate is valid because c is a fresh wire. The same argument works uniformly for arbitrary borrowed initial bits. QED.

In terms of minimum total lengths,

    ell_st(f) <= ell_pass(f) <= 2 ell_st(f)+1.

Thus output passivity is a justified constant-factor normal form, not an unsupported restriction to a clean subgroup. A superpolynomial lower bound for ell_pass would imply one for unrestricted ell_st. This uses the standard compute-copy-uncompute mechanism; no invention of that mechanism is claimed.

A more restrictive write-once-output form also follows: the new target is used in exactly one CNOT.

## 2. Degree generation lemma, including nonlinear reuse

### Lemma 2

Any Boolean function computed by an XOR/NOT/AND circuit using t AND gates has degree at most t+1. An arbitrary coordinate of a NOT/CNOT/Toffoli circuit using t Toffolis therefore has degree at most t+1, after constants are substituted for initially clean wires.

Proof. Regard each AND output h_j as a fresh formal Boolean variable. Between AND gates every wire is an affine combination of the inputs and earlier h_j. Thus h_j=A_j B_j with A_j,B_j affine in those variables. The final output is affine in the inputs and all h_j. Eliminate h_t,h_{t-1},...,h_1 in reverse order. At each step, replacing a single formal variable in a multilinear monomial by a product of two affine forms increases total degree by at most one. Boolean reductions v^2=v never increase degree. Starting from degree at most one and doing t substitutions gives degree at most t+1. This argument admits arbitrary sharing and cancellation. A Toffoli introduces one AND and an XOR; NOT/CNOT introduce no AND. QED.

This is the standard multiplicative-complexity degree bound, reproduced here to make the restoration argument self-contained. See Soeken (2020), Section III.

## 3. A two-sided restoration theorem

### Theorem 3

Every output-passive restored implementation of a function f of degree d>=2 uses at least

    T >= 2d-3

Toffoli gates, independently of the number of clean or borrowed workspace bits and independently of the number of NOT/CNOT gates.

Proof. Remove from the circuit all gates targeting y. The remaining workspace computation is independent of y and starts and ends at the same workspace state (on the specified initial subspace).

At an output-target gate, let a be the number of earlier workspace Toffolis and c the number of later workspace Toffolis. Its current controls can be computed both by running the workspace prefix forward and by running the workspace suffix backward from the restored endpoint.

For an output CNOT with control h, Lemma 2 gives

    deg(h) <= min(a,c)+1.

For an output Toffoli with controls h1,h2, form their product after either prefix or reversed suffix, at one additional multiplication. Thus

    deg(h1 h2) <= min(a,c)+2.

An output NOT adds only the constant 1. Because y is passive, f is the XOR of all these output increments. If deg(f)=d, at least one increment has degree at least d.

If that increment comes from CNOT, a,c>=d-1, and there are at least 2d-2 workspace Toffolis. If it comes from Toffoli, a,c>=d-2 and the output gate adds another Toffoli, giving at least 2(d-2)+1=2d-3. QED.

This is a temporal statement: the same intermediate information is constrained by its construction from the initial state and its reconstruction from the restored final state. No assertion is made that a cleaning suffix must literally reverse the forward prefix.

### Corollary 3.1: exact passive monomial oracle cost

For f(x)=x1 x2 ... xk, k>=2,

    T_pass(f) = ell_pass(f) = 2k-3.

The lower bound is Theorem 3. The upper bound is the chain of k-2 intermediate products, one target Toffoli, and reversal of that chain. All its gates are Toffoli. This is an exact result for output-passive oracles, NOT a claim that arbitrary output-active implementations require the same count.

Combining Theorems 1 and 3 only gives T>=d-1 for arbitrary circuits, which is the standard degree lower bound. The factor-two improvement must not be reported as an unrestricted improvement.

## 4. A compact NP-complete family with full Boolean degree

For M=2^r vertices define

    F_M(G)=1 iff G contains a clique of size M/2+1.

The logical input has N=binom(M,2) independent edge bits. The threshold is part of the family definition, not an additional input.

### Theorem 4

For every M=2^r, r>=1,

    deg_F2(F_M)=N.

Proof. The coefficient of the monomial containing all N edge variables is the XOR of f over all graphs, hence the parity of the number of accepting graphs.

Let H_r be the automorphism group of a complete rooted binary tree on M leaves. It acts on the vertices and hence on graphs. Recursively H_r=(H_(r-1) x H_(r-1)) semidirect C2, so |H_r|=2^(M-1). All non-singleton graph orbits therefore have even size. Clique acceptance is invariant under the group, so the parity of accepting graphs equals the parity of accepting graphs fixed by the whole group.

There are exactly r edge orbits, indexed by the level of the least common ancestor of the two endpoints. Thus a fixed graph is specified by J subset {0,...,r-1}: include all edges at a level in J and exclude all edges at other levels.

Its clique number is 2^|J|. At each selected binary split, join two isomorphic lower graphs and double the clique number; at an unselected split, take their disjoint union and keep that number. Equivalently, with vertices encoded as r-bit strings, vertices supported on the coordinates in J form a clique of size 2^|J|, and v -> v & J is a proper coloring with exactly that many colors.

Such a fixed graph has clique number greater than M/2 only when |J|=r. Exactly one fixed graph accepts: the complete graph. The top coefficient is therefore one, proving full degree N. QED.

The same argument gives, for 2<=k<=2^r,

    coefficient of all edges in CLIQUE_(2^r,k)
      = binom(r-1, ceil(log2(k))-1) mod 2.

It does not say every clique threshold has full degree. For example, the top coefficient vanishes for M=8 and k=3 or 4.

### Theorem 4.1: explicit NP-completeness reduction

The language consisting of F_M on power-of-two vertex counts is NP-complete. Membership in NP follows by supplying the M/2+1 vertices.

For hardness, start from CLIQUE(G,k) on v vertices with 2<=k<=v. Choose the smallest power of two M>=2v, so M<4v. Put K=M/2+1 and a=K-k. Add a vertices forming a clique, adjacent to every original vertex. Then add b=M-v-a isolated vertices, with no edges even to the added clique. Both a,b are nonnegative. The resulting graph has a K-clique iff G has a k-clique: its nonisolated core has clique number a+omega(G), and isolated vertices cannot belong to a K-clique. The construction has polynomial size. Trivial k values can be mapped to fixed yes/no instances.

For a direct link to SAT, the standard clause-occurrence graph uses one vertex for each literal occurrence, with edges between nonconflicting occurrences in distinct clauses. A clique of size equal to the number of clauses exists iff there is a consistent choice of one satisfying literal per clause. Composing with the displayed padding maps SAT to this power-of-two majority-clique family.

### Corollary 4.2: the endpoint actually reached

For M>=4 and N=binom(M,2), every output-passive restored oracle for F_M has

    T >= 2N-3.

Every unrestricted restored oracle has at least N-1 Toffolis, from either Lemma 2 directly or the protected-output normal form.

Examples:

| M | implicit clique threshold | input bits N | passive lower bound | unrestricted degree lower bound |
|---|---|---|---|---|
| 4 | 3 | 6 | 9 | 5 |
| 8 | 5 | 28 | 53 | 27 |
| 16 | 9 | 120 | 237 | 119 |
| 64 | 33 | 2016 | 4029 | 2015 |

These are LOWER bounds, not matching circuit constructions or circuit-synthesis results. They are linear in the actual input length N. They do not separate P from NP and are not claimed as new best unrestricted circuit bounds.

## 5. Exact transport through an output-active midpoint

The previous theorem exploits protected outputs. We also derive an identity for arbitrary output-active circuits, without assuming that an output direction stays linearly visible.

Split an oracle C into a prefix P and suffix Q, so C=Q composed with P. On clean boundary inputs, C(x,y)=(x,y+f(x)), with ancillas suppressed in this notation. Let R=Q inverse. For every register coordinate i define Boolean functions of x:

    A_i=P_i(x,0),       D_i=P_i(x,1)+P_i(x,0),
    B_i=R_i(x,0),       E_i=R_i(x,1)+R_i(x,0).

All additions and products in this section are in the Boolean ring over F2. P(x,y)=R(x,y+f(x)) implies

    D_i=E_i,
    A_i+B_i=f D_i.                                      (5.1)

The D_i have no common zero: otherwise P would map (x,0) and (x,1) to the same state, violating injectivity.

Therefore there exist Boolean coefficient polynomials lambda_i with

    sum_i lambda_i D_i=1.                              (5.2)

One explicit choice is lambda_i=product_(j<i)(1+D_j); its telescoping sum is 1+product_i(1+D_i)=1. Define kappa(P) to be the minimum possible maximum degree of the nonzero lambda_i in (5.2).

Multiplying (5.1) by the lambda_i gives exact reconstruction:

    f=sum_i lambda_i (A_i+B_i).                        (5.3)

If the prefix uses a Toffolis and the suffix uses c, Lemma 2 yields

    deg(A_i)<=a+1, deg(B_i)<=c+1,
    deg(D_i)<=min(a,c),
    deg(f)<=kappa(P)+max(a,c)+1.                       (5.4)

At a cut balanced by Toffoli count, |a-c|<=1, this gives the universal inequality

    T + 2 kappa(P) >= 2 deg(f)-3.                      (5.5)

This is an exact graded transport/restoration relation for arbitrary reversible oracle circuits. It is not a superpolynomial complexity invariant. For a protected output, D_y=1 and other D_i=0, so kappa=0. For output-active circuits it is not legitimate to assume kappa=0.

## 6. Large decoding grade can be created cheaply

We construct an explicit prefix with n logical inputs, one arbitrary target y, and initially clean temporary registers such that its output-direction components are

    D_0=product_i(1+x_i), D_i=x_i (1<=i<=n),

with all other D components zero. Its exact decoding grade is

    kappa=n-1.                                         (6.1)

Construction. In n clean bits t_i, compute t_i=y x_i using n Toffolis. Compute OR(t_1,...,t_n) into temporary registers, XOR it into y, then uncompute that OR computation. The resulting registers on the specified subspace are

    y'=y product_i(1+x_i), t_i=y x_i,

and all OR temporaries have returned to zero. The prefix uses 3n-2 Toffolis and 7n-5 total gates (n>=1). Its inverse restores every register. Thus it can occur at the midpoint of a restored identity loop.

To prove (6.1), evaluate a unit certificate at x=0. Necessarily lambda_0(0)=1. Since D_0 is the indicator of x=0, lambda_0 D_0=D_0 as a Boolean function. Hence

    sum_(i>=1) lambda_i x_i=1+D_0.

The right side has degree n. If all coefficient degrees were less than n-1, the left side would have degree less than n. This proves kappa>=n-1. The telescoping coefficients lambda_0=1 and lambda_i=product_(j<i)(1+x_j) prove equality.

This example has a linear-cost prefix, not an optimal circuit for a difficult f. It refutes a universal assertion that restoration preserves a constant-coefficient direction decoder. It does not prove that optimal circuits must have large kappa. Indeed Theorem 1 permits protected-output implementations with kappa=0 at a constant-factor length overhead.

The coefficients in this example themselves have linear-size shared product circuits. A high coefficient degree or an exponentially expanded monomial list does not imply a large construction cost.

## 7. What the attempted separation still lacks

We now have a legal normal form, a two-sided restoration bound, an explicit NP-complete endpoint, and a precise term accounting for output-direction decoding in arbitrary circuits.

However deg(f)<=N for every N-bit Boolean function, and kappa<=N by multilinear representation. These degree quantities cannot supply a superpolynomial lower bound. Even the N-input OR function has degree N and a linear-size circuit. Replacing the endpoint by another full-degree function does not fix that ceiling.

The surviving sufficient target is to show that the power-of-two majority-clique family has output-passive length not bounded by any polynomial in N. Such a theorem would automatically apply to unrestricted dirty circuits by Theorem 1. We have established only the stated linear lower bound.

A stronger proof must bound the construction cost of many intermediate compatibility functions while allowing their shared preparation and cleanup. It cannot simply add their degrees or count the monomials in their expanded coefficients. Neither this block nor the preceding checkpoint proves that stronger result.

## 8. Verification and limitations

Run `python checks/run_all.py`. All main verifiers use only Python's standard library and exact Boolean/integer arithmetic. The runner writes hashes, timings, commands, logs, and the executed ranges. Timings are operational metadata, not proof data.

- The predecessor's recorded result was reproduced after changing only its hard-coded output destination. This reproduces its original generalized-control simulation; it does not repair its gate model by itself.
- Corrected compilation tests cover 630 source circuits and all 11,760 input/target cases. Repeated-operand gates are simplified before any standard Toffoli is emitted.
- The monomial oracle construction is checked for k=2..10 on every logical input and both target values.
- A borrowed-bit cubic commutator is checked on all 32 complete input registers.
- Protected normalization is checked for 89 specified circuits on 2,568 scalar cases.
- The transport identities and minimum decoder degree are checked at 989 specified cuts, with all logical inputs. These are not all possible circuits.
- The explicit nonlinear decoder family is checked through n=8; minimum degree is obtained by exact GF(2) linear algebra, independently of its symbolic lower-bound proof.
- Full small graph truth tables are checked on 2 and 4 vertices. The binary-tree fixed-graph mechanism is checked through 64 vertices using explicit clique and coloring witnesses, edge orbits, and 5,334 generator invariance checks. This is NOT an enumeration of all graphs on 64 vertices.
- The padding reduction is checked on all source graphs with 2..5 vertices and all nontrivial thresholds, totaling 4,306 source pairs.

An initial clique-check run exceeded its 45-second resource cap because it attempted unconstrained maximum-clique search even on the largest fixed graphs. That run is inconclusive, not a false theorem or an UNSAT result. It was replaced by exact clique/coloring certificates for those structured graphs, retaining independent maximum-clique enumeration only through 16 vertices. The original timed-out script is retained under historical evidence, not the default runner.

No SAT solver, Lean compiler, fresh-agent reviewer, or independent human verification was used. The claims above are written derivations supported by finite checks, not machine-checked universal theorems.

## 9. External context checked

- Mathias Soeken, *Determining the Multiplicative Complexity of Boolean Functions using SAT*, arXiv:2005.01778, Section III. Supports the standard multiplicative-complexity model and degree-minus-one lower bound.
- Ming Li and Paul Vitanyi, *Reversibility and Adiabatic Computation: Trading Time and Space for Energy*, arXiv:quant-ph/9703022. Context for reversible simulation and the role of resource accounting.
- *Reversible Logic Synthesis with Minimal Usage of Ancilla Bits*, arXiv:1506.03777. Context for distinguishing initialized ancillas from arbitrary borrowed bits.
- Clay Mathematics Institute, *P vs NP*, accessed 2026-09-21. Target context only.

The new derivations are proved in the preceding sections. A bounded source check is not a global novelty audit. Recent unrelated preprints returned during discovery were not used as theorem dependencies.
