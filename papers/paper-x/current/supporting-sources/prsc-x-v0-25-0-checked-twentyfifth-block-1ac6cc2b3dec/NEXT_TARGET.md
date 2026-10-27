# Next target after Block 25

The remaining obstruction in Claim 9.1 is now arithmetic prime coverage for general finite Galois quotients. The representation-theoretic transfer and finite separator are available once that input is proved. A finite supplied trace table, ordinary density before finite deletion, or a theorem about one fixed prime does not supply it.

The direct full target is precise: for a finite Galois extension cut out by an open normal subgroup, a chosen conjugacy class and a finite forbidden set of places, produce an unramified place outside that set with the prescribed arithmetic Frobenius class. Attach the chosen Frobenius action to the actual prime ideal and residue field, then prove compatibility under restriction between finite extensions. This is the formal arithmetic coverage obligation; no checked general proof was found in the bounded project/Mathlib/Komorebi inventory. We do not expect a generic finite-group argument to replace it.

A smaller next block has concrete inputs: transfer the new result to representations of the actual absolute Galois group of $\mathbb Q$ that factor through one supplied finite cyclotomic extension $L/\mathbb Q$.

1. Fix an embedding of $L$ into an algebraic closure and use the actual restriction map to $\operatorname{Gal}(L/\mathbb Q)$.
2. Prove that pullback along the surjective restriction map preserves and reflects the required representation equivalences and irreducibility.
3. Connect the sampled prime ideals to the relevant decomposition and inertia actions. Prove that the pulled-back representations are unramified there and that their Frobenius traces equal the already proved cyclotomic values.
4. Apply `finite_prime_system_separator_avoiding`, retaining the common field embeddings and each coefficient prime's good-place condition.

Success would give an actual absolute-Galois application with a supplied common cyclotomic factorization. That factorization would remain an explicit restriction; the result would not cover arbitrary compatible systems or finish full Claim 9.1.

An alternative route to broader coverage would require a checked prime-existence theorem for a larger structured class of finite extensions. Before implementing it, identify the exact theorem and arithmetic attachment available in primary sources. The current inventory does not establish such a theorem outside the cyclotomic case.

Claims 9.2 and 11.1 still need the actual local attachment and recovery work described in `FIVE_PARTIALS_STATUS.md`. Additional separator wrappers alone will not resolve those obligations.
