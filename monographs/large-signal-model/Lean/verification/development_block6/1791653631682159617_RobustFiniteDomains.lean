import KomorebiLSM.PositiveLiftTopology

/-! P40: convex sets of complete operator families and history-dependent
selection. Mixing takes place across whole families, retaining the mass law. -/
set_option autoImplicit false
namespace Komorebi.LSM.RobustDomains
open scoped BigOperators
open FiniteInstruments PositiveLift
variable {E A O : Type*} [AddCommGroup E] [Module ℝ E] [Fintype O]

def ValidFamily (C : Set E) (l : E →ₗ[ℝ] ℝ) (B : A × O → E →ₗ[ℝ] E) : Prop :=
  (∀ s x, x ∈ C → B s x ∈ C) ∧ (∀ a x, ∑ o, l (B (a,o) x) = l x)

/-- A single convex coefficient is shared by every branch of a complete family. -/
theorem validFamily_convex (C : Set E) (hc : Convex ℝ C) (l : E →ₗ[ℝ] ℝ) :
    Convex ℝ {B | ValidFamily C l B} := by
  intro B hB D hD a b ha hb hab
  constructor
  · intro s x hx
    exact hc (hB.1 s x hx) (hD.1 s x hx) ha hb hab
  · intro u x
    change ∑ o, l (a • B (u,o) x + b • D (u,o) x) = l x
    simp only [map_add,map_smul,smul_eq_mul,Finset.sum_add_distrib,← Finset.mul_sum,
      hB.2,hD.2,← add_mul,hab,one_mul]

/-- Membership in the actual convex hull, not merely a list of tested parameters. -/
theorem robust_convex_hull {I : Type*} (C : Set E) (hc : Convex ℝ C)
    (l : E →ₗ[ℝ] ℝ) (families : I → A × O → E →ₗ[ℝ] E)
    (hv : ∀ i, ValidFamily C l (families i)) :
    ∀ B ∈ convexHull ℝ (Set.range families), ValidFamily C l B := by
  apply convexHull_min _ (validFamily_convex C hc l)
  rintro _ ⟨i,rfl⟩
  exact hv i

