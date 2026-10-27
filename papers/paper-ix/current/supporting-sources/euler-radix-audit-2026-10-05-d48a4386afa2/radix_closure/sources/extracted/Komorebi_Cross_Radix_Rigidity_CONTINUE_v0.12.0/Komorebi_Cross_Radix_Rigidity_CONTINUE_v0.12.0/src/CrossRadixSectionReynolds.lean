import CrossRadixFiniteLCMIntersection
import CrossRadixAffineDecoder
import CrossRadixReynoldsAverage

noncomputable section

namespace KomorebiCrossRadix

variable {T : ℕ}

/-- Fixed-left distributivity of gcd over lcm, proved via prime factorization.
The positivity assumptions are exactly the positive-radix regime used below. -/
lemma gcd_lcm_fixed_left
    (T m n : ℕ) (hT : 0 < T) (hm : 0 < m) (hn : 0 < n) :
    Nat.lcm (Nat.gcd T m) (Nat.gcd T n) = Nat.gcd T (Nat.lcm m n) := by
  have hTm : Nat.gcd T m ≠ 0 := Nat.ne_of_gt (Nat.gcd_pos_of_pos_left m hT)
  have hTn : Nat.gcd T n ≠ 0 := Nat.ne_of_gt (Nat.gcd_pos_of_pos_left n hT)
  have hmn : Nat.lcm m n ≠ 0 := Nat.ne_of_gt (Nat.lcm_pos hm hn)
  have hleft : Nat.lcm (Nat.gcd T m) (Nat.gcd T n) ≠ 0 :=
    Nat.ne_of_gt (Nat.lcm_pos (Nat.gcd_pos_of_pos_left m hT)
      (Nat.gcd_pos_of_pos_left n hT))
  have hright : Nat.gcd T (Nat.lcm m n) ≠ 0 :=
    Nat.ne_of_gt (Nat.gcd_pos_of_pos_left (Nat.lcm m n) hT)
  apply Nat.factorization_inj hleft hright
  rw [Nat.factorization_lcm hTm hTn,
      Nat.factorization_gcd hT.ne' hm.ne',
      Nat.factorization_gcd hT.ne' hn.ne',
      Nat.factorization_gcd hT.ne' hmn,
      Nat.factorization_lcm hm.ne' hn.ne']
  ext p
  simp
  omega

/-- Canonical reduced divisor width attached to a positive section/radix width `m`. -/
def sectionDivIdx (hT : 0 < T) (m : ℕ) : DivIdx T := gcdDivIdx hT m

@[simp] lemma sectionDivIdx_val (hT : 0 < T) (m : ℕ) :
    (sectionDivIdx hT m).1 = Nat.gcd T m := rfl

lemma sectionDivIdx_lcm
    (hT : 0 < T) (m n : ℕ) (hm : 0 < m) (hn : 0 < n) :
    lcmIdx hT (sectionDivIdx hT m) (sectionDivIdx hT n) =
      sectionDivIdx hT (Nat.lcm m n) := by
  apply Subtype.ext
  exact gcd_lcm_fixed_left T m n hT hm hn

lemma sectionDivIdx_one (hT : 0 < T) :
    sectionDivIdx hT 1 = oneDivIdx hT := by
  apply Subtype.ext
  simp [sectionDivIdx, gcdDivIdx, oneDivIdx]

section Fourier

variable [NeZero T]

/-- Physical Reynolds projector indexed by a raw positive section width `m`, canonically reduced
through `gcd(T,m)`. -/
def sectionReynolds (hT : 0 < T) (m : ℕ) : Module.End ℂ (ResidueProfile T) :=
  reynoldsProjector (sectionDivIdx hT m)

/-- The section-indexed projector is literally the finite subgroup Reynolds average at
`gcd(T,m)`. -/
lemma sectionReynolds_eq_subgroupAverage (hT : 0 < T) (m : ℕ) :
    sectionReynolds hT m = subgroupReynoldsAverage (sectionDivIdx hT m) := by
  exact (subgroupReynoldsAverage_eq_reynoldsProjector hT (sectionDivIdx hT m)).symm

lemma sectionReynolds_idempotent (hT : 0 < T) (m : ℕ) :
    (sectionReynolds hT m).comp (sectionReynolds hT m) = sectionReynolds hT m :=
  reynoldsProjector_idempotent (sectionDivIdx hT m)

lemma sectionReynolds_commute (hT : 0 < T) (m n : ℕ) :
    (sectionReynolds hT m).comp (sectionReynolds hT n) =
      (sectionReynolds hT n).comp (sectionReynolds hT m) :=
  reynoldsProjector_commute (sectionDivIdx hT m) (sectionDivIdx hT n)

/-- Exact raw-radix lcm law after canonical reduction through `gcd(T,·)`. -/
lemma sectionReynolds_comp_lcm
    (hT : 0 < T) (m n : ℕ) (hm : 0 < m) (hn : 0 < n) :
    (sectionReynolds hT m).comp (sectionReynolds hT n) =
      sectionReynolds hT (Nat.lcm m n) := by
  unfold sectionReynolds
  rw [reynoldsProjector_comp_lcm hT, sectionDivIdx_lcm hT m n hm hn]

