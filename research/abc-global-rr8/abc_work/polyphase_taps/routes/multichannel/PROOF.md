# Multichannel taps: preserved content, movable cancellation, and determinant cost

Parent checkpoint: RR3 archive SHA-256 `557eeb61fcd37c984884b7123e7b599b403200244786f6fb549279d6b4b05302`. This route reads `abc_work/roots_unity/LATEST.md` and creates only the present route files. The target remains primitive ABC; this note does not prove it.

## 1. The exact invariant is minimum depth, not maximum depth

For a nonzero rational vector x define nu_p(x)=min_i v_p(x_i), with v_p(0)=infinity. If M is an integer square matrix with nonzero determinant D, then

    nu_p(x) <= nu_p(Mx) <= nu_p(x)+v_p(D).                    (1)

The first inequality follows because all matrix coefficients are p-integral. For the second, use adj(M)Mx=Dx; the adjugate is integer, so nu_p(Dx)>=nu_p(Mx). If p does not divide D, equality holds. In particular, a unimodular integer bank preserves the common p-adic content of its channels.

For M=N/q, with N integer, q a nonzero integer, and det(N)!=0, the exact corresponding bounds are

    nu_p(x)-v_p(q) <= nu_p(Mx)
       <= nu_p(x)+v_p(det N)-v_p(q).                        (2)

More generally, over the p-adic field, the bounds from M and M^(-1) are

    nu_p(x)+min_ij v_p(M_ij) <= nu_p(Mx)
       <= nu_p(x)-min_ij v_p((M^(-1))_ij).                  (3)

These are statements about minimum coordinate valuation. The maximum coordinate valuation is not invariant under a general unimodular change of channels.

### Field reconstruction versus integral reconstruction

Perfect reconstruction over a field requires only that an inverse or left inverse exists in that field. For a single-tap delay channel y_i=g_i z^(k_i) x_i, a nonzero scalar g_i is enough for reconstruction over the field: synthesis uses g_i^(-1) z^(-k_i). At a p-adic unit z, its coordinate depth changes by v_p(g_i). If analysis is p-integral, v_p(g_i)>=0; synthesis is additionally p-integral exactly when v_p(g_i)=0. Thus nonzero field scalars must be p-units before one can assert integral preservation for both stages.

The same distinction applies to a rectangular analysis bank T and synthesis bank S satisfying ST=I. If both have p-integral coefficients, nu_p(Tx)>=nu_p(x) and nu_p(x)=nu_p(STx)>=nu_p(Tx), giving equality. A field-valued synthesis inverse can instead carry denominator depth and supplies only the coefficient-sensitive bound from (3).

Complex perfect reconstruction or Euclidean energy conservation is a different assertion. To discuss p-adic valuation of its coefficients one needs coefficients with an appropriate arithmetic interpretation and a chosen local embedding. A general complex coefficient has no specified p-adic valuation.

Finally, the selected scalar functional must be retained. If F=ell x and x=Sy, then exactly

    F=(ell S)y.

Its depth is unchanged as a scalar, although it may now arise from cancellation between unit channels or from a synthesis coefficient. Channel content alone cannot replace this transformed functional.

## 2. A deep contact can move out of a channel and into synthesis

Let p be odd, let X be a positive integer with v_p(X+1)=e>=1, and put x=(X,1). Both input channels are units. The unimodular matrix

    M = [[1,0],[-1,1]]

gives y=(X,1-X), whose two coordinates are also units because X=-1 modulo p. Nevertheless

    X+1=2y_1+y_2

has depth e. The maximum finite coordinate depth changed from e in the analysis coordinates (X+1,1), obtained by another unimodular bank, to zero in y. Complete reconstruction retains the high-depth functional as a cancellation in its synthesis row.

For comparison, the integer Haar bank

    H = [[1,1],[1,-1]]

has determinant -2. It maps x to (X+1,X-1), with depths (e,0). At odd p it is p-adically invertible, and synthesis uses 1/2, a unit at p. This creates no bound on e. Globally the factor 2 is a genuine normalization prime, although it has no cost at the odd contact prime.

Thus a statement that all channels cannot be simultaneously deep does not bound one exceptionally deep sum. It proves only that some complementary channel remains a unit.

## 3. When every channel becomes deep, the determinant pays

Consider the tap matrix evaluated at X,

    E(X) = [[1,X],[-1,1]],       det E(X)=1+X.

It sends the unit vector (1,1) to (X+1,0). Hence every output channel has valuation at least e, and the common depth is exactly e. Equation (1) is sharp: v_p(det E(X))=e. Its inverse has denominator X+1. The apparent concentration of all contact into the channel vector has retained precisely that contact in the reconstruction determinant.

