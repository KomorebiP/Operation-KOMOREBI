import PaperXII.AdicMatrixGroups

/-! Continuous companion reconstruction into the actual adic matrix group.
Finite conditions are predicates on continuous quotient representations, and
the comparison with representations over the complete ring is constructed. -/
set_option autoImplicit false
namespace PaperXII.AdicCompanions

open ContinuousMonoidHom Matrix AdicMatrixGroups

variable {R Γ ι : Type} [CommRing R] [Group Γ] [TopologicalSpace Γ]
    [Fintype ι] [DecidableEq ι] (I : Ideal R)

/-- Continuous representations into GL over R with the specified I-adic topology. -/
abbrev AdicRep :=
  let _ : TopologicalSpace R := I.adicTopology
  Γ →ₜ* GL ι R

/-- The actual finite reduction of a continuous adic representation. -/
def reduceRep (n : ℕ) (ρ : AdicRep (Γ := Γ) (ι := ι) I) : Γ →ₜ* GL ι (Coeff I n) := by
  let _ : TopologicalSpace R := I.adicTopology
  exact
    { __ := (AdicMatrixGroups.reduce I n).comp ρ.toMonoidHom
      continuous_toFun := (quotientMap_continuous I n).generalLinearGroup_map.comp ρ.continuous }

