import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Fintype.EquivFin
import Mathlib.Tactic

/-! Actual simultaneous-translation orbits used in the tame tensor decomposition. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TameTensorOrbits

variable (n m : ℕ)

/-- The diagonal cyclic subgroup has order `lcm n m`. -/
def diagonal : ZMod (Nat.lcm n m) →+* ZMod n × ZMod m :=
  ZMod.castHom (dvd_refl (Nat.lcm n m)) _

theorem diagonal_injective : Function.Injective (diagonal n m) :=
  ZMod.castHom_injective _

@[simp] theorem diagonal_intCast (k : ℤ) :
    diagonal n m (k : ZMod (Nat.lcm n m)) = ((k : ZMod n), (k : ZMod m)) := by
  rw [map_intCast]
  rfl

@[simp] theorem diagonal_natCast (k : ℕ) :
    diagonal n m (k : ZMod (Nat.lcm n m)) = ((k : ZMod n), (k : ZMod m)) := by
  rw [map_natCast]
  rfl

/-- The difference of the coordinates modulo the gcd. -/
def difference (x : ZMod n × ZMod m) : ZMod (Nat.gcd n m) :=
  ZMod.castHom (Nat.gcd_dvd_right n m) _ x.2 -
    ZMod.castHom (Nat.gcd_dvd_left n m) _ x.1

theorem difference_diagonal (t : ZMod (Nat.lcm n m)) :
    difference n m (diagonal n m t) = 0 := by
  obtain ⟨k, rfl⟩ := ZMod.intCast_surjective t
  simp [difference, diagonal]

theorem difference_add (x y : ZMod n × ZMod m) :
    difference n m (x + y) = difference n m x + difference n m y := by
  simp only [difference, Prod.fst_add, Prod.snd_add, map_add]
  abel

/-- Orbit coordinates, with representative `(0,i)` and positive simultaneous translation. -/
def orbitMap (x : Fin (Nat.gcd n m) × ZMod (Nat.lcm n m)) : ZMod n × ZMod m :=
  diagonal n m x.2 + (0, (x.1.val : ZMod m))

theorem orbitMap_apply (i : Fin (Nat.gcd n m)) (t : ZMod (Nat.lcm n m)) :
    orbitMap n m (i,t) =
      ((ZMod.cast t : ZMod n), (ZMod.cast t : ZMod m) + (i.val : ZMod m)) := by
  ext <;> simp [orbitMap, diagonal]

@[simp] theorem orbitMap_zero (i : Fin (Nat.gcd n m)) :
    orbitMap n m (i,0) = (0, (i.val : ZMod m)) := by
  simp [orbitMap]

@[simp] theorem difference_orbitMap (x : Fin (Nat.gcd n m) × ZMod (Nat.lcm n m)) :
    difference n m (orbitMap n m x) = (x.1.val : ZMod (Nat.gcd n m)) := by
  rw [orbitMap, difference_add, difference_diagonal]
  simp [difference]

