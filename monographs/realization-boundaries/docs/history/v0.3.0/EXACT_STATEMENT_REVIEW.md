# Exact statement review — v0.3.0

Internal inspection of actual Lean-exported types and axiom lists. This is not external peer review. All inherited production modules remain unchanged.

## selector_tail_signature

The input is an actual selector-group element outside D. The conclusion retains an explicit finite exception set. No infinite-order assumption is silently dropped.

```lean
∀ (S : Set RealizationBoundaries.Prime) (x : ↥(RealizationBoundaries.selectorGroup S)),
  ↑x ∉ RealizationBoundaries.finiteSupport → ∃ E, E.Finite ∧ ∀ p ∉ E, RealizationBoundaries.HasPrimeRoot x p ↔ p ∉ S
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## finite_disagreement_of_nontorsion_image

The homomorphism is arbitrary and additive. No diagonal, continuity, or quotient-scalar formula appears as a hypothesis. The conclusion follows from root preservation.

```lean
∀ (a b : ℕ → Bool) (f : ↥(RealizationBoundaries.pairedGroup a) →+ ↥(RealizationBoundaries.pairedGroup b))
  (x : ↥(RealizationBoundaries.pairedGroup a)), ↑(f x) ∉ RealizationBoundaries.finiteSupport → {n | a n ≠ b n}.Finite
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## pairedGroup_isomorphic_iff

Nonempty actual AddEquiv is equivalent to finite bit disagreement, not literal equality.

```lean
∀ (a b : ℕ → Bool),
  Nonempty (↥(RealizationBoundaries.pairedGroup a) ≃+ ↥(RealizationBoundaries.pairedGroup b)) ↔ {n | a n ≠ b n}.Finite
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## pairedGroup_eq_of_finite_disagreement

Finite differences give equality of the actual subgroups, stronger than abstract isomorphism.

```lean
∀ (a b : ℕ → Bool), {n | a n ≠ b n}.Finite → RealizationBoundaries.pairedGroup a = RealizationBoundaries.pairedGroup b
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## pairedGroup_marked_isomorphic_iff

The equation carrying the original marked element to the target marked element is present and is what upgrades finite agreement to literal equality.

```lean
∀ (a b : ℕ → Bool),
  (∃ e,
      e (RealizationBoundaries.markedElement (RealizationBoundaries.pairedSelector a)) =
        RealizationBoundaries.markedElement (RealizationBoundaries.pairedSelector b)) ↔
    a = b
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## hom_image_torsion

Each image has a positive integer annihilator. Neither zero image nor uniformly bounded exponent is claimed.

```lean
∀ (a b : ℕ → Bool),
  {n | a n ≠ b n}.Infinite →
    ∀ (f : ↥(RealizationBoundaries.pairedGroup a) →+ ↥(RealizationBoundaries.pairedGroup b))
      (x : ↥(RealizationBoundaries.pairedGroup a)), ∃ m, 0 < m ∧ m • f x = 0
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## pairedGroup_embeds_iff

Injectivity of an actual additive homomorphism exists exactly at finite disagreement.

```lean
∀ (a b : ℕ → Bool), (∃ f, Function.Injective ⇑f) ↔ {n | a n ≠ b n}.Finite
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## pairedGroup_surjects_iff

The analogous assertion uses actual surjectivity, not density.

```lean
∀ (a b : ℕ → Bool), (∃ f, Function.Surjective ⇑f) ↔ {n | a n ≠ b n}.Finite
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## normalFormTransportEquiv_apply

The actual additive equivalence is identified with the explicit finite-correction formula. The normal-form type has the inherited twisted group law.

```lean
∀ (a b : ℕ → Bool) (h : {n | a n ≠ b n}.Finite)
  (x : RealizationBoundaries.NormalForm (RealizationBoundaries.pairedSelector a)),
  (RealizationBoundaries.normalFormTransportEquiv a b h) x = RealizationBoundaries.normalFormTransport a b h x
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## normalFormTransport_realization

Transport fixes the full ambient vector, not only its quotient class.

```lean
∀ (a b : ℕ → Bool) (h : {n | a n ≠ b n}.Finite)
  (x : RealizationBoundaries.NormalForm (RealizationBoundaries.pairedSelector a)),
  ↑((RealizationBoundaries.NormalForm.realizationEquiv ⋯) (RealizationBoundaries.normalFormTransport a b h x)) =
    ↑((RealizationBoundaries.NormalForm.realizationEquiv ⋯) x)
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## completion_object_counterexample

The completion objects are the canonical all-finite-index-quotient completions from the prior tranche. The original groups are separately proved nonisomorphic.

```lean
∃ a b,
  Nonempty
      (↑(RealizationBoundaries.CanonicalCompletion
                (RealizationBoundaries.selectorLine (RealizationBoundaries.pairedSelector a))).toProfinite.toTop ≃ₜ+
        ↑(RealizationBoundaries.CanonicalCompletion
                (RealizationBoundaries.selectorLine (RealizationBoundaries.pairedSelector b))).toProfinite.toTop) ∧
    ¬Nonempty (↥(RealizationBoundaries.pairedGroup a) ≃+ ↥(RealizationBoundaries.pairedGroup b))
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## no_completion_invariant_reconstruction

An arbitrary group-valued assignment and its completion-isomorphism invariance are explicit. There is no computability assumption. This is the completion-interface theorem, not an asserted formal Pro-category interface.

```lean
∀ (R : (ℕ → Bool) → Type u_1) [inst : (a : ℕ → Bool) → AddGroup (R a)],
  (∀ (a b : ℕ → Bool),
      Nonempty
          (↑(RealizationBoundaries.CanonicalCompletion
                    (RealizationBoundaries.selectorLine (RealizationBoundaries.pairedSelector a))).toProfinite.toTop ≃ₜ+
            ↑(RealizationBoundaries.CanonicalCompletion
                    (RealizationBoundaries.selectorLine (RealizationBoundaries.pairedSelector b))).toProfinite.toTop) →
        Nonempty (R a ≃+ R b)) →
    (∀ (a : ℕ → Bool), Nonempty (R a ≃+ ↥(RealizationBoundaries.pairedGroup a))) → False
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## no_lift_of_commonCompletionEquiv

The no-lift statement uses compatibility on every canonical eta image. It does not assert the opposite of the pending reflection theorem for an already supplied homomorphism.

```lean
∀ (a b : ℕ → Bool),
  {n | a n ≠ b n}.Infinite →
    ¬∃ f,
        ∀ (x : ↥(RealizationBoundaries.pairedGroup a)),
          (RealizationBoundaries.pairedCommonCompletionEquiv a b)
              (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of ↥(RealizationBoundaries.pairedGroup a)) x) =
            ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of ↥(RealizationBoundaries.pairedGroup b)) (f x)
```

Transitive axioms: propext, Classical.choice, Quot.sound.
