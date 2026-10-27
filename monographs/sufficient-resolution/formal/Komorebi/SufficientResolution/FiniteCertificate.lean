import Komorebi.SufficientResolution.FiniteObservableModel

/-!
# Finite algebraic certificates for minimal realization

A candidate coordinate map is minimal when (1) it is generated from finitely
many original observations, (2) all given operations intertwine, and (3) the
original observation factors through it.  No numeric rank comparison is needed
for the kernel theorem.  Surjectivity is stated separately for ambient minimality.
-/

set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.FiniteCertificate

open Behavioral BehavioralMinimality FiniteObservableModel Module

universe uK uX uY uZ uI
variable {K : Type uK} [Field K]
variable {X : Type uX} [AddCommGroup X] [Module K X]
variable {Y : Type uY} [AddCommGroup Y] [Module K Y]
variable {Z : Type uZ} [AddCommGroup Z] [Module K Z]
variable {I : Type uI} [Fintype I] [DecidableEq I]
variable (T : I → X →ₗ[K] X) (O : X →ₗ[K] Y) (q : X →ₗ[K] Z)

/-- Finite identities sufficient to certify the candidate kernel as exactly minimal. -/
structure Certificate (r : ℕ) where
  generation : (ObservationIndex I r → Y) →ₗ[K] Z
  generated : q = generation.comp (observeUpTo T O r)
  dynamics : I → Z →ₗ[K] Z
  output : Z →ₗ[K] Y
  intertwine : ∀ i : I, q.comp (T i) = (dynamics i).comp q
  output_exact : output.comp q = O

variable {T O q}

/-- Finite observation generation prevents a candidate from retaining irrelevant distinctions. -/
 theorem invisible_le_generated_kernel {r : ℕ} (c : Certificate T O q r) :
    invisible T O ≤ LinearMap.ker q := by
  intro x hx
  have hv : observeUpTo T O r x = 0 := by
    funext w
    exact hx w.val
  change q x = 0
  have hq := LinearMap.congr_fun c.generated x
  rw [hq]
  change c.generation (observeUpTo T O r x) = 0
  rw [hv, map_zero]

/-- Intertwining and exact output prevent a candidate from discarding relevant distinctions. -/
 theorem certificate_kernel_eq {r : ℕ} (c : Certificate T O q r) :
    LinearMap.ker q = invisible T O := by
  exact le_antisymm
    (exact_model_kernel_le T O q c.dynamics c.output c.intertwine c.output_exact)
    (invisible_le_generated_kernel c)

 theorem certificate_same_future_iff {r : ℕ} (c : Certificate T O q r) (x y : X) :
    q x = q y ↔ ∀ w : List I, O (wordOp T w x) = O (wordOp T w y) := by
  have h : q x = q y ↔ x - y ∈ invisible T O := by
    rw [← certificate_kernel_eq c]
    change q x = q y ↔ q (x - y) = 0
    rw [map_sub, sub_eq_zero]
  rw [h]
  simp only [mem_invisible_iff, map_sub, sub_eq_zero]

 theorem certificate_word_intertwining {r : ℕ} (c : Certificate T O q r)
    (w : List I) (x : X) :
    q (wordOp T w x) = wordOp c.dynamics w (q x) := by
  induction w generalizing x with
  | nil => rfl
  | cons i w ih =>
    simp only [wordOp_cons, Module.End.mul_apply]
    rw [ih]
    exact congrArg (wordOp c.dynamics w) (LinearMap.congr_fun (c.intertwine i) x)

 theorem certificate_all_future_fidelity {r : ℕ} (c : Certificate T O q r)
    (w : List I) (x : X) :
    c.output (wordOp c.dynamics w (q x)) = O (wordOp T w x) := by
  rw [← certificate_word_intertwining c]
  exact LinearMap.congr_fun c.output_exact (wordOp T w x)

/-- With surjectivity, the entire candidate state space is the canonical minimal model. -/
def certificateEquiv {r : ℕ} (c : Certificate T O q r) (hq : Function.Surjective q) :
    Z ≃ₗ[K] State T O :=
  (q.quotKerEquivOfSurjective hq).symm.trans
    (Submodule.quotEquivOfEq (LinearMap.ker q) (invisible T O) (certificate_kernel_eq c))

@[simp] theorem certificateEquiv_on_state {r : ℕ} (c : Certificate T O q r)
    (hq : Function.Surjective q) (x : X) :
    certificateEquiv c hq (q x) = quotientMap T O x := by
  change Submodule.quotEquivOfEq (LinearMap.ker q) (invisible T O) (certificate_kernel_eq c)
    ((q.quotKerEquivOfSurjective hq).symm (q x)) = quotientMap T O x
  rw [LinearMap.quotKerEquivOfSurjective_symm_apply, Submodule.quotEquivOfEq_mk]
  rfl

 theorem certificateEquiv_dynamics {r : ℕ} (c : Certificate T O q r)
    (hq : Function.Surjective q) (i : I) (z : Z) :
    certificateEquiv c hq (c.dynamics i z) = induced T O i (certificateEquiv c hq z) := by
  obtain ⟨x, rfl⟩ := hq z
  have hi : q (T i x) = c.dynamics i (q x) := LinearMap.congr_fun (c.intertwine i) x
  rw [← hi, certificateEquiv_on_state, certificateEquiv_on_state, induced_quotient]

 theorem certificateEquiv_observation {r : ℕ} (c : Certificate T O q r)
    (hq : Function.Surjective q) (z : Z) :
    observation T O (certificateEquiv c hq z) = c.output z := by
  obtain ⟨x, rfl⟩ := hq z
  rw [certificateEquiv_on_state, observation_quotient]
  exact (LinearMap.congr_fun c.output_exact x).symm

variable [FiniteDimensional K X]

 theorem certificate_image_dimension {r : ℕ} (c : Certificate T O q r) :
    finrank K (LinearMap.range q) = finrank K (State T O) :=
  (image_dimension_minimal_iff T O q c.dynamics c.output c.intertwine c.output_exact).mpr
    (certificate_kernel_eq c)

 theorem certificate_dimension {r : ℕ} (c : Certificate T O q r)
    (hq : Function.Surjective q) :
    finrank K Z = finrank K X - finrank K (invisible T O) := by
  rw [(certificateEquiv c hq).finrank_eq, finrank_state]

end Komorebi.SufficientResolution.FiniteCertificate
