KOMOREBI: EXACT EULER / SIGNAL BRIDGE

This is a bounded, reproducible demonstration of a shared operator law.
It does not claim that the underlying FIR identities are new.

Let S a(n) = a(n+1), Delta = S-I, and R_(M,s) a(q)=a(Mq+s).
Then

  Delta_q^k R_(M,s) = R_(M,s) (S^M-I)^k.

Proof: advancing one position in the sampled lane advances M positions in
the original sequence. Thus S_q R_(M,s)=R_(M,s) S^M; subtract the identity
and take powers. This is an exact multirate filter identity.

If c_r=Delta^r a(0), then the lane coefficients are

  d_(s,k) = sum_r [t^r](1+t)^s ((1+t)^M-1)^k c_r.

Proof: evaluate S^s(S^M-I)^k a at index zero, and substitute S=I+Delta.
For M>=1 and s>=0 the sum is finite, supported on k<=r<=Mk+s.
This identity is valid for arbitrary integer sequences without an
analytic interpolation assumption.

The same filter has frequency response H_(M,k)(omega)=(exp(i M omega)-1)^k.
For k>=1 its comb zeros lie at omega=2 pi j/M. This follows by applying
the operator to exp(i omega n). The growing Euler sequence itself has
no ordinary convergent DTFT; the frequency response belongs to the filter.
The causal form (I-S^(-M))^k differs by a shift and has the same gain.

SIGNED EULER CONTROL

Use cosh(t)*sech(t)=1 and a(n)=E_(2n). The initial values are
1,-1,5,-61,1385. Initial difference coordinates are 1,-2,8,-80,1664.

M=2: S^2-I=2 Delta+Delta^2, giving d_1=2(-2)+8=4.
The next coefficient is d_2=4(8)+4(-80)+1664=1376.
M=4: S^4-I=4 Delta+6 Delta^2+4 Delta^3+Delta^4.
Its first output is -8+48-320+1664=1384=8*173.
Successive even refinements give 2 d_1+d_2=1384, agreeing exactly.

SIGNAL / ARITHMETIC INTERPRETATIONS

The signal reading evaluates the shift polynomial on the unit circle.
The arithmetic reading expands that same polynomial in Delta and measures
the exact valuations of its integer outputs. A frequency notch and p-adic
divisibility are distinct properties connected through this common operator.

For prime p the residual is explicit:

  S^p-I = Delta^p + p B_p(Delta),
  B_p(t) = sum_(j=1)^(p-1) (binom(p,j)/p) t^j in Z[t].

Modulo p the correction disappears. At higher precision it must be kept.
For p=2, B_2(Delta)=Delta. Thus the residual 2 c_1=-4 cancels part
of c_2=8 to give the output 4. Discarding the residual would give 8.
This is a precise place to retain a residual packet in the calculus.

The general identities are proved algebraically above. The supplied exact
computation checks independent implementations in declared finite ranges.
Whole-branch congruences need bounds on all remaining coefficients.

REPRODUCTION

Run python verify_bridge.py in this folder. Python 3, NumPy and Matplotlib
are required. Inspect exact_results.json and computation_manifest.json.
The source hash is recorded in SOURCE_SHA256.txt.

PROJECT SOURCE

The Euler example extends the finite computations in
Euler_Deep_Polyphase_Refinement_Example.pdf, especially its first and second
refinements and exact kernel-composition law. This demonstration supplies
the explicit FIR interpretation and prime-residual identity.
