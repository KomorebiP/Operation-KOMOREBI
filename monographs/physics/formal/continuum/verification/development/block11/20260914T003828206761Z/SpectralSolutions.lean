module
public import KomorebiPhysics.SpectralSchrodinger

/-! Existence and uniqueness for the constructed real diagonal generator,
and actual source (6.26)--(6.41) continuity without a supplied flow premise. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
open Filter
open scoped Topology BigOperators lp

namespace GraphDomain
variable {H : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
variable {T : H →ₗ.[ℂ] H}

/-- Uniqueness uses symmetry and true derivatives on the actual domain.
This theorem alone does not assert existence for a general symmetric operator. -/
theorem solution_unique (hT : IsSymmetric T) (ψ χ : ℝ → T.domain)
    (hψ : ∀ t, HasDerivAt (fun s => (ψ s : H)) ((-Complex.I) • T (ψ t)) t)
    (hχ : ∀ t, HasDerivAt (fun s => (χ s : H)) ((-Complex.I) • T (χ t)) t)
    {t₀ : ℝ} (h₀ : ψ t₀ = χ t₀) : ψ = χ := by
  let δ : ℝ → T.domain := fun t => ψ t - χ t
  have hd : ∀ t, HasDerivAt (fun s => (δ s : H)) ((-Complex.I) • T (δ t)) t := by
    intro t
    simpa only [δ, Pi.sub_def, Submodule.coe_sub, LinearPMap.map_sub, smul_sub] using (hψ t).sub (hχ t)
  funext t
  have hn := norm_sq_constant hT δ hd t t₀
  have hz : δ t₀ = 0 := sub_eq_zero.mpr h₀
  rw [hz] at hn
  simp only [Submodule.coe_zero, norm_zero, zero_pow (by decide : 2 ≠ 0)] at hn
  have hnorm : ‖(δ t : H)‖ = 0 := sq_eq_zero_iff.mp hn
  have hδ : δ t = 0 := Subtype.ext (norm_eq_zero.mp hnorm)
  exact sub_eq_zero.mp hδ
end GraphDomain

namespace SpectralEvolution
open BoundedSpectral
variable (eig : ℕ → ℝ)

/-- Genuine global existence and uniqueness for arbitrary real diagonal spectra. -/
theorem exists_unique_solution (x : (DiagonalDomain.operator eig).domain) :
    ∃! ψ : ℝ → (DiagonalDomain.operator eig).domain,
      ψ 0 = x ∧ ∀ t, HasDerivAt (fun s => (ψ s : Space))
        ((-Complex.I) • DiagonalDomain.operator eig (ψ t)) t := by
  refine ⟨fun t => domainEvolution eig t x, ⟨domainEvolution_zero eig x, ?_⟩, ?_⟩
  · intro t
    exact orbit_hasDerivAt eig x t
  · intro ψ hψ
    exact GraphDomain.solution_unique (DiagonalDomain.symmetric eig) ψ
      (fun t => domainEvolution eig t x) hψ.2 (orbit_hasDerivAt eig x)
      (hψ.1.trans (domainEvolution_zero eig x).symm)

theorem solution_formula (x : (DiagonalDomain.operator eig).domain)
    (ψ : ℝ → (DiagonalDomain.operator eig).domain) (h₀ : ψ 0 = x)
    (hψ : ∀ t, HasDerivAt (fun s => (ψ s : Space))
      ((-Complex.I) • DiagonalDomain.operator eig (ψ t)) t) (t : ℝ) :
    ψ t = domainEvolution eig t x := by
  have h := GraphDomain.solution_unique (DiagonalDomain.symmetric eig) ψ
    (fun s => domainEvolution eig s x) hψ (orbit_hasDerivAt eig x)
    (h₀.trans (domainEvolution_zero eig x).symm)
  exact congrFun h t

variable {I : Type*}

/-- Packet current sum for an arbitrary domain-invariant strong atlas,
not only the diagonal coordinate atlas. -/
theorem packet_hasDerivAt (P : DomainAtlas (DiagonalDomain.operator eig) I)
    (x : (DiagonalDomain.operator eig).domain) (t : ℝ) (i : I) :
    HasDerivAt (fun s => P.atlas.energy (evolution eig s (x : Space)) i)
      (∑' j, P.current (domainEvolution eig t x) i j) t := by
  exact P.hasDerivAt_energy_tsum (DiagonalDomain.symmetric eig)
    (ψ := fun s => domainEvolution eig s x) (orbit_hasDerivAt eig x t) i

/-- Actual unconditional current-row sum equals the derivative of the constructed orbit. -/
theorem packet_current_hasSum (P : DomainAtlas (DiagonalDomain.operator eig) I)
    (x : (DiagonalDomain.operator eig).domain) (t : ℝ) (i : I) :
    HasSum (P.current (domainEvolution eig t x) i)
      (deriv (fun s => P.atlas.energy (evolution eig s (x : Space)) i) t) := by
  rw [(packet_hasDerivAt eig P x t i).deriv]
  exact (P.current_hasSum (DiagonalDomain.symmetric eig) _ i).summable.hasSum

/-- Finite receiving regions retain the actual infinite boundary-current limit. -/
theorem region_boundary_limit [DecidableEq I]
    (P : DomainAtlas (DiagonalDomain.operator eig) I)
    (x : (DiagonalDomain.operator eig).domain) (t : ℝ) (B : Finset I) :
    Tendsto (fun F : Finset I => ∑ i ∈ B, ∑ j ∈ F \ B,
        P.current (domainEvolution eig t x) i j) atTop
      (𝓝 (deriv (fun s => ∑ i ∈ B, P.atlas.energy (evolution eig s (x : Space)) i) t)) := by
  exact P.region_derivative_boundary_limit (DiagonalDomain.symmetric eig)
    (ψ := fun s => domainEvolution eig s x) (orbit_hasDerivAt eig x t) B

/-- Parseval conservation for every l2 state does not require a derivative or domain membership. -/
theorem total_packet_energy (P : StrongAtlas Space I) (x : Space) (t : ℝ) :
    (∑' i, P.energy (evolution eig t x) i) = ‖x‖ ^ 2 := by
  rw [P.energy_tsum, norm_preserved]

theorem coordinate_energy_constant (x : Space) (t : ℝ) (n : ℕ) :
    DiagonalDomain.coordinateAtlas.energy (evolution eig t x) n = ‖x n‖ ^ 2 := by
  simp only [StrongAtlas.energy, DiagonalDomain.coordinateAtlas,
    DiagonalDomain.coordinate_apply, lp.norm_single (by norm_num : (0 : ENNReal) < 2),
    coordinate_norm]

/-- Spectral populations have no interpacket transport. Other invariant-domain
atlases in the general theorem need not diagonalize the generator. -/
theorem coordinate_current_zero (x : (DiagonalDomain.operator eig).domain)
    (t : ℝ) (i j : ℕ) :
    (DiagonalDomain.atlas eig).current (domainEvolution eig t x) i j = 0 :=
  SpectralGraph.spectral_current_zero eig _ i j

/-- Generator-image norm is conserved for the constructed domain solution. -/
theorem action_norm_preserved (x : (DiagonalDomain.operator eig).domain) (t : ℝ) :
    ‖DiagonalDomain.operator eig (domainEvolution eig t x)‖ = ‖DiagonalDomain.operator eig x‖ := by
  rw [operator_commutes, norm_preserved]

end SpectralEvolution
end KomorebiPhysics
