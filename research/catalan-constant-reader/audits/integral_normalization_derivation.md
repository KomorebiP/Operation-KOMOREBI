# Corrected integral normalization: all indices

This is an explicit derivation of the factor 1/8 for the historical recurrence normalization. It identifies the source typo without using irrationality or independence of 1 and G.

Let J_n denote the double integral in LC03. Put

\[
H_n={}_3F_2\!\left(\begin{matrix}n+1,n+\tfrac12,n+1\\2n+\tfrac32,2n+\tfrac32\end{matrix};1\right),
\qquad
C_n=\frac{\Gamma(n+1)^2\Gamma(n+\tfrac12)^2}{\Gamma(2n+\tfrac32)^2}.
\]

For n≥0, expanding (1−xy)^(−n−1) into its nonnegative binomial series and using Tonelli gives

\[
J_n=C_nH_n.
\]

The resulting two beta integrals are B(n+1/2+k,n+1) and B(n+1+k,n+1/2). Their Pochhammer factors produce precisely the numerator and denominator parameters of H_n. The series converges, since the sum of lower parameters minus the sum of upper parameters is n+1/2>0.

Let F_n be Zudilin's hypergeometric series in equation (8) of the published paper. Its displayed prefactor is

\[
(-1)^n n!\,
\frac{\Gamma(3n+2)\Gamma(n+\tfrac12)^3\Gamma(n+1)}{
\Gamma(2n+\tfrac32)^3\Gamma(2n+1)}
\]

times the indicated well poised 6F5 at −1. The Whipple transformation displayed in §3 of that same source, with a=3n+1, b=c=d=n+1/2, e=n+1, states

\[
H_n=
\frac{\Gamma(3n+2)\Gamma(n+\tfrac12)}{
\Gamma(2n+\tfrac32)\Gamma(2n+1)}
{}_6F_5(\text{the displayed parameters};-1).
\]

Its hypothesis Re(1+a−d−e)>0 becomes n+1/2>0 and holds for every n≥0. Substitution and cancellation give F_n=(−1)^nC_nH_n=(−1)^nJ_n. No factor 2 remains.

Zudilin's Lemmas 4–5 and the initial partial fraction coefficients, pages 7–8, give F_n=8(u_nG−v_n) in the historical recurrence normalization. Thus

\[
u_nG-v_n=\frac{(-1)^n}{8}J_n
\]

for every n≥0. The published final display of §3 and Theorem 3 use factors 2 and 1/4 respectively; these are inconsistent with the gamma prefactors and initial condition. The exact derivation above supplies the corrected factor. Its external dependencies are the displayed Whipple transform and the coefficient identification of the recurrence, both explicitly sourced to the authenticated paper. The beta integral computation and gamma cancellation are written project arguments. The n=0 evaluation J₀=8G independently checks the result.
