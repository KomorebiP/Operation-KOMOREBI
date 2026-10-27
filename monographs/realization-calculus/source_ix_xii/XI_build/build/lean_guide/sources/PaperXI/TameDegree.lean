import PaperXI.TameTensorOrbits
import Mathlib.Algebra.Group.Subgroup.Ker
import Mathlib.Algebra.Group.TypeTags.Hom

/-! Degree subgroups and their actual cyclic translation actions. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TameDegree

variable {G : Type*} [Group G] (ν : G →* Multiplicative ℤ)

/-- The integer degree of a group element. -/
def degree (g : G) : ℤ := (ν g).toAdd

@[simp] theorem degree_one : degree ν 1 = 0 := by simp [degree]

@[simp] theorem degree_mul (g h : G) : degree ν (g*h) = degree ν g + degree ν h := by
  simp [degree]

@[simp] theorem degree_zpow (g : G) (k : ℤ) : degree ν (g^k) = k * degree ν g := by
  simp [degree, toAdd_zpow]

@[simp] theorem degree_inv (g : G) : degree ν g⁻¹ = -degree ν g := by
  simp [degree]

@[simp] theorem degree_conjugate (a g : G) : degree ν (a*g*a⁻¹) = degree ν g := by
  simp

/-- Reduction of degree modulo `n`, in multiplicative notation for induction. -/
def degreeMod (n : ℕ) : G →* Multiplicative (ZMod n) where
  toFun g := Multiplicative.ofAdd ((degree ν g : ℤ) : ZMod n)
  map_one' := by simp
  map_mul' g h := by simp [degree_mul, Int.cast_add]

@[simp] theorem degreeMod_apply (n : ℕ) (g : G) :
    degreeMod ν n g = Multiplicative.ofAdd ((degree ν g : ℤ) : ZMod n) := rfl

/-- The subgroup of elements whose degree is divisible by `n`. -/
def degreeSubgroup (n : ℕ) : Subgroup G := (degreeMod ν n).ker

@[simp] theorem mem_degreeSubgroup (n : ℕ) (g : G) :
    g ∈ degreeSubgroup ν n ↔ (n : ℤ) ∣ degree ν g := by
  change (((degree ν g : ℤ) : ZMod n) = 0) ↔ _
  exact ZMod.intCast_zmod_eq_zero_iff_dvd _ _

theorem degreeSubgroup_inter (n m : ℕ) :
    degreeSubgroup ν n ⊓ degreeSubgroup ν m = degreeSubgroup ν (Nat.lcm n m) := by
  ext g
  simp only [Subgroup.mem_inf, mem_degreeSubgroup]
  simpa using (Int.coe_lcm_dvd_iff (a := (n : ℤ)) (b := (m : ℤ))
    (c := degree ν g)).symm

/-- Divisibility of degrees gives the subgroup inclusions used to restrict characters. -/
theorem degreeSubgroup_le (n l : ℕ) (h : n ∣ l) :
    degreeSubgroup ν l ≤ degreeSubgroup ν n := by
  intro g hg
  rw [mem_degreeSubgroup] at hg ⊢
  exact (Int.natCast_dvd_natCast.mpr h).trans hg

/-- The explicit conjugation map for a shifted character restricted from level `n` to `l`. -/
def conjugationInto (n l : ℕ) (h : n ∣ l) (a : G) :
    degreeSubgroup ν l →* degreeSubgroup ν n where
  toFun g := ⟨a*g.val*a⁻¹, by
    rw [mem_degreeSubgroup, degree_conjugate]
    exact (mem_degreeSubgroup ν n g.val).mp (degreeSubgroup_le ν n l h g.property)⟩
  map_one' := by apply Subtype.ext; simp
  map_mul' g k := by apply Subtype.ext; simp [mul_assoc]

@[simp] theorem conjugationInto_apply (n l : ℕ) (h : n ∣ l) (a : G)
    (g : degreeSubgroup ν l) : (conjugationInto ν n l h a g).val = a*g.val*a⁻¹ := rfl

/-- Actual action on the quotient indices: addition of degree. -/
def translationAction (n : ℕ) : G →* Equiv.Perm (ZMod n) where
  toFun g := Equiv.addRight ((degree ν g : ℤ) : ZMod n)
  map_one' := by ext x; simp
  map_mul' g h := by
    ext x
    change x + ((degree ν (g*h) : ℤ) : ZMod n) =
      (x + ((degree ν h : ℤ) : ZMod n)) + ((degree ν g : ℤ) : ZMod n)
    rw [degree_mul, Int.cast_add]
    abel

@[simp] theorem translationAction_apply (n : ℕ) (g : G) (x : ZMod n) :
    translationAction ν n g x = x + ((degree ν g : ℤ) : ZMod n) := rfl

theorem translationAction_fixed_iff (n : ℕ) (g : G) (x : ZMod n) :
    translationAction ν n g x = x ↔ g ∈ degreeSubgroup ν n := by
  rw [translationAction_apply, add_eq_left, mem_degreeSubgroup]
  exact ZMod.intCast_zmod_eq_zero_iff_dvd _ _

