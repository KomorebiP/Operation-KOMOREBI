# Boundary of a factorial sharpening

The proved translated-flat theorem gives v_2(Delta^k C(n))>=k. Exact computations for the actual N=4 kernels also support the stronger estimate

v_2(Delta^k C_j(n)) >= k+v_2(k!).

For j=0,1 the minimal observed values through order 40 equal k+v_2(k!) exactly. For j=2,3 the observed bounds are stronger. These computations are evidence, not a proof of the stronger all-order statement.

The actual rational kernels satisfy the stronger source condition. For one affine inverse,

Delta^k [1/(A+Bn)] = (-B)^k k! / product_(i=0)^k (A+B(n+i)).

When A is odd and B belongs to 2Z_2, this has valuation at least k+v_2(k!). The exact divided product rule extends this to the actual g_j kernels. Equivalently, the ordinary coefficients of their Newton expansions in 2^k(n)_k are integral.

However, the successful proof of plain flatness CANNOT simply be divided by k!.

Take the actual N=4,j=0 source g(n)=1. Its series F is 1-flat with every positive iterate L_1^k F equal to zero, hence even its divided L_1 iterates are integral. Its reciprocal begins

C(0)=1, C(1)=-1, C(2)=69.

For L_(−1)=(D^4+1)/2,

[L_(−1)^2 H]_0=(C(2)+2C(1)+C(0))/4=17.

Therefore L_(−1)^2 H/2! is not Hurwitz-integral. A divided negative-eigenvalue reciprocal lemma is false even for the first actual kernel. In contrast,

[L_1^2 H]_0=(C(2)-2C(1)+C(0))/4=18

is divisible by 2, exactly as the desired factorial bound predicts.

Thus the stronger theorem would need a genuine cancellation argument when translating back from eigenvalue −1 to eigenvalue +1. The plain translated-flat inverse proof does not supply that argument.

The same issue appears in its multinomial expansion: dividing by k! introduces factors 1/e_i! in the middle-derivative terms. At N=4,k=2 the term from using the D^2⊗D^2 correction twice has coefficient 9/2. Its integrality would require cancellation with other terms; it is not termwise integral.

A generic dyadic N=1 factorial reciprocal theorem is false: g(n)=1 has C(n)=(-1)^n and Delta^k C(n)=(-2)^k(-1)^n, of valuation exactly k. Any valid factorial sharpening must use N>=2 or stronger prescribed-kernel structure.

No factorial-strength all-order theorem is asserted by this note. The all-row k-flat theorem and the separately proved exact first-difference/minimal-period laws remain valid.

## Later proved development: actual j=2

The limitation of the naive divided-negative-eigenvalue inverse lemma remains valid. A separate exact proof now establishes the factorial bound for the actual j=2 lane, using its two Bernoulli-umbra factorization and an explicit integral divided-power algebra. See `factorial_j2/FACTORIAL_J2_PROOF.md`.

That proof gives, uniformly in the row, the mixed-step estimate

v_2(Delta_(H_1)...Delta_(H_k) C_2(n))
 >= k+v_2(k!)+sum_i v_2(H_i)

for positive steps. It also proves ordinary analytic interpolation on |x|_2<2. The remaining factorial candidates in this note concern the other lanes and/or a generic dyadic reciprocal theorem; this appendix resolves j=2 without asserting that generic theorem.
