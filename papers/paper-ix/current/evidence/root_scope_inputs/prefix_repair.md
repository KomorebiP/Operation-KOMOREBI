# Finite prefix repair and the scope of the correction-height obstruction

This short continuation tests whether the preceding packet1 height cost is
an obstruction to every finite actual model. It is not. The construction
below removes that cost at each fixed prefix packet while preserving the
certified error. It supplies no bound on the final stationary discriminant.

Fix the admitted ordinary r and an m with h_m=8m-4s_2(m). In the reviewed
finite-mode theorem set k=ceil(h_m/(2r-1)), and let

    t_q=d_q^[m] e_q^[k],   a_q=d_q e_q,   N=2m.

These are rational numbers. The proved all-q bound is v2(a_q-t_q)>=h_m,
and a_0=t_0=1. Define repaired moments

    t_hat_q=a_q for0<=q<N,    t_hat_q=t_q forq>=N.

They are integral units, match the first2m actual moments exactly, and still
satisfy v2(a_q-t_hat_q)>=h_m for every q. Their generating function is

    sum t_hat_q z^q = sum t_q z^q
                         +sum_(q<N)(a_q-t_q)z^q.

The first term has constant-recurrence rank at most mk. The second has
support below N and is realized by an N-dimensional nilpotent shift.
Taking the direct sum gives rank at most mk+N. This concerns the ordinary
finite recurrence, not a diagonal matrix of nonzero eigenvalues.

With the same scalar packet factors and full source, the corrected model is

    G_hat=G^[m,k]+sum_(1<=q<N) R_(r,q)(a_q-t_q)P_q(x)A(x-q).

The q0 correction vanishes. Each other correction is exactly

    R_(r,q)(a_q-t_q)P_(q-1)(x)(9^(x-q+1)-1)/8.

It therefore adds only polynomial prefactors at exponential bases1 and9,
of degree at most2N-4 before multiplication by the clearing polynomial D_r.
After clearing, the added polynomial degrees are at most2r+2N-2. Retaining
the separate Jordan contributions, a valid differential-order bound is

    4r+4N-2+8mk.

The repaired model remains a finite exponential model. The same integral
unit packet argument and all-q error give

    2^-178(G_hat-G_r) in2^(h_m-178) Z_2<Z>.

For h_m-178>=9 the same half-derivative and stationary comparison apply:
critical-center error is at least h_m-179, and stationary-value error is at
least h_m-178. Neither the ordinary index nor a new approximation rank is
searched in this argument.

In particular the repaired packet1 moment is the exact a_1, independent of
the geometric truncation length. The reduced-height growth of e_1^[k]
proved in the earlier note cannot be promoted to a height obstruction for
every finite model. Its cost may persist in other coefficients or in the
repair terms, but no such lower bound is assumed here. Bernoulli prefix
values and their new combinations require their own height control.

The actual discriminant nonvanishing remains open. This is an executed
symbolic repair of the precise scalar-height discriminator, not a claimed
small-height stationary construction. Restoring finite prefix agreement
does not force v2(Phi_model)<h_m-178.
