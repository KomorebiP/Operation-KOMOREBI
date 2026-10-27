import PaperX.RepresentationClasses
import PaperX.FiniteFiberBranches
import PaperX.CompletionAssembly
import Mathlib.RingTheory.Ideal.Quotient.Index

/-! Complete finite-level representation conditions stated on actual conjugacy
classes. Finiteness of coefficients controls all frames in each class. -/
set_option autoImplicit false
namespace PaperX.ClassCompletion
open PaperX.RepresentationLimits PaperX.RepresentationTopology PaperX.RepresentationForests
open PaperX.RepresentationClasses PaperX.CompletionAssembly
variable {R G ι : Type} [CommRing R] [Group G] [Fintype ι] [DecidableEq ι]
variable (I : Ideal R)

structure ClassConditions where
  allowed : (k : ℕ) → ClassRep (R ⧸ I^k) G ι → Prop
  downward : ∀ {j k} (h : j ≤ k) c, allowed k c → allowed j (transitionClass I h c)

def framed (C : ClassConditions (G := G) (ι := ι) I) : Conditions (G := G) (ι := ι) I where
  allowed k ρ := C.allowed k (classOf ρ)
  downward h ρ hρ := C.downward h (classOf ρ) hρ

theorem framed_nonempty_iff (C : ClassConditions (G := G) (ι := ι) I) (k : ℕ) :
    (∃ ρ, (framed I C).allowed k ρ) ↔ ∃ c, C.allowed k c := by
  constructor
  · rintro ⟨ρ, hρ⟩
    exact ⟨classOf ρ, hρ⟩
  · rintro ⟨c, hc⟩
    obtain ⟨ρ, rfl⟩ := classOf_surjective c
    exact ⟨ρ, hc⟩

theorem framed_finite (C : ClassConditions (G := G) (ι := ι) I) (k : ℕ)
    [Finite (R ⧸ I^k)] [Finite {c // C.allowed k c}] :
    Finite {ρ // (framed I C).allowed k ρ} := by
  let f : {ρ // (framed I C).allowed k ρ} → {c // C.allowed k c} :=
    fun ρ => ⟨classOf ρ.val, ρ.property⟩
  have hf (c : {c // C.allowed k c}) : Finite {ρ // f ρ = c} := by
    let : Finite {ρ : MatrixRep (R ⧸ I^k) G ι // classOf ρ = c.val} := finite_class_fiber c.val
    let j : {ρ // f ρ = c} → {ρ : MatrixRep (R ⧸ I^k) G ι // classOf ρ = c.val} :=
      fun ρ => ⟨ρ.val.val, congrArg Subtype.val ρ.property⟩
    apply Finite.of_injective j
    intro x y h
    apply Subtype.ext
    apply Subtype.ext
    exact congrArg (fun z : {ρ : MatrixRep (R ⧸ I^k) G ι // classOf ρ = c.val} => z.val) h
  exact PaperX.FiniteFiberBranches.finite_of_fibers f hf

/-- Positive finite class levels suffice for actual integral representations. -/
theorem class_realization_iff [IsAdicComplete I R]
    (C : ClassConditions (G := G) (ι := ι) I)
    (finiteR : ∀ k, Finite (R ⧸ I^k))
    (finiteC : ∀ k, 0 < k → Finite {c // C.allowed k c}) :
    (∃ ρ : MatrixRep R G ι, ∀ k, C.allowed k (classOf (reduce I ρ k))) ↔
      ∀ k, 0 < k → ∃ c, C.allowed k c := by
  have hf : ∀ k, Finite {ρ // (framed I C).allowed k ρ} := by
    apply positive_finite_levels
    intro k hk
    let : Finite (R ⧸ I^k) := finiteR k
    let : Finite {c // C.allowed k c} := finiteC k hk
    exact framed_finite I C k
  change (∃ ρ, Realizes I (framed I C) ρ) ↔ _
  rw [realization_iff I (framed I C) hf, ← positive_levels_iff_all]
  exact forall_congr' fun k => forall_congr' fun _ => framed_nonempty_iff I C k

/-- Finitely generated I and finite residue ring derive finiteness at every precision. -/
theorem finite_coefficients (hI : I.FG) [Finite (R ⧸ I)] (k : ℕ) :
    Finite (R ⧸ I^k) := Ideal.finite_quotient_pow hI k

end PaperX.ClassCompletion
