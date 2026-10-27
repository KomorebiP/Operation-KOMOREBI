/- Multiplicative signed packets in a commutative group. This is not a formal
proof of analytic gamma identities or of an arithmetic special-value comparison. -/
module
public import H12SignedGeometry
public import Mathlib.Tactic.Group
public import Mathlib.Algebra.Group.TypeTags.Basic
@[expose] public section
namespace H12.SignedAlgebra
open H12.SignedGeometry
variable {G : Type*} [CommGroup G]

def signed (x : Fin 8 → G) (k : Fin 8) : G :=
  Additive.toMul (walsh (fun i => Additive.ofMul (x i)) k)
def layerOne (x : Fin 8 → G) : G := signed x 1*signed x 2*signed x 4
def layerTwo (x : Fin 8 → G) : G := signed x 3*signed x 5*signed x 6

theorem signed_product (x y : Fin 8 → G) (k : Fin 8) :
    signed (fun i => x i*y i) k=signed x k*signed y k := by
  apply Additive.ofMul.injective
  change walsh (fun i => Additive.ofMul (x i)+Additive.ofMul (y i)) k =
    walsh (fun i => Additive.ofMul (x i)) k+walsh (fun i => Additive.ofMul (y i)) k
  exact walsh_add _ _ k

theorem signed_transport (x : Fin 8 → G) (k : Fin 8) :
    signed (fun i => x (rotate i)) k=signed x (rotate k) := by
  exact congrArg Additive.toMul (walsh_transport (fun i => Additive.ofMul (x i)) k)

theorem carried_transport (x carry : Fin 8 → G) (k : Fin 8) :
    signed (fun i => x (rotate i)*carry i) k =
      signed x (rotate k)*signed carry k := by
  rw [signed_product, signed_transport]

theorem signed_eighth_power (x : Fin 8 → G) (k : Fin 8) :
    signed (signed x) k=(x k)^8 := by
  apply Additive.ofMul.injective
  change walsh (walsh (fun i => Additive.ofMul (x i))) k=8 • Additive.ofMul (x k)
  exact walsh_inversion _ k

theorem signed_powers (n : Fin 8 → ℤ) (r : G) (k : Fin 8) :
    signed (fun i => r^(n i)) k=r^(walsh n k) := by
  apply Additive.ofMul.injective
  change walsh (fun i => n i • Additive.ofMul r) k=walsh n k • Additive.ofMul r
  exact walsh_zsmul n _ k

theorem aggregate_reconstruction (x : Fin 8 → G) :
    signed x 0*layerOne x*layerTwo x*signed x 7=(x 0)^8 := by
  apply Additive.ofMul.injective
  change walsh (fun i => Additive.ofMul (x i)) 0+
      (walsh (fun i => Additive.ofMul (x i)) 1+walsh (fun i => Additive.ofMul (x i)) 2+walsh (fun i => Additive.ofMul (x i)) 4)+
      (walsh (fun i => Additive.ofMul (x i)) 3+walsh (fun i => Additive.ofMul (x i)) 5+walsh (fun i => Additive.ofMul (x i)) 6)+
      walsh (fun i => Additive.ofMul (x i)) 7=8 • Additive.ofMul (x 0)
  exact walsh_aggregate _

theorem conductor_ninth_power (x : Fin 8 → G)
    (hnorm : signed x 0=(x 0)⁻¹) :
    layerOne x*layerTwo x*signed x 7=(x 0)^9 := by
  have h := aggregate_reconstruction x
  rw [hnorm] at h
  calc
    _ = x 0*((x 0)⁻¹*layerOne x*layerTwo x*signed x 7) := by group
    _ = x 0*(x 0)^8 := by rw [h]
    _ = _ := by group

def gauge (r : G) (i : Fin 8) : G := r ^ (affine (-4:ℤ) 3 3 3 i)

theorem gauge_characters (r : G) (k : Fin 8) :
    signed (gauge r) k =
      if k.val=0 then r^4 else
      if k.val=1 ∨ k.val=2 ∨ k.val=4 then (r^12)⁻¹ else 1 := by
  unfold gauge
  rw [signed_powers, affine_gauge_spectrum]
  fin_cases k <;> norm_num

theorem gauge_norm_compatibility (r : G) :
    signed (gauge r) 0=(gauge r 0)⁻¹ := by
  rw [gauge_characters]
  norm_num [gauge,affine]

theorem gauge_preserves_norm_constraint (x : Fin 8 → G) (r : G)
    (hnorm : signed x 0=(x 0)⁻¹) :
    signed (fun i => x i*gauge r i) 0=(x 0*gauge r 0)⁻¹ := by
  rw [signed_product,hnorm,gauge_norm_compatibility,mul_inv_rev,mul_comm]

theorem first_layer_detects_gauge (r : G) :
    layerOne (gauge r)=(r^36)⁻¹ := by
  dsimp [layerOne]
  rw [gauge_characters,gauge_characters,gauge_characters]
  norm_num; group

end H12.SignedAlgebra
