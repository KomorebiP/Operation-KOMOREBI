import KomorebiPadic.IdealClosureExamples

namespace KomorebiPadic
noncomputable section

-- The entire nilpotent ideal box, not only the initial orbit, maps to zero.
example (d : Fin 1) (x : Fin 2 → ZMod 4)
    (hx : CoordinateIdeal.InBox (p := 2) (r := 2) CoordinateIdeal.nilpotentCapacity x) :
    CoordinateSupport.nilpotentSystem.transition d x = 0 := by
  have hy : CoordinateIdeal.InBox (p := 2) (r := 2) CoordinateIdeal.nilpotentCapacity
      (CoordinateSupport.nilpotentSystem.transition d x) :=
    CoordinateIdeal.transition_inBox (p := 2) (r := 2) (by decide : 0 < 2)
      CoordinateSupport.nilpotentSystem CoordinateIdeal.nilpotentCapacity_closed d hx
  funext j
  fin_cases j
  · simp [CoordinateSupport.nilpotentSystem, CoordinateSupport.matrixSystem, Fin.sum_univ_succ]
  · have hz := hy (1 : Fin 2)
    simpa [CoordinateIdeal.nilpotentCapacity] using hz

-- Arbitrary scalar compatibility is already proved on each heterogeneous factor.
example (p r : ℕ) (hp : 0 < p) (w : Fin 3 → ℕ) (hw : ∀ i, w i ≤ r) :
    CoordinateIdeal.CyclicState p w ≃+ CoordinateIdeal.State (p := p) (r := r) w :=
  CoordinateIdeal.cyclicBoxEquiv hp w hw

-- A zero-capacity factor has exactly one value and can be removed.
example (p : ℕ) (w : Fin 3 → ℕ) :
    CoordinateIdeal.CyclicState p w ≃+
      ((i : {i : Fin 3 // 0 < w i}) → ZMod (p^(w i.val))) :=
  CoordinateIdeal.dropZeroCyclicEquiv w

-- Complete actual-mask theorem: the coefficient is obtained without a series oracle.
example (p r : ℕ) (A B : Polynomial ℤ) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    CyclicCanonicalMaskCertificate p r A B hp hr hB :=
  cyclicCanonicalMaskCertificate p r A B hp hr hB hAB

-- The encoding is additive, not multiplicative as a map into the ambient ring.
example :
    (PrimePowerIdeal.cyclicEncode (p := 2) (r := 2) (c := 1)
      (by decide) (by decide) ((1 : ZMod 2)*1)).val = 2 ∧
    (PrimePowerIdeal.cyclicEncode (p := 2) (r := 2) (c := 1)
      (by decide) (by decide) (1 : ZMod 2)).val ^ 2 = 0 := by
  decide +kernel

-- Even coordinate-ideal closure does not capture x0=x1 correlations.
example (x : Fin 3 → ZMod 5) (h01 : x 0 = x 1) :
    CoordinateSupport.correlatedSystem.transition (0 : Fin 1) x = 0 := by
  funext j
  fin_cases j <;>
    simp [CoordinateSupport.correlatedSystem, CoordinateSupport.matrixSystem, Fin.sum_univ_succ, h01]

end
end KomorebiPadic
