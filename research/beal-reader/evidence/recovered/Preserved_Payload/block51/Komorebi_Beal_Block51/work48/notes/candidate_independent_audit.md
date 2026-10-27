# Independent audit of all fourteen norm-2025 candidates

Verdict: **conditional on the stated direct modular comparison**. The local
candidate exclusions and residue restrictions are valid. This audit was performed
by the separate `candidate_audit` agent, which was given the proposed conclusion;
its point counts were independently implemented. The eleven counts were then
checked against the retained Block47 certificate; the nineteen and twenty-nine
counts were independently enumerated over all smooth pairs. It is not a blind
review or a formalization.

## Claim and hypotheses

Let A,B,C be a primitive solution to A^3+B^5=C^7, and let J be the Jacobian of

    Z^2 = X^6 + 10 B X^3 + 12 A X + 5 B^2.

Assume its rank-two residual representation is directly congruent modulo seven,
with the same normalization, to the weight-two, trivial-nebentypus representation
of a parallel-weight-two, trivial-nebentypus newform of level (45) over
K=Q(sqrt5), among the complete fourteen canonical LMFDB orbits
`2.2.5.1-2025.1-a` through `2.2.5.1-2025.1-n`.
Assume the previously stated compatibility of restriction of scalars with J[7],
and the standard multiplicative-prime comparison at eleven, nineteen, and
twenty-nine. For the norm-four sieve assume the previously established good
Frobenius polynomials when C is odd and toric Frobenius eigenvalues when C is
even. Database completeness and the displayed exact Hecke data are imported
primary inputs, not recomputed Hilbert modular form data.

Under these hypotheses, only the orbit l can match. It requires C odd and A odd,
and forces 11|B and A congruent to either 5 or 6 modulo eleven. Combining with
the separately established l-specific trace-zero test at nineteen gives 418|B.
This is a statement about level (45), not the other three possible levels.

## Complete norm-four sieve

The script independently parses all fourteen retained individual pages, checks
their labels, weight and level, and checks the complete search page's fourteen
labels. The respective norm-four traces, in order a through n, are

    0, 3, 4, -4, 1, 0, -2, 0, 3, -2, -3, 0, -2, 2.

For odd C the two parity cases require trace -1 or 0 modulo seven, by the
established full Frobenius polynomials. Only a,f,h,l remain, all requiring
A odd and B even. For even C the established full Frobenius eigenvalues at
norm four are -1 and -4. A rank-two representation of determinant four modulo
seven must have one of each: two copies of -1 or -4 would instead have
determinant one or two. Its trace is therefore -5=2 modulo seven, leaving only n.
These are necessary-condition filters; this script does not reprove the
two-adic geometric inputs.

## Why the four-dimensional comparison at eleven is necessary

Both coefficient polynomials have discriminant five, so seven is inert in their
coefficient fields. The residue field is F49. For a rank-two characteristic
polynomial P over F49, its underlying F7-linear characteristic polynomial is
P times its coefficient Frobenius conjugate. Thus any congruence of the rank-two
representations forces equality of these full polynomials, independently of the
choice of either F49 embedding. Lattice semisimplification compatibility identifies
the Frey side with J[7], as established in Block46's written proof.

Eleven splits in the base field K=Q(sqrt5). Since J is defined over Q, its full
polynomial computed over F11 is the full polynomial at either K-prime above
eleven. This does not identify the two rank-two traces separately; their norm is
all that is required for this necessary-condition test.

For h the two displayed traces are e and -e-9 with e^2+9e+19=0. For l they are e
and -e+9 with e^2-9e+19=0. Taking the norm of T^2-eT+11 gives respectively

    h: T^4 + 9 T^3 + 41 T^2 + 99 T + 121,
    l: T^4 - 9 T^3 + 41 T^2 - 99 T + 121.

## Independent finite check for h and l at eleven

The independent script uses Python integer arithmetic and constructs
F121=F11[u]/(u^2-2). It verifies that two is nonsquare in F11, and counts affine
points using quadratic characters, adding the two rational points at infinity.
It enumerates all 110 pairs with A^3+B^5 nonzero in F11. For each, the counts
N1 and N2 give s1=12-N1 and s2=(s1^2-122+N2)/2, hence

    T^4 - s1 T^3 + s2 T^2 - 11 s1 T + 121.

All 110 independently computed pairs, counts, and polynomials agree with the
Block47 certificate. Comparison modulo seven gives no match for h and precisely
(A,B)=(5,0),(6,0) for l. The complete recomputed table is retained in the JSON.
The five-term polynomial lists in that file are in ascending coefficient order.

