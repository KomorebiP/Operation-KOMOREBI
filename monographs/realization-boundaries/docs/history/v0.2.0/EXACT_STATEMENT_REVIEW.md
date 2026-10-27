# Exact statement review — v0.2.0

Internal review of exported declaration types. This is not independent peer review. In particular, the completion comparison is constructed without a supplied completion isomorphism or a finite-target universal-property hypothesis.

## purePreimageOrderIso

```lean
Submodule ℚ RealizationBoundaries.TailSpace ≃o RealizationBoundaries.PureIntermediate
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## profiniteCompletionEquiv

```lean
(W : Submodule ℚ RealizationBoundaries.TailSpace) →
  ↑(RealizationBoundaries.CanonicalCompletion W).toProfinite.toTop ≃ₜ+ RealizationBoundaries.Ambient
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## profiniteCompletionEquiv_eta

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (x : ↥(RealizationBoundaries.preimage W)),
  (RealizationBoundaries.profiniteCompletionEquiv W)
      (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of ↥(RealizationBoundaries.preimage W)) x) =
    ↑x
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## fullProfiniteTopology_eq

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace), RealizationBoundaries.fullProfiniteTopology W = inferInstance
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## paired_countably_infinite

```lean
∀ (a : ℕ → Bool), Countable ↥(RealizationBoundaries.pairedGroup a) ∧ Infinite ↥(RealizationBoundaries.pairedGroup a)
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## preimage_countable_iff

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace), Countable ↥(RealizationBoundaries.preimage W) ↔ Countable ↥W
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## finiteSupportRestrictionEquiv

```lean
(W : Submodule ℚ RealizationBoundaries.TailSpace) →
  (F : Type u_1) →
    [inst : AddGroup F] →
      [Finite F] → (↥(RealizationBoundaries.preimage W) →+ F) ≃ (↥RealizationBoundaries.finiteSupport →+ F)
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## finiteSupportRestrictionEquiv_apply

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (F : Type u_1) [inst : AddGroup F] [inst_1 : Finite F]
  (f : ↥(RealizationBoundaries.preimage W) →+ F) (d : ↥RealizationBoundaries.finiteSupport),
  ((RealizationBoundaries.finiteSupportRestrictionEquiv W F) f) d = f ⟨↑d, ⋯⟩
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## finiteSupportToPairedCompletion

```lean
(a : ℕ → Bool) →
  ↑(ProfiniteAddGrp.ProfiniteCompletion.completion
            (AddGrpCat.of ↥RealizationBoundaries.finiteSupport)).toProfinite.toTop ≃ₜ+
    ↑(ProfiniteAddGrp.ProfiniteCompletion.completion
            (AddGrpCat.of ↥(RealizationBoundaries.pairedGroup a))).toProfinite.toTop
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## finiteSupportToPairedCompletion_eta

```lean
∀ (a : ℕ → Bool) (d : ↥RealizationBoundaries.finiteSupport),
  (RealizationBoundaries.finiteSupportToPairedCompletion a)
      (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of ↥RealizationBoundaries.finiteSupport) d) =
    ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of ↥(RealizationBoundaries.pairedGroup a)) ⟨↑d, ⋯⟩
```

Transitive axioms: propext, Classical.choice, Quot.sound.

## finiteSupport_inclusion_not_surjective

```lean
∀ (a : ℕ → Bool), ¬Function.Surjective fun d => ⟨↑d, ⋯⟩
```

Transitive axioms: propext, Classical.choice, Quot.sound.
