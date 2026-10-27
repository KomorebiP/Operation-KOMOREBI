module
public import LowRankChains
import all LowRankChains
import all LowRankAlgebra
import all ProductChainError
import all QuantumPacketCore
public import Mathlib.Topology.MetricSpace.HausdorffDistance
public import Mathlib.Analysis.Normed.Operator.NormedSpace
public import Mathlib.LinearAlgebra.Span.Basic
public import Mathlib.Tactic

/-!
Author: Komorebi P.
Paper VIII 7.2 and 7.3. Actual Krylov submodules, independently defined as
spans of finite operator orbits. Directness is proved from the packet ranges.
The distance certificate is for the actual metric infimum distance.
No condition-number or conjugate-gradient convergence theorem is claimed here.
-/
public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
namespace KomorebiPaperVIII
open scoped BigOperators
open KomorebiPaperVII

section Algebra
variable {R I : Type*} [Ring R] [Fintype I] [DecidableEq I]

/-- Zero cross-packet transfer implies actual commutation with every projector. -/
theorem packet_diagonal_commutes (P : PacketFamily R I) (D : R)
    (hD : PacketDiagonal P D) (i : I) : Commute D (P.proj i) := by
  have hc : (∑ b, P.block D b i) = P.block D i i := by
    apply Finset.sum_eq_single i
    · intro b _ hbi
      exact hD b i hbi
    · simp
  have hr : (∑ a, P.block D i a) = P.block D i i := by
    apply Finset.sum_eq_single i
    · intro a _ hai
      exact hD i a hai.symm
    · simp
  have hcl : (∑ b, P.block D b i) = D * P.proj i := by
    simp only [PacketFamily.block, ← Finset.sum_mul, P.sum_proj, one_mul]
  have hrl : (∑ a, P.block D i a) = P.proj i * D := by
    simp only [PacketFamily.block, ← Finset.mul_sum, P.sum_proj, mul_one]
  exact hcl.symm.trans (hc.trans (hr.symm.trans hrl))

/-- Powers of the local block agree with full powers on that packet's range. -/
theorem power_on_packet (P : PacketFamily R I) (A : R)
    (hA : ∀ i, Commute A (P.proj i)) (i : I) (j : ℕ) :
    (P.block A i i) ^ j * P.proj i = A ^ j * P.proj i := by
  have hb : P.block A i i = A * P.proj i := by
    rw [PacketFamily.block, ← (hA i).eq, mul_assoc, P.idempotent]
  have hp : ∀ j : ℕ, P.proj i ^ j * P.proj i = P.proj i := by
    intro k
    induction k with
    | zero => simp
    | succ k ih => simpa only [pow_succ, mul_assoc, P.idempotent] using ih
  rw [hb, (hA i).mul_pow, mul_assoc, hp]
end Algebra

section Krylov
variable {K X I : Type*} [NontriviallyNormedField K]
variable [NormedAddCommGroup X] [NormedSpace K X] [Fintype I] [DecidableEq I]

/-- Span of v, A v, ..., A^(m-1) v; m=0 is the zero subspace. -/
def krylovSpace (A : X →L[K] X) (v : X) (m : ℕ) : Submodule K X :=
  Submodule.span K (Set.range (fun j : Fin m => (A ^ j.val) v))

theorem krylov_generator_mem (A : X →L[K] X) (v : X) (m j : ℕ) (hj : j < m) :
    (A ^ j) v ∈ krylovSpace A v m :=
  Submodule.subset_span ⟨⟨j, hj⟩, rfl⟩

/-- Proposition 7.2: exact decomposition of every actual iterate. -/
theorem invariant_packet_power_expansion (P : PacketFamily (X →L[K] X) I)
    (A : X →L[K] X) (hA : ∀ i, Commute A (P.proj i)) (v : X) (j : ℕ) :
    (A ^ j) v = ∑ i, ((P.block A i i) ^ j) (P.proj i v) := by
  have hv : ∑ i, P.proj i v = v := by
    simpa only [sum_apply, one_apply_eq_self] using
      congrArg (fun (T : X →L[K] X) => T v) P.sum_proj
  calc
    (A ^ j) v = (A ^ j) (∑ i, P.proj i v) := by rw [hv]
    _ = ∑ i, (A ^ j) (P.proj i v) := map_sum _ _ _
    _ = _ := Finset.sum_congr rfl (fun i _ =>
      (congrArg (fun (T : X →L[K] X) => T v) (power_on_packet P A hA i j)).symm)

