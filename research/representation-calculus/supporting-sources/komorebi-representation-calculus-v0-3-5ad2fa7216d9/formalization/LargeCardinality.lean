import GeneratedLarge
import CardinalityCore

namespace Komorebi.Representation.Symbolic.Large
open Komorebi.Representation
open Komorebi.Representation.Matrix
open Komorebi.Representation.Cardinality
open Lean.Grind

/- A compact numeric code for the ACTUAL image. No list of its 2^30 elements. -/
def codeVector (q : Fin 1073741824) : Vec R 2 :=
  fun i => if i.val = 0 then Fin.ofNat 65536 (q.val % 65536)
           else Fin.ofNat 65536 (4 * (q.val / 65536))

theorem codeVector_principal (q : Fin 1073741824) :
    PrincipalCoordinates smith.weights (codeVector q) := by
  intro i
  refine Fin.cases ?_ (fun j => Fin.cases ?_ (fun j => Fin.elim0 j) j) i
  · refine ⟨Fin.ofNat 65536 (q.val % 65536), ?_⟩
    change (1 : R) * _ = _
    exact Semiring.one_mul _
  · refine ⟨Fin.ofNat 65536 (q.val / 65536), ?_⟩
    apply Fin.ext
    change (4 * ((q.val / 65536) % 65536)) % 65536 = (4 * (q.val / 65536)) % 65536
    exact Nat.mul_mod_mod _ _ _

def codeImage (q : Fin 1073741824) : EncodedImage data :=
  ⟨codeVector q, (exact_image (codeVector q)).mpr (codeVector_principal q)⟩

def decodeImage (y : EncodedImage data) : Fin 1073741824 :=
  ⟨(y.val 0).val + 65536 * ((y.val 1).val / 4), by
    have h0 := (y.val 0).isLt
    have h1 := (y.val 1).isLt
    omega⟩

theorem decode_codeImage (q : Fin 1073741824) : decodeImage (codeImage q) = q := by
  apply Fin.ext
  change (q.val % 65536) % 65536 +
    65536 * (((4 * (q.val / 65536)) % 65536) / 4) = q.val
  have hq := q.isLt
  omega

theorem code_decodeImage (y : EncodedImage data) : codeImage (decodeImage y) = y := by
  apply Subtype.ext
  funext i
  have hy := (exact_image y.val).mp y.property
  obtain ⟨a, ha⟩ := hy 1
  have hval := congrArg Fin.val ha
  change (4 * a.val) % 65536 = (y.val 1).val at hval
  have h0 := (y.val 0).isLt
  have h1 := (y.val 1).isLt
  refine Fin.cases ?_ (fun j => Fin.cases ?_ (fun j => Fin.elim0 j) j) i
  · apply Fin.ext
    change (((y.val 0).val + 65536 * ((y.val 1).val / 4)) % 65536) % 65536 = (y.val 0).val
    omega
  · apply Fin.ext
    change (4 * (((y.val 0).val + 65536 * ((y.val 1).val / 4)) / 65536)) % 65536 = (y.val 1).val
    omega

def exactImageCode : Bijection (Fin 1073741824) (EncodedImage data) where
  toFun := codeImage
  invFun := decodeImage
  left_inv := decode_codeImage
  right_inv := code_decodeImage

theorem every_finite_competitor_needs_2pow30 {n : Nat}
    (U : System (Fin n) (Fin 2) (Fin 1) R) (encode : Vec R 8 → Fin n)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    1073741824 ≤ n := by
  obtain ⟨f, hf⟩ := every_competitor_contains_image U encode h
  apply fin_injection_bound (fun q => f (codeImage q))
  intro a b hab
  exact bijection_injective exactImageCode a b (hf _ _ hab)

theorem no_one_scalar_competitor {n : Nat} (hn : n < 2)
    (U : System (Vec R n) (Fin 2) (Fin 1) R) (encode : Vec R 8 → Vec R n)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    False := by
  obtain ⟨f, hf⟩ := every_competitor_contains_image U encode h
  obtain ⟨pack, hpack⟩ := at_most_one_coordinate_pack (m := 65536) hn
  have hbad : 1073741824 ≤ 65536 := by
    apply fin_injection_bound (fun q => pack (f (codeImage q)))
    intro a b hab
    exact bijection_injective exactImageCode a b (hf _ _ (hpack _ _ hab))
  omega

theorem minimum_two_scalar_coordinates :
    (∃ encode : Vec R 8 → Vec R 2,
      ∀ x w j, behavior (sourceSystem data) x w j = behavior (targetSystem data) (encode x) w j) ∧
    (∀ n, n < 2 → ∀ (U : System (Vec R n) (Fin 2) (Fin 1) R) (encode : Vec R 8 → Vec R n),
      ¬ (∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j)) := by
  constructor
  · exact ⟨mv data.encoding, all_states_all_words⟩
  · intro n hn U encode h
    exact no_one_scalar_competitor hn U encode h

end Komorebi.Representation.Symbolic.Large