/-- Exact two-radix range intersection law. -/
lemma sectionReynolds_range_inf
    (hT : 0 < T) (m n : ℕ) (hm : 0 < m) (hn : 0 < n) :
    LinearMap.range (sectionReynolds hT (Nat.lcm m n)) =
      LinearMap.range (sectionReynolds hT m) ⊓ LinearMap.range (sectionReynolds hT n) := by
  unfold sectionReynolds
  rw [← sectionDivIdx_lcm hT m n hm hn]
  exact reynoldsProjector_range_inf hT (sectionDivIdx hT m) (sectionDivIdx hT n)

lemma sectionReynolds_one (hT : 0 < T) :
    sectionReynolds hT 1 = LinearMap.id := by
  unfold sectionReynolds
  rw [sectionDivIdx_one hT]
  exact reynoldsProjector_one hT

/-- Positive finite lcm fold. -/
def sectionLcmList : List ℕ → ℕ
  | [] => 1
  | m :: ms => Nat.lcm m (sectionLcmList ms)

@[simp] lemma sectionLcmList_nil : sectionLcmList [] = 1 := rfl
@[simp] lemma sectionLcmList_cons (m : ℕ) (ms : List ℕ) :
    sectionLcmList (m :: ms) = Nat.lcm m (sectionLcmList ms) := rfl

lemma sectionLcmList_pos {ms : List ℕ} (hms : ms.Forall (fun m => 0 < m)) :
    0 < sectionLcmList ms := by
  induction ms with
  | nil => simp [sectionLcmList]
  | cons m ms ih =>
      simp only [List.forall_cons] at hms
      simp only [sectionLcmList]
      exact Nat.lcm_pos hms.1 (ih hms.2)

/-- Ordered product of raw-radix Reynolds projectors. -/
def sectionReynoldsList (hT : 0 < T) : List ℕ → Module.End ℂ (ResidueProfile T)
  | [] => LinearMap.id
  | m :: ms => (sectionReynolds hT m).comp (sectionReynoldsList hT ms)

@[simp] lemma sectionReynoldsList_nil (hT : 0 < T) :
    sectionReynoldsList hT [] = LinearMap.id := rfl
@[simp] lemma sectionReynoldsList_cons (hT : 0 < T) (m : ℕ) (ms : List ℕ) :
    sectionReynoldsList hT (m :: ms) =
      (sectionReynolds hT m).comp (sectionReynoldsList hT ms) := rfl

/-- Finite-family raw-radix product collapses to one projector at the finite lcm. -/
lemma sectionReynoldsList_eq_lcm
    (hT : 0 < T) (ms : List ℕ) (hms : ms.Forall (fun m => 0 < m)) :
    sectionReynoldsList hT ms = sectionReynolds hT (sectionLcmList ms) := by
  induction ms with
  | nil =>
      simpa using (sectionReynolds_one hT).symm
  | cons m ms ih =>
      simp only [List.forall_cons] at hms
      rw [sectionReynoldsList_cons, ih hms.2, sectionLcmList_cons]
      exact sectionReynolds_comp_lcm hT m (sectionLcmList ms) hms.1
        (sectionLcmList_pos hms.2)

/-- Recursive finite intersection of raw-radix projector ranges. -/
def sectionRangeInf (hT : 0 < T) : List ℕ → Submodule ℂ (ResidueProfile T)
  | [] => ⊤
  | m :: ms => LinearMap.range (sectionReynolds hT m) ⊓ sectionRangeInf hT ms

@[simp] lemma sectionRangeInf_nil (hT : 0 < T) : sectionRangeInf hT [] = ⊤ := rfl
@[simp] lemma sectionRangeInf_cons (hT : 0 < T) (m : ℕ) (ms : List ℕ) :
    sectionRangeInf hT (m :: ms) =
      LinearMap.range (sectionReynolds hT m) ⊓ sectionRangeInf hT ms := rfl

lemma range_sectionReynolds_one (hT : 0 < T) :
    LinearMap.range (sectionReynolds hT 1) = ⊤ := by
  rw [sectionReynolds_one hT]
  exact LinearMap.range_id

/-- Finite-family range intersection is exactly the range at the finite lcm. -/
lemma sectionReynolds_lcmList_range
    (hT : 0 < T) (ms : List ℕ) (hms : ms.Forall (fun m => 0 < m)) :
    LinearMap.range (sectionReynolds hT (sectionLcmList ms)) = sectionRangeInf hT ms := by
  induction ms with
  | nil =>
      simpa using range_sectionReynolds_one hT
  | cons m ms ih =>
      simp only [List.forall_cons] at hms
      rw [sectionLcmList_cons,
        sectionReynolds_range_inf hT m (sectionLcmList ms) hms.1 (sectionLcmList_pos hms.2),
        ih hms.2, sectionRangeInf_cons]

/-- Same finite intersection theorem stated for the actual finite product. -/
lemma sectionReynoldsList_range
    (hT : 0 < T) (ms : List ℕ) (hms : ms.Forall (fun m => 0 < m)) :
    LinearMap.range (sectionReynoldsList hT ms) = sectionRangeInf hT ms := by
  rw [sectionReynoldsList_eq_lcm hT ms hms]
  exact sectionReynolds_lcmList_range hT ms hms

end Fourier

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.gcd_lcm_fixed_left
#print axioms KomorebiCrossRadix.sectionReynolds_eq_subgroupAverage
#print axioms KomorebiCrossRadix.sectionReynolds_comp_lcm
#print axioms KomorebiCrossRadix.sectionReynolds_range_inf
#print axioms KomorebiCrossRadix.sectionReynoldsList_eq_lcm
#print axioms KomorebiCrossRadix.sectionReynolds_lcmList_range
