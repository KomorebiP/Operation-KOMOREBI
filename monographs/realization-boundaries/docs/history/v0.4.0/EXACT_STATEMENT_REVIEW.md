# Exact statement review — v0.4.0

Internal inspection of Lean-exported types and axiom dependencies. This is not external peer review. The twenty inherited production modules are unchanged; their earlier statement reviews are preserved in `docs/history`.

## hom_coordinate_formula

The map is any additive homomorphism between the actual rational preimages. No continuity, diagonality, or finite-support hypothesis is supplied for the input element. The coefficient is defined from the image of the actual prime seed.

```lean
∀ (U V : Submodule ℚ RealizationBoundaries.TailSpace)
  (f : ↥(RealizationBoundaries.preimage U) →+ ↥(RealizationBoundaries.preimage V))
  (x : ↥(RealizationBoundaries.preimage U)) (p : RealizationBoundaries.Prime),
  ↑(f x) p = RealizationBoundaries.homDiagonal U V f p * ↑x p
```

Defining module: `RealizationBoundaries.DiagonalHomomorphisms`. Transitive axioms: propext, Classical.choice, Quot.sound.

## homDiagonal_unique

Uniqueness quantifies over every coordinate and every actual group element, not only the rational quotient.

```lean
∀ (U V : Submodule ℚ RealizationBoundaries.TailSpace)
  (f : ↥(RealizationBoundaries.preimage U) →+ ↥(RealizationBoundaries.preimage V)) (c : RealizationBoundaries.Ambient),
  (∀ (x : ↥(RealizationBoundaries.preimage U)) (p : RealizationBoundaries.Prime), ↑(f x) p = c p * ↑x p) →
    c = RealizationBoundaries.homDiagonal U V f
```

Defining module: `RealizationBoundaries.DiagonalHomomorphisms`. Transitive axioms: propext, Classical.choice, Quot.sound.

## preimage_hom_continuous

Continuity is a conclusion for every additive homomorphism between the actual subspace topologies, not an extra hypothesis used to derive diagonality.

```lean
∀ (U V : Submodule ℚ RealizationBoundaries.TailSpace)
  (f : ↥(RealizationBoundaries.preimage U) →+ ↥(RealizationBoundaries.preimage V)), Continuous ⇑f
```

Defining module: `RealizationBoundaries.DiagonalHomomorphisms`. Transitive axioms: propext, Classical.choice, Quot.sound.

## diagonalTail

The actual induced map on P/D is rational-linear. Its linearity is proved from the additive quotient map and unique rational division.

```lean
RealizationBoundaries.Ambient → RealizationBoundaries.TailSpace →ₗ[ℚ] RealizationBoundaries.TailSpace
```

Defining module: `RealizationBoundaries.DiagonalHomomorphisms`. Transitive axioms: propext, Classical.choice, Quot.sound.

## diagonalHomEquiv

The converse retains exact admissibility: a coordinate family must map the original source preimage into the original target. Arbitrary product endomorphisms need not do this.

```lean
(U V : Submodule ℚ RealizationBoundaries.TailSpace) →
  (↥(RealizationBoundaries.preimage U) →+ ↥(RealizationBoundaries.preimage V)) ≃
    { c // RealizationBoundaries.DiagonalAdmissible U V c }
```

Defining module: `RealizationBoundaries.DiagonalRealization`. Transitive axioms: propext, Classical.choice, Quot.sound.

## diagonalAdmissible_iff_finite_defect

The finite-defect condition contains the actual rational section, including its denominator-zero convention. Membership in D is proved equivalent to exact realization.

```lean
∀ (S T : Set RealizationBoundaries.Prime) (c : RealizationBoundaries.Ambient),
  RealizationBoundaries.DiagonalAdmissible (RealizationBoundaries.selectorLine S) (RealizationBoundaries.selectorLine T)
      c ↔
    ∃ r,
      (RealizationBoundaries.diagonal c) (RealizationBoundaries.indicator S) -
          RealizationBoundaries.rationalSection T r ∈
        RealizationBoundaries.finiteSupport
```

Defining module: `RealizationBoundaries.DiagonalRealization`. Transitive axioms: propext, Classical.choice, Quot.sound.

## selectorHomEquiv

This is an equivalence with all actual additive homomorphisms, not only some constructed subfamily.