/-- Proposition 7.2: inclusion of actual Krylov spans in the sum of the local spans. -/
theorem invariant_packet_krylov (P : PacketFamily (X →L[K] X) I)
    (A : X →L[K] X) (hA : ∀ i, Commute A (P.proj i)) (v : X) (m : ℕ) :
    krylovSpace A v m ≤ ⨆ i, krylovSpace (P.block A i i) (P.proj i v) m := by
  apply Submodule.span_le.mpr
  rintro x ⟨j, rfl⟩
  change (A ^ j.val) v ∈ (⨆ i, krylovSpace (P.block A i i) (P.proj i v) m : Submodule K X)
  rw [invariant_packet_power_expansion P A hA v j.val]
  apply Submodule.sum_mem
  intro i _
  exact Submodule.mem_iSup_of_mem i
    (krylov_generator_mem (P.block A i i) (P.proj i v) m j.val j.isLt)

/-- Local Krylov spaces stay in their actual projector ranges. -/
theorem local_krylov_le_range (P : PacketFamily (X →L[K] X) I)
    (A : X →L[K] X) (v : X) (m : ℕ) (i : I) :
    krylovSpace (P.block A i i) (P.proj i v) m ≤ LinearMap.range (P.proj i).toLinearMap := by
  apply Submodule.span_le.mpr
  rintro x ⟨j, rfl⟩
  cases hj : j.val with
  | zero => exact ⟨v, by simp [hj]⟩
  | succ n =>
    refine ⟨A (P.proj i (((P.block A i i) ^ n) (P.proj i v))), ?_⟩
    simp only [hj, pow_succ', PacketFamily.block, mul_apply_eq_comp,
      ContinuousLinearMap.coe_coe]

/-- Projecting a finite sum of range-supported vectors selects exactly one term. -/
theorem project_packet_sum (P : PacketFamily (X →L[K] X) I) (x : I → X)
    (hx : ∀ i, x i ∈ LinearMap.range (P.proj i).toLinearMap) (j : I) :
    P.proj j (∑ i, x i) = x j := by
  have ht (i : I) : P.proj j (x i) = if j = i then x i else 0 := by
    obtain ⟨v, hv⟩ := hx i
    change P.proj i v = x i at hv
    rw [← hv]
    have hm := congrArg (fun (T : X →L[K] X) => T v) (P.mul_proj j i)
    by_cases hji : j = i
    · subst j
      simpa only [ite_true, mul_apply_eq_comp] using hm
    · simpa [hji] using hm
  simp only [map_sum, ht]
  simp

/-- The sum in Proposition 7.2 is direct: a zero local decomposition is termwise zero. -/
theorem local_krylov_direct (P : PacketFamily (X →L[K] X) I)
    (A : X →L[K] X) (v : X) (m : ℕ) (x : I → X)
    (hx : ∀ i, x i ∈ krylovSpace (P.block A i i) (P.proj i v) m)
    (hsum : ∑ i, x i = 0) : ∀ i, x i = 0 := by
  intro i
  have h := project_packet_sum P x (fun j => local_krylov_le_range P A v m j (hx j)) i
  simpa only [hsum, map_zero] using h.symm
end Krylov

section PowerBound
variable {R : Type*} [NormedRing R]

