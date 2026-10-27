import PaperXI.ActualIntegralGeneralLinear
import PaperXI.ActualLocalUnitDecomposition
import PaperXI.NormalizerExtensionInducing58
import Mathlib.Algebra.Group.Subgroup.Pointwise

/-!
# Periodic lattices and their literal first congruence group

The chain used below is the actual sequence of scalar-uniformizer translates
of the integral lattice in `E^m`, viewed as a vector space over `K`. Its first
congruence group consists of automorphisms preserving every lattice and acting
as the identity modulo the next lattice. Uniformizer normalization is proved
from the coordinate definitions. This is not an identification with the
simple-character group of an arbitrary stratum.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualELatticeNormalizer59

section Chain
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

/-- All automorphisms preserving every additive lattice in a chain. -/
def chainStabilizer (L : ℤ → AddSubgroup V) : Subgroup (V ≃ₗ[K] V) where
  carrier := {g | ∀ i v, g v ∈ L i ↔ v ∈ L i}
  one_mem' := by intro i v; rfl
  mul_mem' := by
    intro g h hg hh i v
    exact (hg i (h v)).trans (hh i v)
  inv_mem' := by
    intro g hg i v
    exact (hg i (g⁻¹ v)).symm.trans (by simp)

/-- The literal first congruence condition on every adjacent lattice pair. -/
def firstCongruence (L : ℤ → AddSubgroup V) : Subgroup (V ≃ₗ[K] V) where
  carrier := {g | g ∈ chainStabilizer L ∧ ∀ i v, v ∈ L i → g v - v ∈ L (i + 1)}
  one_mem' := by
    refine ⟨(chainStabilizer L).one_mem, ?_⟩
    intro i v hv
    simp
  mul_mem' := by
    intro g h hg hh
    refine ⟨(chainStabilizer L).mul_mem hg.1 hh.1, ?_⟩
    intro i v hv
    have ha := (hg.1 (i + 1) (h v - v)).mpr (hh.2 i v hv)
    have hb := hg.2 i v hv
    convert (L (i + 1)).add_mem ha hb using 1
    simp only [LinearEquiv.mul_apply, map_sub]
    abel
  inv_mem' := by
    intro g hg
    refine ⟨(chainStabilizer L).inv_mem hg.1, ?_⟩
    intro i v hv
    have h := hg.2 i (g⁻¹ v) ((hg.1 i (g⁻¹ v)).mp (by simpa using hv))
    have hn := (L (i + 1)).neg_mem h
    simpa using hn

/-- Congruence automorphisms preserve the chain by definition. -/
theorem firstCongruence_le (L : ℤ → AddSubgroup V) :
    firstCongruence (K := K) L ≤ chainStabilizer L := fun _ h => h.1

/-- Every chain stabilizer normalizes the actual first congruence group. -/
theorem stabilizer_normalizes_firstCongruence (L : ℤ → AddSubgroup V) :
    chainStabilizer L ≤ Subgroup.normalizer (firstCongruence (K := K) L : Set (V ≃ₗ[K] V)) := by
  intro h hh
  apply Subgroup.mem_normalizer_iff.mpr
  intro g
  have step (h : V ≃ₗ[K] V) (hh : h ∈ chainStabilizer L)
      (g : V ≃ₗ[K] V) (hg : g ∈ firstCongruence L) :
      h * g * h⁻¹ ∈ firstCongruence L := by
    refine ⟨(chainStabilizer L).mul_mem
      ((chainStabilizer L).mul_mem hh hg.1) ((chainStabilizer L).inv_mem hh), ?_⟩
    intro i v hv
    have hi : h⁻¹ v ∈ L i := (hh i (h⁻¹ v)).mp (by simpa using hv)
    have hx := (hh (i + 1) (g (h⁻¹ v) - h⁻¹ v)).mpr (hg.2 i _ hi)
    simpa using hx
  constructor
  · exact step h hh g
  · intro hg
    have hi := step h⁻¹ ((chainStabilizer L).inv_mem hh) (h * g * h⁻¹) hg
    simpa [mul_assoc] using hi

/-- Integer translates of one lattice by an actual linear automorphism. -/
def periodicChain (t : V ≃ₗ[K] V) (L : AddSubgroup V) (i : ℤ) : AddSubgroup V :=
  L.comap (t ^ (-i)).toAddMonoidHom

/-- Translation of the chain is proved for every positive and negative power. -/
theorem periodicChain_shift (t : V ≃ₗ[K] V) (L : AddSubgroup V)
    (r i : ℤ) (v : V) :
    (t ^ r) v ∈ periodicChain t L (i + r) ↔ v ∈ periodicChain t L i := by
  change (t ^ (-(i + r))) ((t ^ r) v) ∈ L ↔ (t ^ (-i)) v ∈ L
  rw [← LinearEquiv.mul_apply, ← zpow_add]
  rw [show -(i + r) + r = -i by omega]

/-- All translates of the chosen generator normalize first congruence. -/
theorem power_normalizes_firstCongruence (t : V ≃ₗ[K] V) (L : AddSubgroup V)
    (r : ℤ) : t ^ r ∈ Subgroup.normalizer
      (firstCongruence (K := K) (periodicChain t L) : Set (V ≃ₗ[K] V)) := by
  have shift (r i : ℤ) (v : V) :
      (t ^ r) v ∈ periodicChain t L i ↔ v ∈ periodicChain t L (i - r) := by
    have h := periodicChain_shift t L r (i - r) v
    rwa [show i - r + r = i by omega] at h
  have step (r : ℤ) (g : V ≃ₗ[K] V)
      (hg : g ∈ firstCongruence (periodicChain t L)) :
      t ^ r * g * (t ^ r)⁻¹ ∈ firstCongruence (periodicChain t L) := by
    refine ⟨?_, ?_⟩
    · intro i v
      change (t ^ r) (g ((t ^ r)⁻¹ v)) ∈ periodicChain t L i ↔ _
      rw [shift, hg.1 (i - r)]
      simpa [zpow_neg, sub_eq_add_neg] using shift (-r) (i - r) v
    · intro i v hv
      have hi : (t ^ r)⁻¹ v ∈ periodicChain t L (i - r) := by
        rw [← zpow_neg]
        apply (shift (-r) (i - r) v).mpr
        simpa [sub_eq_add_neg] using hv
      have hx := hg.2 (i - r) _ hi
      have hy := (shift r (i + 1) (g ((t ^ r)⁻¹ v) - (t ^ r)⁻¹ v)).mpr
        (by rwa [show i + 1 - r = i - r + 1 by omega])
      simpa using hy
  apply Subgroup.mem_normalizer_iff.mpr
  intro g
  constructor
  · exact step r g
  · intro hg
    have hi := step (-r) (t ^ r * g * (t ^ r)⁻¹) hg
    simpa [zpow_neg, mul_assoc] using hi
end Chain

end PaperXI.ActualELatticeNormalizer59
