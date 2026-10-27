import KomorebiLSM.RationalLorentzMatrix
import KomorebiLSM.DyadicBernsteinCertificate

/-! Arithmetic records retain the submitted lower bound as well as the exact sound certificate. -/
set_option autoImplicit false
namespace Komorebi.LSM.RecordedBernsteinFixture
open TensorBernsteinCertificate

structure RecordedLeaf (p : Polynomial₂) (R : Rectangle) where
  certificate : LocalCertificate p R
  lowerBound : ℚ
  lower_nonnegative : 0≤lowerBound
  lower_valid : ∀ i j,lowerBound≤certificate.coefficient i j
  lower_attained : ∃ i j,certificate.coefficient i j=lowerBound

end Komorebi.LSM.RecordedBernsteinFixture
