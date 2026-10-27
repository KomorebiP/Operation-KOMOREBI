# Block60 — Diagonal periods and the surviving local families

Version6.0.0. 19 September2026.

The two missing diagonal period classes are now determined. They give a complete
local49-torsion criterion and a new necessary residue condition for actual
depth-two beta support. They do NOT eliminate the four surviving primes:
explicit primitive q-adic Frey families pass every period test at each one.
All actual arithmetic conclusions retain the stated inherited geometric inputs.

## 1. The other actual periods

Put epsilon=C^7/A^3, phi=(1+sqrt5)/2. In the same marked node-cycle uniformization,
modulo principal units of the local field,

    Pi_aa = -epsilon*phi^2/(675sqrt5),
    Pi_bb =  epsilon*phi^-2/(675sqrt5),
    Pi_ab=Pi_ba=-phi^-4.

The normalized family and its first smoothing derivative are computed exactly.
The branch-coordinate derivative products are -phi^2/45 and -phi^-2/45. The
formal node equation identifies their precise unit contribution to the
Schottky multipliers, and the checked period product identifies the diagonal
periods. There is no unspecified residue unit left in these formulas.

In additive Kummer coordinates X=[phi] and
Z=7[C]-3[A]-3[3]-5[sqrt5], the full period matrix becomes

    [[Z+2X,-4X],[-4X,Z-2X]].

All period coordinates vanish exactly when X=Z=0. This is a marked local
identity, not the missing global semilinear representation comparison.

## 2. A complete local criterion, not merely another necessary unit test

Let q be a variable prime, F=K_v, Q=#kappa(v), and C=q^k C0 with C0 a unit.
For the actual local Jacobian,

    J^nu[49] entirely F-rational
      iff 49|Q-1, 7|k, phi is a49th residue power,
          3*5^9*A/C0^35 is a49th residue power.

The converse follows from the split torus/lattice torsion sequence after
checking roots of unity and every period coordinate. Principal units are
uniquely7-divisible at q!=7, so no uncomputed higher period coefficients can
change this local power test. At level7 the corresponding new unit is75A.

At actual depth-two beta ramification this is necessary, and the inherited
stronger condition v7(k)=1 remains in force. The local criterion is NOT
sufficient to realize global beta or a global reducible representation.

## 3. What happens at197,883,1373,1667

At all four primes phi has prime-to7 order and49 divides q-1. The rational
unit test can be performed in F_q. For each specified C0 there are respectively
4,18,28,34 possible nonzero A residues passing the49-test.

|q|All unit pairs(A,C0)|Full7 pairs|Full49 pairs|
|---|---:|---:|---:|
|197|38416|5488|784|
|883|777924|111132|15876|
|1373|1882384|268912|38416|
|1667|2775556|396508|56644|

These are residue pairs, not global solution counts. The two independent
algorithms enumerate all5,474,280 pairs and agree on every accepted-pair digest.

## 4. Actual local positive families prevent a false exclusion

For C=q^7 and A congruent to(3*5^9)^-1, the unit condition has residue1. The
following initial data give primitive local solutions:

|q|A|B modq|
|---|---:|---:|
|197|148|81|
|883|228|27|
|1373|1028|497|
|1667|1449|984|

B is the unique q-adic root near the displayed residue of B^5=q^49-A^3.
Hensel's lemma gives an EXACT equation over Q_q. The associated local Frey
Jacobian has full49-torsion over K_v by the complete period criterion. The
node thickness is49 and the natural monodromy content is2.

The certificate computes B modulo q^52; an independent digit-by-digit lift
matches the Newton lift. These are genuine local geometric controls, not
arbitrary toric matrices. They are NOT ordinary integer triples or global
Beal counterexamples. Neither actual global beta nor the common global natural
Kummer coefficients are constructed. Congruence neighborhoods of A and C0
supply whole local families with the same conclusion.

At each prime, multiplying the base A residue by a primitive-root seventh
power preserves local7-torsion but destroys49-torsion. Thus the newly computed
diagonal condition is strictly stronger than the old off-diagonal test, even
though it does not remove the primes.

## 5. Impact on the research target

Under COMPLETE H(C) subsetU, n<=2 is unchanged, and depth2 beta support remains
within{197,883,1373,1667}. The inherited ratio constraints, nonzero unit
coefficient and v7(v_q(C))=1 all remain. The NEW condition is an explicit relation
between the actual A and the actual unit part C0 at each supporting prime.
At883, only18 A residues for each C0 pass, but that set is not empty.

This block closes the missing LOCAL period computation. It does not close the
depth-two GLOBAL compatibility problem. A next argument must tie these local
families to the same natural global class and the chi^-1-twisted opposite
endpoint, including fixed-prime local data. Repeating higher principal-unit
period expansions cannot strengthen this particular torsion-power test.

## 6. Verification and limitations

The exact original Block59 archive was cleanly restored, its entire declared
selected predecessor replay passed, and its bytes remain unchanged. New finite
checks include rational smoothing identities,445 residue fields,5,474,280 unit
pairs, four positive Hensel families, four seventh-only controls and four
controls failing even7. Each of12 roots is checked modulo q^52 by two algorithms.
The independent implementation uses sqrt5 arithmetic and inverse-conic
coordinates; it imports no primary arithmetic code. Production verification
requires only Python's standard library.

The final package verifier regenerates both outputs in a scratch copy, compares
complete JSONs, audits payload and immediate inherited source hashes, and tests
rejection of altered smoothing constants and altered local torsion data. The
archive audit and final fresh replay are outside the immutable ZIP.

The intended prime-elimination route failed and the positive local controls
are retained. Broad source searches were unhelpful; exact primary-source pages
were opened directly. No new Lean compilation or independent mathematical
review was performed. The formal/analytic comparison and all upstream actual
geometry remain prose proofs with explicit dependencies, not consequences of
finite test counts. Depth1, general depth2, unrestricted high support, CM,
higher Hilbert levels, full signature and Beal remain separate obligations.
