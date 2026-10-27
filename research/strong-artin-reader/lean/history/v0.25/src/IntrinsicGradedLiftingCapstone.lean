import PolynomialMovingSyzygyHensel
import SyzygyCompatibleTarget

/-! The dual exactness endpoint of syzygy-corrected auxiliary selection feeds
the nonlinear moving-relation theorem, once actual relation rows are supplied. -/
namespace Komorebi.StrongArtin.IntrinsicGradedLiftingCapstone
open Komorebi.StrongArtin.SyzygyCompatibleTarget
open Komorebi.StrongArtin.PolynomialMovingSyzygyHensel
open Komorebi.StrongArtin.PolynomialResidueModel
open Komorebi.StrongArtin.PolynomialExpressionTaylor
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.VariableJacobianHensel

section Linear
variable {k U W Z : Type*} [Field k]
  [AddCommGroup U] [Module k U] [AddCommGroup W] [Module k W]
  [AddCommGroup Z] [Module k Z]

/-- The remaining dual kernel consists exactly of the supplied relation rows
then the primal correction image is the compatible relation kernel. -/
theorem image_eq_relation_kernel_of_dual_exactness
    (J : U →ₗ[k] W) (B : W →ₗ[k] Z)
    (hdual : LinearMap.ker J.dualMap = LinearMap.range B.dualMap) :
    LinearMap.range J = LinearMap.ker B := by
  rw [range_eq_compatibleTarget_dualKernel, compatibleTarget, hdual,
    LinearMap.range_dualMap_eq_dualAnnihilator_ker,
    Subspace.dualAnnihilator_dualCoannihilator_eq]

end Linear

/-- Formal endpoint: an exact moving relation system plus syzygy-corrected
residual dual exactness lifts the original nonlinear equations over a principal
nilpotent residue ring. The input identifies actual relation rows, not just an
abstract isomorphic syzygy space. -/
theorem exists_exact_root_from_syzygy_corrected_dual_exactness
    {R k ι κ η : Type*} [CommRing R] [Field k] [Fintype κ]
    (pi : R) (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span {pi}) (hnil : IsNilpotent pi)
    (F : System ι κ R) (B : η → κ → Expr ι R) (base : ι → R)
    (hbase : ∀ j, q (evalSystem F base j) = 0)
    (hidentity : ∀ x, SameResidual pi base x → relationMap B x (evalSystem F x) = 0)
    (hdual :
      LinearMap.ker
        (systemDerivative (reduceSystem q F) (fun i => q (base i))).dualMap =
      LinearMap.range
        (relationMap (reduceRelations q B) (fun i => q (base i))).dualMap) :
    ∃ x : ι → R, SameResidual pi base x ∧ evalSystem F x = 0 := by
  apply exists_exact_root_over_principal_nilpotent_residue pi q hq hker hnil
    F B base hbase hidentity
  exact image_eq_relation_kernel_of_dual_exactness _ _ hdual

end Komorebi.StrongArtin.IntrinsicGradedLiftingCapstone
