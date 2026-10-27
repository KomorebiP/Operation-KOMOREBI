import GradedCompatibleHensel
import PolynomialResidueModel
import TruncatedUniformizerLayer
import PrincipalResidueFaithfulness

/-! Redundant polynomial systems lift using exact moving relation identities.
All polynomial residue comparisons and nonlinear Taylor gains are automatic.
The theorem retains the residual exactness hypothesis explicitly. -/
namespace Komorebi.StrongArtin.PolynomialMovingSyzygyHensel
open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.ResidualLayer
open Komorebi.StrongArtin.GradedCompatibleHensel
open Komorebi.StrongArtin.PolynomialResidueModel
open Komorebi.StrongArtin.PolynomialExpressionTaylor
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.VariableJacobianHensel
open Komorebi.StrongArtin.TruncatedUniformizerLayer

variable {R k ι κ η : Type*} [CommRing R] [Field k] [Fintype κ]

/-- Exact moving polynomial identities give a root of the original redundant
system. There is no integral splitting or integral right-inverse assumption. -/
theorem exists_exact_root_of_moving_polynomial_relations
    (pi : R) (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span {pi})
    (F : System ι κ R) (B : η → κ → Expr ι R) (base : ι → R)
    (N : ℕ) (hN : 1 ≤ N) (hpi : pi ^ N = 0)
    (hfaithful : ∀ n, 1 ≤ n → n < N → ∀ z : R, pi ^ n * z = 0 → q z = 0)
    (hbase : ∀ j, q (evalSystem F base j) = 0)
    (hidentity : ∀ x, SameResidual pi base x → relationMap B x (evalSystem F x) = 0)
    (hexact :
      LinearMap.range (systemDerivative (reduceSystem q F) (fun i => q (base i))) =
      LinearMap.ker (relationMap (reduceRelations q B) (fun i => q (base i)))) :
    ∃ x : ι → R, SameResidual pi base x ∧ evalSystem F x = 0 := by
  let rx := coordinateReduction (ι := ι) pi q hq hker
  let rw := coordinateReduction (ι := κ) pi q hq hker
  let rz := coordinateReduction (ι := η) pi q hq hker
  apply exists_exact_root_from_graded_compatibility pi rx rw rz
    (evalSystem F) (systemDerivative F) (relationMap B)
    (systemDerivative (reduceSystem q F) (fun i => q (base i)))
    (relationMap (reduceRelations q B) (fun i => q (base i)))
    base N hN hpi
  · intro n hn hnN z hz
    funext l
    apply hfaithful n hn hnN (z l)
    simpa only [Pi.smul_apply, smul_eq_mul, Pi.zero_apply] using congrFun hz l
  · apply (rw.zero_iff _).mp
    exact funext hbase
  · exact hidentity
  · intro x hx w
    exact relation_residue_comparison pi q hq hker B base x hx w
  · intro x hx u
    exact derivative_residue_comparison pi q hq hker F base x hx u
  · exact hexact
  · exact polynomialSystem_remainder_raises_one pi F

/-- In a quotient of a domain by `a^N`, leading-layer faithfulness and finite
termination follow from the coefficient-ring presentation, including mixed
characteristic examples. Only the exact relation and residue exactness inputs
are left for the equation system. -/
theorem exists_exact_root_over_truncated_regular_coefficients
    {A : Type*} [CommRing A] [IsDomain A]
    (a : A) (ha : a ≠ 0) (N : ℕ) (hN : 1 ≤ N)
    (f : A →+* R) (hf : Function.Surjective f)
    (hfker : RingHom.ker f = Ideal.span {a ^ N})
    (q : R →+* k) (hq : Function.Surjective q)
    (hqker : RingHom.ker q = Ideal.span {f a})
    (F : System ι κ R) (B : η → κ → Expr ι R) (base : ι → R)
    (hbase : ∀ j, q (evalSystem F base j) = 0)
    (hidentity : ∀ x, SameResidual (f a) base x →
      relationMap B x (evalSystem F x) = 0)
    (hexact :
      LinearMap.range (systemDerivative (reduceSystem q F) (fun i => q (base i))) =
      LinearMap.ker (relationMap (reduceRelations q B) (fun i => q (base i)))) :
    ∃ x : ι → R, SameResidual (f a) base x ∧ evalSystem F x = 0 := by
  have hnil : (f a) ^ N = 0 := by
    rw [← map_pow]
    change a ^ N ∈ RingHom.ker f
    rw [hfker]
    exact Ideal.subset_span (by simp)
  have hqa : q (f a) = 0 := by
    change f a ∈ RingHom.ker q
    rw [hqker]
    exact Ideal.subset_span (by simp)
  apply exists_exact_root_of_moving_polynomial_relations
    (f a) q hq hqker F B base N hN hnil
  · intro n _ hn z hz
    exact residue_zero_of_killed_by_power a ha N n hn f hf hfker q hqa z hz
  · exact hbase
  · exact hidentity
  · exact hexact

/-- Principal nilpotent residue kernels require no separate faithfulness
assumption. Exact moving relations and residue-level exactness imply a root of
the original polynomial equations, even when the full Jacobian is not onto. -/
theorem exists_exact_root_over_principal_nilpotent_residue
    (pi : R) (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span {pi}) (hnil : IsNilpotent pi)
    (F : System ι κ R) (B : η → κ → Expr ι R) (base : ι → R)
    (hbase : ∀ j, q (evalSystem F base j) = 0)
    (hidentity : ∀ x, SameResidual pi base x → relationMap B x (evalSystem F x) = 0)
    (hexact :
      LinearMap.range (systemDerivative (reduceSystem q F) (fun i => q (base i))) =
      LinearMap.ker (relationMap (reduceRelations q B) (fun i => q (base i)))) :
    ∃ x : ι → R, SameResidual pi base x ∧ evalSystem F x = 0 := by
  classical
  let N := Nat.find hnil
  have hpi : pi ^ N = 0 := Nat.find_spec hnil
  have hN : 1 ≤ N := by
    by_contra h
    have hzero : N = 0 := by omega
    have hone : (1 : R) = 0 := by simpa [hzero] using hpi
    have hf : (1 : k) = 0 := by simpa using congrArg q hone
    exact one_ne_zero hf
  apply exists_exact_root_of_moving_polynomial_relations
    pi q hq hker F B base N hN hpi
  · intro n _ hn z hz
    have hp : pi ^ n ≠ 0 := Nat.find_min hnil hn
    exact PrincipalResidueFaithfulness.residue_zero_of_nonterminal_power_kills
      pi q hq hker hnil n hp z hz
  · exact hbase
  · exact hidentity
  · exact hexact

end Komorebi.StrongArtin.PolynomialMovingSyzygyHensel
