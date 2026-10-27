module
public import KomorebiPhysics.InfiniteCellCurrents
public import KomorebiPhysics.SpectralSolutions

/-!
Actual infinite spectral cells: coordinate formulas, maximal-domain invariance,
graph estimates, energy sums, and constructed-orbit consequences.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace SpectralCells
open Filter Classical
open scoped BigOperators Topology lp
variable {I J : Type*} [DecidableEq I]
variable (eig : I → ℝ)

/-- The spectral mask is the already constructed strong cell projector. -/
def mask (C : Set I) : ℓ²(I, ℂ) →L[ℂ] ℓ²(I, ℂ) := DiagonalDomain.coordinateAtlas.cell C

theorem mask_apply (C : Set I) (x : ℓ²(I, ℂ)) (n : I) :
    mask C x n = if n ∈ C then x n else 0 := by
  have h := congrArg (fun y : ℓ²(I, ℂ) => y n)
    (DiagonalDomain.coordinateAtlas.proj_cell C n x)
  change (DiagonalDomain.coordinate n (mask C x)) n = _ at h
  by_cases hn : n ∈ C
  · simpa [DiagonalDomain.coordinateAtlas, DiagonalDomain.coordinate_apply, hn] using h
  · simpa [DiagonalDomain.coordinateAtlas, DiagonalDomain.coordinate_apply, hn] using h

theorem mask_mem_domain (C : Set I) (x : (DiagonalDomain.operator eig).domain) :
    mask C x ∈ (DiagonalDomain.operator eig).domain :=
  (DiagonalDomain.atlas eig).cell_mem_domain (DiagonalDomain.closed eig)
    (DiagonalDomain.graph_compatible eig) C x

def domainMask (C : Set I) : (DiagonalDomain.operator eig).domain →ₗ[ℂ]
    (DiagonalDomain.operator eig).domain :=
  (DiagonalDomain.atlas eig).cellProject (DiagonalDomain.closed eig)
    (DiagonalDomain.graph_compatible eig) C

theorem domainMask_coe (C : Set I) (x : (DiagonalDomain.operator eig).domain) :
    (domainMask eig C x : ℓ²(I, ℂ)) = mask C x := rfl

theorem operator_mask (C : Set I) (x : (DiagonalDomain.operator eig).domain) :
    DiagonalDomain.operator eig (domainMask eig C x) = mask C (DiagonalDomain.operator eig x) := by
  apply lp.ext
  funext n
  simp only [DiagonalDomain.operator_apply, domainMask_coe, mask_apply]
  by_cases hn : n ∈ C <;> simp [hn]

/-- Boundedness holds in the actual graph norm as well as the state norm. -/
theorem graph_norm_mask_le (C : Set I) (x : (DiagonalDomain.operator eig).domain) :
    GraphDomain.graphNorm (DiagonalDomain.operator eig) (domainMask eig C x) ≤
      GraphDomain.graphNorm (DiagonalDomain.operator eig) x := by
  have hx := DiagonalDomain.coordinateAtlas.cell_norm_le C (x : ℓ²(I, ℂ))
  have hy := DiagonalDomain.coordinateAtlas.cell_norm_le C (DiagonalDomain.operator eig x)
  have hs := GraphDomain.graphNorm_sq (DiagonalDomain.operator eig) (domainMask eig C x)
  rw [domainMask_coe, operator_mask] at hs
  have ht := GraphDomain.graphNorm_sq (DiagonalDomain.operator eig) x
  change ‖mask C x‖ ≤ ‖(x : ℓ²(I, ℂ))‖ at hx
  change ‖mask C (DiagonalDomain.operator eig x)‖ ≤ ‖DiagonalDomain.operator eig x‖ at hy
  nlinarith [norm_nonneg (mask C x), norm_nonneg (mask C (DiagonalDomain.operator eig x)),
    GraphDomain.graphNorm_nonneg (DiagonalDomain.operator eig) (domainMask eig C x),
    GraphDomain.graphNorm_nonneg (DiagonalDomain.operator eig) x]

theorem mask_energy_hasSum (C : Set I) (x : ℓ²(I, ℂ)) :
    HasSum (fun i : C => ‖x i‖ ^ 2) (‖mask C x‖ ^ 2) := by
  have h := DiagonalDomain.coordinateAtlas.cell_energy_hasSum C x
  have he : ∀ i : C, DiagonalDomain.coordinateAtlas.energy x i = ‖x i‖ ^ 2 := by
    intro i
    simp [StrongAtlas.energy, DiagonalDomain.coordinateAtlas, DiagonalDomain.coordinate_apply,
      lp.norm_single (by norm_num : (0 : ENNReal) < 2)]
  exact h.congr_fun (fun i => (he i).symm)

