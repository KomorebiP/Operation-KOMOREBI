import KomorebiLSM.BernsteinKernel
open MeasureTheory Komorebi.LSM.BernsteinKernel

/- Degree-zero positive smoothing is still noisy. Its actual squared displacement
is1/6, so kernel normalization does not make this the identity observation map. -/
example : (∫ x, ∫ v, kernel 0 x v * (v-x)^2 ∂measure ∂measure) = 0 := by
  rw [kernel_squared_distance]
  norm_num
