import PaperXI.SchrodingerUniversal
import PaperXI.HeisenbergSelector

/-! Character support and actual isotropic selectors in every irreducible
representation with the prescribed nontrivial central character. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SchrodingerConsequences
open scoped Classical
open PaperXI.Heisenberg PaperXI.HeisenbergForm PaperXI.HeisenbergGeometry
variable {K X W : Type*} [Field K] [AddCommGroup X] [Module K X]
variable [AddCommGroup W] [Module ℂ W]

/-- Restriction of the arbitrary representation to the actual zero-central lift. -/
def restriction (σ : Representation ℂ (Element K X) W)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) :
    Representation ℂ (Multiplicative L) W :=
  σ.comp (HeisenbergProjector.liftHom L hL)

/-- The literal isotropic averaging operator in the arbitrary target. -/
def projector (σ : Representation ℂ (Element K X) W)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) [Fintype L] :
    Module.End ℂ W := FiniteAverage.average (G := Multiplicative L) (restriction σ L hL)

/-- These actual target averages are idempotent without any irreducibility assumption. -/
theorem projector_idempotent (σ : Representation ℂ (Element K X) W)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) [Fintype L] :
    (projector σ L hL).comp (projector σ L hL) = projector σ L hL := by
  simpa only [projector] using
    FiniteAverage.idempotent (G := Multiplicative L) (restriction σ L hL)

/-- The range is the target's actual common fixed subspace. -/
theorem range_eq_invariants (σ : Representation ℂ (Element K X) W)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) [Fintype L] :
    LinearMap.range (projector σ L hL) =
      Representation.invariants (G := Multiplicative L) (restriction σ L hL) := by
  simpa only [projector] using
    FiniteAverage.range_eq (G := Multiplicative L) (restriction σ L hL)

/-- The same target average indexed by the actual embedded subgroup. -/
def subgroupProjector (σ : Representation ℂ (Element K X) W)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) [Fintype L] :
    Module.End ℂ W :=
  FiniteAverage.average (σ.comp (HeisenbergProjector.liftedSubgroup L hL).subtype)

/-- The additive-coordinate and actual-subgroup averages agree. -/
theorem projector_eq_subgroupProjector (σ : Representation ℂ (Element K X) W)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) [Fintype L] :
    projector σ L hL = subgroupProjector σ L hL := by
  ext w
  simp only [projector, subgroupProjector, FiniteAverage.average_apply]
  change (Fintype.card (Multiplicative L) : ℂ)⁻¹ •
      ∑ a : Multiplicative L, σ (HeisenbergProjector.liftHom L hL a) w =
    (Fintype.card (HeisenbergProjector.liftedSubgroup L hL) : ℂ)⁻¹ •
      ∑ a : HeisenbergProjector.liftedSubgroup L hL, σ a.val w
  rw [← Fintype.card_congr (HeisenbergProjector.liftEquiv L hL).toEquiv]
  congr 1
  exact Function.Bijective.sum_comp (HeisenbergProjector.liftEquiv L hL).bijective
    (fun a : HeisenbergProjector.liftedSubgroup L hL => σ a.val w)

