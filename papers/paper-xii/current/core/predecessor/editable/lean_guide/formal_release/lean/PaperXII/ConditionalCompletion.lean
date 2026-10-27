import PaperXII.AdicLocalConditions

/-! Exact conditional completion statement for the amended Paper XII 10.5.
All arithmetic existence, continuity, integrality, and finite local equations
are explicit inputs; the completion and quotient factors are constructed. -/
set_option autoImplicit false
namespace PaperXII.ConditionalCompletion

open ContinuousMonoidHom Matrix
open AdicMatrixGroups AdicCompanions ContinuousClasses ClassCompanions AdicSpines
open AdicLocalConditions LocalQuotients PaperX.ClassInvariants

variable {Γ ι : Type} [Group Γ] [TopologicalSpace Γ] [Fintype ι] [DecidableEq ι]

/-- Positive finite class forests realize the prescribed common spine and every
declared polynomial quotient condition on the actual representation entries. -/
theorem simultaneous_companion_completion
    {Λ Ω L V : Type} [Field L] (O K : Λ → Type)
    [∀ l, CommRing (O l)] [∀ l, Field (K l)] [∀ l, TopologicalSpace (K l)]
    (J : ∀ l, Ideal (O l)) [∀ l, IsAdicComplete (J l) (O l)]
    (hJ : ∀ l, (J l).FG) [∀ l, Finite (O l ⧸ J l)]
    (C : ∀ l n, LevelClass (Γ := Γ) (ι := ι) (J l) n → Prop)
    (hC : ∀ l n c, C l (n + 1) c → C l n (classStep (J l) n c))
    (finiteC : ∀ l n, 0 < n → Finite {c // C l n c})
    (hc : ∀ l n, 0 < n → ∀ c, C l n c → ClassContinuous c)
    (hne : ∀ l n, 0 < n → ∃ c, C l n c)
    (root : ∀ l, LevelClass (Γ := Γ) (ι := ι) (J l) 1)
    (hroot : ∀ l c, C l 1 c → c = root l)
    (inc : ∀ l, O l →+* K l)
    (hinc : ∀ l, @Continuous (O l) (K l) (J l).adicTopology inferInstance (inc l))
    (emb : ∀ l, L →+* K l) (frob : Ω → Γ) (good : Λ → Ω → Prop)
    (P : Ω → Polynomial L) (localP : ∀ l, Ω → Polynomial (O l))
    (hmatch : ∀ l v, good l v → (localP l v).map (inc l) = (P v).map (emb l))
    (hspec : ∀ l n, 0 < n → ∀ c, C l n c → ∀ v, good l v →
      classCharpoly c (frob v) = (localP l v).map (quotientMap (J l) n))
    (H : Λ → Subgroup Γ)
    (hH : ∀ l n, 0 < n → ∀ c, C l n c → ClassTrivial (H l) c)
    (relations : ∀ l, V → Ideal (MvPolynomial (Coordinates (Γ := Γ) (ι := ι)) (O l)))
    (hrelations : ∀ l v n, 0 < n → ∀ σ, Framed (J l) (C l) n σ →
      relations l v ≤ RingHom.ker (finitePoint (J l) n σ)) :
    ∃ ρ : ∀ l, AdicRealization (J l) (Framed (J l) (C l)),
      (∀ l, classOfRep (reduceRep (J l) 1 (ρ l).val) = root l) ∧
      (∀ l v, good l v →
        (fieldRep (J l) (inc l) (hinc l) (ρ l).val (frob v)).val.charpoly =
          (P v).map (emb l)) ∧
      (∀ l g, g ∈ H l → fieldRep (J l) (inc l) (hinc l) (ρ l).val g = 1) ∧
      ∀ l v, Factors (relations l v) (point (J l) (ρ l).val) := by
  obtain ⟨ρ, hrootρ, hpolyρ, hHρ⟩ := ClassSpines.simultaneous_class_spine
    O K J hJ C hC finiteC hc hne root hroot inc hinc emb frob good P localP
    hmatch hspec H hH
  exact ⟨ρ, hrootρ, hpolyρ, hHρ, fun l v ↦
    class_condition_preserved (J l) (C l) (relations l v) (ρ l) (hrelations l v)⟩

end PaperXII.ConditionalCompletion
