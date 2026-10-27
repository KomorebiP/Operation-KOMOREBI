# Route C: exact nonescape families

Base checkpoint: `ABC_Square_Kernel_Reverse_Realization_2026-10-25.zip`, SHA-256 `f9e5f22f454acf335f7267e6b69d0ee7c06394bf8744c3c3652fb9dec8ac9b59`.

Target contract remains primitive positive integer triples a+b=c and the assertion that, for every epsilon>0, there is C_epsilon with c<=C_epsilon rad(abc)^(1+epsilon). These results do not establish that target or contradict it.

## 1. Fixed Q, fixed radical, unbounded height

For every integer k>=0 put

    Q=243, m=10, u_k=5^(3+486k), c_k=10u_k^2,
    h_k=(c_k-1)/243.

Since 5^486=1 modulo 729 and 10*5^6-1=243*643, c_k=1 modulo 243 and h_k=643=1 modulo 3. Thus h_k is a positive integer coprime to Q. Also u_k=125 modulo 243, so t_k=(u_k-125)/243 is a nonnegative integer and

    h_k=2430t_k^2+2500t_k+643.

The output radical is rad(c_k)=rad(mu_k)=10 for every k, while h_k tends to infinity. The output squarefree kernel is exactly m=10>1. Moreover

    rad(h_k Q c_k)=30 rad(h_k)<=30h_k<243h_k+1=c_k.

Consequently these are infinitely many ordinary abc hits, although h_k is neither asserted prime nor asserted squarefree. This disproves any unconditional radical-escape lemma based only on the congruence mu^2=1 modulo Q, its irreducible quadratic progression, and multiplier coprimality. The prime or squarefree multiplier condition is additional information that such a lemma would have to use.

The family is not a counterexample to abc. An ordinary hit has quality>1, whereas abc permits infinitely many ordinary hits and constrains fixed excesses above 1.

## 2. Prime multipliers with varying Q and irreducible output kernel

Fix any prime p>=5. Let B=p+1 and choose any prime divisor q of B^2+B+1. Then q is odd, and q!=p because B^2+B+1=3 modulo p. For integers t>=0 set

    n_t=3q^t, c_t=B^n_t, Q_t=(c_t-1)/p.

First, Q_t is an integer because B=1 modulo p. The binomial expansion of (1+p)^n_t shows v_p(c_t-1)=1, since p does not divide n_t. Therefore gcd(p,Q_t)=1.

Second, q divides B^3-1. For odd q and x=1 modulo q, a binomial expansion shows

    v_q(x^q-1)=v_q(x-1)+1.

Indeed, if v_q(x-1)=s>=1, the first binomial term q(x-1) has valuation s+1, and every other term has valuation at least s+2. Iterating gives

    v_q(Q_t)=v_q(B^3-1)+t>=t+1,
    U(Q_t)=Q_t/rad(Q_t)>=q^t.

For every t with q^t>=rad(B), we therefore have rad(c_t)=rad(B)<=U(Q_t). The exact radical-ceiling criterion proves

    c_t>rad(p Q_t c_t).

This gives infinitely many Q_t for each fixed prime multiplier p>=5. Since n_t is odd, the squarefree kernel of c_t equals the squarefree kernel m of B. It satisfies m>1: otherwise B=s^2 and p=s^2-1=(s-1)(s+1), forcing p=3. Hence this family occurs in the irreducible quadratic branch, rather than the perfect-square branch.

This disproves a blanket exclusion of ordinary hits at all sufficiently large prime multipliers when Q is unrestricted. It does not refute the restricted growing-Q exceptional-set estimates, and does not establish violations of abc with a fixed positive epsilon. The certified gain c_t/rad(pQ_tc_t)>q^t/rad(B) is insufficient to decide fixed-excess quality, since log(c_t)=3q^t log(B).

## 3. Audit of the inherited checkpoint

The exact hit criterion, quadratic root-coset count, squarefree-kernel counting inequality, dyadic quality restriction, discriminant 4m, prime perfect-square cutoff, and fixed-offset normalization were reconstructed from the displayed hypotheses. No mathematical error was found in those elementary arguments.

One reporting limitation in the inherited verifier is that `checked_cases.prime_multiplier_instances` sums the upper bounds H, rather than counting the primes actually iterated. The quality and offset fields do the same. These values are search interval extents, not counts of prime-multiplier instances. This does not affect the mathematical inequalities. No inherited files were changed.

## 4. Finite checks, limitations, and continuation

`verify.py` uses only exact integer arithmetic and Python's standard library. The new proofs do not depend on the finite checks. `results.json` records exact parameters, code/input hashes, elapsed time, and interpreter version. The generated large Q values are not fully factored: the finite assertion checks the proved prime-power divisor lower bound on U(Q), which is enough for the sufficient ordinary-hit inequality. Radical formulas for outputs follow from their explicit powers of the factored small B.

A preliminary optional attempt to import SymPy failed because that module is absent. The delivered verifier has no SymPy dependency.

The next unresolved implication is a fixed-positive-epsilon height estimate on the simultaneous exponent realizations, rather than ordinary-hit exclusion or uniform radical escape. The fixed-Q nonescape family leaves open what multiplier primality or squarefreeness can force. The varying-Q family leaves open radical lower bounds for Q_t, which is precisely the missing arithmetic input for controlling its actual quality. These routes remain open under those narrowed questions.
