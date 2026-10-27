# Parent review: local stratification and primitive scaling

Reviewed the full raw proof in `notes/stratification.md`, not just the finite
output. Primary verdict: **proved as written**. This is a collaborative
review, not independent rediscovery of the entire route.

The exact claim concerns positive pairwise-coprime squarefree coefficients
a,b,c, with nonzero p-adic roots and at most one p-divisible base. It gives
local solutions varying with p, not a rational or integral solution.

| Obligation | Result and decisive reason |
|---|---|
| Odd-prime ramified coefficient criterion | Passed: power-ratio images are squares because pairwise gcd of 6,10,14 is 2; the C-sector sign is negative |
| Odd-prime unramified coefficients | Passed: a zero-base phase handles all but the two sign patterns at p=3 mod4; the universal identity and nonsquare scaling handle those |
| Existence of t and 1-t nonsquares | Passed: character sum gives (p+1)/4, including p=3 |
| Uniform lifting | Passed: at least two roots are units and at most one derivative coefficient 6,10,14 is divisible by any odd prime |
| Nonzero roots in lifted zero-residue phase | Passed: fix that root to p before lifting a different unit variable |
| Dyadic necessity and sufficiency | Passed: even term vanishes mod8; sixth, tenth, fourteenth powers of 2-adic units all have image 1+8Z_2 |
| Squarefree parity coverage | Passed: at most one even coefficient; an even coefficient forces its phase, while all-odd coefficients allow any admissible phase |
| Explicit (3,5,2) and (2,3,11) survivors | Passed at every coefficient prime and at2; other odd primes follow the proved universal criterion |
| Finite congruence CRT corollary | Passed: enlarge modulus by abc, then choose roots successively to avoid the prime factors of preceding roots outside the enlarged modulus |
| Global conclusion | Correctly limited: local solvability and finite congruences do not establish equality over the integers |

The finite residue counts corroborate the theorem and are not its universal
justification. The local survivor examples are a decisive obstruction to
completing Beal from this coefficient projection and arbitrary prime-power
refinement alone.

The separate exact scaling criterion in `primitive_scaling.md` is the
parent's derivation and has received a fresh review from the stratification
agent. Its scope is recognition of one rational parameter. It restates the
global cube/fifth/seventh power conditions without solving them.

Execution note: the initial primitive-scaling runner invocation resolved the
contract relative to the wrong current directory and failed before executing
the experiment. Repeating from the declared project directory completed and
its manifest validated. No failed computation was relabelled as a result.
