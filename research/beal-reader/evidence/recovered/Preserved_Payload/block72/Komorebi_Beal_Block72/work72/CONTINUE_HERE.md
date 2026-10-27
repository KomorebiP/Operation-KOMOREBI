# Continue with Block73

Use Komorebi_Beal_Block72_Higher_Seven_Natural_Lift_v7.2.0.zip as sole checkpoint.
Read README, all work72 contracts/reports/notes, source audit, failures and verification.
Preserve the exact Block71 archive and nested history. Keep bytecode disabled:

    python -B verify.py --report ../Block72_Replay.json

Default replay rebuilds the new finite assertions only. --replay-predecessor adds
one immediate Block71 default run, not the entire history.

Authoritative new results:
- At c=v7(C)>=1, exact marked period classes and actual RM=epsilon R are known
  modulo7^j for1<=j<=7c-1, with one compatible sign.
- kappa_j=2epsilon*w X_j+Lambda_j H_j+7c T_j. T_j=[7] is a THIRD coordinate.
- Lambda_2=47+38Q_A+14Q_A^2-7q7(C0) mod49, Q_A=(A^6-1)/7 mod49.
- The actual global alpha_j is supplied only at j<=m=floor(n/2)+1 (or a separately
  proved stronger triangular precision). Its valuation coordinate has valuation
  min(j,1+v7(c)), even beyond the explicit unit-formula window.
- At n>=2, W_2=7c*v/(2epsilon) mod49; a no-[7]-component lift is impossible if7∤c.
  W_j=0 is an extra hypothesis, not a theorem or an automatic finite-flat condition.
- All EIGHT depth-one patterns remain. Every allowed A mod49 has all seven lifts
  to A mod343 locally. There are28224 pattern/A/C0 choices and7056 genuine local
  Hensel-root controls. They are not global integer solutions or actual beta.

Next target: a constraint on the SAME actual global deformation. At n=1 retain
lower-left7*beta terms instead of declaring a global mod49 Kummer lift. At n>=2,
compare the forced fixed-seven valuation W_2 with genuine global/fixed-prime data,
not an arbitrarily chosen lift of the residual three-generator class. The actual
higher unit coordinates are not free once a global representation is fixed.

Do not discard the uniformizer, extend the precision window without computing
actual period errors, fix the local sign at unrelated primes, or re-enumerate
these local residues and announce global exclusion. The eight bounded patterns,
unrestricted support/depth, minus component, integral realization, independent
upstream acceptance, CM/higher levels, full signature and full Beal remain open.