```lean
(S T : Set RealizationBoundaries.Prime) →
  (↥(RealizationBoundaries.selectorGroup S) →+ ↥(RealizationBoundaries.selectorGroup T)) ≃
    { c //
      ∃ r,
        (RealizationBoundaries.diagonal c) (RealizationBoundaries.indicator S) -
            RealizationBoundaries.rationalSection T r ∈
          RealizationBoundaries.finiteSupport }
```

Defining module: `RealizationBoundaries.DiagonalRealization`. Transitive axioms: propext, Classical.choice, Quot.sound.

## endomorphismRingEquiv

The equivalence is a RingEquiv with actual endomorphism composition. It is not merely an equivalence of sets or additive groups.

```lean
(W : Submodule ℚ RealizationBoundaries.TailSpace) →
  AddMonoid.End ↥(RealizationBoundaries.preimage W) ≃+* ↥(RealizationBoundaries.diagonalEndRing W)
```

Defining module: `RealizationBoundaries.DiagonalRealization`. Transitive axioms: propext, Classical.choice, Quot.sound.

## diagonalEndRing_mem_iff

The eventual-rational criterion is finite disagreement on selected primes. The totalized rational cast at exceptional denominator primes does not delete the finite-exception condition.

```lean
∀ (S : Set RealizationBoundaries.Prime) (c : RealizationBoundaries.Ambient),
  c ∈ RealizationBoundaries.diagonalEndRing (RealizationBoundaries.selectorLine S) ↔ ∃ r, {p | p ∈ S ∧ c p ≠ ↑r}.Finite
```

Defining module: `RealizationBoundaries.EndomorphismScalars`. Transitive axioms: propext, Classical.choice, Quot.sound.

## diagonalSlope_unique

Infinite target support is explicit and is what makes the target rational generator nonzero. Without it, the chosen rational is not uniquely determined.

```lean
∀ (S T : Set RealizationBoundaries.Prime),
  T.Infinite →
    ∀ (c : RealizationBoundaries.Ambient)
      (hc :
        RealizationBoundaries.DiagonalAdmissible (RealizationBoundaries.selectorLine S)
          (RealizationBoundaries.selectorLine T) c)
      (r : ℚ),
      (RealizationBoundaries.diagonalTail c) (RealizationBoundaries.quotientMap (RealizationBoundaries.indicator S)) =
          r • RealizationBoundaries.quotientMap (RealizationBoundaries.indicator T) →
        RealizationBoundaries.diagonalSlope S T c hc = r
```

Defining module: `RealizationBoundaries.EndomorphismScalars`. Transitive axioms: propext, Classical.choice, Quot.sound.

## quotientScalar

The quotient scalar is an actual ring homomorphism for infinite selector support. Its map_zero, map_one, map_add and map_mul fields are checked.

```lean
(S : Set RealizationBoundaries.Prime) →
  S.Infinite → ↥(RealizationBoundaries.diagonalEndRing (RealizationBoundaries.selectorLine S)) →+* ℚ
```

Defining module: `RealizationBoundaries.EndomorphismScalars`. Transitive axioms: propext, Classical.choice, Quot.sound.

## quotientScalar_surjective

Every rational has an admissible diagonal lift. Surjectivity alone does not assert an additive or multiplicative lift map.

```lean
∀ (S : Set RealizationBoundaries.Prime) (hS : S.Infinite),
  Function.Surjective ⇑(RealizationBoundaries.quotientScalar S hS)
```

Defining module: `RealizationBoundaries.EndomorphismScalars`. Transitive axioms: propext, Classical.choice, Quot.sound.

## quotientScalar_eq_zero_iff

The zero-scalar condition constrains only selected coordinates. Complementary coordinates remain unrestricted and may have infinite support.

```lean
∀ (S : Set RealizationBoundaries.Prime) (hS : S.Infinite)
  (c : ↥(RealizationBoundaries.diagonalEndRing (RealizationBoundaries.selectorLine S))),
  (RealizationBoundaries.quotientScalar S hS) c = 0 ↔ {p | p ∈ S ∧ ↑c p ≠ 0}.Finite
```

Defining module: `RealizationBoundaries.EndomorphismScalars`. Transitive axioms: propext, Classical.choice, Quot.sound.