/-- A sharp first-order power perturbation bound valid even in the trivial ring. -/
theorem power_difference_bound_succ (A D : R) (n : ℕ) :
    ‖A ^ (n + 1) - D ^ (n + 1)‖ ≤
      ((n + 1 : ℕ) : ℝ) * (max ‖A‖ ‖D‖) ^ n * ‖A - D‖ := by
  let M := max ‖A‖ ‖D‖
  have hM : 0 ≤ M := (norm_nonneg A).trans (le_max_left _ _)
  have hA : ‖A‖ ≤ M := le_max_left _ _
  have hD : ‖D‖ ≤ M := le_max_right _ _
  induction n with
  | zero => simp
  | succ n ih =>
    have hid : A ^ (n + 1 + 1) - D ^ (n + 1 + 1) =
        A * (A ^ (n + 1) - D ^ (n + 1)) + (A - D) * D ^ (n + 1) := by
      rw [pow_succ' A (n + 1), pow_succ' D (n + 1)]
      noncomm_ring
    have hp : ‖D ^ (n + 1)‖ ≤ M ^ (n + 1) :=
      (norm_pow_le' D (Nat.succ_pos n)).trans (pow_le_pow_left₀ (norm_nonneg D) hD _)
    calc
      _ = ‖A * (A ^ (n + 1) - D ^ (n + 1)) + (A - D) * D ^ (n + 1)‖ := by rw [hid]
      _ ≤ ‖A‖ * ‖A ^ (n + 1) - D ^ (n + 1)‖ + ‖A - D‖ * ‖D ^ (n + 1)‖ :=
        (norm_add_le _ _).trans (add_le_add (norm_mul_le _ _) (norm_mul_le _ _))
      _ ≤ M * (((n + 1 : ℕ) : ℝ) * M ^ n * ‖A - D‖) + ‖A - D‖ * M ^ (n + 1) :=
        add_le_add (mul_le_mul hA ih (norm_nonneg _) hM)
          (mul_le_mul_of_nonneg_left hp (norm_nonneg _))
      _ = _ := by dsimp [M]; push_cast; rw [pow_succ]; ring

/-- Theorem 7.3's operator estimate in the manuscript's positive-index convention. -/
theorem approximate_packet_power_bound (D K : R) (j : ℕ) (hj : 0 < j) :
    ‖(D + K) ^ j - D ^ j‖ ≤
      (j : ℝ) * (max ‖D + K‖ ‖D‖) ^ (j - 1) * ‖K‖ := by
  have h := power_difference_bound_succ (D + K) D (j - 1)
  have he : j - 1 + 1 = j := by omega
  simpa only [he, add_sub_cancel_left] using h
end PowerBound

section Distance
variable {K X I : Type*} [NontriviallyNormedField K]
variable [NormedAddCommGroup X] [NormedSpace K X] [Fintype I] [DecidableEq I]

/-- Theorem 7.3's actual distance-to-local-Krylov-space certificate. -/
theorem approximate_packet_krylov_distance (P : PacketFamily (X →L[K] X) I)
    (D E : X →L[K] X) (hD : PacketDiagonal P D) (v : X) (j : ℕ) (hj : 0 < j) :
    Metric.infDist (((D + E) ^ j) v)
      ((⨆ i, krylovSpace (P.block D i i) (P.proj i v) (j + 1) : Submodule K X) : Set X) ≤
      (j : ℝ) * (max ‖D + E‖ ‖D‖) ^ (j - 1) * ‖E‖ * ‖v‖ := by
  have hm : (D ^ j) v ∈ (⨆ i, krylovSpace (P.block D i i) (P.proj i v) (j + 1) : Submodule K X) :=
    invariant_packet_krylov P D (packet_diagonal_commutes P D hD) v (j + 1)
      (krylov_generator_mem D v (j + 1) j (Nat.lt_succ_self j))
  calc
    _ ≤ dist (((D + E) ^ j) v) ((D ^ j) v) := Metric.infDist_le_dist_of_mem hm
    _ = ‖((D + E) ^ j - D ^ j) v‖ := by rw [dist_eq_norm]; rfl
    _ ≤ ‖(D + E) ^ j - D ^ j‖ * ‖v‖ := ((D + E) ^ j - D ^ j).le_opNorm v
    _ ≤ _ := mul_le_mul_of_nonneg_right (approximate_packet_power_bound D E j hj) (norm_nonneg _)
end Distance
end KomorebiPaperVIII

#print axioms KomorebiPaperVIII.packet_diagonal_commutes
#print axioms KomorebiPaperVIII.power_on_packet
#print axioms KomorebiPaperVIII.krylov_generator_mem
#print axioms KomorebiPaperVIII.invariant_packet_power_expansion
#print axioms KomorebiPaperVIII.invariant_packet_krylov
#print axioms KomorebiPaperVIII.local_krylov_le_range
#print axioms KomorebiPaperVIII.project_packet_sum
#print axioms KomorebiPaperVIII.local_krylov_direct
#print axioms KomorebiPaperVIII.power_difference_bound_succ
#print axioms KomorebiPaperVIII.approximate_packet_power_bound
#print axioms KomorebiPaperVIII.approximate_packet_krylov_distance
