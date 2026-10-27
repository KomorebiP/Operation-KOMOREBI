module
public import EchelonPeakCore

@[expose] public section
namespace Komorebi.Echelon.Cost

/-- Arithmetic peak for the actual bounded-coefficient insertion recursion.
Includes individual products, not only their possibly cancelling sums. -/
def insertionPeak : {n : Nat} → Basis n → (Fin n → ℤ) → ℤ
  | 0, .nil, _ => 0
  | _+1, .cons q _ b B, v =>
    let a := v 0
    let g : ℤ := Int.gcd q a
    let z := smallBezout q a
    let s := z.1
    let t := z.2
    let Q := q/g
    let A := a/g
    let row := s • b+t • tailV v
    let rem := (-A) • b+Q • tailV v
    max (vectorPeak v) (max q (max g
      (max (euclidPeak q.natAbs a.natAbs) (max |s| (max |t| (max |Q| (max |A|
        (max (vectorPeak (s • b)) (max (vectorPeak (t • tailV v))
        (max (vectorPeak ((-A) • b)) (max (vectorPeak (Q • tailV v))
        (max (vectorPeak row) (max (vectorPeak rem) (insertionPeak B rem))))))))))))))

theorem boundedInsert_peak_bound {n : Nat} (m C : ℤ) (hm : 1≤m) (hC : m≤C)
    (B : Basis n) (hB : Uniform m B) (v : Fin n → ℤ) (hv : vectorPeak v≤C) :
    Uniform ((2*m)^n*C) (boundedInsert B v) ∧
    insertionPeak B v≤(2*m)^n*C := by
  induction B generalizing C with
  | nil => exact ⟨trivial, by simpa only [insertionPeak,pow_zero,one_mul] using (show (0:ℤ)≤C by omega)⟩
  | @cons n q hq b B ih =>
    let a := v 0
    let g : ℤ := Int.gcd q a
    let s := (smallBezout q a).1
    let t := (smallBezout q a).2
    let Q := q/g
    let A := a/g
    let row := s • b+t • tailV v
    let rem := (-A) • b+Q • tailV v
    let C' := 2*m*C
    have hC0 : 0≤C := by omega
    have hCm : C≤C' := by dsimp [C']; nlinarith
    have hmC : m≤C' := le_trans hC hCm
    have hgpos : 0<g := (bounded_update_data q a hq).1
    have hg : g≤m := le_trans (Int.gcd_le_left a hq) hB.1
    have ha : |a|≤C := le_trans (coord_le_peak v 0) hv
    have hs : |s|≤C := by
      have hh := (euclidCoeff_bounds q.natAbs a.natAbs).1
      apply le_trans hh
      rw [Nat.cast_max, Int.natCast_natAbs, Nat.cast_one]
      exact max_le (by omega) ha
    have ht : |t|≤m := le_trans (smallBezout_bounds q a hq).2 hB.1
    have hQ : |Q|≤m := le_trans (abs_ediv_bound q g hgpos) (by rw [abs_of_pos hq]; exact hB.1)
    have hA : |A|≤C := le_trans (abs_ediv_bound a g hgpos) ha
    have hsb : vectorPeak (s • b)≤m*C := by
      apply vectorPeak_le _ _ (by positivity)
      intro j
      simp only [Pi.smul_apply,smul_eq_mul,abs_mul]
      calc |s| * |b j|≤C*m := by gcongr; exact le_trans (coord_le_peak b j) hB.2.1
           _ = m*C := mul_comm _ _
    have htv : vectorPeak (t • tailV v)≤m*C := by
      apply vectorPeak_le _ _ (by positivity)
      intro j
      simp only [Pi.smul_apply,smul_eq_mul,abs_mul,tailV]
      gcongr
      exact le_trans (coord_le_peak v j.succ) hv
    have hAb : vectorPeak ((-A) • b)≤m*C := by
      apply vectorPeak_le _ _ (by positivity)
      intro j
      simp only [Pi.smul_apply,smul_eq_mul,abs_mul,abs_neg]
      calc |A| * |b j|≤C*m := by gcongr; exact le_trans (coord_le_peak b j) hB.2.1
           _ = m*C := mul_comm _ _
    have hQv : vectorPeak (Q • tailV v)≤m*C := by
      apply vectorPeak_le _ _ (by positivity)
      intro j
      simp only [Pi.smul_apply,smul_eq_mul,abs_mul,tailV]
      gcongr
      exact le_trans (coord_le_peak v j.succ) hv
    have hrow : vectorPeak row≤C' := by
      apply vectorPeak_le _ _ (by dsimp [C']; positivity)
      intro j
      change |s*b j+t*v j.succ|≤C'
      calc |s*b j+t*v j.succ|≤ |s*b j|+|t*v j.succ| := abs_add_le _ _
           _ ≤ m*C+m*C := add_le_add (le_trans (coord_le_peak (s • b) j) hsb)
               (le_trans (coord_le_peak (t • tailV v) j) htv)
           _ = C' := by dsimp [C']; ring
    have hrem : vectorPeak rem≤C' := by
      apply vectorPeak_le _ _ (by dsimp [C']; positivity)
      intro j
      change |(-A)*b j+Q*v j.succ|≤C'
      calc |(-A)*b j+Q*v j.succ|≤ |(-A)*b j|+|Q*v j.succ| := abs_add_le _ _
           _ ≤ m*C+m*C := add_le_add (le_trans (coord_le_peak ((-A) • b) j) hAb)
               (le_trans (coord_le_peak (Q • tailV v) j) hQv)
           _ = C' := by dsimp [C']; ring
    have heuc : euclidPeak q.natAbs a.natAbs≤C := by
      apply euclidPeak_bound _ _ C (by omega)
      · rw [Int.natCast_natAbs, abs_of_pos hq]; exact le_trans hB.1 hC
      · rwa [Int.natCast_natAbs]
    have hi := ih C' hmC hB.2.2 rem hrem
    have hcap : C'≤(2*m)^n*C' := scale_grows _ _ (by omega) (by omega) n
    have hmul : m*C≤C' := by dsimp [C']; nlinarith
    have heq : (2*m)^n*C'=(2*m)^(n+1)*C := by dsimp [C']; rw [pow_succ]; ring
    rw [←heq]
    constructor
    · change g≤_ ∧ vectorPeak row≤_ ∧ Uniform _ (boundedInsert B rem)
      exact ⟨le_trans hg (le_trans hmC hcap),le_trans hrow hcap,hi.1⟩
    · change max (vectorPeak v) (max q (max g
        (max (euclidPeak q.natAbs a.natAbs) (max |s| (max |t| (max |Q| (max |A|
        (max (vectorPeak (s • b)) (max (vectorPeak (t • tailV v))
        (max (vectorPeak ((-A) • b)) (max (vectorPeak (Q • tailV v))
        (max (vectorPeak row) (max (vectorPeak rem) (insertionPeak B rem))))))))))))))≤_
      simp only [max_le_iff]
      exact ⟨le_trans hv (le_trans hCm hcap),le_trans hB.1 (le_trans hmC hcap),
        le_trans hg (le_trans hmC hcap),le_trans heuc (le_trans hCm hcap),
        le_trans hs (le_trans hCm hcap),le_trans ht (le_trans hmC hcap),
        le_trans hQ (le_trans hmC hcap),le_trans hA (le_trans hCm hcap),
        le_trans hsb (le_trans hmul hcap),le_trans htv (le_trans hmul hcap),
        le_trans hAb (le_trans hmul hcap),le_trans hQv (le_trans hmul hcap),
        le_trans hrow hcap,le_trans hrem hcap,hi.2⟩

