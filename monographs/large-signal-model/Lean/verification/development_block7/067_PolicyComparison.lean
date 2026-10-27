import KomorebiLSM.ObservationTree

/-! P43 includes shared randomized history-dependent policies.
The weights multiply complete instruments, not separately selected branches. -/
set_option autoImplicit false
namespace Komorebi.LSM.ObservationTree
open scoped BigOperators
open BaseNorm FiniteBayes
variable {E A O : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [Fintype A] [Fintype O] (C : ProbabilityCone E)

noncomputable def policyBranches (π : List (A × O) → A → ℝ)
    (B : List (A × O) → A × O → E →ₗ[ℝ] E) (h : List (A × O))
    (s : A × O) : E →ₗ[ℝ] E := π h s.1 • B h s

theorem policy_instrument (π : List (A × O) → A → ℝ) (hπ : ∀ h, IsPrior (π h))
    (B : List (A × O) → A × O → E →ₗ[ℝ] E)
    (hB : ∀ h a, C.Instrument (fun o => B h (a,o))) (h : List (A × O)) :
    C.Instrument (policyBranches π B h) := by
  constructor
  · intro s x hx
    exact C.smul_mem ((hπ h).1 s.1) ((hB h s.1).1 s.2 x hx)
  · intro x
    change (∑ s : A × O, C.mass (π h s.1 • B h s x))=C.mass x
    rw [Fintype.sum_prod_type]
    simp only [map_smul,smul_eq_mul,← Finset.mul_sum]
    simp_rw [(hB h _).2 x]
    rw [← Finset.sum_mul,(hπ h).2,one_mul]

/-- Zero policy probabilities are permitted. No lower propensity is needed for comparison. -/
theorem policy_discrepancy (π : List (A × O) → A → ℝ) (hπ : ∀ h, IsPrior (π h))
    (B D : List (A × O) → A × O → E →ₗ[ℝ] E) (ε : ℕ → ℝ)
    (hε : ∀ h a z, z ∈ C.base →
      C.discrepancy (fun o => B h (a,o)) (fun o => D h (a,o)) z ≤ ε h.length)
    (h : List (A × O)) (z : E) (hz : z ∈ C.base) :
    C.discrepancy (policyBranches π B h) (policyBranches π D h) z ≤ ε h.length := by
  calc
    _ = ∑ a, π h a*C.discrepancy (fun o => B h (a,o)) (fun o => D h (a,o)) z := by
      unfold ProbabilityCone.discrepancy
      rw [Fintype.sum_prod_type]
      apply Finset.sum_congr rfl
      intro a _
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro o _
      have he : (policyBranches π B h (a,o)-policyBranches π D h (a,o)) z =
          π h a • ((B h (a,o)-D h (a,o)) z) := by
        simp only [policyBranches,LinearMap.sub_apply,LinearMap.smul_apply,smul_sub]
      rw [he,C.value_smul_of_nonneg ((hπ h).1 a)]
    _ ≤ ∑ a, π h a*ε h.length :=
      Finset.sum_le_sum (fun a _ => mul_le_mul_of_nonneg_left (hε h a z hz) ((hπ h).1 a))
    _ = ε h.length := by rw [← Finset.sum_mul,(hπ h).2,one_mul]

/-- P43 for the actual joint distribution of action and observation records. -/
theorem shared_randomized_policy_tv_bound
    (π : List (A × O) → A → ℝ) (hπ : ∀ h, IsPrior (π h))
    (B D : List (A × O) → A × O → E →ₗ[ℝ] E)
    (hB : ∀ h a, C.Instrument (fun o => B h (a,o)))
    (hD : ∀ h a, C.Instrument (fun o => D h (a,o)))
    (ε : ℕ → ℝ) (hε : ∀ h a z, z ∈ C.base →
      C.discrepancy (fun o => B h (a,o)) (fun o => D h (a,o)) z ≤ ε h.length)
    (n : ℕ) (x y : E) (hx : x ∈ C.base) (hy : y ∈ C.base) :
    FiniteTV.distance (recordLaw C (policyBranches π B) n [] x)
      (recordLaw C (policyBranches π D) n [] y) ≤
      min 1 (C.value (x-y)/2+(∑ t ∈ Finset.range n, ε t)/2) :=
  observation_tree_tv_bound C _ _ (policy_instrument C π hπ B hB)
    (policy_instrument C π hπ D hD) ε (policy_discrepancy C π hπ B D ε hε) n x y hx hy

/-- The observation-only distribution is the pushforward forgetting actions. -/
noncomputable def observationLaw (π : List (A × O) → A → ℝ)
    (B : List (A × O) → A × O → E →ₗ[ℝ] E) (n : ℕ) (x : E) : Record O n → ℝ := by
  classical
  exact aggregate (recordMap Prod.snd) (recordLaw C (policyBranches π B) n [] x)

/-- The same bound holds after action coordinates have been summed out. -/
theorem shared_policy_observation_tv_bound
    (π : List (A × O) → A → ℝ) (hπ : ∀ h, IsPrior (π h))
    (B D : List (A × O) → A × O → E →ₗ[ℝ] E)
    (hB : ∀ h a, C.Instrument (fun o => B h (a,o)))
    (hD : ∀ h a, C.Instrument (fun o => D h (a,o)))
    (ε : ℕ → ℝ) (hε : ∀ h a z, z ∈ C.base →
      C.discrepancy (fun o => B h (a,o)) (fun o => D h (a,o)) z ≤ ε h.length)
    (n : ℕ) (x y : E) (hx : x ∈ C.base) (hy : y ∈ C.base) :
    FiniteTV.distance (observationLaw C π B n x) (observationLaw C π D n y) ≤
      min 1 (C.value (x-y)/2+(∑ t ∈ Finset.range n, ε t)/2) := by
  classical
  exact (FiniteTV.distance_aggregate_le (recordMap Prod.snd) _ _).trans
    (shared_randomized_policy_tv_bound C π hπ B D hB hD ε hε n x y hx hy)

/-- Deterministic policies are included as point-mass randomizations. -/
noncomputable def deterministicPolicy (π : List (A × O) → A) (h : List (A × O)) : A → ℝ := by
  classical
  exact pointMass (π h)

omit [NormedAddCommGroup E] [NormedSpace ℝ E] [Fintype O] in
theorem deterministicPolicy_prior (π : List (A × O) → A) (h : List (A × O)) :
    IsPrior (deterministicPolicy π h) := by
  classical
  exact point_prior (π h)

end Komorebi.LSM.ObservationTree
