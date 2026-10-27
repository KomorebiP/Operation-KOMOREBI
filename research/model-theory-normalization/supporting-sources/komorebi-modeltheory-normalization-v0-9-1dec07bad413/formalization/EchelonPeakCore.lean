module
public import BoundedInsertion

@[expose] public section
namespace Komorebi.Echelon.Cost

/-- Maximum absolute coordinate; zero in dimension zero. -/
def vectorPeak : {n : Nat} → (Fin n → ℤ) → ℤ
  | 0, _ => 0
  | _+1, v => max |v 0| (vectorPeak (tailV v))

theorem vectorPeak_nonneg {n : Nat} (v : Fin n → ℤ) : 0≤vectorPeak v := by
  induction n with
  | zero => rfl
  | succ n _ => exact le_trans (abs_nonneg _) (le_max_left _ _)

theorem coord_le_peak {n : Nat} (v : Fin n → ℤ) (i : Fin n) : |v i|≤vectorPeak v := by
  induction n with
  | zero => exact Fin.elim0 i
  | succ n ih =>
    exact Fin.cases (le_max_left _ _) (fun j => le_trans (ih (tailV v) j) (le_max_right _ _)) i

theorem vectorPeak_le {n : Nat} (v : Fin n → ℤ) (C : ℤ) (hC : 0≤C)
    (h : ∀i, |v i|≤C) : vectorPeak v≤C := by
  induction n with
  | zero => exact hC
  | succ n ih => exact max_le (h 0) (ih _ (fun j => h j.succ))

/-- Integer Euclidean division by a positive pivot never increases absolute size. -/
theorem abs_ediv_bound (a q : ℤ) (hq : 0<q) : |a/q|≤|a| := by
  apply abs_le.mpr
  have hq1 : 1≤q := by omega
  have ha := le_abs_self a
  have hn := neg_abs_le a
  have hpos := abs_nonneg a
  constructor
  · apply (Int.le_ediv_iff_mul_le hq).mpr
    nlinarith
  · have hu : a/q< |a| +1 := (Int.ediv_lt_iff_lt_mul hq).mpr (by nlinarith)
    omega

def Uniform : {n : Nat} → ℤ → Basis n → Prop
  | 0, _, .nil => True
  | _+1, m, .cons q _ b B => q≤m ∧ vectorPeak b≤m ∧ Uniform m B

theorem uniform_of_reduced {n : Nat} (m : ℤ) (hm : 0<m) (B : Basis n)
    (hB : ContainsModulus m B) (hr : Reduced B) : Uniform m B := by
  induction B with
  | nil => trivial
  | cons q hq b B ih =>
    have ht := containsModulus_tail m q hq b B hB
    refine ⟨Int.le_of_dvd hm (containsModulus_head_dvd m q hq b B hB), ?_, ih ht hr.2⟩
    apply vectorPeak_le _ _ (le_of_lt hm)
    intro j
    have hb := inBox_bounds B b hr.1 j
    rw [abs_of_nonneg hb.1]
    exact le_trans (le_of_lt hb.2) (pivots_le_modulus m hm B ht j)

theorem uniform_tail {n : Nat} (m q : ℤ) (hq : 0<q) (b : Fin n → ℤ)
    (B : Basis n) (h : Uniform m (.cons q hq b B)) : Uniform m B := h.2.2

theorem uniform_entries {n : Nat} (m : ℤ) (hm : 0≤m) (B : Basis n)
    (h : Uniform m B) (i j : Fin n) : |entries B i j|≤m := by
  induction B with
  | nil => exact Fin.elim0 i
  | cons q hq b B ih =>
    refine Fin.cases ?_ (fun a => ?_) i
    · refine Fin.cases ?_ (fun c => ?_) j
      · change |q|≤m; rw [abs_of_pos hq]; exact h.1
      · exact le_trans (coord_le_peak b c) h.2.1
    · refine Fin.cases ?_ (fun c => ?_) j
      · exact hm
      · exact ih h.2.2 a c

theorem scale_grows (a C : ℤ) (ha : 1≤a) (hC : 0≤C) (n : Nat) :
    C≤a^n*C := by
  have hp : (1:ℤ)≤a^n := one_le_pow₀ ha
  nlinarith

/-- Peak of explicit integer values in triangular residue reduction.
The same upper bound covers the predecessor's membership solver, which stops earlier. -/
def residuePeak : {n : Nat} → Basis n → (Fin n → ℤ) → ℤ
  | 0, .nil, _ => 0
  | _+1, .cons q _ b B, v =>
    let c := v 0/q
    max (vectorPeak v) (max q (max |c| (max (vectorPeak (c • b))
      (residuePeak B (tailV v-c • b)))))

theorem residuePeak_bound {n : Nat} (m C : ℤ) (hm : 1≤m) (hC : m≤C)
    (B : Basis n) (hB : Uniform m B) (v : Fin n → ℤ) (hv : vectorPeak v≤C) :
    residuePeak B v≤(m+1)^n*C := by
  induction B generalizing C with
  | nil => simpa only [residuePeak, pow_zero, one_mul] using (show (0:ℤ)≤C by omega)
  | @cons n q hq b B ih =>
    let c := v 0/q
    let C' := (m+1)*C
    have hC0 : 0≤C := by omega
    have hc : |c|≤C := le_trans (abs_ediv_bound _ _ hq) (le_trans (coord_le_peak v 0) hv)
    have ht : vectorPeak (c • b)≤m*C := by
      apply vectorPeak_le _ _ (mul_nonneg (by omega) hC0)
      intro j
      simp only [Pi.smul_apply, smul_eq_mul, abs_mul]
      calc |c| *|b j|≤C*m := by gcongr; exact le_trans (coord_le_peak b j) hB.2.1
           _ = m*C := mul_comm _ _
    have hr : vectorPeak (tailV v-c • b)≤C' := by
      apply vectorPeak_le _ _ (by dsimp [C']; positivity)
      intro j
      change |v j.succ-c*b j|≤C'
      calc |v j.succ-c*b j|≤|v j.succ| +|c*b j| := abs_sub _ _
           _ ≤ C+m*C := add_le_add (le_trans (coord_le_peak v j.succ) hv)
               (le_trans (coord_le_peak (c • b) j) ht)
           _ = C' := by dsimp [C']; ring
    have hCC : C≤C' := by dsimp [C']; nlinarith
    have hb : m≤C' := le_trans hC hCC
    have hi := ih C' hb hB.2.2 _ hr
    have hcap : C'≤(m+1)^n*C' := scale_grows _ _ (by omega) (by omega) n
    have heq : (m+1)^n*C'=(m+1)^(n+1)*C := by dsimp [C']; rw [pow_succ]; ring
    rw [←heq]
    change max (vectorPeak v) (max q (max |c| (max (vectorPeak (c • b)) _)))≤_
    simp only [max_le_iff]
    exact ⟨le_trans hv (le_trans hCC hcap), le_trans hB.1 (le_trans hb hcap),
      le_trans hc (le_trans hCC hcap), le_trans ht (by dsimp [C'] at hcap; nlinarith), hi⟩

end Komorebi.Echelon.Cost
