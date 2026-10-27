import KomorebiPadic.LeastProfileMaskAutomaton
namespace KomorebiPadic.Block27Examples
open KomorebiPadic Polynomial
noncomputable section

/-- The isolated third row has a self-loop but no initial support. -/
def toy : DegreePropagationSystem 3 1 3 where
  target i _ := if i.val = 2 then 2 else 1
  seed i := if i.val = 0 then 1 else 0
  seed_bound i := by split <;> omega
  transfer i _ n := if i.val = 2 then n else if n = 0 then 0 else 2
  transfer_mono i _ := by
    intro n m h
    change (if i.val = 2 then n else if n = 0 then 0 else 2) ≤
      (if i.val = 2 then m else if m = 0 then 0 else 2)
    split_ifs <;> omega
  transfer_bound i _ := by split_ifs <;> omega

example : List.ofFn (leastDegreeProfile toy) = [1,2,0] := by decide +kernel
example : List.ofFn (degreeProfileIterate toy 0) = [0,0,0] := by decide +kernel
example : List.ofFn (degreeProfileIterate toy 1) = [1,0,0] := by decide +kernel
example : List.ofFn (degreeProfileIterate toy 2) = [1,2,0] := by decide +kernel
example : DegreeProfileClosed toy (leastDegreeProfile toy) := leastDegreeProfile_closed toy
example : ¬ DegreeProfileClosed toy (fun i => if i.val = 0 then 1 else 0) := by
  unfold DegreeProfileClosed
  decide +kernel
example : leastDegreeProfile toy 2 = 0 := by decide +kernel
example : degreeProfileMass (leastDegreeProfile toy) = 3 := by decide +kernel

def empty : DegreePropagationSystem 0 0 0 where
  target i := Fin.elim0 i
  seed i := Fin.elim0 i
  seed_bound i := Fin.elim0 i
  transfer i := Fin.elim0 i
  transfer_mono i := Fin.elim0 i
  transfer_bound i := Fin.elim0 i
example : List.ofFn (leastDegreeProfile empty) = [] := by decide +kernel
example : DegreeProfileClosed empty (leastDegreeProfile empty) := leastDegreeProfile_closed empty

example : FitsRowCapacity 0 (0 : ℤ[X]) := fitsRowCapacity_zero 0
example : ¬ FitsRowCapacity 0 (1 : ℤ[X]) := by norm_num [FitsRowCapacity]
example : FitsRowCapacity 1 (1 : ℤ[X]) := by norm_num [FitsRowCapacity]
example : ¬ FitsRowCapacity 1 (X : ℤ[X]) := by norm_num [FitsRowCapacity]
example : FitsRowCapacity 2 (X : ℤ[X]) := by norm_num [FitsRowCapacity]
example : polynomialCapacity (0 : ℤ[X]) = 0 := by simp [polynomialCapacity]
example : polynomialCapacity (1 : ℤ[X]) = 1 := by simp [polynomialCapacity]
example : kernelCapacityTransfer 2 (0 : ℤ[X]) 5 = 0 := by simp [kernelCapacityTransfer]
example : kernelCapacityTransfer 2 (X^2 : ℤ[X]) 0 = 0 := by simp [kernelCapacityTransfer]
example : kernelCapacityTransfer 2 (1 : ℤ[X]) 1 = 1 := by simp [kernelCapacityTransfer]
example : kernelCapacityTransfer 2 (1 : ℤ[X]) 3 = 2 := by simp [kernelCapacityTransfer]
example : kernelCapacityTransfer 2 (X^2 : ℤ[X]) 2 = 2 := by simp [kernelCapacityTransfer]
example : Fintype.card (ProfileCoefficientState (ZMod 5) (fun _ : Fin 2 => 0)) = 1 := by
  rw [profileCoefficientState_card]; norm_num
example : Fintype.card (ProfileCoefficientState (ZMod 5) (fun _ : Fin 2 => 1)) = 25 := by
  rw [profileCoefficientState_card]; norm_num

/-- Zero-capacity coordinates reconstruct exactly zero. -/
example (s : ProfileCoefficientState ℤ (fun _ : Fin 2 => 0)) :
    profileRowPolynomial (fun _ : Fin 2 => 0) s 1 = 0 :=
  profileRowPolynomial_zero_capacity _ _ _ rfl

example (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬(p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    LeastProfileCanonicalMaskCertificate p r A B hp hr hB :=
  leastProfileCanonicalMaskCertificate p r A B hp hr hB hAB

example (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬(p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    leastProfileMaskOutput p r A B hp hr hB
      (iterateProfileMachine (degreePrunedMaskMachine p r A B hp) (leastMaskDegreeProfile p r A B hp)
        (Nat.digits p n) (leastProfileMaskInitial p r A B hp)) =
      PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB) :=
  leastProfileMask_output_canonical_coefficient p r A B hp hr hB hAB n

end
end KomorebiPadic.Block27Examples
