import KomorebiQCOS
open KomorebiQCOS
example {x middle estimate a b tolerance : ℝ}
    (ha : ErrorBound x middle a) (hb : ErrorBound middle estimate b) :
    ErrorBound x estimate tolerance := by
  exact errorBound_accept ha hb
