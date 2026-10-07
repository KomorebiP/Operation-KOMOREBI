import KomorebiPadic.LeastDegreeProfile

/-! # Variable-width Cartier coordinates from least degree profiles
Zero capacity means the polynomial is zero. All transfer degrees are computed
from actual residue kernels, with zero kernels removed before propagation.
-/
namespace KomorebiPadic
open Polynomial
attribute [local instance] Classical.propDecidable
variable {R : Type*} [CommRing R] {p L J D : ℕ}

/-- Capacity is a coefficient count, rather than a natural degree. -/
def FitsRowCapacity (n : ℕ) (P : R[X]) : Prop := P = 0 ∨ P.natDegree < n

theorem fitsRowCapacity_zero (n : ℕ) : FitsRowCapacity n (0 : R[X]) := Or.inl rfl

theorem fitsRowCapacity_mono {n m : ℕ} {P : R[X]} (hn : FitsRowCapacity n P) (h : n ≤ m) :
    FitsRowCapacity m P := hn.imp_right (fun hh => hh.trans_le h)

theorem fitsRowCapacity_iff_coeff (n : ℕ) (P : R[X]) :
    FitsRowCapacity n P ↔ ∀ j, n ≤ j → P.coeff j = 0 := by
  constructor
  · rintro (rfl | h) j hj
    · simp
    · exact Polynomial.coeff_eq_zero_of_natDegree_lt (h.trans_le hj)
  · intro h
    by_cases hz : P = 0
    · exact Or.inl hz
    · right
      by_contra hn
      have he := h P.natDegree (Nat.le_of_not_gt hn)
      exact (Polynomial.leadingCoeff_ne_zero.mpr hz) (by simpa using he)

theorem fitsRowCapacity_ofFn (n : ℕ) (v : Fin n → R) :
    FitsRowCapacity n (open scoped Classical in Polynomial.ofFn n v) := by
  classical
  apply (fitsRowCapacity_iff_coeff _ _).mpr
  intro j hj
  exact Polynomial.ofFn_coeff_eq_zero_of_ge _ hj

theorem fitsRowCapacity_decode {n : ℕ} {P : R[X]} (hP : FitsRowCapacity n P) :
    (open scoped Classical in Polynomial.ofFn n (Polynomial.toFn n P)) = P := by
  classical
  rcases hP with rfl | h
  · simp
  · exact Polynomial.ofFn_comp_toFn_eq_id_of_natDegree_lt h

noncomputable def polynomialCapacity (P : R[X]) : ℕ :=
  if P = 0 then 0 else P.natDegree+1

theorem fits_polynomialCapacity (P : R[X]) : FitsRowCapacity (polynomialCapacity P) P := by
  classical
  unfold polynomialCapacity
  split_ifs with h
  · exact Or.inl h
  · exact Or.inr (Nat.lt_succ_self _)

theorem polynomialCapacity_le_iff (P : R[X]) (n : ℕ) :
    polynomialCapacity P ≤ n ↔ FitsRowCapacity n P := by
  classical
  by_cases h : P = 0
  · simp [polynomialCapacity, h, FitsRowCapacity]
  · simp [polynomialCapacity, h, FitsRowCapacity]

/-- Worst-case all-digit degree transport. It does not assume absence of cancellation. -/
noncomputable def kernelCapacityTransfer (p : ℕ) (H : R[X]) (n : ℕ) : ℕ :=
  if n = 0 ∨ H = 0 then 0 else (n-1+H.natDegree)/p+1

theorem kernelCapacityTransfer_mono (p : ℕ) (H : R[X]) :
    Monotone (kernelCapacityTransfer p H) := by
  classical
  intro n m hnm
  by_cases hH : H = 0
  · simp [kernelCapacityTransfer, hH]
  · by_cases hn : n = 0
    · simp [kernelCapacityTransfer, hn]
    · have hm : m ≠ 0 := by omega
      simp only [kernelCapacityTransfer, hn, hm, hH, or_self, ↓reduceIte]
      exact Nat.add_le_add_right
        (Nat.div_le_div_right (Nat.add_le_add_right (Nat.sub_le_sub_right hnm 1) _)) 1

