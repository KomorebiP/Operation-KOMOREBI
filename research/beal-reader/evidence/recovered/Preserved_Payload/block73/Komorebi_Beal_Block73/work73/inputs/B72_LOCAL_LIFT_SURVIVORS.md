# B72.5. All residual-compatible local configurations lift

This is a positive local existence statement, not a global realization theorem.
Fix a residual pattern alpha=(vw,r,1), and actual7-adic units A,C0 satisfying
B71's residual square condition. Choose its sign epsilon and put g0=v/(2epsilon)
inF7*. For any level j<=7c-1, choose one unit lift g_j of g0. Then

    g_j*kappa_j

is a local lift of the SAME residual class: its X,H,T coordinates reduce to
vw,r+4,0. This works for EVERY lift of A in its permitted class modulo49 and for
EVERY7-adic unit C0. It does not prescribe the global alpha_j, the global beta,
or an actual global integral endpoint. Their values cannot be selected anew to
fit each prime.

Thus the attempt to remove the eight patterns using local higher liftability alone
fails, not just at the first extra digit but throughout the proven window.

## Exact j2 classification

The residual36 directions are tested against all294 rational unit A mod343 and42
rational unit C0 mod49:444528 inputs. Exactly116424 are residual-compatible and
have the local lifts above. This count is396*7*42, using the396 predecessor
coefficient/A mod49 combinations. No additional A digit is lost locally.

For the actual frozen eight patterns, each of its12 allowed A mod49 residues
has all7 lifts modulo343, and C0 has all42 unit residues modulo49. Therefore

    8*12*7*42=28224

augmented pattern/A/C0 choices survive. They correspond to7056 distinct(A,C0)
unit pairs. No ninth-prime or conductor assertion changes, and no pattern is
eliminated. The gauge used for the positive control is the fixed lift
v/(2epsilon) modulo49; V and W are the coordinates of the resulting LOCAL
geometric extension, not asserted global lift coefficients.

## Genuine local equation controls

For every one of the7056 distinct unit pairs take its integer representatives,
put C=7C0, and let B be the unique7-adic fifth root of

    B^5=(7C0)^7-A^3.

Fifth powering is bijective onF7*, and the derivative5B^4 is a unit. Hensel
therefore gives an exact primitive local triple inQ7. All7056 roots are computed
modulo7^18 by Newton lifting and separately by single-digit Hensel lifting; the
ordered root-list hashes agree. Neither algorithm asserts the root is an ordinary
integer, or that the same integer triple works at every prime.

Full natural J[7] rationality atF is not claimed; F does not contain mu7. The
objects compared here are extension classes. These controls preserve, rather
than contradict, all prior local positive Frey families.

## An explicit valuation contrast

At A=C0=c=1, r=6, v=3, choose epsilon=-1 and g_2=23 mod49. Then

    (U_2,V_2,W_2)=(3w,3,14).

The residual values are(3w,3,0), as required. A candidate higher class with the
same residual values but W_2=0 cannot match this local period extension. The
valid local lift has W_2=14 instead. This does not exclude the residual pattern.