/-- The product action on the two factors. -/
def pairAction (n m : ℕ) : G →* Equiv.Perm (ZMod n × ZMod m) where
  toFun g := (translationAction ν n g).prodCongr (translationAction ν m g)
  map_one' := by ext x <;> simp
  map_mul' g h := by
    ext x <;> simp [Equiv.Perm.mul_apply, add_comm, add_left_comm]

@[simp] theorem pairAction_apply (n m : ℕ) (g : G) (x : ZMod n × ZMod m) :
    pairAction ν n m g x = TameTensorOrbits.translate n m (degree ν g) x := rfl

/-- The stabilizer of each actual pair-index is the degree-lcm subgroup. -/
theorem pairAction_fixed_iff (n m : ℕ) (g : G) (x : ZMod n × ZMod m) :
    pairAction ν n m g x = x ↔ g ∈ degreeSubgroup ν (Nat.lcm n m) := by
  rw [pairAction_apply, TameTensorOrbits.translate_eq_iff, mem_degreeSubgroup]

/-- The block-index is fixed and the lcm-cycle coordinate is translated. -/
def blockAction (n m : ℕ) : G →* Equiv.Perm (Fin (Nat.gcd n m) × ZMod (Nat.lcm n m)) where
  toFun g := (Equiv.refl _).prodCongr (translationAction ν (Nat.lcm n m) g)
  map_one' := by ext x <;> simp
  map_mul' g h := by
    ext x <;> simp [Equiv.Perm.mul_apply, add_comm, add_left_comm]

@[simp] theorem blockAction_apply (n m : ℕ) (g : G)
    (x : Fin (Nat.gcd n m) × ZMod (Nat.lcm n m)) :
    blockAction ν n m g x = (x.1, x.2 + ((degree ν g : ℤ) : ZMod (Nat.lcm n m))) := rfl

theorem orbitMap_intertwines (n m : ℕ) (g : G)
    (x : Fin (Nat.gcd n m) × ZMod (Nat.lcm n m)) :
    TameTensorOrbits.orbitMap n m (blockAction ν n m g x) =
      pairAction ν n m g (TameTensorOrbits.orbitMap n m x) :=
  TameTensorOrbits.orbitMap_translate_int n m x.1 x.2 (degree ν g)

theorem orbitEquiv_intertwines (n m : ℕ) [NeZero n] [NeZero m] (g : G)
    (x : Fin (Nat.gcd n m) × ZMod (Nat.lcm n m)) :
    TameTensorOrbits.orbitEquiv n m (blockAction ν n m g x) =
      pairAction ν n m g (TameTensorOrbits.orbitEquiv n m x) :=
  orbitMap_intertwines ν n m g x

variable (φ : G) (hφ : ν φ = Multiplicative.ofAdd (1 : ℤ))

include hφ in
theorem degree_phi : degree ν φ = 1 := by simp [degree, hφ]

include hφ in
theorem degree_phi_zpow (k : ℤ) : degree ν (φ^k) = k := by
  rw [degree_zpow, degree_phi ν φ hφ, mul_one]

include hφ in
theorem degreeMod_phi_zpow (n : ℕ) (k : ℤ) :
    degreeMod ν n (φ^k) = Multiplicative.ofAdd (k : ZMod n) := by
  rw [degreeMod_apply, degree_phi_zpow ν φ hφ]

include hφ in
theorem degreeMod_surjective (n : ℕ) : Function.Surjective (degreeMod ν n) := by
  intro q
  obtain ⟨k,hk⟩ := ZMod.intCast_surjective q.toAdd
  refine ⟨φ^k, ?_⟩
  rw [degreeMod_phi_zpow ν φ hφ, hk]
  rfl

include hφ in
theorem translationAction_phi_zpow (n : ℕ) (k : ℤ) (x : ZMod n) :
    translationAction ν n (φ^k) x = x + (k : ZMod n) := by
  rw [translationAction_apply, degree_phi_zpow ν φ hφ]

include hφ in
theorem pairAction_phi_zpow (n m : ℕ) (k : ℤ) (x : ZMod n × ZMod m) :
    pairAction ν n m (φ^k) x = TameTensorOrbits.translate n m k x := by
  rw [pairAction_apply, degree_phi_zpow ν φ hφ]

include hφ in
/-- The powers of the degree-one element act transitively inside each actual gcd fiber. -/
theorem fiber_transitive (n m : ℕ) [NeZero n] [NeZero m]
    (x y : ZMod n × ZMod m) (h : TameTensorOrbits.difference n m x =
      TameTensorOrbits.difference n m y) :
    ∃ k : ℤ, pairAction ν n m (φ^k) x = y := by
  obtain ⟨k,hk⟩ := (TameTensorOrbits.sameOrbit_iff n m x y).mpr h
  exact ⟨k, (pairAction_phi_zpow ν φ hφ n m k x).trans hk⟩

end PaperXI.TameDegree
