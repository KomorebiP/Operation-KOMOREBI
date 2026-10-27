import Mathlib.Topology.Algebra.InfiniteSum.Real
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

set_option autoImplicit false
noncomputable section
namespace KomorebiSpace.DiagonalRegularization

/-- Natural index `j` denotes the printed positive coordinate `j+1`. -/
def index (j : ℕ) : ℝ := (j : ℝ) + 1

def aCoord (m j : ℕ) : ℝ := (m : ℝ)^2 / ((m : ℝ)^2 + (index j)^2)
def vCoord (m j : ℕ) : ℝ := index j / ((m : ℝ)^2 + (index j)^2)
def cCoord (m j : ℕ) : ℝ := (m : ℝ)^2 / (index j * ((m : ℝ)^2 + (index j)^2))
def wCoord (j : ℕ) : ℝ := (index j)⁻¹
def bCoord (j : ℕ) : ℝ := ((index j)^2)⁻¹

def A (m : ℕ) : ℝ := ∑' j, (aCoord m j)^2
def B (m : ℕ) : ℝ := ∑' j, (vCoord m j)^2
def partialA (m K : ℕ) : ℝ := ∑ j ∈ Finset.range K, (aCoord m j)^2
def partialB (m K : ℕ) : ℝ := ∑ j ∈ Finset.range K, (vCoord m j)^2

end KomorebiSpace.DiagonalRegularization
