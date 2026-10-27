import KomorebiLSM
-- Additive conservation of two half-components does not preserve energy.
example : ‖(1/2 : ℝ)‖^2 + ‖(1/2 : ℝ)‖^2 = ‖(1 : ℝ)‖^2 := by norm_num
