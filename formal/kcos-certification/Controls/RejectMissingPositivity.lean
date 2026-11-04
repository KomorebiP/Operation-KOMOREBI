import KCosCertification

set_option autoImplicit false
open KCosCertification KomorebiQCOS

-- Expected type error: the positive lower endpoint is an essential premise.
example {p lower upper : ℝ} (h : Enclosed p lower upper) :
    Enclosed (Real.log p) (Real.log lower) (Real.log upper) := by
  exact enclosed_log h
