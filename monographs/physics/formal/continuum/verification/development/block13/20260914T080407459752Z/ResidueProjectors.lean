module
public import KomorebiPhysics.ResidueCharacters
public import KomorebiPhysics.SpectralCells

/-! Finite-character projectors are proved equal to actual infinite masks.
The phases use the number spectrum n, not the harmonic spectrum n+1/2. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace ResidueProjectors
open scoped BigOperators lp
open BoundedSpectral
variable (M : ℕ) [NeZero M]

def rotationSymbol (k : ZMod M) : Symbol :=
  ofBound (fun n => ZMod.stdAddChar (k * (n : ZMod M))) 1
    (fun _ => (ResidueCharacters.character_norm M _).le)

def rotation (k : ZMod M) : Space →L[ℂ] Space := diagonal (rotationSymbol M k)

theorem rotation_apply (k : ZMod M) (x : Space) (n : ℕ) :
    rotation M k x n = ZMod.stdAddChar (k*(n : ZMod M)) * x n := rfl

theorem rotation_exponential (k : ZMod M) (x : Space) (n : ℕ) :
    rotation M k x n =
      Complex.exp (2 * Real.pi * Complex.I * (k.val : ℂ) * (n : ℂ) / (M : ℂ)) * x n := by
  rw [rotation_apply]
  have h := ResidueCharacters.character_nat M k.val n
  simpa only [ZMod.natCast_zmod_val] using congrArg (fun z : ℂ => z * x n) h

theorem rotation_zero : rotation M 0 = ContinuousLinearMap.id ℂ Space := by
  ext x n
  simp [rotation_apply]

theorem rotation_add (j k : ZMod M) :
    rotation M (j+k) = (rotation M j).comp (rotation M k) := by
  ext x n
  simp only [ContinuousLinearMap.comp_apply, rotation_apply, add_mul,
    AddChar.map_add_eq_mul, mul_assoc]

theorem rotation_inverse (k : ZMod M) :
    (rotation M (-k)).comp (rotation M k) = ContinuousLinearMap.id ℂ Space := by
  rw [← rotation_add, neg_add_cancel, rotation_zero]

/-- Actual finite sum of bounded operators, before any mask is supplied. -/
def projector (r : ZMod M) : Space →L[ℂ] Space :=
  (M : ℂ)⁻¹ • ∑ k : ZMod M, ZMod.stdAddChar (-(r*k)) • rotation M k

theorem projector_apply (r : ZMod M) (x : Space) (n : ℕ) :
    projector M r x n = if (n : ZMod M) = r then x n else 0 := by
  simp only [projector, smul_apply, sum_apply,
    lp.coeFn_smul, Pi.smul_apply, lp.coeFn_sum, Finset.sum_apply, smul_eq_mul,
    rotation_apply]
  simp_rw [← mul_assoc]
  rw [← Finset.sum_mul, ← mul_assoc, ResidueCharacters.selection]
  split_ifs <;> simp

/-- Equality in the space of bounded operators, not only on finite vectors. -/
theorem projector_eq_mask (r : ZMod M) :
    projector M r = SpectralCells.mask {n : ℕ | (n : ZMod M) = r} := by
  ext x n
  simp only [projector_apply, SpectralCells.mask_apply, Set.mem_ofPred_eq]

/-- The literal infinite series has a proved HasSum. -/
theorem projector_hasSum (r : ZMod M) (x : Space) :
    HasSum (fun n : {n : ℕ | (n : ZMod M) = r} => DiagonalDomain.coordinate (n : ℕ) x)
      (projector M r x) := by
  rw [projector_eq_mask]
  exact DiagonalDomain.coordinateAtlas.cell_sum _ x

/-- ZMod labels avoid an accidental truncated subtraction at the vacuum. -/
def atlas : StrongAtlas Space (ZMod M) :=
  DiagonalDomain.coordinateAtlas.coarsenInfinite (fun n : ℕ => (n : ZMod M))

theorem atlas_proj (r : ZMod M) : (atlas M).proj r = projector M r := by
  exact (projector_eq_mask M r).symm

theorem projector_idempotent (r : ZMod M) (x : Space) :
    projector M r (projector M r x) = projector M r x := by
  simpa only [atlas_proj] using (atlas M).idempotent r x

theorem projector_orthogonal (r s : ZMod M) (hrs : r ≠ s) (x : Space) :
    projector M r (projector M s x) = 0 := by
  simpa only [atlas_proj] using (atlas M).orthogonal r s hrs x

theorem projector_selfAdjoint (r : ZMod M) (x y : Space) :
    inner ℂ (projector M r x) y = inner ℂ x (projector M r y) := by
  simpa only [atlas_proj] using (atlas M).selfAdjoint r x y

theorem projector_complete (x : Space) : ∑ r : ZMod M, projector M r x = x := by
  have h := (atlas M).strong x
  simpa only [tsum_fintype, atlas_proj] using h.tsum_eq

theorem projector_energy (r : ZMod M) (x : Space) :
    HasSum (fun n : {n : ℕ | (n : ZMod M) = r} => ‖x n‖ ^ 2)
      (‖projector M r x‖ ^ 2) := by
  rw [projector_eq_mask]
  exact SpectralCells.mask_energy_hasSum _ x

theorem projector_mem_domain (eig : ℕ → ℝ) (r : ZMod M)
    (x : (DiagonalDomain.operator eig).domain) :
    projector M r x ∈ (DiagonalDomain.operator eig).domain := by
  rw [projector_eq_mask]
  exact SpectralCells.mask_mem_domain eig _ x

theorem projector_evolution (eig : ℕ → ℝ) (r : ZMod M) (x : Space) (t : ℝ) :
    projector M r (SpectralEvolution.evolution eig t x) =
      SpectralEvolution.evolution eig t (projector M r x) := by
  simp only [projector_eq_mask, SpectralCells.mask_evolution]

/-- The character rotation is the constructed number-spectrum phase evolution. -/
theorem rotation_eq_number_evolution (k : ZMod M) :
    rotation M k = SpectralEvolution.evolution (fun n : ℕ => (n : ℝ))
      (-(2 * Real.pi * (k.val : ℝ) / (M : ℝ))) := by
  ext x n
  rw [rotation_exponential, SpectralEvolution.evolution_apply]
  congr 1
  congr 1
  push_cast
  ring

/-- Exact bridge to the conventional n mod M label. -/
theorem label_iff (n : ℕ) (r : ZMod M) :
    (n : ZMod M) = r ↔ n % M = r.val := by
  constructor
  · intro h
    have hh := congrArg ZMod.val h
    simpa only [ZMod.val_natCast] using hh
  · intro h
    apply ZMod.val_injective
    simpa only [ZMod.val_natCast] using h

end ResidueProjectors
end KomorebiPhysics
