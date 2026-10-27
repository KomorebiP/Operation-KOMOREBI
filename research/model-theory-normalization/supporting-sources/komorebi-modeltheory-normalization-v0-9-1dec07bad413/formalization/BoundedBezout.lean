module
public import EchelonBounds

@[expose] public section
namespace Komorebi.Echelon.Cost

/-- Recursive extended Euclid with explicitly bounded returned coefficients. -/
def euclidCoeff (a b : Nat) : ℤ × ℤ :=
  if _h : b = 0 then (1, 0)
  else
    let z := euclidCoeff b (a % b)
    (z.2, z.1 - (a / b : Nat) * z.2)
termination_by b
decreasing_by exact Nat.mod_lt _ (Nat.pos_of_ne_zero _h)

@[simp] theorem euclidCoeff_zero (a : Nat) : euclidCoeff a 0 = (1,0) := by
  rw [euclidCoeff]; simp

theorem euclidCoeff_step (a b : Nat) (hb : b ≠ 0) :
    euclidCoeff a b =
    ((euclidCoeff b (a%b)).2,
      (euclidCoeff b (a%b)).1 - (a/b:Nat)*(euclidCoeff b (a%b)).2) := by
  rw [euclidCoeff]; simp [hb]

/-- The returned coefficients satisfy the actual integer Bézout identity. -/
theorem euclidCoeff_correct (a b : Nat) :
    (a:ℤ)*(euclidCoeff a b).1+(b:ℤ)*(euclidCoeff a b).2 = (a.gcd b : Nat) := by
  induction b using Nat.strong_induction_on generalizing a with
  | h b ih =>
    by_cases hb : b=0
    · subst b; simp
    · rw [euclidCoeff_step a b hb]
      have hi := ih (a%b) (Nat.mod_lt a (Nat.pos_of_ne_zero hb)) b
      have he : (a:ℤ) = (a/b:Nat)*(b:ℤ)+(a%b:Nat) := by
        exact_mod_cast (show a=a/b*b+a%b by nlinarith [Nat.div_add_mod a b])
      have hg : a.gcd b = b.gcd (a%b) := by
        calc a.gcd b = b.gcd a := Nat.gcd_comm a b
             _ = (a%b).gcd b := Nat.gcd_rec b a
             _ = b.gcd (a%b) := Nat.gcd_comm _ _
      rw [hg]
      linear_combination hi + (euclidCoeff b (a%b)).2 * he

/-- Uniform coefficient bounds, including zero arguments. -/
theorem euclidCoeff_bounds (a b : Nat) :
    |(euclidCoeff a b).1| ≤ (max 1 b : Nat) ∧
    |(euclidCoeff a b).2| ≤ (max 1 a : Nat) := by
  induction b using Nat.strong_induction_on generalizing a with
  | h b ih =>
    by_cases hb : b=0
    · subst b; simp
    · rw [euclidCoeff_step a b hb]
      have hbpos : 0<b := Nat.pos_of_ne_zero hb
      have hi := ih (a%b) (Nat.mod_lt a hbpos) b
      have hb1 : max 1 b=b := max_eq_right hbpos
      rw [hb1] at hi
      refine ⟨by simpa [hb1] using hi.2, ?_⟩
      by_cases hr : a%b=0
      · simp [hr]
      · have hr1 : max 1 (a%b)=a%b := max_eq_right (Nat.pos_of_ne_zero hr)
        rw [hr1] at hi
        have hq : (0:ℤ) ≤ (a/b:Nat) := by positivity
        calc
          |(euclidCoeff b (a%b)).1-(a/b:Nat)*(euclidCoeff b (a%b)).2|
              ≤ |(euclidCoeff b (a%b)).1|+
                  |(a/b:Nat)*(euclidCoeff b (a%b)).2| := abs_sub _ _
          _ = |(euclidCoeff b (a%b)).1|+
                  (a/b:Nat)*|(euclidCoeff b (a%b)).2| := by
                    rw [abs_mul, abs_of_nonneg hq]
          _ ≤ (a%b:Nat)+(a/b:Nat)*(b:ℤ) := by
            gcongr
            · exact hi.1
            · exact hi.2
          _ = (a:ℤ) := by exact_mod_cast (show a%b+a/b*b=a by nlinarith [Nat.mod_add_div a b])
          _ ≤ (max 1 a : Nat) := by exact_mod_cast le_max_right 1 a

