module

public import FiniteUnits
public import DyadicUnits

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.UnitRefinement

variable (p : ℕ) [Fact p.Prime]

def reduce (L K : ℕ) (h : K ≤ L) : ZMod (p^(L+1)) →+* ZMod (p^(K+1)) :=
  ZMod.castHom (pow_dvd_pow p (by omega : K+1 ≤ L+1)) (ZMod (p^(K+1)))

def reduceUnits (L K : ℕ) (h : K ≤ L) :
    (ZMod (p^(L+1)))ˣ →* (ZMod (p^(K+1)))ˣ :=
  Units.map (reduce p L K h).toMonoidHom

/-- The explicit roots commute with loss of precision. -/
theorem omega_compatible (L K : ℕ) (h : K ≤ L) (a : (ZMod (p^(L+1)))ˣ) :
    reduceUnits p L K h (FiniteUnits.omega p L a) =
      FiniteUnits.omega p K (reduceUnits p L K h a) := by
  obtain ⟨d, rfl⟩ := Nat.exists_eq_add_of_le h
  simp only [FiniteUnits.omega, map_pow, pow_add p K d, pow_mul]
  exact FiniteUnits.root_fixed_by_prime_power p K d
    (FiniteUnits.omega p K (reduceUnits p (K+d) K h a))
    (FiniteUnits.omega_root p K _)

theorem principal_compatible (L K : ℕ) (h : K ≤ L) (a : (ZMod (p^(L+1)))ˣ) :
    reduceUnits p L K h (FiniteUnits.principal p L a) =
      FiniteUnits.principal p K (reduceUnits p L K h a) := by
  simp only [FiniteUnits.principal, map_mul, map_inv, omega_compatible]

/-- A principal factor has p-power order, with a proved bound. -/
theorem principal_power (L : ℕ) (a : (ZMod (p^(L+1)))ˣ) :
    (FiniteUnits.principal p L a)^(p^L)=1 := by
  have hr := FiniteUnits.principal_residue p L a
  have he : FiniteUnits.residue p L
      (FiniteUnits.principal p L a : ZMod (p^(L+1))) =
      FiniteUnits.residue p L (1 : ZMod (p^(L+1))) := by
    have he := congrArg (fun u : (ZMod p)ˣ => (u : ZMod p)) hr
    change FiniteUnits.residue p L (FiniteUnits.principal p L a : ZMod (p^(L+1))) = 1 at he
    rw [map_one]
    exact he
  have h := FiniteUnits.power_lift_congruence p L _ _ he
  apply Units.ext
  simpa using h

theorem base_precision_principal (a : (ZMod (p^(0+1)))ˣ) :
    FiniteUnits.principal p 0 a = 1 := by
  simpa using principal_power p 0 a

end KomorebiPaperIX.UnitRefinement
