import PaperXII.ContinuousClasses
import Mathlib.RingTheory.Ideal.Quotient.Index

/-! Continuous companion completion from actual conjugacy classes.
Finite class fibers let compactness choose strictly compatible frames.
There is no assumption that conjugating matrices lift through reduction. -/
set_option autoImplicit false
namespace PaperXII.ClassCompanions

open ContinuousMonoidHom Matrix
open AdicMatrixGroups AdicCompanions ContinuousClasses
open PaperX.RepresentationClasses PaperX.ClassInvariants

variable {R Γ ι : Type} [CommRing R] [Group Γ] [TopologicalSpace Γ]
    [Fintype ι] [DecidableEq ι] (I : Ideal R)

/-- Actual conjugacy classes at adic precision n. -/
abbrev LevelClass (n : ℕ) := ClassRep (Coeff I n) Γ ι

/-- Adjacent reduction of actual conjugacy classes. -/
def classStep (n : ℕ) : LevelClass (Γ := Γ) (ι := ι) I (n + 1) →
    LevelClass (Γ := Γ) (ι := ι) I n :=
  changeClassCoefficients (coefficientStep I n)

/-- Taking classes commutes with the actual continuous reduction map. -/
theorem classOfRep_step (n : ℕ) (ρ : Γ →ₜ* GL ι (Coeff I (n + 1))) :
    classOfRep ((step I n).comp ρ) = classStep I n (classOfRep ρ) := rfl

/-- Pull back the class predicate to actual continuous frames. -/
def Framed (C : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n → Prop)
    (n : ℕ) (ρ : Γ →ₜ* GL ι (Coeff I n)) : Prop := C n (classOfRep ρ)

/-- Class admissibility under reduction gives genuine frame admissibility. -/
theorem framed_downward (C : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n → Prop)
    (hC : ∀ n c, C (n + 1) c → C n (classStep I n c)) :
    ∀ n ρ, Framed I C (n + 1) ρ → Framed I C n ((step I n).comp ρ) := by
  intro n ρ hρ
  exact hC n (classOfRep ρ) hρ

