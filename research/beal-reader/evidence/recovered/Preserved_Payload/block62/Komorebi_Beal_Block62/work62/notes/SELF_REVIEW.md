# Adversarial self-review

This is review by the same assistant, not an independent mathematical reviewer.

1. The exact determinant expansion is recomputed before reduction. Alpha=b and
   beta=c/chi agree with the inherited cocycles; chi(F)=1 is used only at Q=1
   mod7. The det3 control shows why that condition cannot be suppressed.
2. All product tests are at places unramified in beta under the explicitly
   specified complete conductor. In the added ramified43 branch no unramified
   Frobenius test at43 is applied. Natural inertia is known to vanish at good
   places and the inherited variable bad places.
3. At29 and491, good reduction is allowed. Exact toric trace is used only on
   the bad alternative. The only initial full-zero row is71, genuinely forced
   bad at depth one and with nonseventh phi. Thus no n>=2 assumption is recycled.
4. The beta twist is chi^-1. Cyclotomic prime permutation gives weights b, and
   the principal-idele sign is retained. The same primitive root selects the
   Kummer logarithm at the test prime. A global sign change can be absorbed in
   beta's unrestricted global scaling, but independent local changes cannot.
5. Inert43 uses squared Frobenius for the curve and a factor2 for beta. The
   natural Kummer symbols are already in F43^2. The independent implementation
   rederives, rather than omits, both factors.
6. Base-field sqrt5 and coefficient-field w are separate. The coefficient
   conjugates are allowed independently at test places, which overapproximates
   actual realizations. The exclusion therefore does not require a missing
   semilinear lattice map or identification of those two radicals.
7. Each good parameter pair is tested for seventh-power equation admissibility.
   Curve-orbit equivalence alone does not preserve that condition. The second
   implementation uses another orbit construction and checks every pair's gcd.
8. Rational quartic data are converted to rank-two trace corrections using both
   trace and norm in the independent program. It does not infer a rank-two
   scalar lift merely from a repeated quartic congruence.
9. All48 possible nonzero natural ratios are considered; the reduction to r1/r6
   is a consequence of the stipulated support and71 row. The seven added-prime
   supports use three other forced ratios and include every subset. No universal
   coefficient descent or universal support-size bound is claimed.
10. The nine and one intermediate survivors, and the surviving local Frey
    families, are mandatory controls. The final empty set applies to complete
    beta conductors in Splus, not to C whose high set alone is in U.
11. The extension of the old n2 argument to n>=2 requires FULL eta_n=1. It is
    not valid merely from the weaker half-precision theorem. Each reused local,
    descent and natural-ratio hypothesis is stated in the consequence proof.
12. For the E(C) consequence, a nontrivial highest eta layer has h>=2 and passes
    the phi period condition, so the three h1 additions cannot support it.
    Block58 then forces eta=1 if complete E(C) lies in V. In the unrestricted
    case an outside-V eligible divisor need not be beta-supporting or2549.
13. Exact arithmetic agreement is not an independent proof of the upstream
    analytical periods, actual natural Kummer identification, or class-group
    and inertia-localization inputs. These remain hash-pinned conditional leaves.
    No Lean compilation or independent mathematical acceptance occurred.
