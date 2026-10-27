# B77.2. Local-global injectivity for the secondary H^2 obstruction

Let

    K=Q(sqrt(5)),    k=F_49,    M=k(chi).

The localization map

    H^2(K,M) -> product_v H^2(K_v,M)                        (1)

is injective.

## Proof

Put `L=K(zeta_7)`.  Then `[L:K]=6`.  Restriction followed by corestriction on
`H^2(K,M)` is multiplication by six.  Since six is invertible on seven-primary
cohomology, restriction

    H^2(K,M) -> H^2(L,M)

is injective.

Over `L` the cyclotomic action on `M` is trivial.  As an `F_7`-module,

    k = F_7 direct-sum F_7.

Since `L` contains `mu_7`, choose the usual identification `F_7 ~= mu_7`.
Kummer theory gives

    H^2(L,F_7) ~= H^2(L,mu_7) ~= Br(L)[7].                  (2)

The Brauer-Hasse-Noether local-global sequence makes

    Br(L) -> direct-sum_w Br(L_w)

injective.  Applying it to both `F_7` coordinates proves injectivity over `L`.
If a class over `K` is zero at every completion, its restriction is zero at
every completion of `L`, hence zero over `L`, and therefore zero over `K`.
This proves (1).

Archimedean completions contribute no seven-primary obstruction.

## Consequence for Block 77

Fix a global solution `p` of

    dp=-alpha cup beta.

By B77.1, its `q` obstruction is `[mu_p]` in `H^2(K,k(chi))`.  Therefore

    [mu_p]=0 globally

if and only if

    [mu_p]|_(K_v)=0 for every place v.                      (3)

There is no additional hidden global H^2 class once the *same* first-stage `p`
has locally vanishing secondary obstruction everywhere.

This does not solve the arithmetic problem.  Different local first-stage
solutions need not arise from one global `p`, and after a global `q` exists its
local values still need to match the toric, endpoint, semilinear, and fixed-seven
conditions.  Those are H^1/affine-Selmer questions, isolated in B77.3.

External inputs used in this proof are standard restriction/corestriction,
Kummer theory, and the Brauer-Hasse-Noether local-global theorem.  The project
should independently audit their exact coefficient translation before treating
this conditional branch as externally accepted mathematics.
