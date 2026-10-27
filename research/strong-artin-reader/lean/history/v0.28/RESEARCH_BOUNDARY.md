# Research boundary — v0.28

## Closed as written

- Continuous simultaneous literal lifting criterion for arbitrary families of continuous local
  group maps, across discrete square-zero coefficient extensions.
- Local mismatches are constructed from actual local representation lifts, not arbitrary
  cochain data or a section assumed already to satisfy every prescription.
- No local openness or clopenness hypothesis. Thus the criterion applies to closed nonopen
  subgroup inclusions once their actual topologies and representation data are supplied.
- The constrained obstruction records global multiplicativity and local matching simultaneously.
- After an absolute primitive is supplied, strict gluing is measured by the cokernel of restriction
  on continuous Z1. The cokernel class is independent of that primitive.
- Explicit strict-gluing sufficiency under surjectivity of that restriction map.
- Finite-group H1 averaging yields actual 1+kernel conjugators between two lifts.
- A finite quotient of invertible order, with local prescriptions factoring through finite
  groups of invertible order, has one lift matching every prescription up to independent local
  kernel conjugacy. Matrix and continuous pullback versions are checked.
- Kernel-checked failures of pairwise-to-global gluing and of literal-versus-conjugate matching.

## Crucial limits

1. The strict quotient is explicitly constructed from continuous inhomogeneous cochains. No
   equivalence to a separate homogeneous/derived cohomology API or arithmetic Selmer complex
   is proved. The local degree-zero gauge terms are not included in its boundary group.
2. The secondary cokernel uses Z1, not H1. Replacing Z1 by H1 without changing the deformation
   problem would discard literal matching information. A general up-to-conjugacy obstruction
   complex remains open; the positive up-to-conjugacy theorem is proved separately by averaging.
3. The cokernel class is proved independent of the absolute primitive in the fixed coefficient
   action. Across different provisional-section Datum objects, the zero criterion is intrinsic
   by its equivalence to liftability; a canonical full quotient transport is not supplied here.
4. These are necessary-and-sufficient criteria, not universal obstruction vanishing. The finite
   order-invertible theorem proves a genuine positive sector with its displayed hypotheses.
5. Local conjugators may differ with i. The tame counterexample shows why they cannot be replaced
   by a single global conjugator or simultaneous literal equalities.
6. In the finite positive theorem, local prescriptions factor through the specified finite H_i.
   This is substantive. Wild/noninvertible residual images and arbitrary nonfactoring local
   prescriptions are not covered by that vanishing argument.
7. No p-adic Hodge, de Rham, crystalline, fixed inertial type, unramified, or polarized local
   deformation condition is silently identified with a prescribed representation on a group.
8. One square-zero step is not a compatible complete coefficient-tower theorem.
9. No arithmetic Tate-duality comparison, Chebotarev auxiliary-prime theorem, auxiliary descent,
   automorphic carrier, automorphic support theorem, or Strong Artin result is proved.
10. Standard cochain and averaging mechanisms are being formalized; historical novelty is not
    asserted. An elementary counterexample to an intermediate implication is not a counterexample
    to Strong Artin.

## Next consequential target

For one specified arithmetic local deformation condition, form the correct continuous relative
complex including any allowed local kernel conjugacies. Compute or control the image of the global
localization map on the relevant classes. Prove the distinguished gluing class vanishes, rather
than assuming a surjective localization map or conflating absolute and local vanishing.
