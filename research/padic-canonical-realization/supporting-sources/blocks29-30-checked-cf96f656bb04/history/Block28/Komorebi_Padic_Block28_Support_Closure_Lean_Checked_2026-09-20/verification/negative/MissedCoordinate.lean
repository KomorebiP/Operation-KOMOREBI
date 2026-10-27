import KomorebiPadic.SupportExamples
open KomorebiPadic.CoordinateSupport
example : (2 : Fin 3) ∉ least correlatedSystem := by rw [correlatedSystem_least_full]; decide