theorem graph_mask_hasSum (C : Set I) (x : (DiagonalDomain.operator eig).domain) :
    HasSum (fun i : C => (1 + eig i ^ 2) * ‖(x : ℓ²(I, ℂ)) i‖ ^ 2)
      (GraphDomain.graphNorm (DiagonalDomain.operator eig) (domainMask eig C x) ^ 2) := by
  have h := (mask_energy_hasSum C (x : ℓ²(I, ℂ))).add
    (mask_energy_hasSum C (DiagonalDomain.operator eig x))
  have hs : GraphDomain.graphNorm (DiagonalDomain.operator eig) (domainMask eig C x) ^ 2 =
      ‖mask C x‖ ^ 2 + ‖mask C (DiagonalDomain.operator eig x)‖ ^ 2 := by
    rw [GraphDomain.graphNorm_sq, domainMask_coe, operator_mask]
  rw [hs]
  exact h.congr_fun (fun i => by
    rw [DiagonalDomain.operator_apply, SpectralGraph.weighted_norm_sq]
    ring)

/-- Spectral coarse atlas with arbitrary infinite fibers and all its domain
and graph obligations discharged, not supplied by the caller. -/
def coarse (f : I → J) : DomainAtlas (DiagonalDomain.operator eig) J :=
  (DiagonalDomain.atlas eig).coarsenClosed (DiagonalDomain.closed eig)
    (DiagonalDomain.graph_compatible eig) f

theorem coarse_project_coe (f : I → J) (a : J) (x : (DiagonalDomain.operator eig).domain) :
    ((coarse eig f).project a x : ℓ²(I, ℂ)) = mask (f ⁻¹' {a}) x := rfl

theorem coarse_graph_compatible (f : I → J) : (coarse eig f).GraphCompatible :=
  (DiagonalDomain.atlas eig).coarsenClosed_graph (DiagonalDomain.closed eig)
    (DiagonalDomain.graph_compatible eig) f

theorem coarse_current_zero (f : I → J) (x : (DiagonalDomain.operator eig).domain) (a b : J) :
    (coarse eig f).current x a b = 0 := by
  calc
    _ = ∑' i : f ⁻¹' {a}, ∑' j : f ⁻¹' {b}, (DiagonalDomain.atlas eig).current x i j :=
      (DiagonalDomain.atlas eig).coarse_current_iterated f
        (fun a x => (DiagonalDomain.atlas eig).cell_mem_domain (DiagonalDomain.closed eig)
          (DiagonalDomain.graph_compatible eig) (f ⁻¹' {a}) x)
        (DiagonalDomain.symmetric eig) x a b
    _ = 0 := by simp only [SpectralGraph.spectral_current_zero, tsum_zero]

section Time
open BoundedSpectral SpectralEvolution
variable (values : ℕ → ℝ)

theorem mask_evolution (C : Set ℕ) (x : Space) (t : ℝ) :
    mask C (evolution values t x) = evolution values t (mask C x) := by
  apply lp.ext
  funext n
  simp only [mask_apply, evolution_apply]
  by_cases hn : n ∈ C <;> simp [hn]

theorem cell_energy_constant (C : Set ℕ) (x : Space) (t : ℝ) :
    ‖mask C (evolution values t x)‖ ^ 2 = ‖mask C x‖ ^ 2 := by
  rw [mask_evolution, norm_preserved]

/-- A true derivative of an infinite spectral-cell energy, with no supplied
Schrödinger trajectory assumption. -/
theorem spectral_cell_hasDerivAt (C : Set ℕ)
    (x : (DiagonalDomain.operator values).domain) (t : ℝ) :
    HasDerivAt (fun s => ‖mask C (evolution values s (x : Space))‖ ^ 2) 0 t := by
  have he : (fun s => ‖mask C (evolution values s (x : Space))‖ ^ 2) =
      (fun _ : ℝ => ‖mask C (x : Space)‖ ^ 2) := funext (cell_energy_constant values C (x : Space))
  rw [he]
  exact hasDerivAt_const t _

/-- Constructed non-diagonal packet solutions may use any graph-compatible
fine atlas. Closedness of this spectral operator discharges all coarse domains. -/
theorem constructed_coarse_hasDerivAt {A B : Type*}
    (P : DomainAtlas (DiagonalDomain.operator values) A) (hG : P.GraphCompatible)
    (f : A → B) (x : (DiagonalDomain.operator values).domain) (t : ℝ) (a : B) :
    HasDerivAt (fun s => ∑' i : f ⁻¹' {a}, P.atlas.energy (evolution values s (x : Space)) i)
      (∑' b, (P.coarsenClosed (DiagonalDomain.closed values) hG f).current
        (domainEvolution values t x) a b) t := by
  exact P.infinite_cell_hasDerivAt f
    (fun a y => P.cell_mem_domain (DiagonalDomain.closed values) hG (f ⁻¹' {a}) y)
    (DiagonalDomain.symmetric values) (ψ := fun s => domainEvolution values s x)
    (orbit_hasDerivAt values x t) a
end Time
end SpectralCells
end KomorebiPhysics
