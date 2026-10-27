import KomorebiLSM.ConditionalBernoulli

open Real
/- At Bernoulli parameter one, deleting the centering factor would assert
exp(1)≤exp(1/8). The actual centered envelope does not make that assertion. -/
example : ((1-(1:ℝ))+(1:ℝ)*exp 1)≤exp ((1:ℝ)^2/8) := by
  norm_num only [sub_self,one_mul,zero_add,one_pow]
  have hn : ¬exp (1:ℝ)≤exp (1/8:ℝ) :=
    not_le_of_gt (exp_lt_exp.mpr (by norm_num : (1/8:ℝ)<1))
  simp only [hn]
