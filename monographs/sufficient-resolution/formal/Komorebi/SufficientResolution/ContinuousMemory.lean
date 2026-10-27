import Komorebi.SufficientResolution.VariationOfConstants
import Komorebi.SufficientResolution.ExponentialTransfer
import Komorebi.SufficientResolution.DiscreteMemory

/-!
# Hidden-state elimination from actual continuous full dynamics

All four blocks are bounded real linear maps on Banach spaces. The trajectories
are constructed by the full operator exponential. Prepared and arbitrary hidden
initial states are not identified.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution

/-- Bounded visible/hidden blocks for real continuous-time evolution. -/
structure ContinuousBlockDynamics (V : Type*) [NormedAddCommGroup V] [NormedSpace ℝ V]
    (H : Type*) [NormedAddCommGroup H] [NormedSpace ℝ H] where
  A : V →L[ℝ] V
  B : H →L[ℝ] V
  G : V →L[ℝ] H
  D : H →L[ℝ] H

namespace ContinuousBlockDynamics
open ContinuousFlow
variable {V H : Type*}
variable [NormedAddCommGroup V] [NormedSpace ℝ V]
variable [NormedAddCommGroup H] [NormedSpace ℝ H]
variable (b : ContinuousBlockDynamics V H)

/-- The algebraic blocks retained by the previously checked discrete theory. -/
def linear : BlockDynamics ℝ V H :=
  ⟨b.A.toLinearMap, b.B.toLinearMap, b.G.toLinearMap, b.D.toLinearMap⟩

/-- The actual bounded full-state generator. -/
def generator : (V × H) →L[ℝ] (V × H) :=
  ((b.A.comp (ContinuousLinearMap.fst ℝ V H)) +
    (b.B.comp (ContinuousLinearMap.snd ℝ V H))).prod
  ((b.G.comp (ContinuousLinearMap.fst ℝ V H)) +
    (b.D.comp (ContinuousLinearMap.snd ℝ V H)))

@[simp] theorem generator_apply (y : V) (z : H) :
    b.generator (y,z) = (b.A y + b.B z, b.G y + b.D z) := rfl

@[simp] theorem generator_toLinearMap : b.generator.toLinearMap = b.linear.step := rfl

/-- The actual observed trajectory, with the complete initial state retained. -/
def visible (y : V) (z : H) (t : ℝ) : V := (flow b.generator t (y,z)).1
/-- The actual hidden trajectory of the full system. -/
def hiddenState (y : V) (z : H) (t : ℝ) : H := (flow b.generator t (y,z)).2
/-- Bounded continuous-time hidden-return kernel. -/
def memory (t : ℝ) : V →L[ℝ] V := b.B.comp ((flow b.D t).comp b.G)
/-- Prepared initial state means the hidden coordinate is exactly zero. -/
def prepared (t : ℝ) : V →L[ℝ] V :=
  (ContinuousLinearMap.fst ℝ V H).comp
    ((flow b.generator t).comp (ContinuousLinearMap.inl ℝ V H))

@[simp] theorem visible_zero (y : V) (z : H) : b.visible y z 0 = y := by
  simp [visible]
@[simp] theorem hiddenState_zero (y : V) (z : H) : b.hiddenState y z 0 = z := by
  simp [hiddenState]
@[simp] theorem prepared_apply (t : ℝ) (y : V) : b.prepared t y = b.visible y 0 t := rfl
@[simp] theorem prepared_zero : b.prepared 0 = 1 := by
  ext y; simp
@[simp] theorem memory_at_zero : b.memory 0 = b.B.comp b.G := by
  ext y; simp [memory]

variable [CompleteSpace V] [CompleteSpace H]

 theorem hasDerivAt_visible (y : V) (z : H) (t : ℝ) :
    HasDerivAt (b.visible y z)
      (b.A (b.visible y z t) + b.B (b.hiddenState y z t)) t :=
  (hasDerivAt_flow_apply b.generator (y,z) t).fst

 theorem hasDerivAt_hiddenState (y : V) (z : H) (t : ℝ) :
    HasDerivAt (b.hiddenState y z)
      (b.G (b.visible y z t) + b.D (b.hiddenState y z t)) t :=
  (hasDerivAt_flow_apply b.generator (y,z) t).snd

 theorem continuous_visible (y : V) (z : H) : Continuous (b.visible y z) :=
  continuous_iff_continuousAt.mpr (fun t => (b.hasDerivAt_visible y z t).continuousAt)

 theorem continuous_hiddenState (y : V) (z : H) : Continuous (b.hiddenState y z) :=
  continuous_iff_continuousAt.mpr (fun t => (b.hasDerivAt_hiddenState y z t).continuousAt)

omit [CompleteSpace V] in
 theorem continuous_memory : Continuous b.memory :=
  (sandwich b.B b.G).continuous.comp (continuous_flow b.D)

/-- Exact hidden elimination, derived from the full exponential trajectory. -/
 theorem hidden_elimination (y : V) (z : H) (t : ℝ) :
    b.hiddenState y z t = flow b.D t z +
      ∫ s in (0:ℝ)..t, flow b.D (t-s) (b.G (b.visible y z s)) := by
  have h := variation_of_constants b.D (b.hiddenState y z)
    (fun s => b.G (b.visible y z s))
    (b.G.continuous.comp (b.continuous_visible y z))
    (fun s => by simpa [add_comm] using b.hasDerivAt_hiddenState y z s) t
  simpa using h

 theorem hidden_integrand_continuous (y : V) (z : H) (t : ℝ) :
    Continuous (fun s => flow b.D (t-s) (b.G (b.visible y z s))) :=
  ((continuous_flow b.D).comp (continuous_const.sub continuous_id)).clm_apply
    (b.G.continuous.comp (b.continuous_visible y z))

/-- The observable hidden forcing splits into initialization and feedback memory. -/
 theorem hidden_forcing_decomposition (y : V) (z : H) (t : ℝ) :
    b.B (b.hiddenState y z t) = b.B (flow b.D t z) +
      ∫ s in (0:ℝ)..t, b.memory (t-s) (b.visible y z s) := by
  rw [b.hidden_elimination, map_add]
  rw [← b.B.intervalIntegral_comp_comm
    ((b.hidden_integrand_continuous y z t).intervalIntegrable 0 t)]
  rfl

/-- The genuine continuous Volterra memory equation, including hidden initialization. -/
 theorem continuous_memory_equation (y : V) (z : H) (t : ℝ) :
    HasDerivAt (b.visible y z)
      (b.A (b.visible y z t) + b.B (flow b.D t z) +
        ∫ s in (0:ℝ)..t, b.memory (t-s) (b.visible y z s)) t := by
  have h := b.hasDerivAt_visible y z t
  rw [b.hidden_forcing_decomposition, ← add_assoc] at h
  exact h

/-- Prepared hidden initialization removes only the initial-state forcing. -/
 theorem prepared_memory_equation (y : V) (t : ℝ) :
    HasDerivAt (fun s => b.prepared s y)
      (b.A (b.prepared t y) +
        ∫ s in (0:ℝ)..t, b.memory (t-s) (b.prepared s y)) t := by
  simpa using b.continuous_memory_equation y 0 t

/-- The full first-order system has the constructed exponential as its unique solution. -/
 theorem full_solution_unique (x : ℝ → V × H)
    (hx : ∀ t, HasDerivAt x (b.generator (x t)) t) :
    x = fun t => flow b.generator t (x 0) := by
  funext t
  exact homogeneous_solution b.generator x hx t

end ContinuousBlockDynamics
end Komorebi.SufficientResolution
