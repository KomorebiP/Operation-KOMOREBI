import RealizationBoundaries.RadicalCounts
import Mathlib.Data.ZMod.QuotientRing

/-! # Canonical cyclic coordinates for every integer quotient

Chinese remainder identifies the product of distinct prime coordinates with
ZMod(rad m). Both the original quotient representative map and the transition
maps for divisibility of multipliers are retained explicitly.
-/
set_option autoImplicit false
noncomputable section
open scoped BigOperators
namespace RealizationBoundaries

/-- The CRT equivalence is a ring equivalence on the coordinate target. -/
def divisorCrtEquiv {m : ℕ} (hm : 0 < m) :
    ZMod (primeRadical m) ≃+* DivisorCoordinates m := by
  letI : Finite (DivisorPrime m) := divisorPrime_finite hm
  letI := Fintype.ofFinite (DivisorPrime m)
  have hc : Pairwise (fun p q : DivisorPrime m => Nat.Coprime p.val.val q.val.val) := by
    intro p q hpq
    exact (Nat.coprime_primes p.val.property q.val.property).mpr
      (fun h => hpq (Subtype.ext (Subtype.ext h)))
  exact (ZMod.ringEquivCongr (divisorPrime_prod hm).symm).trans
    (ZMod.prodEquivPi (fun p : DivisorPrime m => p.val.val) hc)

/-- Integer representatives are reduced to their actual prime-coordinate residues. -/
@[simp] theorem divisorCrtEquiv_natCast {m : ℕ} (hm : 0 < m) (n : ℕ)
    (p : DivisorPrime m) : divisorCrtEquiv hm (n : ZMod (primeRadical m)) p =
      (n : Coordinate p.val) := by
  exact congrArg (fun z : DivisorCoordinates m => z p) (map_natCast (divisorCrtEquiv hm) n)

@[simp] theorem divisorCrtEquiv_intCast {m : ℕ} (hm : 0 < m) (n : ℤ)
    (p : DivisorPrime m) : divisorCrtEquiv hm (n : ZMod (primeRadical m)) p =
      (n : Coordinate p.val) := by
  exact congrArg (fun z : DivisorCoordinates m => z p) (map_intCast (divisorCrtEquiv hm) n)

/-- Complete cyclic identification of the actual quotient by m H_W. -/
def cyclicIntegerQuotientEquiv (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m) :
    (preimage W ⧸ multiples W m) ≃+ ZMod (primeRadical m) :=
  (integerQuotientEquiv W hm).trans (divisorCrtEquiv hm).toAddEquiv.symm

/-- The cyclic and product coordinates agree on every quotient element. -/
@[simp] theorem cyclicIntegerQuotientEquiv_coordinates (W : Submodule ℚ TailSpace) {m : ℕ}
    (hm : 0 < m) (x : preimage W ⧸ multiples W m) :
    divisorCrtEquiv hm (cyclicIntegerQuotientEquiv W hm x) = integerQuotientEquiv W hm x :=
  (divisorCrtEquiv hm).toAddEquiv.apply_symm_apply _

/-- The cyclic identification remembers the supplied original element. -/
@[simp] theorem cyclicIntegerQuotientEquiv_mk (W : Submodule ℚ TailSpace) {m : ℕ}
    (hm : 0 < m) (x : preimage W) :
    divisorCrtEquiv hm (cyclicIntegerQuotientEquiv W hm (QuotientAddGroup.mk x)) =
      coordinateMap W m x := by
  simp [cyclicIntegerQuotientEquiv]

/-- Every root fiber can also be coordinatized by one cyclic radical residue. -/
def cyclicRootFiberEquiv (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m)
    (x : preimage W) (y : RootFiber W m x) : RootFiber W m x ≃ ZMod (primeRadical m) :=
  (rootFiberEquiv W hm x y).trans (divisorCrtEquiv hm).symm.toEquiv

