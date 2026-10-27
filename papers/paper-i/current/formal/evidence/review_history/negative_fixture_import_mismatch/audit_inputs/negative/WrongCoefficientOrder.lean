import BoundaryConsumers
open PaperIBlock08Tests
example (a b : H) (hb : b ≠ 0) : (b⁻¹ * a) * b = a := by
  exact right_division_coefficient a b hb