/-- Finite coefficients and finitely many classes give finite admissible frame sets. -/
theorem framed_finite (C : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n → Prop) (n : ℕ)
    [Finite (Coeff I n)] [Finite {c // C n c}] :
    Finite {ρ : Γ →ₜ* GL ι (Coeff I n) // Framed I C n ρ} :=
  finite_allowed_frames (C n)

/-- One admissible continuous class gives one actual admissible continuous frame. -/
theorem framed_nonempty (C : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n → Prop) (n : ℕ)
    (hc : ∀ c, C n c → ClassContinuous c) (hne : ∃ c, C n c) :
    Nonempty {ρ : Γ →ₜ* GL ι (Coeff I n) // Framed I C n ρ} := by
  obtain ⟨c, hC⟩ := hne
  obtain ⟨ρ, hρ⟩ := exists_continuous_representative c (hc c hC)
  refine ⟨ρ, ?_⟩
  change C n (classOfRep ρ)
  rw [hρ]
  exact hC

/-- Finite occupied continuous class levels give a strictly compatible completion.
No adic completeness is required for this frame-selection step. -/
theorem exists_class_complete
    (C : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n → Prop)
    (hC : ∀ n c, C (n + 1) c → C n (classStep I n c))
    [∀ n, Finite (Coeff I n)] [∀ n, Finite {c // C n c}]
    (hc : ∀ n c, C n c → ClassContinuous c) (hne : ∀ n, ∃ c, C n c) :
    Nonempty (InverseLimitRepresentations.Complete (step I) (Framed I C)) := by
  let _ : ∀ n, Finite {ρ : Γ →ₜ* GL ι (Coeff I n) // Framed I C n ρ} :=
    fun n ↦ framed_finite I C n
  exact InverseLimitRepresentations.exists_complete (step I) (Framed I C)
    (framed_downward I C hC) (fun n ↦ framed_nonempty I C n (hc n) (hne n))

/-- Actual continuous integral representations realize finite occupied class forests. -/
theorem exists_class_realization [IsAdicComplete I R]
    (C : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n → Prop)
    (hC : ∀ n c, C (n + 1) c → C n (classStep I n c))
    [∀ n, Finite (Coeff I n)] [∀ n, Finite {c // C n c}]
    (hc : ∀ n c, C n c → ClassContinuous c) (hne : ∀ n, ∃ c, C n c) :
    Nonempty (AdicRealization I (Framed I C)) := by
  obtain ⟨c⟩ := exists_class_complete I C hC hc hne
  exact ⟨fromComplete I (Framed I C) c⟩

/-- Fixing a compatible class branch yields a completion over exactly those classes. -/
theorem exists_prescribed_complete
    [∀ n, Finite (Coeff I n)] (c : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n)
    (hcompat : ∀ n, classStep I n (c (n + 1)) = c n)
    (hc : ∀ n, ClassContinuous (c n)) :
    Nonempty (InverseLimitRepresentations.Complete (step I)
      (Framed I (fun n d ↦ d = c n))) := by
  let _ : ∀ n, Subsingleton {d // d = c n} :=
    fun _ ↦ ⟨fun a b ↦ Subtype.ext (a.property.trans b.property.symm)⟩
  apply exists_class_complete I (fun n d ↦ d = c n)
  · intro n d hd
    rw [hd]
    exact hcompat n
  · intro n d hd
    rw [hd]
    exact hc n
  · intro n
    exact ⟨c n, rfl⟩

/-- Every prescribed continuous class branch has strictly compatible continuous frames.
Neither completeness nor surjectivity of transition maps is assumed. -/
theorem prescribed_branch_representatives
    [∀ n, Finite (Coeff I n)] (c : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n)
    (hcompat : ∀ n, classStep I n (c (n + 1)) = c n)
    (hc : ∀ n, ClassContinuous (c n)) :
    ∃ ρ : ∀ n, Γ →ₜ* GL ι (Coeff I n),
      (∀ n, (step I n).comp (ρ (n + 1)) = ρ n) ∧
      ∀ n, classOfRep (ρ n) = c n := by
  obtain ⟨s⟩ := exists_prescribed_complete I c hcompat hc
  let hC : ∀ n d, d = c (n + 1) → classStep I n d = c n := by
    intro n d hd
    rw [hd]
    exact hcompat n
  let b := InverseLimitRepresentations.toBranch (step I)
    (Framed I (fun n d ↦ d = c n))
    (framed_downward I _ hC) s
  exact ⟨fun n ↦ (b.value n).val,
    fun n ↦ congrArg Subtype.val (b.compatible n), fun n ↦ (b.value n).property⟩

/-- A prescribed compatible class branch is realized by an actual continuous adic map. -/
theorem prescribed_branch_adic [IsAdicComplete I R]
    [∀ n, Finite (Coeff I n)] (c : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n)
    (hcompat : ∀ n, classStep I n (c (n + 1)) = c n)
    (hc : ∀ n, ClassContinuous (c n)) :
    ∃ ρ : AdicRep (Γ := Γ) (ι := ι) I, ∀ n, classOfRep (reduceRep I n ρ) = c n := by
  obtain ⟨s⟩ := exists_prescribed_complete I c hcompat hc
  exact ⟨realize I (Framed I (fun n d ↦ d = c n)) s,
    realize_admissible I (Framed I (fun n d ↦ d = c n)) s⟩

/-- The declared residual conjugacy class is retained at precision one. -/
theorem exists_class_realization_with_root [IsAdicComplete I R]
    (C : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n → Prop)
    (hC : ∀ n c, C (n + 1) c → C n (classStep I n c))
    [∀ n, Finite (Coeff I n)] [∀ n, Finite {c // C n c}]
    (hc : ∀ n c, C n c → ClassContinuous c) (hne : ∀ n, ∃ c, C n c)
    (root : LevelClass (Γ := Γ) (ι := ι) I 1) (hroot : ∀ c, C 1 c → c = root) :
    ∃ ρ : AdicRealization I (Framed I C), classOfRep (reduceRep I 1 ρ.val) = root := by
  obtain ⟨ρ⟩ := exists_class_realization I C hC hc hne
  exact ⟨ρ, hroot _ (ρ.property 1)⟩

/-- A finitely generated ideal with finite residue gives finite coefficients at every precision. -/
theorem finite_coefficients (hI : I.FG) [Finite (R ⧸ I)] (n : ℕ) :
    Finite (Coeff I n) := Ideal.finite_quotient_pow hI n

/-- The auxiliary precision-zero coefficient ring is trivial. -/
theorem coeff_zero_subsingleton : Subsingleton (Coeff I 0) := by
  change Subsingleton (R ⧸ I ^ 0)
  simp only [pow_zero, Ideal.one_eq_top]
  infer_instance

omit [TopologicalSpace Γ] in
/-- Precision zero requires no separate finiteness hypothesis on classes. -/
theorem finite_zero_class_level (C : LevelClass (Γ := Γ) (ι := ι) I 0 → Prop) :
    Finite {c // C c} := by
  let _ := coeff_zero_subsingleton I
  let _ : Subsingleton (PaperX.RepresentationLimits.MatrixRep (Coeff I 0) Γ ι) :=
    ⟨fun a b ↦ by ext g i j; exact Subsingleton.elim _ _⟩
  let _ : Subsingleton (LevelClass (Γ := Γ) (ι := ι) I 0) := by
    unfold LevelClass ClassRep
    infer_instance
  infer_instance

/-- Precision-zero classes are automatically continuous. -/
theorem zero_class_continuous (c : LevelClass (Γ := Γ) (ι := ι) I 0) :
    ClassContinuous c := by
  let _ := coeff_zero_subsingleton I
  obtain ⟨ρ, rfl⟩ := classOf_surjective c
  intro i j g
  exact Filter.Eventually.of_forall (fun _ ↦ Subsingleton.elim _ _)

/-- Positive precision data suffice, matching the manuscript's forest starting at level one. -/
theorem exists_class_realization_positive [IsAdicComplete I R]
    (hI : I.FG) [Finite (R ⧸ I)]
    (C : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n → Prop)
    (hC : ∀ n c, C (n + 1) c → C n (classStep I n c))
    (finiteC : ∀ n, 0 < n → Finite {c // C n c})
    (hc : ∀ n, 0 < n → ∀ c, C n c → ClassContinuous c)
    (hne : ∀ n, 0 < n → ∃ c, C n c) :
    Nonempty (AdicRealization I (Framed I C)) := by
  let _ : ∀ n, Finite (Coeff I n) := finite_coefficients I hI
  let _ : ∀ n, Finite {c // C n c} := by
    intro n
    cases n with
    | zero => exact finite_zero_class_level I (C 0)
    | succ n => exact finiteC (n + 1) (Nat.succ_pos n)
  apply exists_class_realization I C hC
  · intro n c h
    cases n with
    | zero => exact zero_class_continuous I c
    | succ n => exact hc (n + 1) (Nat.succ_pos n) c h
  · intro n
    cases n with
    | zero =>
      obtain ⟨c, h⟩ := hne 1 (by decide)
      exact ⟨classStep I 0 c, hC 0 c h⟩
    | succ n => exact hne (n + 1) (Nat.succ_pos n)

end PaperXII.ClassCompanions