theorem kernelCapacityTransfer_bound (hp : 0 < p) (H : R[X])
    (hH : H.natDegree ≤ (p-1)*D) : kernelCapacityTransfer p H (D+1) ≤ D+1 := by
  classical
  by_cases hz : H = 0
  · simp [kernelCapacityTransfer, hz]
  · have hnon : ¬(D+1 = 0 ∨ H = 0) := by simp [hz]
    simp only [kernelCapacityTransfer, hnon, ↓reduceIte]
    apply Nat.add_le_add_right
    have he : D + (p-1)*D = p*D := by
      have hh : 1+(p-1) = p := by omega
      calc
        D+(p-1)*D = (1+(p-1))*D := by ring
        _ = p*D := by rw [hh]
    have hh : D+1-1+H.natDegree ≤ p*D := by omega
    simpa [Nat.mul_div_right, hp.ne'] using Nat.div_le_div_right (c := p) hh

theorem polynomialCartier_fits_transfer (hp : 0 < p) (d n : ℕ) (P H : R[X])
    (hP : FitsRowCapacity n P) :
    FitsRowCapacity (kernelCapacityTransfer p H n) (polynomialCartier p d (P*H)) := by
  classical
  by_cases hz : P = 0 ∨ H = 0
  · left
    have h0 : polynomialCartier p d (0 : R[X]) = 0 := (polynomialCartierLinear p d hp).map_zero
    rcases hz with h | h <;> simpa only [h, zero_mul, mul_zero] using h0
  · have hn : 0 < n := by rcases hP with h | h; exact False.elim (hz (Or.inl h)); omega
    have hPn : P.natDegree ≤ n-1 := by
      rcases hP with h | h
      · exact False.elim (hz (Or.inl h))
      · omega
    have hdeg := polynomialCartier_natDegree_le hp d (P*H)
    have hm : (P*H).natDegree ≤ n-1+H.natDegree :=
      Polynomial.natDegree_mul_le.trans (Nat.add_le_add_right hPn _)
    have hdv := Nat.div_le_div_right (c := p) hm
    right
    have hg : ¬ (n = 0 ∨ H = 0) := by
      rintro (h | h)
      · omega
      · exact hz (Or.inr h)
    simp only [kernelCapacityTransfer, hg, ↓reduceIte]
    omega

/-- The system uses the actual encoded initial row and actual residue kernel degrees. -/
noncomputable def machineDegreeSystem (M : PolynomialCartierMachine R p L J D)
    (s₀ : CartierCoefficientState R L D) : DegreePropagationSystem L J (D+1) where
  target := M.target
  seed i := polynomialCapacity (numeratorPolynomial D (s₀ i))
  seed_bound _i := (polynomialCapacity_le_iff _ _).mpr
    (Or.inr (Nat.lt_succ_of_le (numeratorPolynomial_degree _ _)))
  transfer i k := kernelCapacityTransfer p (M.kernel i k)
  transfer_mono i k := kernelCapacityTransfer_mono p (M.kernel i k)
  transfer_bound i k := kernelCapacityTransfer_bound M.radix_pos _ (M.kernel_degree i k)

noncomputable def leastMachineDegreeProfile (M : PolynomialCartierMachine R p L J D)
    (s₀ : CartierCoefficientState R L D) : Fin L → ℕ := leastDegreeProfile (machineDegreeSystem M s₀)

/-- A capacity-zero row has no coefficient positions at all. -/
abbrev ProfileCoefficientState (R : Type*) {L : ℕ} (w : Fin L → ℕ) :=
  (i : Fin L) → Fin (w i) → R

noncomputable def profileRowPolynomial (w : Fin L → ℕ) (s : ProfileCoefficientState R w)
    (i : Fin L) : R[X] := open scoped Classical in Polynomial.ofFn (w i) (s i)

/-- An absent row decodes to zero, rather than to an unconstrained constant. -/
theorem profileRowPolynomial_zero_capacity (w : Fin L → ℕ) (s : ProfileCoefficientState R w)
    (i : Fin L) (hi : w i = 0) : profileRowPolynomial w s i = 0 := by
  have hf : FitsRowCapacity (w i) (profileRowPolynomial w s i) := fitsRowCapacity_ofFn _ _
  rw [hi] at hf
  rcases hf with h | h
  · exact h
  · exact False.elim (Nat.not_lt_zero _ h)

noncomputable def profileEncode (w : Fin L → ℕ) (P : Fin L → R[X]) : ProfileCoefficientState R w :=
  fun i => Polynomial.toFn (w i) (P i)

@[simp] theorem profileEncode_decode (w : Fin L → ℕ) (s : ProfileCoefficientState R w) :
    profileEncode w (profileRowPolynomial w s) = s := by
  classical
  funext i
  exact Polynomial.toFn_comp_ofFn_eq_id _ _

theorem profileRowPolynomial_encode (w : Fin L → ℕ) (P : Fin L → R[X])
    (hP : ∀ i, FitsRowCapacity (w i) (P i)) (i : Fin L) :
    profileRowPolynomial w (profileEncode w P) i = P i := fitsRowCapacity_decode (hP i)

noncomputable def embedProfileState (D : ℕ) (w : Fin L → ℕ)
    (s : ProfileCoefficientState R w) : CartierCoefficientState R L D :=
  fun i => numeratorCoordinates D (profileRowPolynomial w s i)

theorem embedProfileState_decode (w : Fin L → ℕ) (hw : ∀ i, w i ≤ D+1)
    (s : ProfileCoefficientState R w) (i : Fin L) :
    numeratorPolynomial D (embedProfileState D w s i) = profileRowPolynomial w s i :=
  fitsRowCapacity_decode (fitsRowCapacity_mono (fitsRowCapacity_ofFn _ _) (hw i))

theorem embedProfileState_injective (w : Fin L → ℕ) (hw : ∀ i, w i ≤ D+1) :
    Function.Injective (embedProfileState (R := R) D w) := by
  intro s t h
  have hp : profileRowPolynomial w s = profileRowPolynomial w t := by
    funext i
    have hh := congrArg (fun v => numeratorPolynomial D (v i)) h
    simpa only [embedProfileState_decode w hw] using hh
  have hc := congrArg (profileEncode w) hp
  simpa only [profileEncode_decode] using hc

/-- Closure of the profile certifies every routed next-row polynomial, including absent rows. -/
theorem machineNextNumerator_fits_profile (M : PolynomialCartierMachine R p L J D)
    (s₀ : CartierCoefficientState R L D) (w : Fin L → ℕ)
    (hw : ∀ i, w i ≤ D+1) (hc : DegreeProfileClosed (machineDegreeSystem M s₀) w)
    (d : ℕ) (s : ProfileCoefficientState R w) (j : Fin L) :
    FitsRowCapacity (w j) (machineNextNumerator M d (embedProfileState D w s) j) := by
  classical
  apply (fitsRowCapacity_iff_coeff _ _).mpr
  intro n hn
  simp only [machineNextNumerator, Polynomial.finsetSum_coeff]
  apply Finset.sum_eq_zero
  intro i _
  apply Finset.sum_eq_zero
  intro k _
  split_ifs with ht
  · have hP : FitsRowCapacity (w i) (numeratorPolynomial D (embedProfileState D w s i)) := by
      rw [embedProfileState_decode w hw]
      exact fitsRowCapacity_ofFn _ _
    have hf := polynomialCartier_fits_transfer M.radix_pos d (w i) _ (M.kernel i k) hP
    have hb : kernelCapacityTransfer p (M.kernel i k) (w i) ≤ w j := by
      simpa only [machineDegreeSystem, ht] using hc.2 i k
    exact (fitsRowCapacity_iff_coeff _ _).mp (fitsRowCapacity_mono hf hb) n hn
  · simp

noncomputable def profileMachineTransition (M : PolynomialCartierMachine R p L J D)
    (w : Fin L → ℕ) (d : ℕ) (s : ProfileCoefficientState R w) : ProfileCoefficientState R w :=
  profileEncode w (machineNextNumerator M d (embedProfileState D w s))

theorem profileMachineTransition_embedding (M : PolynomialCartierMachine R p L J D)
    (s₀ : CartierCoefficientState R L D) (w : Fin L → ℕ)
    (hw : ∀ i, w i ≤ D+1) (hc : DegreeProfileClosed (machineDegreeSystem M s₀) w)
    (d : ℕ) (s : ProfileCoefficientState R w) :
    embedProfileState D w (profileMachineTransition M w d s) =
      machineTransition M d (embedProfileState D w s) := by
  funext j
  change numeratorCoordinates D (profileRowPolynomial w
    (profileEncode w (machineNextNumerator M d (embedProfileState D w s))) j) = _
  rw [profileRowPolynomial_encode w _ (machineNextNumerator_fits_profile M s₀ w hw hc d s)]
  rfl

noncomputable def iterateProfileMachine (M : PolynomialCartierMachine R p L J D)
    (w : Fin L → ℕ) : List ℕ → ProfileCoefficientState R w → ProfileCoefficientState R w
  | [], s => s
  | d::ds, s => iterateProfileMachine M w ds (profileMachineTransition M w d s)

theorem iterateProfileMachine_embedding (M : PolynomialCartierMachine R p L J D)
    (s₀ : CartierCoefficientState R L D) (w : Fin L → ℕ)
    (hw : ∀ i, w i ≤ D+1) (hc : DegreeProfileClosed (machineDegreeSystem M s₀) w)
    (ds : List ℕ) (s : ProfileCoefficientState R w) :
    embedProfileState D w (iterateProfileMachine M w ds s) =
      iterateMachine M ds (embedProfileState D w s) := by
  induction ds generalizing s with
  | nil => rfl
  | cons d ds ih =>
    simp only [iterateProfileMachine, iterateMachine]
    rw [ih, profileMachineTransition_embedding M s₀ w hw hc]

noncomputable def profileMachineInitial (s₀ : CartierCoefficientState R L D)
    (w : Fin L → ℕ) : ProfileCoefficientState R w :=
  profileEncode w (fun i => numeratorPolynomial D (s₀ i))

theorem profileMachineInitial_embedding (M : PolynomialCartierMachine R p L J D)
    (s₀ : CartierCoefficientState R L D) (w : Fin L → ℕ)
    (hc : DegreeProfileClosed (machineDegreeSystem M s₀) w) :
    embedProfileState D w (profileMachineInitial s₀ w) = s₀ := by
  have hf : ∀ i, FitsRowCapacity (w i) (numeratorPolynomial D (s₀ i)) := fun i =>
    (polynomialCapacity_le_iff _ _).mp (hc.1 i)
  funext i
  change numeratorCoordinates D (profileRowPolynomial w (profileEncode w _) i) = _
  rw [profileRowPolynomial_encode w _ hf, numeratorCoordinates_polynomial]

omit [CommRing R] in
/-- Exact cardinality for variable row lengths, including empty rows. -/
theorem profileCoefficientState_card [Fintype R] (w : Fin L → ℕ) :
    Fintype.card (ProfileCoefficientState R w) = (Fintype.card R)^(∑ i, w i) := by
  simp [ProfileCoefficientState, Fintype.card_pi, Finset.prod_pow_eq_pow_sum]

end KomorebiPadic