Taking X=A^n displays an important coefficient distinction. As a polynomial tap matrix E(z)=[[1,z^n],[-1,1]], every nonzero coefficient is plus or minus one. But det E(A)=A^n+1, and the evaluated matrix entries have archimedean size A^n. Small formal tap coefficients alone do not bound the height of the evaluated bank.

A polynomial bank unimodular over Z[z,z^(-1)] has determinant plus or minus z^k. Evaluating at a p-adic unit z=A/B gives a p-adic unit determinant and p-integral entries, so it preserves common depth. A bank whose determinant vanishes at the relevant root of unity instead carries the original contact in that determinant. Neither fact controls a deep individual functional.

## 4. Adaptive normalization removes depth only with a recorded inverse cost

If e=v_p(X+1) is known, the rational bank

    N_e = [[p^(-e),p^(-e)],[0,1]]

maps (X,1) to ((X+1)/p^e,1), both units. Here det N_e=p^(-e), its coefficients have denominator p^e, and its inverse is

    N_e^(-1) = [[p^e,-1],[0,1]].

Reconstruction of the contact is X+1=p^e y_1. The depth has moved into a synthesis coefficient. The synthesis matrix has archimedean norm at least p^e. This is exact bookkeeping, not a proof that every adaptive bank must have this particular cost or that useful adaptive methods are impossible.

An adaptive unimodular shear [[1,lambda],[0,1]] can choose a deep combination X+lambda. It requires lambda=-X modulo p^e. A representative always exists with 0<=lambda<p^e; it may be much smaller on special inputs, including lambda=1 for an existing contact. Consequently the existence of a short tap vector cannot bound e without a separately proved comparison between its value, its coefficient height, and the input arithmetic.

## 5. Strict integer paraunitarity is exceptionally rigid

Let F(z) be a square finite Laurent-polynomial matrix with integer coefficients satisfying

    F(z) F(z^(-1))^T = I.

The constant coefficient of each diagonal entry on the left is the sum of the squares of every tap coefficient in that row. It equals one. Each row therefore contains exactly one nonzero tap coefficient, equal to plus or minus one. Orthogonality of distinct rows forces their occupied columns to differ. Thus F is a signed permutation of monomial delays.

For p-adic unit z, such a bank merely permutes channel valuations. Nontrivial paraunitary banks require a scale or noninteger coefficients. Their p-adic behavior must be checked from those coefficients and inverses, rather than inferred from real energy conservation. For example [[3/5,4/5],[-4/5,3/5]] is a rational orthogonal matrix; at p=5 both it and its inverse carry denominator depth one.

## 6. Strongest surviving next step

Determinant or Bezout certificates can give a true local bound on simultaneous channel vanishing. If p^e divides every coordinate of Mx and nu_p(x)=0 for an integral bank, equation (1) forces e<=v_p(det M). Summing such inequalities can be useful only if the determinant values have a global height bound that improves on the original output height, and if the construction actually forces all relevant channels to vanish. The usual reconstructed ABC sum supplies one deep functional and does not supply that stronger premise.

A prospective adaptive-tap proof should therefore construct an explicitly nonzero integer Z that is divisible by the required exceptional-prime product, while proving an independent upper bound for |Z| strong enough for the ABC criterion. Determinant, denominator, degree, and evaluation-height bounds belong in that certificate. These requirements leave open useful adaptive constructions. The present argument rules out only treating an invertible coordinate change, real paraunitarity, or short modular tap vector as the missing arithmetic estimate by itself.

In RR3's common-power notation, c=A^n+B^n, D=rad(AB), and U(c)=B_2 W_n G_n. A precise sufficient certificate, for gamma=epsilon/(1+epsilon), is

    0!=Z in Z,    W_n divides Z,
    |Z| <= D c^gamma/(B_2 G_n).

It implies U(c)<=D c^gamma, hence rad(ABc)=D c/U(c)>=c^(1-gamma), which is exactly c<=rad(ABc)^(1+epsilon). The new work would be constructing such a Z and proving its nonvanishing and size; the coordinate-change lemmas do not construct one.

## 7. Finite evidence

The accompanying standard-library verifier constructs exact-depth contacts X=A^8 at p=17 for e=1,...,8 using explicit Hensel lifting. It checks all displayed matrices and their rational inverses using exact fractions, the determinant depth, the projected scalar contact, and the normalization cost. It also exhaustively checks equation (1) for every 2-by-2 integer matrix with entries in [-3,3] and nonzero determinant on three vectors at each depth. No full output factorization, universal ABC bound, Lean compilation, or novelty claim is made.
