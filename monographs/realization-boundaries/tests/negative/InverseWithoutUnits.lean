import RealizationBoundaries
open RealizationBoundaries
set_option autoImplicit false
example (x : Ambient) : diagonal (inverseDiagonal 0) (diagonal 0 x) = x :=
  diagonal_inverse_left 0 (fun p => (one_ne_zero : (1 : Coordinate p) ≠ 0)) x
