import KomorebiSpace.ProtectedLinearCertificates
-- Zero functionals cannot be normalized separating certificates.
example : KomorebiSpace.ProtectedLinearCertificates.Certificate
    (LinearMap.id : ℚ →ₗ[ℚ] ℚ) (LinearMap.id : ℚ →ₗ[ℚ] ℚ) 1 := by
  refine ⟨0, 0, rfl, ?_⟩
  norm_num
