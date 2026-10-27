import KomorebiPhysics.MixedTransfer
import Mathlib.Analysis.Matrix.Normed
#check map_ofNat
#check map_natCast
#check star_ofNat
#check Complex.conj_ofReal
#check map_inv₀
example : (starRingEnd ℂ) (2:ℂ) = 2 := by exact map_ofNat _ _
