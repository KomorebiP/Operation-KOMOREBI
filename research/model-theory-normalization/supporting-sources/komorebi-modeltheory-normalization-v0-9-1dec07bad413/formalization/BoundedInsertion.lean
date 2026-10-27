module
public import BoundedBezout
public import EchelonCanonical

@[expose] public section
namespace Komorebi.Echelon.Cost

/-- The Bézout update matrix has determinant one, even at nonunit pivots. -/
theorem bounded_update_data (q a : ℤ) (hq : 0 < q) :
    let g : ℤ := Int.gcd q a
    0 < g ∧ q = g*(q/g) ∧ a = g*(a/g) ∧
    (smallBezout q a).1*(q/g) + (smallBezout q a).2*(a/g) = 1 := by
  dsimp only
  have hg : (0:ℤ) < Int.gcd q a := by
    exact_mod_cast Int.gcd_pos_of_ne_zero_left a (ne_of_gt hq)
  have hq' : q = (Int.gcd q a : ℤ)*(q/(Int.gcd q a : ℤ)) := by
    simpa only [mul_comm] using (Int.ediv_mul_cancel (Int.gcd_dvd_left q a)).symm
  have ha' : a = (Int.gcd q a : ℤ)*(a/(Int.gcd q a : ℤ)) := by
    simpa only [mul_comm] using (Int.ediv_mul_cancel (Int.gcd_dvd_right q a)).symm
  refine ⟨hg,hq',ha',?_⟩
  apply mul_left_cancel₀ (ne_of_gt hg)
  calc
    (Int.gcd q a : ℤ)*((smallBezout q a).1*(q/Int.gcd q a) +
        (smallBezout q a).2*(a/Int.gcd q a)) = q*(smallBezout q a).1+a*(smallBezout q a).2 := by
      linear_combination -((smallBezout q a).1)*hq' - ((smallBezout q a).2)*ha'
    _ = (Int.gcd q a : ℤ)*1 := by rw [smallBezout_correct q a hq]; ring

/-- Insert one vector using one Bézout two-row update per column. No pivot is inverted. -/
def boundedInsert : {n : Nat} → Basis n → (Fin n → ℤ) → Basis n
  | 0, .nil, _ => .nil
  | _+1, .cons q hq b B, v =>
      let g : ℤ := Int.gcd q (v 0)
      let s := (smallBezout q (v 0)).1
      let t := (smallBezout q (v 0)).2
      .cons g (bounded_update_data q (v 0) hq).1
        (s • b + t • tailV v)
        (boundedInsert B ((-(v 0/g)) • b + (q/g) • tailV v))

/-- Exact integer span enlargement, not its saturation and not a rational span. -/
theorem boundedInsert_correct {n : Nat} (B : Basis n) (v x : Fin n → ℤ) :
    Represents (boundedInsert B v) x ↔ ∃ c : ℤ, Represents B (x-c • v) := by
  induction B with
  | nil =>
      constructor
      · intro _; exact ⟨0,0,Subsingleton.elim _ _⟩
      · intro _; exact ⟨0,Subsingleton.elim _ _⟩
  | cons q hq b B ih =>
      let g : ℤ := Int.gcd q (v 0)
      let s := (smallBezout q (v 0)).1
      let t := (smallBezout q (v 0)).2
      let Q := q/g
      let A := v 0/g
      have data := bounded_update_data q (v 0) hq
      have hq' : q = g*Q := data.2.1
      have hv' : v 0 = g*A := data.2.2.1
      have hdet : s*Q+t*A=1 := data.2.2.2
      change Represents (.cons g _ (s • b+t • tailV v)
        (boundedInsert B ((-A) • b+Q • tailV v))) x ↔ _
      rw [represents_cons_iff]
      constructor
      · rintro ⟨a,ha,htail⟩
        obtain ⟨c,hc⟩ := (ih _ _).mp htail
        refine ⟨a*t+c*Q, (represents_cons_iff q hq b B _).mpr
          ⟨a*s-c*A, ?_, ?_⟩⟩
        · simp only [Pi.sub_apply,Pi.smul_apply,smul_eq_mul]
          rw [ha,hv',hq']
          linear_combination -(a*g)*hdet
        · have he : tailV (x-(a*t+c*Q) • v)-(a*s-c*A) • b =
              (tailV x-a • (s • b+t • tailV v))-c • ((-A) • b+Q • tailV v) := by
            ext j
            simp only [tailV,Pi.sub_apply,Pi.smul_apply,Pi.add_apply,smul_eq_mul]
            ring
          rw [he]
          exact hc
      · rintro ⟨z,hz⟩
        obtain ⟨a,ha,ht⟩ := (represents_cons_iff q hq b B _).mp hz
        refine ⟨a*Q+z*A,?_,(ih _ _).mpr ⟨-a*t+z*s,?_⟩⟩
        · simp only [Pi.sub_apply,Pi.smul_apply,smul_eq_mul] at ha
          rw [hq',hv'] at ha
          linear_combination ha
        · have he : (tailV x-(a*Q+z*A) • (s • b+t • tailV v))-
              (-a*t+z*s) • ((-A) • b+Q • tailV v) =
              tailV (x-z • v)-a • b := by
            ext j
            simp only [tailV,Pi.sub_apply,Pi.smul_apply,Pi.add_apply,smul_eq_mul]
            linear_combination -(a*b j+z*v j.succ)*hdet
          rw [he]
          exact ht

/-- The executable update realizes the exact module join. -/
theorem lattice_boundedInsert {n : Nat} (B : Basis n) (v : Fin n → ℤ) :
    lattice (boundedInsert B v) = lattice B ⊔ Submodule.span ℤ {v} := by
  ext x
  change Represents (boundedInsert B v) x ↔ _
  rw [boundedInsert_correct,Submodule.mem_sup]
  constructor
  · rintro ⟨c,hc⟩
    exact ⟨x-c • v,hc,c • v,Submodule.mem_span_singleton.mpr ⟨c,rfl⟩,by abel⟩
  · rintro ⟨y,hy,z,hz,he⟩
    obtain ⟨c,rfl⟩ := Submodule.mem_span_singleton.mp hz
    refine ⟨c,?_⟩
    have hx : x-c • v=y := by rw [← he]; abel
    rw [hx]; exact hy

/-- Bounded-coefficient insertion has the same canonical cache as the old algorithm. -/
def boundedNormalizedInsert {n : Nat} (B : Basis n) (v : Fin n → ℤ) : Basis n :=
  normalize (boundedInsert B v)

theorem boundedNormalizedInsert_eq {n : Nat} (B : Basis n) (v : Fin n → ℤ) :
    boundedNormalizedInsert B v=normalizedInsert B v := by
  apply (normalize_eq_iff_lattice_eq _ _).mpr
  rw [lattice_boundedInsert, lattice_insert]

end Komorebi.Echelon.Cost