## endomorphismQuotientScalar_surjective

Surjectivity is transported to the actual original endomorphism ring, rather than left solely as a property of an auxiliary coefficient set.

```lean
∀ (S : Set RealizationBoundaries.Prime) (hS : S.Infinite),
  Function.Surjective ⇑(RealizationBoundaries.endomorphismQuotientScalar S hS)
```

Defining module: `RealizationBoundaries.EndomorphismScalars`. Transitive axioms: propext, Classical.choice, Quot.sound.

## hom_injective_iff_diagonal_nonzero

Injectivity of a supplied map is equivalent to all coordinate coefficients being nonzero, for every rational preimage source and target. Surjectivity of the original map is not asserted here.

```lean
∀ (U V : Submodule ℚ RealizationBoundaries.TailSpace)
  (f : ↥(RealizationBoundaries.preimage U) →+ ↥(RealizationBoundaries.preimage V)),
  Function.Injective ⇑f ↔ ∀ (p : RealizationBoundaries.Prime), RealizationBoundaries.homDiagonal U V f p ≠ 0
```

Defining module: `RealizationBoundaries.DiagonalAutomorphisms`. Transitive axioms: propext, Classical.choice, Quot.sound.

## inverseDiagonal_admissible

The source selector is infinite. Admissibility of the reciprocal family on the original target-to-source map is derived from the rational-line equation and its nonzero scalar.

```lean
∀ (S T : Set RealizationBoundaries.Prime),
  S.Infinite →
    ∀ (c : RealizationBoundaries.Ambient),
      RealizationBoundaries.DiagonalAdmissible (RealizationBoundaries.selectorLine S)
          (RealizationBoundaries.selectorLine T) c →
        (∀ (p : RealizationBoundaries.Prime), c p ≠ 0) →
          RealizationBoundaries.DiagonalAdmissible (RealizationBoundaries.selectorLine T)
            (RealizationBoundaries.selectorLine S) (RealizationBoundaries.inverseDiagonal c)
```

Defining module: `RealizationBoundaries.DiagonalAutomorphisms`. Transitive axioms: propext, Classical.choice, Quot.sound.

## selectorEquiv_inverse_coordinate

The actual inverse on the original groups has the exact reciprocal formula at every prime. There is no tail exception in this inverse formula.

```lean
∀ (S T : Set RealizationBoundaries.Prime) (hS : S.Infinite)
  (f : ↥(RealizationBoundaries.selectorGroup S) →+ ↥(RealizationBoundaries.selectorGroup T))
  (hn :
    ∀ (p : RealizationBoundaries.Prime),
      RealizationBoundaries.homDiagonal (RealizationBoundaries.selectorLine S) (RealizationBoundaries.selectorLine T) f
          p ≠
        0)
  (y : ↥(RealizationBoundaries.selectorGroup T)) (p : RealizationBoundaries.Prime),
  ↑((RealizationBoundaries.selectorEquivOfNonzeroDiagonal S T hS f hn).symm y) p =
    (RealizationBoundaries.homDiagonal (RealizationBoundaries.selectorLine S) (RealizationBoundaries.selectorLine T) f
          p)⁻¹ *
      ↑y p
```

Defining module: `RealizationBoundaries.DiagonalAutomorphisms`. Transitive axioms: propext, Classical.choice, Quot.sound.

## selector_hom_bijective_iff

The equivalence includes an explicit infinite-source-selector hypothesis. It is not generalized to arbitrary preimages such as D -> G_A.

```lean
∀ (S T : Set RealizationBoundaries.Prime),
  S.Infinite →
    ∀ (f : ↥(RealizationBoundaries.selectorGroup S) →+ ↥(RealizationBoundaries.selectorGroup T)),
      Function.Bijective ⇑f ↔
        ∀ (p : RealizationBoundaries.Prime),
          RealizationBoundaries.homDiagonal (RealizationBoundaries.selectorLine S)
              (RealizationBoundaries.selectorLine T) f p ≠
            0
```

Defining module: `RealizationBoundaries.DiagonalAutomorphisms`. Transitive axioms: propext, Classical.choice, Quot.sound.

## selector_hom_injective_iff_bijective

For an already supplied map in this infinite-selector rank-one family, injectivity suffices for bijectivity. This is stronger than existence of some embedding.