/-- Explicit cyclic enumeration of all roots, as translated finite-support corrections. -/
theorem cyclicRootFiberEquiv_symm_natCast (W : Submodule ℚ TailSpace) {m : ℕ}
    (hm : 0 < m) (x : preimage W) (y : RootFiber W m x) (n : ℕ) :
    ((cyclicRootFiberEquiv W hm x y).symm (n : ZMod (primeRadical m))).val.val =
      y.val.val + coordinateExtension m (fun p => (n : Coordinate p.val)) := by
  change y.val.val + coordinateExtension m (divisorCrtEquiv hm (n : ZMod (primeRadical m))) = _
  have he : divisorCrtEquiv hm (n : ZMod (primeRadical m)) =
      (fun p : DivisorPrime m => (n : Coordinate p.val)) := by
    funext p
    exact divisorCrtEquiv_natCast hm n p
  rw [he]

/-- Divisibility reverses the inclusion of the original multiple subgroups. -/
theorem multiples_antitone (W : Submodule ℚ TailSpace) {m n : ℕ} (hmn : m ∣ n) :
    multiples W n ≤ multiples W m := by
  obtain ⟨k, rfl⟩ := hmn
  rintro x ⟨y, rfl⟩
  refine ⟨k • y, ?_⟩
  change m • (k • y) = (m * k) • y
  rw [mul_comm m k, mul_nsmul]

/-- The genuine transition between quotient groups. -/
def quotientRestriction (W : Submodule ℚ TailSpace) {m n : ℕ} (hmn : m ∣ n) :
    (preimage W ⧸ multiples W n) →+ (preimage W ⧸ multiples W m) :=
  QuotientAddGroup.map (multiples W n) (multiples W m) (AddMonoidHom.id (preimage W))
    (multiples_antitone W hmn)

@[simp] theorem quotientRestriction_mk (W : Submodule ℚ TailSpace) {m n : ℕ}
    (hmn : m ∣ n) (x : preimage W) :
    quotientRestriction W hmn (QuotientAddGroup.mk x) = QuotientAddGroup.mk x := rfl

/-- Coordinate restriction is the actual quotient transition, on every quotient element. -/
theorem integerQuotientEquiv_restriction (W : Submodule ℚ TailSpace) {m n : ℕ}
    (hm : 0 < m) (hn : 0 < n) (hmn : m ∣ n) (x : preimage W ⧸ multiples W n) :
    integerQuotientEquiv W hm (quotientRestriction W hmn x) =
      coordinateRestriction hmn (integerQuotientEquiv W hn x) := by
  induction x using QuotientAddGroup.induction_on with
  | H x => rfl

/-- Cyclic coordinates turn quotient transitions into the ordinary residue reduction. -/
theorem divisorCrtEquiv_restriction {m n : ℕ} (hm : 0 < m) (hn : 0 < n)
    (hmn : m ∣ n) (z : ZMod (primeRadical n)) :
    coordinateRestriction hmn (divisorCrtEquiv hn z) =
      divisorCrtEquiv hm (ZMod.castHom (primeRadical_dvd_of_dvd hn hmn)
        (ZMod (primeRadical m)) z) := by
  let : NeZero (primeRadical n) := ⟨Nat.ne_of_gt (primeRadical_pos n)⟩
  have he : (z.val : ZMod (primeRadical n)) = z := ZMod.natCast_zmod_val z
  rw [← he]
  simp only [map_natCast]
  rfl

/-- The complete commuting square in cyclic coordinates. -/
theorem cyclicIntegerQuotientEquiv_restriction (W : Submodule ℚ TailSpace) {m n : ℕ}
    (hm : 0 < m) (hn : 0 < n) (hmn : m ∣ n) (x : preimage W ⧸ multiples W n) :
    cyclicIntegerQuotientEquiv W hm (quotientRestriction W hmn x) =
      ZMod.castHom (primeRadical_dvd_of_dvd hn hmn) (ZMod (primeRadical m))
        (cyclicIntegerQuotientEquiv W hn x) := by
  apply (divisorCrtEquiv hm).injective
  rw [cyclicIntegerQuotientEquiv_coordinates, ← divisorCrtEquiv_restriction hm hn hmn,
    cyclicIntegerQuotientEquiv_coordinates]
  exact integerQuotientEquiv_restriction W hm hn hmn x

end RealizationBoundaries
