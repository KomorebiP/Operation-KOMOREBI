import Mathlib.NumberTheory.ArithmeticFunction.Moebius
import Mathlib.Dynamics.PeriodicPts.Lemmas
import Mathlib.Data.ZMod.QuotientGroup
import Mathlib.Tactic

/-! Exact-period counting for finite dynamical systems.  The count is the
cardinality of an actual subtype, not a recurrence defined to force inversion. -/
set_option autoImplicit false
namespace PaperXI.FrobeniusPeriodCount
open Function Finset
open scoped Classical

variable {X : Type*} [Finite X]

noncomputable def exactCount (f : X → X) (n : ℕ) : ℕ :=
  Nat.card {x : X // minimalPeriod f x = n}

noncomputable def fixedCount (f : X → X) (n : ℕ) : ℕ :=
  Nat.card {x : X // IsPeriodicPt f n x}

omit [Finite X] in
lemma exactCount_eq_filter (f : X → X) (n : ℕ) [Fintype X] :
    exactCount f n = (univ.filter (fun x => minimalPeriod f x = n)).card := by
  classical
  simp [exactCount, Nat.card_eq_fintype_card, Fintype.card_subtype]

omit [Finite X] in
lemma fixedCount_eq_filter (f : X → X) (n : ℕ) [Fintype X] :
    fixedCount f n = (univ.filter (fun x => IsPeriodicPt f n x)).card := by
  classical
  simp [fixedCount, Nat.card_eq_fintype_card, Fintype.card_subtype]

/-- Partition points fixed by the nth iterate by their genuine minimal period. -/
theorem sum_exactCount (f : X → X) (n : ℕ) (hn : 0 < n) :
    ∑ d ∈ n.divisors, exactCount f d = fixedCount f n := by
  classical
  let := Fintype.ofFinite X
  let S := univ.filter (fun x : X => IsPeriodicPt f n x)
  have hm : ∀ x ∈ S, minimalPeriod f x ∈ n.divisors := by
    intro x hx
    exact Nat.mem_divisors.mpr ⟨(mem_filter.mp hx).2.minimalPeriod_dvd, hn.ne'⟩
  have hs := sum_fiberwise_of_maps_to hm (fun _ => (1 : ℕ))
  simp only [sum_const, smul_eq_mul, mul_one] at hs
  rw [fixedCount_eq_filter]
  change ∑ d ∈ n.divisors, exactCount f d = S.card
  rw [← hs]
  apply sum_congr rfl
  intro d hd
  rw [exactCount_eq_filter]
  congr 1
  ext x
  simp only [S, mem_filter, mem_univ, true_and]
  constructor
  · intro hx
    exact ⟨isPeriodicPt_iff_minimalPeriod_dvd.mpr (hx ▸ (Nat.mem_divisors.mp hd).1), hx⟩
  · exact fun hx => hx.2

/-- Möbius inversion for actual exact-period points of a finite map. -/
theorem moebius_exactCount (f : X → X) (n : ℕ) (hn : 0 < n) :
    (exactCount f n : ℤ) =
      ∑ d ∈ n.divisors, ArithmeticFunction.moebius d * (fixedCount f (n / d) : ℤ) := by
  have hsum : ∀ k > 0, ∑ d ∈ k.divisors, (exactCount f d : ℤ) = (fixedCount f k : ℤ) := by
    intro k hk
    exact_mod_cast sum_exactCount f k hk
  have h := ArithmeticFunction.sum_eq_iff_sum_mul_moebius_eq.mp hsum n hn
  calc
    (exactCount f n : ℤ) =
        ∑ x ∈ n.divisorsAntidiagonal, ArithmeticFunction.moebius x.1 * (fixedCount f x.2 : ℤ) := by
      simpa only [Int.cast_id] using h.symm
    _ = _ := Nat.sum_divisorsAntidiagonal
      (fun d k => ArithmeticFunction.moebius d * (fixedCount f k : ℤ))


/-- The permutation restricted to points of exact period n. -/
noncomputable def regularPerm (e : Equiv.Perm X) (n : ℕ) :
    Equiv.Perm {x : X // minimalPeriod e x = n} :=
  e.subtypePerm (fun x => by rw [minimalPeriod_apply (e.injective.mem_periodicPts x)])

/-- Number of genuine orbits on exact-period points. -/
noncomputable def orbitCount (e : Equiv.Perm X) (n : ℕ) : ℕ :=
  Nat.card (MulAction.orbitRel.Quotient (Subgroup.zpowers (regularPerm e n))
    {x : X // minimalPeriod e x = n})

theorem regularPerm_minimalPeriod (e : Equiv.Perm X) (n : ℕ)
    (x : {x : X // minimalPeriod e x = n}) :
    minimalPeriod (regularPerm e n) x = n := by
  have hs : Semiconj Subtype.val (regularPerm e n) e := fun _ => rfl
  have hp : minimalPeriod (regularPerm e n) x = minimalPeriod e x.val := by
    apply minimalPeriod_eq_minimalPeriod_iff.mpr
    intro k
    change ((regularPerm e n)^[k] x = x) ↔ e^[k] x.val = x.val
    rw [← Subtype.val_inj, hs.iterate_right k x]
  exact hp.trans x.property

/-- Every exact-period orbit has n elements, including the n=1 fixed-point case. -/
theorem exactCount_eq_orbitCount_mul (e : Equiv.Perm X) (n : ℕ) :
    exactCount e n = orbitCount e n * n := by
  classical
  let Y := {x : X // minimalPeriod e x = n}
  let e' := regularPerm e n
  let G := Subgroup.zpowers e'
  let Q := MulAction.orbitRel.Quotient G Y
  let := Fintype.ofFinite Y
  let := Fintype.ofFinite Q
  let (y : Y) : Fintype (MulAction.orbit G y) := Fintype.ofFinite _
  have hc (y : Y) : Fintype.card (MulAction.orbit G y) = n := by
    calc
      _ = minimalPeriod e' y := (MulAction.minimalPeriod_eq_card e' y).symm
      _ = n := regularPerm_minimalPeriod e n y
  calc
    exactCount e n = Fintype.card Y := Nat.card_eq_fintype_card
    _ = Fintype.card ((w : Q) × MulAction.orbit G (Quotient.out w)) :=
      Fintype.card_congr (MulAction.selfEquivSigmaOrbits G Y)
    _ = ∑ w : Q, Fintype.card (MulAction.orbit G (Quotient.out w)) := Fintype.card_sigma
    _ = Fintype.card Q * n := by simp only [hc, sum_const, card_univ, smul_eq_mul]
    _ = orbitCount e n * n := by rw [orbitCount, Nat.card_eq_fintype_card]

/-- Integer divisibility follows from orbit cardinality, not from rounding a sum. -/
theorem period_dvd_exactCount (e : Equiv.Perm X) (n : ℕ) :
    n ∣ exactCount e n := by
  rw [exactCount_eq_orbitCount_mul]
  exact dvd_mul_left n _

end PaperXI.FrobeniusPeriodCount