```lean
∀ (S T : Set RealizationBoundaries.Prime),
  S.Infinite →
    ∀ (f : ↥(RealizationBoundaries.selectorGroup S) →+ ↥(RealizationBoundaries.selectorGroup T)),
      Function.Injective ⇑f ↔ Function.Bijective ⇑f
```

Defining module: `RealizationBoundaries.DiagonalAutomorphisms`. Transitive axioms: propext, Classical.choice, Quot.sound.

## selector_hom_surjective_iff_bijective

Surjectivity of the supplied rank-one map also suffices. No analogous unrestricted-group statement is claimed.

```lean
∀ (S T : Set RealizationBoundaries.Prime),
  S.Infinite →
    ∀ (f : ↥(RealizationBoundaries.selectorGroup S) →+ ↥(RealizationBoundaries.selectorGroup T)),
      Function.Surjective ⇑f ↔ Function.Bijective ⇑f
```

Defining module: `RealizationBoundaries.DiagonalAutomorphisms`. Transitive axioms: propext, Classical.choice, Quot.sound.

## selector_endomorphism_automorphism_iff

The conclusion supplies an actual AddEquiv whose underlying AddMonoidHom is precisely the supplied endomorphism, not an unrelated group isomorphism.

```lean
∀ (S : Set RealizationBoundaries.Prime),
  S.Infinite →
    ∀ (f : AddMonoid.End ↥(RealizationBoundaries.selectorGroup S)),
      (∃ e, e.toAddMonoidHom = f) ↔
        ∀ (p : RealizationBoundaries.Prime),
          RealizationBoundaries.homDiagonal (RealizationBoundaries.selectorLine S)
              (RealizationBoundaries.selectorLine S) f p ≠
            0
```

Defining module: `RealizationBoundaries.DiagonalAutomorphisms`. Transitive axioms: propext, Classical.choice, Quot.sound.

## completionHom

This acts on Mathlib canonical completions, constructed using checked comparison equivalences. The current pinned Mathlib lacks the convenient additive completion-functor map/lift API names tested during development; none of those nonexistent APIs is used.

```lean
(U V : Submodule ℚ RealizationBoundaries.TailSpace) →
  (↥(RealizationBoundaries.preimage U) →+ ↥(RealizationBoundaries.preimage V)) →
    ↑(RealizationBoundaries.CanonicalCompletion U).toProfinite.toTop →ₜ+
      ↑(RealizationBoundaries.CanonicalCompletion V).toProfinite.toTop
```

Defining module: `RealizationBoundaries.CompletionReflection`. Transitive axioms: propext, Classical.choice, Quot.sound.

## completionHom_eta

The extension agrees with the supplied original map at every canonical eta image, binding it to that map rather than merely comparing isomorphic completion objects.

```lean
∀ (U V : Submodule ℚ RealizationBoundaries.TailSpace)
  (f : ↥(RealizationBoundaries.preimage U) →+ ↥(RealizationBoundaries.preimage V))
  (x : ↥(RealizationBoundaries.preimage U)),
  (RealizationBoundaries.completionHom U V f)
      (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of ↥(RealizationBoundaries.preimage U)) x) =
    ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of ↥(RealizationBoundaries.preimage V)) (f x)
```

Defining module: `RealizationBoundaries.CompletionReflection`. Transitive axioms: propext, Classical.choice, Quot.sound.

## completionHom_unique

The extension is unique among continuous additive maps with the eta equation. Density proves this assertion, identifying the constructed map as the induced one.

```lean
∀ (U V : Submodule ℚ RealizationBoundaries.TailSpace)
  (f : ↥(RealizationBoundaries.preimage U) →+ ↥(RealizationBoundaries.preimage V))
  (g :
    ↑(RealizationBoundaries.CanonicalCompletion U).toProfinite.toTop →ₜ+
      ↑(RealizationBoundaries.CanonicalCompletion V).toProfinite.toTop),
  (∀ (x : ↥(RealizationBoundaries.preimage U)),
      g (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of ↥(RealizationBoundaries.preimage U)) x) =
        ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of ↥(RealizationBoundaries.preimage V)) (f x)) →
    g = RealizationBoundaries.completionHom U V f
```

Defining module: `RealizationBoundaries.CompletionReflection`. Transitive axioms: propext, Classical.choice, Quot.sound.

