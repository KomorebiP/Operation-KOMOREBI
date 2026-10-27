# Paper XII Deep Mathematical Audit

## Audit conclusion

The revised manuscript is internally coherent under its printed hypotheses. The proof chain has been narrowed to formal statements about quotient deformation conditions, ordinary and derived support, finite Hecke packets, inverse limit occupancy, and conditional pointwise realization. The paper does not claim to prove the arithmetic inputs supplied by published automorphy lifting, classicality, or Galois realization theorems.

## Principal corrections to the legacy manuscript

### Deformation components are not projector packets

A complete local deformation ring has no nontrivial idempotents. Its irreducible components are generally closed support loci rather than open and closed factors. The revised manuscript therefore encodes local conditions through quotient rings and module or derived support. Central idempotents are used only for finite Artin Hecke algebras, where a genuine product decomposition exists.

### Full support is the patching conclusion that matters

For a finite module over a Noetherian ring, near faithfulness is equivalent to full support. The manuscript proves that full support descends through the quotient that removes auxiliary variables. The derived version is proved by base change of residue field fibers.

### Auxiliary freeness does not imply deformation support

The ring

\[
R=k[[t,x]]/(x(x-t))
\]

has two components. The module \(R/(x)\) is free over \(k[[t]]\) but occupies only one component. This blocks the inference from freeness over the Taylor Wiles auxiliary algebra to full support over the deformation ring.

### An isomorphism transports support but a quotient may erase it

An isomorphism \(R\cong\mathbb T\) transports support and Fitting ideals exactly. A surjection need not do so. The example

\[
k[[x,y]]/(xy)\longrightarrow k[[y]]
\]

removes one irreducible component.

### Hecke packets do not require semisimplicity

A finite commutative algebra over a field is a product of Artin local algebras. Its canonical idempotents isolate maximal Hecke packets as simultaneous generalized eigenspaces. Trace is used only in characteristic zero. Localization and rank remain the primary occupancy tests.

### Finite and infinite occupancy are separated

Nested nonzero packets in one finite dimensional carrier stabilize. This statement fails in an infinite dimensional carrier. When the carriers change with the level, nonzero stable cores and surjective maps between them are the correct inverse limit hypothesis.

### Support does not imply classicality

A supported characteristic zero point gives a nonzero ordinary or derived Hecke fiber. Classicality, an attached Galois representation, and local global compatibility remain separate external inputs. The pointwise theorem invokes them explicitly.

### One automorphic member does not create companions

Automorphy propagates across a strictly compatible system once the system and its common Frobenius polynomials already exist. Companion existence is treated through finite companion forests and remains a separate problem.

### The coefficient prime two is split into algebra and arithmetic

Augmentation and coinvariant recovery work unchanged at two. Integral sign projectors fail, and the residual group algebra is local. Adequacy, local deformation geometry, and classicality at two require their own arithmetic theorems.

## Delicate internal results reviewed

1. The completed tensor quotient is proved from the universal property of completed tensor products.
2. The finite adequacy certificate uses the standard representation of \(S_3\) over \(\mathbb F_7\), where the group order is invertible.
3. The support quotient theorem uses finite generation and Nakayama's lemma.
4. The Fitting support and higher Fitting stratum formulas are derived from presentation matrix ranks.
5. The derived quotient support theorem is an exact residue field base change identity.
6. The stable core surjectivity lemma uses stabilization of descending affine subspaces in finite dimension.
7. The pointwise Galois identification is explicitly conditional on Chebotarev dense Frobenius agreement and semisimplicity.
8. The final theorem is a composition of five separate gates and does not merge their hypotheses.

## Remaining external risks

The following statements require specialist review or published input beyond the internal algebra.

1. Applicability of a chosen automorphy lifting theorem to the actual residual image and local conditions.
2. Construction and geometry of the required local deformation rings.
3. Near faithfulness or full derived support of the patched object in the intended arithmetic setting.
4. The specific comparison between the global deformation ring and Hecke algebra.
5. Classicality of the supported characteristic zero fiber.
6. Construction and local compatibility of the attached Galois representation.
7. Existence of residual and coefficient place companions.
8. Historical novelty of the formal organization and any individual algebraic statement.

## Status

The manuscript is internally complete as a formal algebraic and logical treatment. Internal completion is not independent specialist validation and does not establish unrestricted global reciprocity.