/-- Nonnegative vertex witnesses establish validity on the full uncertainty hull. -/
theorem robust_positive_lift {I J : Type*} [Fintype J] [DecidableEq J]
    (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (families : I → A × O → E →ₗ[ℝ] E)
    (M : I → A × O → Matrix J J ℝ)
    (hp : ∀ i s j k, 0 ≤ M i s j k)
    (he : ∀ i s, (families i s).comp V = V.comp (M i s).mulVecLin)
    (hm : ∀ i a x, ∑ o, l (families i (a,o) x) = l x) :
    ∀ B ∈ convexHull ℝ (Set.range families), ValidFamily (hull V) l B := by
  apply robust_convex_hull (hull V) (hull_convex V) l families
  intro i
  exact ⟨fun s => (positive_lift_iff V (families i s)).mpr ⟨M i s,hp i s,he i s⟩,hm i⟩

/-- Explicit mixed lifts retain intertwining, including redundant generators. -/
theorem mixed_lift {I J : Type*} [Fintype I] [Fintype J]
    (V : (J → ℝ) →ₗ[ℝ] E) (B : I → E →ₗ[ℝ] E) (M : I → Matrix J J ℝ)
    (he : ∀ i, (B i).comp V = V.comp (M i).mulVecLin) (θ : I → ℝ) :
    (∑ i, θ i • B i).comp V = V.comp (∑ i, θ i • (M i).mulVecLin) := by
  apply LinearMap.ext
  intro x
  simp only [LinearMap.comp_apply,LinearMap.sum_apply,LinearMap.smul_apply,map_sum,map_smul]
  apply Finset.sum_congr rfl
  intro i _
  exact congrArg (θ i • ·) (congrArg (fun F : (J → ℝ) →ₗ[ℝ] E => F x) (he i))

omit [Fintype O] in
theorem mixed_entries_nonnegative {I J : Type*} [Fintype I]
    (M : I → Matrix J J ℝ) (hp : ∀ i j k, 0 ≤ M i j k)
    (θ : I → ℝ) (hθ : ∀ i, 0 ≤ θ i) : ∀ j k, 0 ≤ (∑ i, θ i • M i) j k := by
  intro j k
  simp only [Matrix.sum_apply,Matrix.smul_apply,smul_eq_mul]
  exact Finset.sum_nonneg (fun i _ => mul_nonneg (hθ i) (hp i j k))

/-- A chronological word can use a different family after every observed prefix. -/
def adaptiveWord (B : List (A × O) → A × O → E →ₗ[ℝ] E) :
    List (A × O) → List (A × O) → E → E
  | _, [], x => x
  | h, s::w, x => adaptiveWord B (h ++ [s]) w (B h s x)

theorem adaptiveWord_in_cone (C : Set E) (l : E →ₗ[ℝ] ℝ)
    (B : List (A × O) → A × O → E →ₗ[ℝ] E)
    (hv : ∀ h, ValidFamily C l (B h)) (h w : List (A × O)) {x : E} (hx : x ∈ C) :
    adaptiveWord B h w x ∈ C := by
  induction w generalizing h x with
  | nil => exact hx
  | cons s w ih => exact ih _ ((hv h).1 s x hx)

theorem adaptiveWord_nonnegative (C : Set E) (l : E →ₗ[ℝ] ℝ)
    (hC : ∀ x ∈ C, 0 ≤ l x) (B : List (A × O) → A × O → E →ₗ[ℝ] E)
    (hv : ∀ h, ValidFamily C l (B h)) (h w : List (A × O)) {x : E} (hx : x ∈ C) :
    0 ≤ l (adaptiveWord B h w x) :=
  hC _ (adaptiveWord_in_cone C l B hv h w hx)

theorem adaptiveWord_mass_le (C : Set E) (l : E →ₗ[ℝ] ℝ)
    (hC : ∀ x ∈ C, 0 ≤ l x) (B : List (A × O) → A × O → E →ₗ[ℝ] E)
    (hv : ∀ h, ValidFamily C l (B h)) (h w : List (A × O)) {x : E} (hx : x ∈ C) :
    l (adaptiveWord B h w x) ≤ l x := by
  induction w generalizing h x with
  | nil => exact le_rfl
  | cons s w ih =>
    apply (ih (h ++ [s]) ((hv h).1 s x hx)).trans
    rw [← (hv h).2 s.1 x]
    exact Finset.single_le_sum (fun o _ => hC _ ((hv h).1 (s.1,o) x hx)) (Finset.mem_univ s.2)

/-- Full observation-tree mass for an arbitrary deterministic history-based policy. -/
noncomputable def adaptiveTreeMass (B : List (A × O) → A × O → E →ₗ[ℝ] E)
    (l : E →ₗ[ℝ] ℝ) (policy : List (A × O) → A) : ℕ → List (A × O) → E → ℝ
  | 0, _, x => l x
  | n+1, h, x => ∑ o, adaptiveTreeMass B l policy n (h ++ [(policy h,o)]) (B h (policy h,o) x)

theorem adaptiveTreeMass_eq (C : Set E) (l : E →ₗ[ℝ] ℝ)
    (B : List (A × O) → A × O → E →ₗ[ℝ] E)
    (hv : ∀ h, ValidFamily C l (B h)) (policy : List (A × O) → A)
    (n : ℕ) (h : List (A × O)) (x : E) : adaptiveTreeMass B l policy n h x = l x := by
  induction n generalizing h x with
  | zero => rfl
  | succ n ih =>
    simp only [adaptiveTreeMass,ih]
    exact (hv h).2 (policy h) x

end Komorebi.LSM.RobustDomains