## completionHom_coordinates

The formula holds on the entire actual completion after the checked comparison equivalences, not only on the dense subgroup.

```lean
∀ (U V : Submodule ℚ RealizationBoundaries.TailSpace)
  (f : ↥(RealizationBoundaries.preimage U) →+ ↥(RealizationBoundaries.preimage V))
  (x : ↑(RealizationBoundaries.CanonicalCompletion U).toProfinite.toTop),
  (RealizationBoundaries.profiniteCompletionEquiv V) ((RealizationBoundaries.completionHom U V f) x) =
    (RealizationBoundaries.diagonal (RealizationBoundaries.homDiagonal U V f))
      ((RealizationBoundaries.profiniteCompletionEquiv U) x)
```

Defining module: `RealizationBoundaries.CompletionReflection`. Transitive axioms: propext, Classical.choice, Quot.sound.

## completionHom_injective

Faithfulness is proved on hom sets between rational-preimage groups. This does not yet instantiate the global categorical statement for all residually finite groups.

```lean
∀ (U V : Submodule ℚ RealizationBoundaries.TailSpace), Function.Injective (RealizationBoundaries.completionHom U V)
```

Defining module: `RealizationBoundaries.CompletionReflection`. Transitive axioms: propext, Classical.choice, Quot.sound.

## completionHom_isomorphism_iff

The completed isomorphism is continuous in both directions and is pointwise equal to the constructed induced map. It is not merely existence of some isomorphism between the completion objects.

```lean
∀ (U V : Submodule ℚ RealizationBoundaries.TailSpace)
  (f : ↥(RealizationBoundaries.preimage U) →+ ↥(RealizationBoundaries.preimage V)),
  (∃ e,
      ∀ (x : ↑(RealizationBoundaries.CanonicalCompletion U).toProfinite.toTop),
        e x = (RealizationBoundaries.completionHom U V f) x) ↔
    ∀ (p : RealizationBoundaries.Prime), RealizationBoundaries.homDiagonal U V f p ≠ 0
```

Defining module: `RealizationBoundaries.CompletionReflection`. Transitive axioms: propext, Classical.choice, Quot.sound.

## paired_completion_reflects_isomorphisms

Both sides concern the same supplied f. This does not contradict nonisomorphic paired groups having isomorphic completions, nor the proper D -> G_A inclusion having invertible completion.

```lean
∀ (a b : ℕ → Bool) (f : ↥(RealizationBoundaries.pairedGroup a) →+ ↥(RealizationBoundaries.pairedGroup b)),
  (∃ e,
      ∀
        (x :
          ↑(RealizationBoundaries.CanonicalCompletion
                  (RealizationBoundaries.selectorLine (RealizationBoundaries.pairedSelector a))).toProfinite.toTop),
        e x =
          (RealizationBoundaries.completionHom
              (RealizationBoundaries.selectorLine (RealizationBoundaries.pairedSelector a))
              (RealizationBoundaries.selectorLine (RealizationBoundaries.pairedSelector b)) f)
            x) ↔
    ∃ e, e.toAddMonoidHom = f
```

Defining module: `RealizationBoundaries.CompletionReflection`. Transitive axioms: propext, Classical.choice, Quot.sound.

## finiteSupportEndomorphismRingEquiv

The actual finite-support subgroup D, rather than its completion or a finite-array proxy, has its full endomorphism ring identified with the product ring.

```lean
AddMonoid.End ↥RealizationBoundaries.finiteSupport ≃+* RealizationBoundaries.Ambient
```

Defining module: `RealizationBoundaries.DirectSumEndomorphisms`. Transitive axioms: propext, Classical.choice, Quot.sound.

## finiteSupport_endomorphism_preserves_zero

Every original D endomorphism preserves any zero coordinate. This is a checked prerequisite for the still-unformalized exact seed-rank theorem.

```lean
∀ (f : AddMonoid.End ↥RealizationBoundaries.finiteSupport) (x : ↥RealizationBoundaries.finiteSupport)
  (p : RealizationBoundaries.Prime), ↑x p = 0 → ↑(f x) p = 0
```

Defining module: `RealizationBoundaries.DirectSumEndomorphisms`. Transitive axioms: propext, Classical.choice, Quot.sound.
