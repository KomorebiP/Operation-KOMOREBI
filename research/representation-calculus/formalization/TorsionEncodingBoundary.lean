module
public import MatrixPrimeMinimality

@[expose] public section
set_option backward.isDefEq.respectTransparency false
set_option maxHeartbeats 4000000
set_option maxRecDepth 100000
open Fin.CommRing
namespace Komorebi.Representation.TorsionBoundary
open Komorebi.Representation Komorebi.Representation.Matrix
abbrev R := Fin 16

def data : CertificateData R 2 2 1 2 2 where
  actions := fun _ => eye 2
  observations := fun i j => if i=j then 8 else 0
  encoding := fun i j => if i=j then 8 else 0
  transitions := fun _ => eye 2
  decoder := eye 2
  tests := fun i => ([],i)
  combinations := eye 2

def smith : SmithData R 2 2 where
  width := Nat.le_refl 2
  weights := fun _ => 8
  change := eye 2
  inverse := eye 2

theorem valid : Valid data := by decide
theorem smith_valid : SmithValid data.encoding smith := by decide
theorem nonzero_weights : ∀ i, smith.weights i ≠ 0 := by decide

theorem two_linear_coordinates_necessary {n : Nat}
    (U : System (Fin n → R) (Fin 1) (Fin 2) R)
    (e : (Fin 2 → R) →ₗ[R] (Fin n → R))
    (he : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) :
    2 ≤ n :=
  prime_certificate_linear_lower (p:=2) (r:=4) (by decide) (by decide)
    data valid smith smith_valid nonzero_weights U e he

/-- A nonlinear bit code fits the four behaviors into one residue. -/
def pack (x : Fin 2 → R) : R :=
  Fin.ofNat 16 ((x 0).val % 2 + 2*((x 1).val % 2))

def packedSystem : System R (Fin 1) (Fin 2) R where
  step := fun _ y => y
  observe := fun j y =>
    if j=0 then Fin.ofNat 16 (8*(y.val % 2))
    else Fin.ofNat 16 (8*((y.val / 2) % 2))

def packingTransport : Transport (sourceSystem data) packedSystem where
  encode := pack
  step_ok := by
    intro a x
    change pack (mv (eye 2) x) = pack x
    rw [mv_eye]
  observe_ok := by decide

theorem one_nonlinear_residue_suffices (x : Fin 2 → R) (w : List (Fin 1)) (j : Fin 2) :
    behavior (sourceSystem data) x w j = behavior packedSystem (pack x) w j :=
  transport_behavior packingTransport w j x

def firstUnit : Fin 2 → R := fun i => if i=0 then 1 else 0

theorem packing_is_not_additive :
    pack (firstUnit + firstUnit) ≠ pack firstUnit + pack firstUnit := by decide

end Komorebi.Representation.TorsionBoundary
