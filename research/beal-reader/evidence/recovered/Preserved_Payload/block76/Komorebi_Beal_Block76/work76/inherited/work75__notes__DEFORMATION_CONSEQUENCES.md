# B75.4. Consequences for the same higher deformation and mixed traces

## Exact higher diagonal comparison

In any natural endpoint frame the integral intertwiner C is upper triangular
modulo7^n. So is rho. Diagonal entries of a conjugated upper triangular matrix are
unchanged. The actual diagonal characters therefore satisfy

    a_n(j g j^-1)=sigma(a_n(g)),
    d_n(j g j^-1)=sigma(d_n(g)),
    eta_n(j g j^-1)=sigma(eta_n(g)).                      (6)

This is exact at the entire available diagonal precision, not only a residual
statement about beta. It does not say eta_n=1. The exact rank-two trace satisfies
T(j g j^-1)=sigma(T(g)) at ALL precisions and for every word g.

## A single semilinear frame for the adjoint problem

Use the normalized j and global frame of NORMAL_FORM.md. A triangular auxiliary
Kummer lift rho0 modulo49 can be chosen with the same residual representative and
strict j/sigma covariance. To see this without assuming a lift of the actual line,
choose coefficient lifts u in wZ7, r in Z7 and last coefficient1. The corresponding
unit Kummer class is fixed by the combined operation b(g)|->sigma(b(jgj^-1)).
The chosen j^2 kills its local Kummer roots, so b(j^2)=0; the combined operation is
an involution on this cocycle. Average a representative with its transform using
1/2. After first matching the actual residual splitting, the average preserves
that residual representative. It gives the claimed AUXILIARY rho0.

Now retain the actual nontriangular expression

    rho=(I+7X)rho0,     X=[[p,q],[beta,-p]].

The exact integral covariance forces the additional simultaneous equations

    X(j g j^-1)=sigma(X(g)),
    p(j g j^-1)=sigma(p(g)),  q(j g j^-1)=sigma(q(g)).      (7)

The original coupled cocycle equations remain. They are NOT replaced by freely
chosen Kummer characters, and the lower-left7 beta term remains present.
Equation(7) supplies a common integral symmetry for a future global p,q solver.
Neither that solver nor a compatible complete Galois presentation is provided.

## Why the mixed trace is still unevaluated

For a uniformizer probe tau in the normalized local Kummer tower, conjugation by
j preserves its valuation-dual action. Both rho(tau) and rho(j tau j^-1) are thus
the same modulo the requested precision: units are killed and[7] is fixed. Hence

    Delta(tau,j g j^-1)=sigma(Delta(tau,g)).               (8)

The existing value nu7 is rational modulo7, and j beta=sigma beta, so Block74's
formula already satisfies(8). It does not acquire a numerical value from the
new symmetry alone. The missing labelled trace is still a trace of ONE actual
unknown global deformation, not a conjugacy label assignable to unrelated primes.

This closes the previously missing existence of a global INTEGRAL semilinear
endpoint comparison under G1-G4. It does NOT close global realization or compute
C, the frame, p,q, or any of the eight candidates' mixed traces.
