import PaperXII.ClassCompanions

/-! Frobenius polynomials and inertia triviality pass from conjugacy-class
forests to actual continuous adic and local-field representations.
Every finite-level specification below starts at positive precision. -/
set_option autoImplicit false
namespace PaperXII.ClassSpines

open ContinuousMonoidHom Matrix
open AdicMatrixGroups AdicCompanions ContinuousClasses ClassCompanions AdicSpines
open PaperX.ClassInvariants

variable {R Γ ι : Type} [CommRing R] [Group Γ] [TopologicalSpace Γ]
    [Fintype ι] [DecidableEq ι] (I : Ideal R)

/-- Entire prescribed polynomials survive class completion from positive precisions. -/
theorem class_spine_preserved [IsHausdorff I R]
    (C : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n → Prop)
    (ρ : AdicRealization I (Framed I C))
    {Ω : Type} (frob : Ω → Γ) (good : Ω → Prop) (P : Ω → Polynomial R)
    (hspec : ∀ n, 0 < n → ∀ c, C n c → ∀ v, good v →
      classCharpoly c (frob v) = (P v).map (quotientMap I n)) :
    ∀ v, good v → (ρ.val (frob v)).val.charpoly = P v := by
  apply spine_preserved I (Framed I C) ρ frob good P
  intro n σ hσ v hv
  cases n with
  | zero =>
    let _ := coeff_zero_subsingleton I
    exact Subsingleton.elim _ _
  | succ n => exact hspec (n + 1) (Nat.succ_pos n) (classOfRep σ) hσ v hv

/-- Positive-precision class triviality gives actual trivial inertia action. -/
theorem class_unramified_preserved [IsHausdorff I R]
    (C : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n → Prop)
    (ρ : AdicRealization I (Framed I C)) (H : Subgroup Γ)
    (hspec : ∀ n, 0 < n → ∀ c, C n c → ClassTrivial H c) :
    ∀ g, g ∈ H → ρ.val g = 1 := by
  apply unramified_preserved I (Framed I C) ρ H
  intro n σ hσ
  cases n with
  | zero =>
    let _ := coeff_zero_subsingleton I
    intro g _
    exact Subsingleton.elim _ _
  | succ n =>
    exact (classTrivial_classOfRep H σ).mp
      (hspec (n + 1) (Nat.succ_pos n) (classOfRep σ) hσ)

/-- A finite occupied class forest gives a continuous integral realization with
its residual class, complete Frobenius polynomials, and declared inertia triviality. -/
theorem class_realization_with_spine [IsAdicComplete I R]
    (hI : I.FG) [Finite (R ⧸ I)]
    (C : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n → Prop)
    (hC : ∀ n c, C (n + 1) c → C n (classStep I n c))
    (finiteC : ∀ n, 0 < n → Finite {c // C n c})
    (hc : ∀ n, 0 < n → ∀ c, C n c → ClassContinuous c)
    (hne : ∀ n, 0 < n → ∃ c, C n c)
    (root : LevelClass (Γ := Γ) (ι := ι) I 1) (hroot : ∀ c, C 1 c → c = root)
    {Ω : Type} (frob : Ω → Γ) (good : Ω → Prop) (P : Ω → Polynomial R)
    (hspec : ∀ n, 0 < n → ∀ c, C n c → ∀ v, good v →
      classCharpoly c (frob v) = (P v).map (quotientMap I n))
    (H : Subgroup Γ) (hH : ∀ n, 0 < n → ∀ c, C n c → ClassTrivial H c) :
    ∃ ρ : AdicRealization I (Framed I C),
      classOfRep (reduceRep I 1 ρ.val) = root ∧
      (∀ v, good v → (ρ.val (frob v)).val.charpoly = P v) ∧
      ∀ g, g ∈ H → ρ.val g = 1 := by
  obtain ⟨ρ⟩ := exists_class_realization_positive I hI C hC finiteC hc hne
  exact ⟨ρ, hroot _ (ρ.property 1),
    class_spine_preserved I C ρ frob good P hspec,
    class_unramified_preserved I C ρ H hH⟩

/-- Simultaneous continuous local-field realizations from positive finite class forests.
Coherent frames are constructed. Local integrality and coefficient-map continuity
remain explicit hypotheses, as do finiteness and occupancy of admissible classes. -/
theorem simultaneous_class_spine
    {Λ Ω L : Type} [Field L] (O K : Λ → Type)
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
    (hH : ∀ l n, 0 < n → ∀ c, C l n c → ClassTrivial (H l) c) :
    ∃ ρ : ∀ l, AdicRealization (J l) (Framed (J l) (C l)),
      (∀ l, classOfRep (reduceRep (J l) 1 (ρ l).val) = root l) ∧
      (∀ l v, good l v →
        (fieldRep (J l) (inc l) (hinc l) (ρ l).val (frob v)).val.charpoly =
          (P v).map (emb l)) ∧
      ∀ l g, g ∈ H l → fieldRep (J l) (inc l) (hinc l) (ρ l).val g = 1 := by
  classical
  let ρ : ∀ l, AdicRealization (J l) (Framed (J l) (C l)) := fun l ↦
    Classical.choice (exists_class_realization_positive (J l) (hJ l) (C l)
      (hC l) (finiteC l) (hc l) (hne l))
  refine ⟨ρ, fun l ↦ hroot l _ ((ρ l).property 1), ?_, ?_⟩
  · intro l v hv
    exact fieldRep_charpoly (J l) (inc l) (hinc l) (emb l) (ρ l).val (frob v)
      (localP l v) (P v)
      (class_spine_preserved (J l) (C l) (ρ l) frob (good l) (localP l) (hspec l) v hv)
      (hmatch l v hv)
  · intro l
    exact fieldRep_unramified (J l) (inc l) (hinc l) (ρ l).val (H l)
      (class_unramified_preserved (J l) (C l) (ρ l) (H l) (hH l))

end PaperXII.ClassSpines