/-- Integral realizations satisfying every declared finite condition. -/
def AdicRealization (A : ∀ n, (Γ →ₜ* GL ι (Coeff I n)) → Prop) :=
  {ρ : AdicRep (Γ := Γ) (ι := ι) I // ∀ n, A n (reduceRep I n ρ)}

/-- Use the proved group homeomorphism to realize a completed branch over R. -/
noncomputable def realize [IsAdicComplete I R]
    (A : ∀ n, (Γ →ₜ* GL ι (Coeff I n)) → Prop)
    (c : InverseLimitRepresentations.Complete (step I) A) : AdicRep (Γ := Γ) (ι := ι) I := by
  let _ : TopologicalSpace R := I.adicTopology
  exact
    { __ := (lift I).comp c.val.toMonoidHom
      continuous_toFun := (lift_continuous I).comp c.val.continuous }

/-- Integral realization has exactly the finite reductions of the completed branch. -/
theorem realize_reduces [IsAdicComplete I R]
    (A : ∀ n, (Γ →ₜ* GL ι (Coeff I n)) → Prop)
    (c : InverseLimitRepresentations.Complete (step I) A) (n : ℕ) :
    reduceRep I n (realize I A c) =
      (InverseLimitRepresentations.coordinate (G := fun n ↦ GL ι (Coeff I n))
        (step (ι := ι) I) n).comp c.val := by
  let _ : TopologicalSpace R := I.adicTopology
  apply ContinuousMonoidHom.ext
  intro g
  exact reduce_lift I (c.val g) n

/-- All finite admissibility predicates survive the actual adic reconstruction. -/
theorem realize_admissible [IsAdicComplete I R]
    (A : ∀ n, (Γ →ₜ* GL ι (Coeff I n)) → Prop)
    (c : InverseLimitRepresentations.Complete (step I) A) (n : ℕ) :
    A n (reduceRep I n (realize I A c)) := by
  rw [realize_reduces]
  exact c.property n

/-- Reconstruction as a map to the actual integral realization space. -/
noncomputable def fromComplete [IsAdicComplete I R]
    (A : ∀ n, (Γ →ₜ* GL ι (Coeff I n)) → Prop)
    (c : InverseLimitRepresentations.Complete (step I) A) : AdicRealization I A :=
  ⟨realize I A c, realize_admissible I A c⟩

/-- An integral realization determines its continuous representation in the limit group. -/
def toComplete (A : ∀ n, (Γ →ₜ* GL ι (Coeff I n)) → Prop)
    (ρ : AdicRealization I A) : InverseLimitRepresentations.Complete (step I) A := by
  let _ : TopologicalSpace R := I.adicTopology
  exact ⟨{ __ := (toLimit I).comp ρ.val.toMonoidHom
           continuous_toFun := (toLimit_continuous I).comp ρ.val.continuous },
    fun n ↦ ρ.property n⟩

/-- Recovering the integral realization after reduction gives the original map. -/
theorem fromComplete_toComplete [IsAdicComplete I R]
    (A : ∀ n, (Γ →ₜ* GL ι (Coeff I n)) → Prop) (ρ : AdicRealization I A) :
    fromComplete I A (toComplete I A ρ) = ρ := by
  let _ : TopologicalSpace R := I.adicTopology
  apply Subtype.ext
  apply ContinuousMonoidHom.ext
  intro g
  exact lift_toLimit I (ρ.val g)

/-- Reducing the integral reconstruction recovers the original completed branch. -/
theorem toComplete_fromComplete [IsAdicComplete I R]
    (A : ∀ n, (Γ →ₜ* GL ι (Coeff I n)) → Prop)
    (c : InverseLimitRepresentations.Complete (step I) A) :
    toComplete I A (fromComplete I A c) = c := by
  let _ : TopologicalSpace R := I.adicTopology
  apply Subtype.ext
  apply ContinuousMonoidHom.ext
  intro g
  exact toLimit_lift I (c.val g)

/-- The realization comparison is an actual equivalence, not an assumed effectivity map. -/
noncomputable def completionEquiv [IsAdicComplete I R]
    (A : ∀ n, (Γ →ₜ* GL ι (Coeff I n)) → Prop) :
    InverseLimitRepresentations.Complete (step I) A ≃ AdicRealization I A where
  toFun := fromComplete I A
  invFun := toComplete I A
  left_inv := toComplete_fromComplete I A
  right_inv := fromComplete_toComplete I A

/-- Finite occupied forests of continuous matrix representations have actual adic realizations. -/
theorem exists_adic_realization [IsAdicComplete I R]
    (A : ∀ n, (Γ →ₜ* GL ι (Coeff I n)) → Prop)
    (hA : ∀ n ρ, A (n + 1) ρ → A n ((step I n).comp ρ))
    [∀ n, Finite {ρ : Γ →ₜ* GL ι (Coeff I n) // A n ρ}]
    (hne : ∀ n, Nonempty {ρ : Γ →ₜ* GL ι (Coeff I n) // A n ρ}) :
    Nonempty (AdicRealization I A) := by
  obtain ⟨c⟩ := InverseLimitRepresentations.exists_complete (step I) A hA hne
  exact ⟨fromComplete I A c⟩

/-- The residual representation is retained at the first positive precision. -/
theorem exists_adic_realization_with_root [IsAdicComplete I R]
    (A : ∀ n, (Γ →ₜ* GL ι (Coeff I n)) → Prop)
    (hA : ∀ n ρ, A (n + 1) ρ → A n ((step I n).comp ρ))
    [∀ n, Finite {ρ : Γ →ₜ* GL ι (Coeff I n) // A n ρ}]
    (hne : ∀ n, Nonempty {ρ : Γ →ₜ* GL ι (Coeff I n) // A n ρ})
    (root : Γ →ₜ* GL ι (Coeff I 1)) (hroot : ∀ ρ, A 1 ρ → ρ = root) :
    ∃ ρ : AdicRealization I A, reduceRep I 1 ρ.val = root := by
  obtain ⟨ρ⟩ := exists_adic_realization I A hA hne
  exact ⟨ρ, hroot _ (ρ.property 1)⟩

/-- Separatedness alone determines an integral representation from all its finite reductions. -/
theorem adicRep_ext [IsHausdorff I R] (ρ σ : AdicRep (Γ := Γ) (ι := ι) I)
    (h : ∀ n, reduceRep I n ρ = reduceRep I n σ) : ρ = σ := by
  let _ : TopologicalSpace R := I.adicTopology
  apply ContinuousMonoidHom.ext
  intro g
  apply ext_of_reductions I
  intro n
  exact DFunLike.congr_fun (h n) g

end PaperXII.AdicCompanions
