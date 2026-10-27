import KomorebiPhysics.Relativistic3DFourierHilbertStability
import Mathlib.Analysis.SpecialFunctions.Exponential
import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Analysis.Normed.Group.Bounded
open Filter Asymptotics
open scoped Topology
#check NormedSpace.exp_analytic
#check Analytic.contDiff
#check AnalyticAt.contDiffAt
#check ContDiff.continuous
#check ContDiff.contDiff_fderiv_apply
#check ContDiff.fderiv_right
#check IsCompact.exists_bound_of_continuousOn
#check isCompact_closedBall
#check Metric.isCompact_closedBall
#check ProperSpace.isCompact_closedBall
#check FiniteDimensional.proper
#check Convex.norm_image_sub_le_of_norm_fderiv_le
#check Convex.lipschitzOnWith_of_nnnorm_fderiv_le
#check Convex.norm_image_sub_le_of_norm_hasFDerivWithin_le
#check Analytic.differentiable
#check AnalyticAt.differentiableAt
#check Differentiable.continuous
#check norm_smul
#check norm_smul_of_nonneg
#check norm_smul_ofReal