/-- Arithmetic peak for bottom-up tail normalization, including all residue subcalls. -/
def normalizationPeak : {n : Nat} → Basis n → ℤ
  | 0, .nil => 0
  | _+1, .cons q _ b B =>
    max q (max (vectorPeak b) (max (normalizationPeak B) (residuePeak (normalize B) b)))

theorem normalizationPeak_bound {n : Nat} (m C : ℤ) (hm : 1≤m) (hC : m≤C)
    (B : Basis n) (hB : Uniform C B) (hmod : ContainsModulus m B) :
    normalizationPeak B≤(m+1)^n*C := by
  induction B with
  | nil => simpa only [normalizationPeak,pow_zero,one_mul] using (show (0:ℤ)≤C by omega)
  | @cons n q hq b B ih =>
    have ht := containsModulus_tail m q hq b B hmod
    have hb := uniform_of_reduced m (by omega) (normalize B)
      ((containsModulus_normalize m B).mpr ht) (normalize_reduced B)
    have hr := residuePeak_bound m C hm hC (normalize B) hb b hB.2.1
    have hi := ih hB.2.2 ht
    have hc : C≤(m+1)^n*C := scale_grows _ _ (by omega) (by omega) n
    have hnext : (m+1)^n*C≤(m+1)^(n+1)*C := by
      rw [pow_succ]; nlinarith [pow_nonneg (show (0:ℤ)≤m+1 by omega) n]
    change max q (max (vectorPeak b) (max _ _))≤_
    exact max_le (le_trans hB.1 (le_trans hc hnext))
      (max_le (le_trans hB.2.1 (le_trans hc hnext))
       (max_le (le_trans hi hnext) (le_trans hr hnext)))

def updatePeak {n : Nat} (B : Basis n) (v : Fin n → ℤ) : ℤ :=
  max (insertionPeak B v) (normalizationPeak (boundedInsert B v))

/-- Uniform bound on explicit coefficient arithmetic throughout an accepted update. -/
theorem updatePeak_bound {n : Nat} (m : ℤ) (hm : 1≤m) (B : Basis n)
    (hmod : ContainsModulus m B) (hred : Reduced B)
    (v : Fin n → ℤ) (hv : vectorPeak v≤m) :
    updatePeak B v≤m*(2*m*(m+1))^n := by
  have hu := uniform_of_reduced m (by omega) B hmod hred
  have hi := boundedInsert_peak_bound m m hm (le_refl m) B hu v hv
  have hc : m≤(2*m)^n*m := scale_grows _ _ (by omega) (by omega) n
  have hmi : ContainsModulus m (boundedInsert B v) := by
    intro x
    exact (boundedInsert_correct B v _).mpr ⟨0,by simpa using hmod x⟩
  have hn := normalizationPeak_bound m ((2*m)^n*m) hm hc _ hi.1 hmi
  have hh := scale_grows (m+1) ((2*m)^n*m) (by omega) (by positivity) n
  have heq : (m+1)^n*((2*m)^n*m)=m*(2*m*(m+1))^n := by simp only [mul_pow]; ring
  rw [updatePeak,←heq]
  exact max_le (le_trans hi.2 hh) hn

end Komorebi.Echelon.Cost