variable [Fintype X] [Fintype (Module.Dual K X)] [FiniteDimensional K X]
variable (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
variable (σ : Representation ℂ (Element K X) W) [Representation.IsIrreducible σ]
variable (hcentral : ∀ z, σ (centralElement z) = ψ z • LinearMap.id)
include hψ h2 hcentral

/-- The constructed equivalence conjugates each actual model operator to the target. -/
theorem conjugates (g : Element K X) :
    (SchrodingerUniversal.equiv ψ hψ h2 σ hcentral).toLinearEquiv.conj
      (representation ψ h2 g) = σ g := by
  ext w
  rw [LinearEquiv.conj_apply_apply]
  let U := (SchrodingerUniversal.equiv ψ hψ h2 σ hcentral).toLinearEquiv
  have h : U ((representation ψ h2 g) (U.symm w)) = σ g (U (U.symm w)) :=
    SchrodingerUniversal.equiv_intertwines ψ hψ h2 σ hcentral g (U.symm w)
  simpa only [LinearEquiv.apply_symm_apply] using h

/-- Trace is preserved under the constructed equivalence, not postulated. -/
theorem trace_eq_model (g : Element K X) :
    LinearMap.trace ℂ W (σ g) =
      LinearMap.trace ℂ (X → ℂ) (representation ψ h2 g) := by
  rw [← conjugates ψ hψ h2 σ hcentral g, LinearMap.trace_conj']

/-- The irreducible target character is supported exactly on the center. -/
theorem character_support (g : Element K X) :
    LinearMap.trace ℂ W (σ g) =
      if g.position = 0 ∧ g.frequency = 0 then
        (Fintype.card X : ℂ) * ψ g.central else 0 := by
  rw [trace_eq_model ψ hψ h2 σ hcentral]
  exact SchrodingerTrace.character_support hψ g.position g.frequency g.central

/-- The equivalence transports the actual finite averaging operator. -/
theorem conjugates_projector (L : Submodule K (X × Module.Dual K X))
    (hL : IsIsotropic form L) [Fintype L] :
    (SchrodingerUniversal.equiv ψ hψ h2 σ hcentral).toLinearEquiv.conj
      (HeisenbergProjector.projector ψ h2 L hL) = projector σ L hL := by
  change (SchrodingerUniversal.equiv ψ hψ h2 σ hcentral).toLinearEquiv.conj
      ((Fintype.card (Multiplicative L) : ℂ)⁻¹ •
        ∑ a : Multiplicative L, representation ψ h2 (HeisenbergProjector.liftHom L hL a)) =
    (Fintype.card (Multiplicative L) : ℂ)⁻¹ •
      ∑ a : Multiplicative L, σ (HeisenbergProjector.liftHom L hL a)
  rw [map_smul, map_sum]
  simp_rw [conjugates ψ hψ h2 σ hcentral]

/-- The target isotropic projector has the same exact cardinality-ratio trace. -/
theorem trace_projector (L : Submodule K (X × Module.Dual K X))
    (hL : IsIsotropic form L) [Fintype L] :
    LinearMap.trace ℂ W (projector σ L hL) =
      (Fintype.card L : ℂ)⁻¹ * Fintype.card X := by
  rw [← conjugates_projector ψ hψ h2 σ hcentral L hL, LinearMap.trace_conj']
  exact HeisenbergSelector.trace_projector hψ h2 L hL

/-- The dimension of every isotropic selector range is the cardinality ratio. -/
theorem rank_projector (L : Submodule K (X × Module.Dual K X))
    (hL : IsIsotropic form L) [Fintype L] :
    (Module.finrank ℂ (LinearMap.range (projector σ L hL)) : ℂ) =
      (Fintype.card L : ℂ)⁻¹ * Fintype.card X := by
  let : FiniteDimensional ℂ W := SchrodingerUniversal.finiteDimensional ψ hψ h2 σ hcentral
  have h := HeisenbergSelector.rank_average (G := Multiplicative L) (V := W)
    (restriction σ L hL)
  exact h.trans (trace_projector ψ hψ h2 σ hcentral L hL)

/-- Every maximal isotropic selector has trace one in the arbitrary target. -/
theorem maximal_trace_one (L : Submodule K (X × Module.Dual K X))
    (hL : IsMaximalIsotropic form L) [Fintype L] :
    LinearMap.trace ℂ W (projector σ L hL.1) = 1 := by
  rw [← conjugates_projector ψ hψ h2 σ hcentral L hL.1, LinearMap.trace_conj']
  exact HeisenbergSelector.maximal_trace_one hψ h2 L hL

/-- A maximal isotropic average has a one-dimensional range in the target.
Target finite dimensionality is derived from Stone–von Neumann inside the proof. -/
theorem maximal_rank_one (L : Submodule K (X × Module.Dual K X))
    (hL : IsMaximalIsotropic form L) [Fintype L] :
    Module.finrank ℂ (LinearMap.range (projector σ L hL.1)) = 1 := by
  let : FiniteDimensional ℂ W := SchrodingerUniversal.finiteDimensional ψ hψ h2 σ hcentral
  have h := HeisenbergSelector.rank_average (G := Multiplicative L) (V := W)
    (restriction σ L hL.1)
  change (Module.finrank ℂ (LinearMap.range (projector σ L hL.1)) : ℂ) =
    LinearMap.trace ℂ W (projector σ L hL.1) at h
  rw [maximal_trace_one ψ hψ h2 σ hcentral L hL] at h
  exact_mod_cast h

/-- Every maximal isotropic zero-central lift fixes exactly a line in the target. -/
theorem maximal_fixed_line (L : Submodule K (X × Module.Dual K X))
    (hL : IsMaximalIsotropic form L) [Fintype L] :
    Module.finrank ℂ
      (Representation.invariants (G := Multiplicative L) (restriction σ L hL.1)) = 1 := by
  rw [← range_eq_invariants]
  exact maximal_rank_one ψ hψ h2 σ hcentral L hL

end PaperXI.SchrodingerConsequences