theorem orbitMap_injective : Function.Injective (orbitMap n m) := by
  rintro ⟨i,t⟩ ⟨j,u⟩ h
  have hij := congrArg (difference n m) h
  simp only [difference_orbitMap] at hij
  have hij' : i = j := by
    apply Fin.ext
    have heq := (ZMod.natCast_eq_natCast_iff' i.val j.val (Nat.gcd n m)).mp hij
    simpa only [Nat.mod_eq_of_lt i.isLt, Nat.mod_eq_of_lt j.isLt] using heq
  subst j
  have htu : t = u := diagonal_injective n m (add_right_cancel h)
  subst u
  rfl

variable [NeZero n] [NeZero m]

instance lcm_neZero : NeZero (Nat.lcm n m) :=
  ⟨Nat.lcm_ne_zero (NeZero.ne n) (NeZero.ne m)⟩

instance gcd_neZero : NeZero (Nat.gcd n m) :=
  ⟨Nat.ne_of_gt (Nat.gcd_pos_of_pos_left m (Nat.pos_of_ne_zero (NeZero.ne n)))⟩

theorem orbitMap_bijective : Function.Bijective (orbitMap n m) := by
  rw [Fintype.bijective_iff_injective_and_card]
  refine ⟨orbitMap_injective n m, ?_⟩
  simp only [Fintype.card_prod, Fintype.card_fin, ZMod.card]
  exact Nat.gcd_mul_lcm n m

/-- Explicit decomposition of the pair-index set into gcd-many lcm-cycles. -/
def orbitEquiv : (Fin (Nat.gcd n m) × ZMod (Nat.lcm n m)) ≃ (ZMod n × ZMod m) :=
  Equiv.ofBijective (orbitMap n m) (orbitMap_bijective n m)

@[simp] theorem orbitEquiv_apply (x : Fin (Nat.gcd n m) × ZMod (Nat.lcm n m)) :
    orbitEquiv n m x = orbitMap n m x := rfl

omit [NeZero n] [NeZero m] in
theorem orbitMap_translate (i : Fin (Nat.gcd n m)) (t k : ZMod (Nat.lcm n m)) :
    orbitMap n m (i,t+k) = orbitMap n m (i,t) + diagonal n m k := by
  simp only [orbitMap, map_add]
  abel

/-- Integer simultaneous translation on the actual pair-index set. -/
def translate (k : ℤ) (x : ZMod n × ZMod m) : ZMod n × ZMod m :=
  x + ((k : ZMod n), (k : ZMod m))

omit [NeZero n] [NeZero m] in
theorem orbitMap_translate_int (i : Fin (Nat.gcd n m))
    (t : ZMod (Nat.lcm n m)) (k : ℤ) :
    orbitMap n m (i,t+k) = translate n m k (orbitMap n m (i,t)) := by
  rw [orbitMap_translate]
  rw [diagonal_intCast]
  rfl

omit [NeZero n] [NeZero m] in
/-- The stabilizer of every pair is precisely the integer multiples of the lcm. -/
theorem translate_eq_iff (k : ℤ) (x : ZMod n × ZMod m) :
    translate n m k x = x ↔ (Nat.lcm n m : ℤ) ∣ k := by
  rw [translate, add_eq_left]
  rw [← diagonal_intCast]
  rw [map_eq_zero_iff (diagonal n m) (diagonal_injective n m)]
  exact ZMod.intCast_zmod_eq_zero_iff_dvd k _

omit [NeZero n] [NeZero m] in
theorem interaction_count : Fintype.card (Fin (Nat.gcd n m)) = Nat.gcd n m :=
  Fintype.card_fin _

theorem interaction_length : Fintype.card (ZMod (Nat.lcm n m)) = Nat.lcm n m :=
  ZMod.card _

omit [NeZero n] [NeZero m] in
theorem total_dimension : Nat.gcd n m * Nat.lcm n m = n * m :=
  Nat.gcd_mul_lcm n m

omit [NeZero n] [NeZero m] in
theorem difference_translate (k : ℤ) (x : ZMod n × ZMod m) :
    difference n m (translate n m k x) = difference n m x := by
  rw [translate, ← diagonal_intCast, difference_add, difference_diagonal, add_zero]

/-- Equality of the gcd invariant is exactly equality of actual integer orbits. -/
theorem sameOrbit_iff (x y : ZMod n × ZMod m) :
    (∃ k : ℤ, translate n m k x = y) ↔ difference n m x = difference n m y := by
  constructor
  · rintro ⟨k, rfl⟩
    exact (difference_translate n m k x).symm
  · intro h
    obtain ⟨⟨i,t⟩, rfl⟩ := (orbitMap_bijective n m).surjective x
    obtain ⟨⟨j,u⟩, rfl⟩ := (orbitMap_bijective n m).surjective y
    simp only [difference_orbitMap] at h
    have hij : i = j := by
      apply Fin.ext
      have heq := (ZMod.natCast_eq_natCast_iff' i.val j.val (Nat.gcd n m)).mp h
      simpa only [Nat.mod_eq_of_lt i.isLt, Nat.mod_eq_of_lt j.isLt] using heq
    subst j
    obtain ⟨k, hk⟩ := ZMod.intCast_surjective (u-t)
    refine ⟨k, ?_⟩
    rw [← orbitMap_translate_int, hk, ← add_sub_assoc, add_sub_cancel_left]

/-- Distinct chosen representatives are never in the same simultaneous-translation orbit. -/
theorem representatives_sameOrbit_iff (i j : Fin (Nat.gcd n m)) :
    (∃ k : ℤ, translate n m k (0, (i.val : ZMod m)) = (0, (j.val : ZMod m))) ↔
      i = j := by
  rw [← orbitMap_zero n m i, ← orbitMap_zero n m j, sameOrbit_iff]
  simp only [difference_orbitMap]
  constructor
  · intro h
    apply Fin.ext
    have heq := (ZMod.natCast_eq_natCast_iff' i.val j.val (Nat.gcd n m)).mp h
    simpa only [Nat.mod_eq_of_lt i.isLt, Nat.mod_eq_of_lt j.isLt] using heq
  · rintro rfl
    rfl

/-- Each fiber of the actual orbit invariant is an lcm-cycle. -/
def fiberEquiv (i : Fin (Nat.gcd n m)) :
    ZMod (Nat.lcm n m) ≃
      {x : ZMod n × ZMod m // difference n m x = (i.val : ZMod (Nat.gcd n m))} :=
  Equiv.ofBijective
    (fun t => ⟨orbitMap n m (i,t), difference_orbitMap n m (i,t)⟩) (by
      constructor
      · intro t u h
        exact congrArg Prod.snd ((orbitMap_injective n m) (congrArg Subtype.val h))
      · rintro ⟨x,hx⟩
        obtain ⟨⟨j,t⟩, rfl⟩ := (orbitMap_bijective n m).surjective x
        have hji : j = i := by
          simp only [difference_orbitMap] at hx
          apply Fin.ext
          have heq := (ZMod.natCast_eq_natCast_iff' j.val i.val (Nat.gcd n m)).mp hx
          simpa only [Nat.mod_eq_of_lt j.isLt, Nat.mod_eq_of_lt i.isLt] using heq
        subst j
        exact ⟨t, rfl⟩)

theorem fiber_card (i : Fin (Nat.gcd n m)) :
    Fintype.card {x : ZMod n × ZMod m //
      difference n m x = (i.val : ZMod (Nat.gcd n m))} = Nat.lcm n m := by
  rw [← Fintype.card_congr (fiberEquiv n m i), ZMod.card]

@[simp] theorem fiberEquiv_apply (i : Fin (Nat.gcd n m)) (t : ZMod (Nat.lcm n m)) :
    (fiberEquiv n m i t).val = orbitMap n m (i,t) := rfl

/-- The inverse coordinate map intertwines translation with motion inside one cycle. -/
theorem orbitEquiv_symm_translate (k : ℤ) (x : ZMod n × ZMod m) :
    (orbitEquiv n m).symm (translate n m k x) =
      (((orbitEquiv n m).symm x).1, ((orbitEquiv n m).symm x).2 + k) := by
  obtain ⟨⟨i,t⟩, rfl⟩ := (orbitEquiv n m).surjective x
  have ht : (orbitEquiv n m).symm (orbitMap n m (i,t)) = (i,t) :=
    (orbitEquiv n m).symm_apply_apply (i,t)
  simp only [orbitEquiv_apply, ht]
  rw [← orbitMap_translate_int]
  exact (orbitEquiv n m).symm_apply_apply (i,t+k)

end PaperXI.TameTensorOrbits
