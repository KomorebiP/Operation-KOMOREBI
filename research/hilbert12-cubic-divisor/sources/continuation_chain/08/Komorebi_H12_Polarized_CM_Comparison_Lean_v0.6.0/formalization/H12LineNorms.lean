module
public import Mathlib.Algebra.BigOperators.Fin
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.FieldSimp
@[expose] public section
namespace H12.LineNorms

/-- Four order-three subgroups of the explicit two-dimensional F3 grid. -/
def lineProducts {K : Type*} [CommRing K] (f : Fin 3 → Fin 3 → K) : Fin 4 → K :=
  ![f 0 0 * f 1 0 * f 2 0,
    f 0 0 * f 0 1 * f 0 2,
    f 0 0 * f 1 1 * f 2 2,
    f 0 0 * f 1 2 * f 2 1]

/-- Each nonzero grid point occurs on exactly one line; the origin on four. -/
theorem four_line_incidence {K : Type*} [CommRing K]
    (f : Fin 3 → Fin 3 → K) :
    (∏ i : Fin 4, lineProducts f i) =
      (f 0 0)^3 * (∏ i : Fin 3, ∏ j : Fin 3, f i j) := by
  simp [lineProducts, Fin.prod_univ_succ, pow_succ]
  ring

/-- The norm-one case gives exact cube reconstruction, not a root choice. -/
theorem cube_reconstruction {K : Type*} [CommRing K]
    (f : Fin 3 → Fin 3 → K) (hn : (∏ i : Fin 3, ∏ j : Fin 3, f i j)=1) :
    (∏ i : Fin 4, lineProducts f i) = (f 0 0)^3 := by
  rw [four_line_incidence, hn, mul_one]

/-- Reconstruction with an arbitrary nonzero total norm. -/
theorem cube_reconstruction_with_norm {K : Type*} [Field K]
    (f : Fin 3 → Fin 3 → K) (hn : (∏ i : Fin 3, ∏ j : Fin 3, f i j) ≠ 0) :
    (f 0 0)^3 = (∏ i : Fin 4, lineProducts f i) /
      (∏ i : Fin 3, ∏ j : Fin 3, f i j) := by
  rw [four_line_incidence, mul_div_cancel_right₀ _ hn]

/-- Pure algebra behind the positive-real polarization. Barred variables here
are supplied independently; their interpretation as conjugates is separate. -/
theorem polarized_product {K : Type*} [Field K]
    (u w e eb a ab d db : K) (hw : w ≠ 0) (hd : d ≠ 0)
    (hu : u^3 = w*e*eb^2*a^2*ab^3*db^2/d) :
    u^3 * (e*a*d^3/w) = (e*eb)^2*(a*ab)^3*(d*db)^2 := by
  rw [hu]
  field_simp

end H12.LineNorms
