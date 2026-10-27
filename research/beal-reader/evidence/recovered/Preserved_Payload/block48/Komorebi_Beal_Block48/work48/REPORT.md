# Komorebi Beal research — Block 48

Beal's conjecture is not proved. The full primitive equation
\(A^3+B^5=C^7\) also remains unresolved in this work. This continuation
does establish a stronger irreducibility result, eliminates thirteen of
fourteen forms at one complete Hilbert modular level, and obtains a new
necessary divisibility condition on actual solutions.

All statements below concern positive, pairwise-coprime integers
\(A,B,C\) satisfying \(A^3+B^5=C^7\). The auxiliary abelian surface is
the Jacobian of

\[
 y^2+(x^3+B)y=2Bx^3+3Ax+B^2,
 \qquad K=\mathbf Q(\sqrt5).
\]

These are written arithmetic arguments with checked external inputs and
separate internal reviews. Only the explicitly identified finite algebra
is Lean-certified. No publication, global novelty, or complete formal
verification is claimed.

## What changed

| Result | Exact scope |
|---|---|
| Stronger irreducibility | The residual rank-two RM representation at seven is absolutely irreducible whenever \(3990\nmid C\). |
| Modular attachment | Absolute irreducibility supplies a parallel-weight-two, trivial-character Hilbert newform of level \((3)^i(\sqrt5)^j\), with \(i,j\in\{2,3\}\), retaining the original local types. |
| Complete smallest-level elimination | At ideal level \((45)=(3)^2(\sqrt5)^2\), of norm 2025, only `2.2.5.1-2025.1-l` can match. It requires \(A,C\) odd, \(418\mid B\), and \((A,C)\equiv(5,9)\) or \((6,2)\pmod{11}\). |
| Restriction on actual solutions | \(15\mid C\Longrightarrow3990\mid C\). In particular, the branch \(15\mid C\), \(3990\nmid C\) is excluded. |

The first result concerns a representation, so it does **not** exclude
solutions whenever \(3990\nmid C\). The last result is a Diophantine
consequence and has the stated narrower hypothesis.

Combining the proofs gives a sharper description for any hypothetical
primitive solution: residual reducibility is equivalent to \(15\mid C\),
and hence to \(3990\mid C\). This does not establish that such a solution
exists. It identifies the branch where this representation is forced to
be reducible.

## The new local argument

The complete ray-character calculation leaves two quadratic characters.
An exact Frobenius test at eleven excludes one; nineteen forces
\(19\mid C\) under reducibility. The surviving character is the one of
\(\mathbf Q(\zeta_{15})^+/K\). The Weil pairing then determines the
entire four-dimensional residual semisimplification.

At three and five, suppose the corresponding prime does not divide
\(C\). The Jacobian has potentially good reduction. Its finite
seven-adic inertia image has order prime to seven: a nontrivial element
of order seven would require a degree-six cyclotomic factor in a
degree-four characteristic polynomial. The residual character identity
therefore forces actual scalar quadratic inertia.

Twisting by that quadratic character gives good reduction and makes the
two-torsion unramified. Twisting leaves the two-torsion unchanged. The
faithful action of the six Weierstrass points on genus-two two-torsion
then forces every root of

\[
F(X)=X^6+10BX^3+12AX+5B^2
\]

to be unramified. Their collisions in the residue field contradict
\(\operatorname{disc}(F)=2^{12}3^65^5C^{14}\):

| Place, assuming it does not divide \(C\) | Actual discriminant valuation | Required by unramified roots |
|---|---:|---:|
| Three, with \(v(3)=1\) | 6 | at least 12, or 30 |
| Five, with \(v(\sqrt5)=1\) | 10 | at least 20, or 30 |

Thus reducibility forces \(15\mid C\). Combining this with the earlier
two/seven result and the new nineteen test gives \(3990\mid C\).
The subtle potential-good-reduction case at three was checked in two
ways: Liu's invariant criterion and an independent calculation of two
clusters of three roots. The proofs are in
`notes/reducibility_local_inertia.md` and its independent audit.

## Actual modular forms, with one embedding retained

All fourteen canonical LMFDB forms at norm 2025 were retrieved. The
calculation uses exact Hecke values and the complete list, without a
guessed correspondence to historical numerical indices or reliance on
positive CM flags.

At the prime of norm four, only a/f/h/l survive when \(C\) is odd; only
n survives when \(C\) is even. Further comparisons exclude a at nineteen,
f at twenty-nine, and h at eleven. For n, the two primes above eleven
give incompatible full polynomials at **every fixed coefficient prime
above seven**. Switching the coefficient embedding between those tests
would conceal this obstruction. The sole remaining form is l, with the
restrictions in the table above.

There is a further consequence when \(15\mid C\). Both retained local
types are ramified quadratic special types. Twisting the attached form
by the surviving real quadratic character lowers its exact level to
\((3)(\sqrt5)\), of norm 45. The complete space has one form, whose
trace at norm four is \(-3\). The twisted Jacobian permits only traces
\(0,1,5\) modulo seven; \(-3\equiv4\) matches none. Hence this branch
cannot be irreducible. The already established irreducibility result
then gives \(15\mid C\Rightarrow3990\mid C\).

See `notes/modular_candidates.md`, `notes/candidate_independent_audit.md`,
and `notes/solution_divisibility_corollary.md`. Source-data completeness
and exact eigenvalues are imported from the
[LMFDB Hilbert modular forms database](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/Completeness);
the spaces were not recomputed in Magma.

## Verification and failed routes

- Independent point counting covered all 110, 342, and 812 smooth
  coefficient pairs at eleven, nineteen, and twenty-nine. The global
  character calculation also has a bounded fourteen-prime run.
- Eight public Lean theorems check the actual characteristic-seven
  polynomial obstructions and the finite filtration-dimension equation.
  Their axiom audits pass. They do not formalize modularity or the local
  geometry.
- The seven-specific modular attachment hypotheses were checked in the
  primary dependency chain, including cyclotomic restriction,
  finite-flatness, crystalline weights, and the dyadic prime. This closes
  the previously open attachment input, conditional on irreducibility.
- The bad-seven Frobenius route fails for a mathematical reason: its
  value is \(-1\), exactly the value demanded globally. The explicit
  finite-flat model is useful, but supplies no contradiction.
- The surviving real character is the actual graph character of the
  \(C=0\) degeneration at every auxiliary prime. Any finite sieve using
  only those torus characters retains a compatible local branch.
- The previous coefficient-only local saturation and failed direct
  transfer of the raw hypergeometric period remain in force. More
  polyphase subdivision alone does not supply the missing global input.

## What still blocks a complete proof

1. Exclusion of the necessarily reducible branch \(3990\mid C\).
   An independent irreducibility argument there would yield a
   contradiction; another Frey construction may be needed.
2. Elimination of the last norm-2025 form l, and complete correlated
   elimination at the other three possible levels, of norms 10125,
   18225, and 91125.
3. The other exponent signatures needed for the full Beal conjecture.

Exact higher-level eigenvalue exports remain unavailable in this
environment. An exporter is retained as **unexecuted** code. No remote
computation is represented as running or completed. The next executable
targets and the changes needed to reopen failed routes are recorded in
`CONTINUE_HERE.md`.

The base checkpoint is the unchanged Block-47 archive, SHA-256
`6ff3719bb869cd262b42acd25ed4e768da23c4d6fda815440dc3b08135483466`.
This package preserves that ancestry, current proofs, reviews, exact
computations, source records, and replay instructions.
