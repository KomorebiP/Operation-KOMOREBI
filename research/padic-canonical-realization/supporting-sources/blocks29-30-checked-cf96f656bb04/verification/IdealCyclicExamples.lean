import KomorebiPadic.IdealClosureExamples
namespace KomorebiPadic
example : PrimePowerIdeal.order 2 2 (0 : ZMod 4) = 2 := by decide +kernel
example : PrimePowerIdeal.order 2 2 (2 : ZMod 4) = 1 := by decide +kernel
example : PrimePowerIdeal.capacity 2 2 (2 : ZMod 4) = 1 := by decide +kernel
example : PrimePowerIdeal.transfer 2 2 (2 : ZMod 4) 1 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 2 3 (2 : ZMod 8) 3 = 2 := by decide +kernel
example : PrimePowerIdeal.transfer 3 2 (3 : ZMod 9) 1 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 3 2 (3 : ZMod 9) 2 = 1 := by decide +kernel
example : PrimePowerIdeal.capacity 2 0 (0 : ZMod 1) = 0 := by decide +kernel
example (p r c : ℕ) (hp : 0 < p) (hc : c ≤ r) (x : ZMod (p^c)) :
    PrimePowerIdeal.cyclicDecode (PrimePowerIdeal.cyclicEncode hp hc x) = x :=
  PrimePowerIdeal.cyclicDecode_encode hp hc x
example (p r c : ℕ) (hp : 0 < p) (hc : c ≤ r)
    (x : PrimePowerIdeal.capacityIdeal p r c) :
    PrimePowerIdeal.cyclicEncode hp hc (PrimePowerIdeal.cyclicDecode x) = x :=
  PrimePowerIdeal.cyclicEncode_decode hp hc x
example (p r c : ℕ) (hp : 0 < p) (hc : c ≤ r)
    (a : ZMod (p^r)) (x : ZMod (p^c)) :
    PrimePowerIdeal.cyclicEncode hp hc
      (ZMod.castHom (pow_dvd_pow p hc) (ZMod (p^c)) a*x) =
        a • PrimePowerIdeal.cyclicEncode hp hc x := PrimePowerIdeal.cyclicEncode_scalar hp hc a x
end KomorebiPadic