/-- Signed-input coefficients for the exact basis insertion interface. -/
def smallBezout (q a : ℤ) : ℤ × ℤ :=
  let z := euclidCoeff q.natAbs a.natAbs
  (z.1, if 0 ≤ a then z.2 else -z.2)

 theorem smallBezout_correct (q a : ℤ) (hq : 0<q) :
    q*(smallBezout q a).1+a*(smallBezout q a).2=(Int.gcd q a : ℤ) := by
  have he := euclidCoeff_correct q.natAbs a.natAbs
  have hq' : (q.natAbs:ℤ)=q := by rw [Int.natCast_natAbs, abs_of_pos hq]
  simp only [smallBezout]
  split
  · rename_i ha
    have ha' : (a.natAbs:ℤ)=a := by rw [Int.natCast_natAbs, abs_of_nonneg ha]
    simpa only [hq',ha',Int.gcd_def] using he
  · rename_i ha
    have ha' : (a.natAbs:ℤ)=-a := by rw [Int.natCast_natAbs, abs_of_neg (lt_of_not_ge ha)]
    rw [hq',ha'] at he
    simpa only [Int.gcd_def, neg_mul, mul_neg] using he

 theorem smallBezout_bounds (q a : ℤ) (hq : 0<q) :
    |(smallBezout q a).1| ≤ |a|+1 ∧ |(smallBezout q a).2| ≤ q := by
  have hb := euclidCoeff_bounds q.natAbs a.natAbs
  have hq' : (q.natAbs:ℤ)=q := by rw [Int.natCast_natAbs, abs_of_pos hq]
  have hq1 : max 1 q.natAbs=q.natAbs := max_eq_right (by omega)
  rw [hq1,hq'] at hb
  have ha : ((max 1 a.natAbs : Nat):ℤ) ≤ |a|+1 := by
    rw [Nat.cast_max, Int.natCast_natAbs]; simp only [Nat.cast_one]
    exact max_le (by linarith [abs_nonneg a]) (by omega)
  refine ⟨le_trans hb.1 ha, ?_⟩
  simp only [smallBezout]
  split
  · exact hb.2
  · simpa only [abs_neg] using hb.2

/-- Largest high-level arithmetic value in the recursive extended-Euclid calculation.
This records inputs, quotient, product, coefficient update, and recursive calls.
It does not model the internals of machine integer multiplication or division. -/
def euclidPeak (a b : Nat) : ℤ :=
  if _h : b=0 then max (a:ℤ) 1
  else
    let z := euclidCoeff b (a%b)
    max (a:ℤ) (max (b:ℤ) (max (a/b:Nat)
      (max |(a/b:Nat)*z.2| (max |z.1-(a/b:Nat)*z.2|
        (euclidPeak b (a%b))))))
termination_by b
decreasing_by exact Nat.mod_lt _ (Nat.pos_of_ne_zero _h)

/-- All temporary coefficient products in extended Euclid are bounded by its inputs. -/
theorem euclidPeak_bound (a b : Nat) (M : ℤ)
    (hM : 1≤M) (ha : (a:ℤ)≤M) (hb : (b:ℤ)≤M) :
    euclidPeak a b≤M := by
  induction b using Nat.strong_induction_on generalizing a with
  | h b ih =>
    by_cases hz : b=0
    · subst b; simp only [euclidPeak, ↓reduceDIte, max_le_iff]; exact ⟨ha,hM⟩
    · have hp := Nat.pos_of_ne_zero hz
      have hr : (a%b:ℤ)≤M := by
        have h : a%b<b := Nat.mod_lt a hp
        exact le_trans (by exact_mod_cast Nat.le_of_lt h) hb
      have hq : (a/b:ℤ)≤M := le_trans (by exact_mod_cast Nat.div_le_self a b) ha
      have hcoeff := (euclidCoeff_bounds b (a%b)).2
      rw [max_eq_right hp] at hcoeff
      have hprod : |(a/b:Nat)*(euclidCoeff b (a%b)).2|≤M := by
        rw [abs_mul, abs_of_nonneg (by positivity : (0:ℤ)≤(a/b:Nat))]
        calc (a/b:Nat)*|(euclidCoeff b (a%b)).2| ≤ (a/b:Nat)*(b:ℤ) := by gcongr
             _ ≤ (a:ℤ) := by exact_mod_cast (Nat.div_mul_le_self a b)
             _ ≤ M := ha
      have hout : |(euclidCoeff b (a%b)).1-(a/b:Nat)*(euclidCoeff b (a%b)).2|≤M := by
        have hh := (euclidCoeff_bounds a b).2
        rw [euclidCoeff_step a b hz] at hh
        exact le_trans hh (by exact_mod_cast (show max (1:ℤ) (a:ℤ)≤M from max_le hM ha))
      rw [euclidPeak]; simp only [hz, ↓reduceDIte, max_le_iff]
      exact ⟨ha,hb,hq,hprod,hout,ih (a%b) (Nat.mod_lt a hp) b hb hr⟩

end Komorebi.Echelon.Cost
