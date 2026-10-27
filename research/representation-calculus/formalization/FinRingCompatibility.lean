module
public import MatrixLinearBridge
@[expose] public section
namespace Komorebi.Representation.Matrix
open Fin.CommRing
theorem grindSemiring_ext_fields {R : Type} (s t : Lean.Grind.Semiring R)
    (ha : s.toAdd = t.toAdd) (hm : s.toMul = t.toMul)
    (hn : s.natCast = t.natCast) (ho : s.ofNat = t.ofNat)
    (hs : s.nsmul = t.nsmul) (hp : s.npow = t.npow) : s=t := by
  cases s
  cases t
  cases ha
  cases hm
  cases hn
  cases ho
  cases hs
  cases hp
  rfl
theorem ofNat_ext_value {A : Type} {n : Nat} (a b : OfNat A n) (h : a.ofNat = b.ofNat) : a=b := by
  cases a
  cases b
  cases h
  rfl

theorem fin_grindSemiring_eq (m : Nat) [NeZero m] :
  (Lean.Grind.Fin.instCommRingFinOfNeZeroNat m).toCommSemiring.toSemiring =
  (@CommRing.toGrindCommRing (Fin m) (Fin.instCommRing m)).toCommSemiring.toSemiring := by
  apply grindSemiring_ext_fields
  · rfl
  · rfl
  · rfl
  · funext n
    apply ofNat_ext_value
    rw [Lean.Grind.Semiring.ofNat_eq_natCast]
    exact (Lean.Grind.Semiring.ofNat_eq_natCast
      (self := (@CommRing.toGrindCommRing (Fin m) (Fin.instCommRing m)).toCommSemiring.toSemiring) n).symm
  · apply SMul.ext
    funext k a
    change (k : Fin m) * a = k • a
    simp only [nsmul_eq_mul]
  · congr 1

end Komorebi.Representation.Matrix
