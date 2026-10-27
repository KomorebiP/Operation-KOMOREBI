# Independent finite check for the proposed twist at level norm 45

Verdict: **conditional on the actual twist and exact-level comparison**. The
finite norm-four exclusion passes in every parity branch. This check does not
establish those arithmetic hypotheses.

The independent parser reads the retained complete norm-45 search page and the
individual page `2.2.5.1-45.1-a`. It verifies the unique search match, the displayed
weight (2,2), level ideal `[45, 15, -6 w + 3]`, rational coefficient field,
and the exact Hecke trace -3 at the K-prime (2), which has norm four. It also
checks the page hash against the retained lookup receipt. No Hecke value is
inferred from the other level or from numerical PV labels.

Let eta be the proposed quadratic twisting character. Assume it is unramified
at this K-prime and eta(Frob_(2))=-1. The Frobenius value meant here is at the
K-prime of norm four, not a Frobenius value at a rational prime on an unstated
character of Gal(Qbar/Q). The quadratic twist preserves the determinant four
and negates every local eigenvalue.

For odd C, the previously established untwisted full polynomials are
(T^2+T+4)^2 and (T^2+4)^2. The twisted ones are therefore

    (T^2-T+4)^2 and (T^2+4)^2.

The norm-45 form has rank-two polynomial R=T^2+3T+4. Its resultants with the
two required quadratic factors are 64 and 36, both nonzero modulo seven.
The independent script also compares the full squared polynomials directly.
Thus neither odd-C parity can match. Equivalently, the allowed rank-two traces
are one and zero modulo seven, while the actual trace -3 equals four.

For even C, the established untwisted eigenvalues -1,-4 become 1,4. Neither can
be an eigenvalue of the candidate: R(1)=8=1 mod7 and R(4)=32=4 mod7. Alternatively,
determinant four forces a rank-two pair to contain both distinct roots, giving
trace five modulo seven, again unequal to four. Repeated roots have determinants
one or sixteen, which are not four modulo seven.

Consequently, assuming a direct normalized residual comparison of the twisted
rank-two Frey representation to a parallel-weight-two, trivial-nebentypus
newform of this exact norm-45 level, there is no possible parity branch.
Database completeness is an imported primary-source input. This audit makes
no claim that the twist exists with the required Frobenius value, that its
conductor lowers to this level, or that the modular comparison has been proved.
It therefore does not establish an unconditional Diophantine contradiction.

Reproduce with:

    python3 work48/computations/candidate_twisted45_independent.py

The output `work48/verification/candidate_twisted45_independent.json` records
the exact parsed data, source and script/report hashes, all polynomial checks,
run time, and the explicit hypotheses and nonclaims. The implementation uses
only the Python standard library and does not execute downloaded code.
