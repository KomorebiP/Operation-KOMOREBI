import KomorebiLSM.RationalCertificateSearch
import KomorebiLSM.PositiveLiftTopology

/-! P45 soundness: accepted rational data instantiate the existing P39 cone and
positive-instrument theorem, not just a syntactic checker. -/
set_option autoImplicit false
namespace Komorebi.LSM.RationalSearch
open scoped BigOperators
open FiniteBayes FiniteInstruments PositiveLift

noncomputable def readout {r : ℕ} (l : Fin r → ℚ) : (Fin r → ℝ) →ₗ[ℝ] ℝ where
  toFun x := ∑ i, (l i : ℝ) * x i
  map_add' x y := by simp [mul_add,Finset.sum_add_distrib]
  map_smul' c x := by simp [Finset.mul_sum]; congr 1; funext i; ring

theorem valid_normalized {r s : ℕ} (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (c : Candidate r s)
    (h : Valid l z B c) :
    (readout l).comp (realMatrix (synthesis c)).mulVecLin = mass := by
  apply LinearMap.ext
  intro x
  change (∑ i, (l i : ℝ) * ∑ j, (synthesis c i j : ℝ) * x j) = ∑ j, x j
  simp_rw [Finset.mul_sum,← mul_assoc]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro j _
  rw [← Finset.sum_mul]
  have hn : ∑ i, (l i : ℝ) * (synthesis c i j : ℝ) = 1 := by exact_mod_cast h.1 j
  rw [hn,one_mul]

theorem valid_intertwining {r s : ℕ} (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (c : Candidate r s)
    (h : Valid l z B c) (t : Fin s) :
    (realMatrix (B t)).mulVecLin.comp (realMatrix (synthesis c)).mulVecLin =
    (realMatrix (synthesis c)).mulVecLin.comp (realMatrix (lifts c t)).mulVecLin := by
  rw [← Matrix.mulVecLin_mul,← Matrix.mulVecLin_mul,← realMatrix_mul,← realMatrix_mul,h.2.2.1 t]

theorem valid_initial {r s : ℕ} (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (c : Candidate r s)
    (h : Valid l z B c) :
    IsPrior (fun j => (initial c j : ℝ)) ∧
    (realMatrix (synthesis c)).mulVecLin (fun j => (initial c j : ℝ)) = fun i => (z i : ℝ) := by
  refine ⟨⟨fun j => by exact_mod_cast h.2.2.2.2.1 j, ?_⟩,?_⟩
  · exact_mod_cast h.2.2.2.2.2.1
  · funext i
    have he := congrFun h.2.2.2.2.2.2 i
    change ∑ j, (synthesis c i j : ℝ) * (initial c j : ℝ) = (z i : ℝ)
    exact_mod_cast he

/-- An accepted certificate supplies a closed, pointed, generating invariant
cone containing the initial state, with normalized strictly positive mass. -/
theorem accepted_probability_domain {r s : ℕ} (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (n : ℕ) (c : Candidate r s)
    (hs : search l z B n = some c) :
    let V := (realMatrix (synthesis c)).mulVecLin
    IsClosed (hull V) ∧ Submodule.span ℝ (hull V) = ⊤ ∧
    PositivePackets.StrictMass (hull V) (readout l) ∧
    (∀ x, x ∈ hull V → -x ∈ hull V → x = 0) ∧
    ((fun i => (z i : ℝ)) ∈ hull V) ∧
    (∀ t x, x ∈ hull V → (realMatrix (B t)).mulVecLin x ∈ hull V) := by
  dsimp only
  have h := search_sound l z B n c hs
  have hn := valid_normalized l z B c h
  have hi := valid_initial l z B c h
  refine ⟨hull_closed _ _ hn,hull_spans _ (real_synthesis_surjective l z B c h),
    hull_strict_mass _ _ hn,?_,?_,?_⟩
  · intro x hx hmx
    exact hull_pointed _ _ hn hx hmx
  · exact ⟨_,hi.1.1,hi.2⟩
  · intro t
    apply (positive_lift_iff _ _).mpr
    refine ⟨realMatrix (lifts c t),?_,valid_intertwining l z B c h t⟩
    intro i j
    exact_mod_cast h.2.2.2.1 t i j

/-- Exact mass identities turn every returned certificate into all-word
probabilities in [0,1], for any finite observation alphabet and action coding. -/
theorem accepted_all_word_probabilities {r s : ℕ} {A O : Type*} [Fintype O]
    (code : A × O → Fin s) (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (n : ℕ) (c : Candidate r s)
    (hs : search l z B n = some c)
    (hm : ∀ a x, ∑ o, readout l ((realMatrix (B (code (a,o)))).mulVecLin x) = readout l x) :
    ∀ w : List (A × O),
      0 ≤ readout l (wordAction (fun t => (realMatrix (B (code t))).mulVecLin) w
        (fun i => (z i : ℝ))) ∧
      readout l (wordAction (fun t => (realMatrix (B (code t))).mulVecLin) w
        (fun i => (z i : ℝ))) ≤ 1 := by
  have h := search_sound l z B n c hs
  have hn := valid_normalized l z B c h
  have hi := valid_initial l z B c h
  have he := fun t => valid_intertwining l z B c h (code t)
  have hp : ∀ t i j, 0 ≤ realMatrix (lifts c (code t)) i j := by
    intro t i j
    exact_mod_cast h.2.2.2.1 (code t) i j
  have hh := finite_positive_lift_certificate
    (fun t => (realMatrix (B (code t))).mulVecLin)
    (realMatrix (synthesis c)).mulVecLin (readout l) hn hm
    (fun t => realMatrix (lifts c (code t))) he hp _ hi.1
  rw [hi.2] at hh
  exact hh.2.2
end Komorebi.LSM.RationalSearch
