import RealizationBoundaries.Preimages
import Mathlib.Order.Hom.Basic

/-!
# The reverse pure-preimage correspondence

Purity means lifting roots that already exist in the ambient group. It does not
mean that every element has every root. Containment of the actual torsion subgroup
D is retained explicitly; it is what upgrades root lifting to root closure.
-/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- Standard root-lifting purity relative to the actual ambient product. -/
def IsPure (H : AddSubgroup Ambient) : Prop :=
  ∀ (m : ℕ), 0 < m → ∀ x : H,
    (∃ y : Ambient, m • y = x.val) → ∃ y : H, m • y = x

/-- A pure intermediate subgroup includes all finite-support torsion. -/
abbrev PureIntermediate := {H : AddSubgroup Ambient // finiteSupport ≤ H ∧ IsPure H}

/-- With D included, any ambient root of a point of H lies in H. -/
theorem pure_root_closed (H : AddSubgroup Ambient) (hD : finiteSupport ≤ H)
    (hH : IsPure H) {m : ℕ} (hm : 0 < m) (x : Ambient) (hx : m • x ∈ H) :
    x ∈ H := by
  obtain ⟨y, hy⟩ := hH m hm ⟨m • x, hx⟩ ⟨x, rfl⟩
  have hdiff : m • (x - y.val) = 0 := by
    rw [nsmul_sub]
    exact sub_eq_zero.mpr (congrArg Subtype.val hy).symm
  have hd : x - y.val ∈ finiteSupport :=
    (torsion_iff_finiteSupport _).mp ⟨m, hm, hdiff⟩
  have := H.add_mem (hD hd) y.property
  simpa using this

/-- The image of H under the quotient map remembers H exactly when D is included. -/
theorem mem_quotient_image_iff (H : AddSubgroup Ambient) (hD : finiteSupport ≤ H)
    (x : Ambient) : quotientMap x ∈ H.map quotientMap ↔ x ∈ H := by
  constructor
  · rintro ⟨y, hy, hxy⟩
    have hd : x - y ∈ finiteSupport := (quotientMap_eq_iff x y).mp hxy.symm
    have := H.add_mem (hD hd) hy
    simpa using this
  · intro hx
    exact ⟨x, hx, rfl⟩

/-- Root closure descends to the actual quotient image. -/
theorem quotient_image_nsmul_closed (H : AddSubgroup Ambient)
    (hD : finiteSupport ≤ H) (hH : IsPure H) {m : ℕ} (hm : 0 < m)
    (v : TailSpace) (hv : m • v ∈ H.map quotientMap) : v ∈ H.map quotientMap := by
  obtain ⟨x, rfl⟩ := quotientMap_surjective v
  have hx : m • x ∈ H := (mem_quotient_image_iff H hD _).mp (by
    simpa only [map_nsmul] using hv)
  exact ⟨x, pure_root_closed H hD hH hm x hx, rfl⟩

/-- The rational action on the quotient image is proved by clearing denominators. -/
theorem quotient_image_smul_mem (H : AddSubgroup Ambient)
    (hD : finiteSupport ≤ H) (hH : IsPure H) (r : ℚ) (v : TailSpace)
    (hv : v ∈ H.map quotientMap) : r • v ∈ H.map quotientMap := by
  apply quotient_image_nsmul_closed H hD hH r.den_pos
  have heq : r.den • (r • v) = r.num • v := by
    rw [← Nat.cast_smul_eq_nsmul ℚ, ← Int.cast_smul_eq_zsmul ℚ, smul_smul,
      Rat.den_mul_eq_num]
  rw [heq]
  exact (H.map quotientMap).zsmul_mem hv r.num

/-- The rational subspace is constructed from the subgroup, not supplied as an input. -/
def rationalImage (H : AddSubgroup Ambient) (hD : finiteSupport ≤ H) (hH : IsPure H) :
    Submodule ℚ TailSpace where
  carrier := H.map quotientMap
  zero_mem' := (H.map quotientMap).zero_mem
  add_mem' := (H.map quotientMap).add_mem
  smul_mem' := quotient_image_smul_mem H hD hH

@[simp] theorem mem_rationalImage (H : AddSubgroup Ambient)
    (hD : finiteSupport ≤ H) (hH : IsPure H) (v : TailSpace) :
    v ∈ rationalImage H hD hH ↔ v ∈ H.map quotientMap := Iff.rfl

/-- The reverse construction recovers the literal original subgroup. -/
@[simp] theorem preimage_rationalImage (H : AddSubgroup Ambient)
    (hD : finiteSupport ≤ H) (hH : IsPure H) : preimage (rationalImage H hD hH) = H := by
  ext x
  exact mem_quotient_image_iff H hD x

/-- Every rational preimage satisfies the root-lifting definition of purity. -/
theorem preimage_isPure (W : Submodule ℚ TailSpace) : IsPure (preimage W) := by
  intro m hm x hx
  exact preimage_pure W hm x hx

/-- Quotienting a rational preimage recovers exactly the original rational subspace. -/
@[simp] theorem rationalImage_preimage (W : Submodule ℚ TailSpace) :
    rationalImage (preimage W) (finiteSupport_le_preimage W) (preimage_isPure W) = W := by
  ext v
  constructor
  · rintro ⟨x, hx, rfl⟩
    exact hx
  · intro hv
    obtain ⟨x, rfl⟩ := quotientMap_surjective v
    exact ⟨x, hv, rfl⟩

/-- Canonical inclusion reflects the order on rational subspaces. -/
theorem preimage_le_iff (V W : Submodule ℚ TailSpace) : preimage V ≤ preimage W ↔ V ≤ W := by
  constructor
  · intro h v hv
    obtain ⟨x, rfl⟩ := quotientMap_surjective v
    exact h hv
  · intro h x hx
    exact h hx

/-- Monograph Theorem 4.2: order equivalence, including both inverse laws. -/
def purePreimageOrderIso : Submodule ℚ TailSpace ≃o PureIntermediate where
  toFun W := ⟨preimage W, finiteSupport_le_preimage W, preimage_isPure W⟩
  invFun H := rationalImage H.val H.property.1 H.property.2
  left_inv W := rationalImage_preimage W
  right_inv H := Subtype.ext (preimage_rationalImage H.val H.property.1 H.property.2)
  map_rel_iff' := fun {_ _} => preimage_le_iff _ _

/-- A rational subspace witnessing a pure intermediate group exists uniquely. -/
theorem exists_unique_rational_preimage (H : AddSubgroup Ambient)
    (hD : finiteSupport ≤ H) (hH : IsPure H) :
    ∃! W : Submodule ℚ TailSpace, preimage W = H := by
  refine ⟨rationalImage H hD hH, preimage_rationalImage H hD hH, ?_⟩
  intro W hW
  apply le_antisymm
  · exact (preimage_le_iff _ _).mp (by rw [hW, preimage_rationalImage])
  · exact (preimage_le_iff _ _).mp (by rw [hW, preimage_rationalImage])

end RealizationBoundaries