If 11 divides C, the standard multiplicative-prime comparison requires modular
trace +12 or -12 modulo seven. Substitution into each coefficient polynomial
gives the nonzero residues five and six, in the respective orders. Equivalently,
both coefficient polynomials are irreducible modulo seven, with nonsquare
discriminant five, so neither trace lies in F7. Thus the bad-reduction branch
cannot match either form.

Combining l's restriction with the separately established two-adic and nineteen
restrictions yields C odd, A odd, and 418|B. This final combination relies on the
previous even-C exclusion and l-specific nineteen comparison; those geometric
inputs were not recomputed by this script. These divisibility conditions are not a
contradiction or a Diophantine nonexistence proof.

## Independent full enumerations for a and f

Candidate a has rational trace -5 at both K-primes above nineteen. Its required
full polynomial is

    (T^2 + 5 T + 19)^2 = T^4 + 10 T^3 + 63 T^2 + 190 T + 361.

The independent script enumerates all 342 pairs (A,B) in F19^2 with
A^3+B^5 nonzero, and computes their point counts over F19 and F361 using
F361=F19[u]/(u^2-2). None has this full polynomial modulo seven.
If nineteen divides C, the necessary modular trace is +/-20; neither equals
-5 modulo seven. Therefore a cannot match, for either parity of C.

Candidate f has rational trace 10 at both K-primes above twenty-nine. Its
required full polynomial is

    (T^2 - 10 T + 29)^2 = T^4 - 20 T^3 + 158 T^2 - 580 T + 841.

The script enumerates all 812 pairs (A,B) in F29^2 with A^3+B^5 nonzero and counts
points over F29 and F841 using F841=F29[u]/(u^2-2). Again there are no matches
modulo seven. The bad-reduction trace +/-30 is also unequal to 10 modulo seven.
Thus f cannot match, for either parity of C.

Both enumerations use all smooth pairs, without a weighted-orbit reduction.
The complete counts and polynomials, together with the imported exact traces,
are retained in the JSON. Primes nineteen and twenty-nine split in K, so the
rational Jacobian's point-count polynomials are the full polynomials at the
K-primes being compared.

## Fixed coefficient prime obstruction for n

The coefficient field of n is Q(e), e^2=18. Its two primes above seven give
e=2 or e=5=-2 modulo seven. The displayed traces at the two K-primes above
eleven are -e and e. A residual congruence uses one fixed coefficient prime
and embedding at both base primes.

At that fixed choice these traces lie in F7. Extending the rank-two modular
representation to F49 and then restricting scalars to F7 therefore gives

    (T^2 + e T + 11)^2 and (T^2 - e T + 11)^2.

Their cubic coefficients are respectively 2e and -2e, which differ modulo
seven for both allowed nonzero values of e. The script checks both full
polynomials for both choices.

On the Frey side J is defined over Q. Choose Frobenius lifts at the two split
primes above eleven that are conjugate in Gal(Qbar/Q). Their full characteristic
polynomials on J[7] are equal by conjugacy. The modular candidate is unramified
at eleven, so its polynomial does not depend on the choice of these lifts.
The assumed representation comparison and lattice semisimplification
compatibility therefore force equality of the two displayed squares, a
contradiction. This proof does not assume good reduction of J at eleven and
applies to either parity of C. It preserves the fixed coefficient prime rather
than swapping it between the two base primes.

Together with the norm-four sieve and the h exclusion, these arguments leave
only l among the entire fourteen-orbit level-(45) list.

## Scope and provenance

Run from the project directory:

    python3 work48/computations/candidate_independent_q11.py

The result is `work48/verification/candidate_independent_q11.json`. It records
the script and this report's SHA256 hashes, hashes of all fourteen retained
LMFDB pages, the complete search page, the prior certificate and the two-adic
proof inputs, the exact command, run time, every recomputed point count,
parsed traces and coefficient polynomials, and explicit proof boundaries.
The retained source pages are read directly; no downloaded code is executed.
No implementation from the preceding scripts is imported.

Primary inputs are the retained individual LMFDB pages, the complete search
page, the Block47 point-count certificate, and the preceding two-adic proof
inputs. Eigenvalues are accepted as imported exact data; there is no new
computation of a Hilbert modular form space. No numerical PV-to-LMFDB index
identification, elimination at other levels, or Diophantine nonexistence theorem
is asserted. The only claim of exhaustive coverage concerns the fourteen-orbit
level-(45) list and the explicitly enumerated finite residue domains.

LMFDB's reliability page distinguishes rigorous eigenform data and certified
CM=no from a CM=yes flag, which is evidence rather than a certified conclusion:
<https://www.lmfdb.org/ModularForm/GL2/TotallyReal/Reliability>. This candidate
argument uses the actual eigenvalues and does not require CM classification.
