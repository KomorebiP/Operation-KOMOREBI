import MovingSyzygyError
import VariableJacobianHensel
import SyzygyCompatibleTarget
import Mathlib.Tactic.Abel

/-! Layer-by-layer nonlinear correction using a residue exact sequence.
No integral compatible-target splitting or integral right inverse is assumed. -/
namespace Komorebi.StrongArtin.GradedCompatibleHensel
open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.ResidualLayer
open Komorebi.StrongArtin.MovingSyzygyError
open Komorebi.StrongArtin.VariableJacobianHensel
open Komorebi.StrongArtin.SyzygyCompatibleTarget

variable {R k X W Z Xbar Wbar Zbar : Type*} [CommRing R] [Field k]
  [AddCommGroup X] [Module R X] [AddCommGroup W] [Module R W]
  [AddCommGroup Z] [Module R Z]
  [AddCommGroup Xbar] [Module k Xbar] [AddCommGroup Wbar] [Module k Wbar]
  [AddCommGroup Zbar] [Module k Zbar]

/-- A compatible normalized residue is enough for one nonlinear improvement. -/
theorem next_order_of_normalized_error_in_range
    (pi : R) (redX : Reduction pi X Xbar) (redW : Reduction pi W Wbar)
    (F : X → W) (D : X → X →ₗ[R] W) (Jbar : Xbar →ₗ[k] Wbar)
    (n : ℕ) (hn : 1 ≤ n) (x : X) (e : W)
    (herror : (pi ^ n) • e = F x)
    (hcompare : ∀ u, redW.map (D x u) = Jbar (redX.map u))
    (hcompatible : redW.map e ∈ LinearMap.range Jbar)
    (hgain : VariableRemainderRaisesOne pi F D) :
    ∃ x' : X, PowDivisible pi n (x' - x) ∧
      PowDivisible pi (n + 1) (F x') := by
  obtain ⟨ubar, hubar⟩ := hcompatible
  obtain ⟨u, hu⟩ := redX.onto (-ubar)
  have hres : redW.map (e + D x u) = 0 := by
    rw [map_add, hcompare, hu, map_neg, hubar, add_neg_cancel]
  have hlinear : PowDivisible pi (n + 1) (F x + D x ((pi ^ n) • u)) := by
    rw [map_smul, ← herror, ← smul_add]
    exact redW.scaled_error_raises_one n hres
  have hdelta : PowDivisible pi n ((pi ^ n) • u) := ⟨u, rfl⟩
  have hrem := hgain n hn x ((pi ^ n) • u) hdelta
  refine ⟨x + (pi ^ n) • u, ?_, ?_⟩
  · simpa only [add_sub_cancel_left] using hdelta
  · have heq : F (x + (pi ^ n) • u) =
        (F x + D x ((pi ^ n) • u)) +
          variableRemainder F D x ((pi ^ n) • u) := by
      unfold variableRemainder
      abel
    rw [heq]
    exact hlinear.add hrem

/-- Exact moving syzygies and residue exactness imply an actual next lift. -/
theorem next_order_of_exact_moving_relations
    (pi : R) (redX : Reduction pi X Xbar) (redW : Reduction pi W Wbar)
    (redZ : Reduction pi Z Zbar)
    (F : X → W) (D : X → X →ₗ[R] W)
    (B : X → W →ₗ[R] Z)
    (Jbar : Xbar →ₗ[k] Wbar) (Bbar : Wbar →ₗ[k] Zbar)
    (n : ℕ) (hn : 1 ≤ n) (x : X)
    (hfaithful : FaithfulAt pi redZ n)
    (herror : PowDivisible pi n (F x))
    (hidentity : B x (F x) = 0)
    (hB : ∀ w, redZ.map (B x w) = Bbar (redW.map w))
    (hD : ∀ u, redW.map (D x u) = Jbar (redX.map u))
    (hexact : LinearMap.range Jbar = LinearMap.ker Bbar)
    (hgain : VariableRemainderRaisesOne pi F D) :
    ∃ x' : X, PowDivisible pi n (x' - x) ∧
      PowDivisible pi (n + 1) (F x') := by
  obtain ⟨e, he⟩ := herror
  have hcompat := normalized_error_compatible pi redW redZ F B Bbar
    x n e hfaithful he hidentity hB
  apply next_order_of_normalized_error_in_range pi redX redW F D Jbar n hn x e he hD
    (by rw [hexact]; exact hcompat) hgain

/-- The v0.24 dual-kernel formulation supplies the same compatible residue target. -/
theorem next_order_of_dual_kernel_compatibility
    (pi : R) (redX : Reduction pi X Xbar) (redW : Reduction pi W Wbar)
    (F : X → W) (D : X → X →ₗ[R] W) (Jbar : Xbar →ₗ[k] Wbar)
    (S : Submodule k (Module.Dual k Wbar))
    (hS : LinearMap.ker Jbar.dualMap = S)
    (n : ℕ) (hn : 1 ≤ n) (x : X) (e : W)
    (herror : (pi ^ n) • e = F x)
    (hD : ∀ u, redW.map (D x u) = Jbar (redX.map u))
    (hcompatible : ∀ phi ∈ S, phi (redW.map e) = 0)
    (hgain : VariableRemainderRaisesOne pi F D) :
    ∃ x' : X, PowDivisible pi n (x' - x) ∧
      PowDivisible pi (n + 1) (F x') := by
  apply next_order_of_normalized_error_in_range pi redX redW F D Jbar n hn x e herror
  all_goals try assumption
  · rw [range_eq_compatibleTarget_of_dualKernel_eq Jbar S hS]
    exact (mem_compatibleTarget _ _).mpr hcompatible

/-- Exact relations at every residual state give compatible finite precision,
without a fixed integral target. Faithfulness is needed only below the cutoff. -/
theorem exists_approximation_to_finite_order
    (pi : R) (redX : Reduction pi X Xbar) (redW : Reduction pi W Wbar)
    (redZ : Reduction pi Z Zbar)
    (F : X → W) (D : X → X →ₗ[R] W) (B : X → W →ₗ[R] Z)
    (Jbar : Xbar →ₗ[k] Wbar) (Bbar : Wbar →ₗ[k] Zbar)
    (base : X) (N : ℕ)
    (hfaithful : ∀ n, 1 ≤ n → n < N → FaithfulAt pi redZ n)
    (hbase : PowDivisible pi 1 (F base))
    (hidentity : ∀ x, SameResidual pi base x → B x (F x) = 0)
    (hB : ∀ x, SameResidual pi base x → ∀ w,
      redZ.map (B x w) = Bbar (redW.map w))
    (hD : ∀ x, SameResidual pi base x → ∀ u,
      redW.map (D x u) = Jbar (redX.map u))
    (hexact : LinearMap.range Jbar = LinearMap.ker Bbar)
    (hgain : VariableRemainderRaisesOne pi F D) :
    ∀ n, 1 ≤ n → n ≤ N →
      ∃ x, SameResidual pi base x ∧ PowDivisible pi n (F x) := by
  intro n hn hN
  induction n with
  | zero => omega
  | succ n ih =>
      by_cases hn0 : n = 0
      · subst n
        exact ⟨base, sameResidual_self pi base, hbase⟩
      · have hn1 : 1 ≤ n := by omega
        obtain ⟨x, hx, herr⟩ := ih hn1 (by omega)
        obtain ⟨x', hstep, herr'⟩ := next_order_of_exact_moving_relations
          pi redX redW redZ F D B Jbar Bbar n hn1 x
          (hfaithful n hn1 (by omega)) herr (hidentity x hx)
          (hB x hx) (hD x hx) hexact hgain
        exact ⟨x', sameResidual_of_sameResidual_of_powDivisible_sub
          pi base x x' hn1 hx hstep, herr'⟩

/-- Terminating a faithful finite filtration produces an exact original root. -/
theorem exists_exact_root_from_graded_compatibility
    (pi : R) (redX : Reduction pi X Xbar) (redW : Reduction pi W Wbar)
    (redZ : Reduction pi Z Zbar)
    (F : X → W) (D : X → X →ₗ[R] W) (B : X → W →ₗ[R] Z)
    (Jbar : Xbar →ₗ[k] Wbar) (Bbar : Wbar →ₗ[k] Zbar)
    (base : X) (N : ℕ) (hN : 1 ≤ N) (hpi : pi ^ N = 0)
    (hfaithful : ∀ n, 1 ≤ n → n < N → FaithfulAt pi redZ n)
    (hbase : PowDivisible pi 1 (F base))
    (hidentity : ∀ x, SameResidual pi base x → B x (F x) = 0)
    (hB : ∀ x, SameResidual pi base x → ∀ w,
      redZ.map (B x w) = Bbar (redW.map w))
    (hD : ∀ x, SameResidual pi base x → ∀ u,
      redW.map (D x u) = Jbar (redX.map u))
    (hexact : LinearMap.range Jbar = LinearMap.ker Bbar)
    (hgain : VariableRemainderRaisesOne pi F D) :
    ∃ x, SameResidual pi base x ∧ F x = 0 := by
  obtain ⟨x, hx, hFx⟩ := exists_approximation_to_finite_order
    pi redX redW redZ F D B Jbar Bbar base N hfaithful hbase
    hidentity hB hD hexact hgain N hN le_rfl
  exact ⟨x, hx, eq_zero_of_pow_eq_zero hFx hpi⟩

end Komorebi.StrongArtin.GradedCompatibleHensel
