module

public import PaperX.FiniteArtinRestore

/-!
# Constructed cyclotomic Artin boundary values and nonvanishing

The global abelian factorization, the actual ramified correction, and the
finite boundary limits are now constructed. The residue-domination theorem
therefore has no remaining factorization or convergence hypothesis in the
cyclotomic application. This is not yet a Chebotarev occurrence theorem.
-/
@[expose] public section
noncomputable section
open NumberField Chebotarev Filter
open PaperX.ArtinLocalFactors PaperX.ArtinFactorization
open PaperX.FrobeniusArtinDomination PaperX.FiniteArtinRestore
open scoped Topology
namespace PaperX.ConstructedArtinBoundary

abbrev NontrivialCharacter (K L : Type*) [Field K] [Field L] [Algebra K L] :=
  {χ : Character K L // χ ≠ 1}

instance nontrivialFintype (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] : Fintype (NontrivialCharacter K L) := Fintype.ofFinite _

/-- The factorization in the exact form used by the residue bridge, with the
trivial character separated and the actual ramified prime set retained. -/
theorem separated_factorization (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    [IsMulCommutative Gal(L/K)] (s : ℝ) (hs : 1 < s) :
    NumberField.dedekindZeta L (s : ℂ) = idealArtinSeries K L 1 s *
      (ramifiedCorrection K L (s : ℂ) *
        ∏ χ : NontrivialCharacter K L, idealArtinSeries K L χ.1 s) := by
  classical
  let : Fintype (Character K L) := Fintype.ofFinite _
  rw [zeta_factorization K L (s := (s : ℂ)) hs, tprod_fintype]
  simp_rw [seriesC_real]
  rw [Fintype.prod_eq_mul_prod_compl (1 : Character K L) (fun χ ↦ idealArtinSeries K L χ s),
    Finset.prod_subtype (p := fun χ : Character K L ↦ χ ≠ 1) ({(1 : Character K L)}ᶜ) (fun χ ↦ by simp)
      (fun χ ↦ idealArtinSeries K L χ s)]
  ring

/-- For a general finite abelian extension, only the regular-factor boundary
limits remain premises; factorization and ramified correction are constructed. -/
theorem nonzero_of_boundary_limits (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    [IsMulCommutative Gal(L/K)] (v : NontrivialCharacter K L → ℂ)
    (hv : ∀ χ, Tendsto (fun s : ℝ ↦ idealArtinSeries K L χ.1 s) (𝓝[>] 1) (𝓝 (v χ))) :
    ∀ χ, v χ ≠ 0 := by
  obtain ⟨r, _, hR⟩ := ramifiedCorrection_limit_nonzero K L
  have hf : ∀ᶠ s : ℝ in 𝓝[>] 1, NumberField.dedekindZeta L (s : ℂ) =
      idealArtinSeries K L 1 s * (ramifiedCorrection K L (s : ℂ) *
        ∏ χ : NontrivialCharacter K L, idealArtinSeries K L χ.1 s) := by
    filter_upwards [self_mem_nhdsWithin] with s hs
    exact separated_factorization K L s hs
  exact (actual_factors_nonzero K L hf hR hv).2

/-- Both former analytic inputs are discharged for an actual cyclotomic
extension over an arbitrary number field. Commutativity is constructed from
the faithful cyclotomic character, not supplied as a custom interface. -/
theorem cyclotomic_family_boundary_nonzero (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    (m : ℕ) [NeZero m] [IsCyclotomicExtension {m} K L] :
    ∃ v : NontrivialCharacter K L → ℂ,
      (∀ χ, Tendsto (fun s : ℝ ↦ idealArtinSeries K L χ.1 s) (𝓝[>] 1) (𝓝 (v χ))) ∧
      ∀ χ, v χ ≠ 0 := by
  classical
  obtain ⟨ζ, hζ⟩ := IsCyclotomicExtension.exists_isPrimitiveRoot K L
    (Set.mem_singleton m) (NeZero.ne m)
  have : IsMulCommutative Gal(L/K) := .of_comm fun a b ↦
    IsPrimitiveRoot.autToPow_injective K hζ (by rw [map_mul, map_mul, mul_comm])
  choose v hv using fun χ : NontrivialCharacter K L ↦ cyclotomic_boundary_limit K L m χ.1 χ.2
  have hv' : ∀ χ, Tendsto (fun s : ℝ ↦ idealArtinSeries K L χ.1 s) (𝓝[>] 1) (𝓝 (v χ)) := by
    simpa only [seriesC_real] using hv
  exact ⟨v, hv', nonzero_of_boundary_limits K L v hv'⟩

/-- Single-character form on the original residue bridge's exact ideal series. -/
theorem cyclotomic_artin_boundary_nonzero (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    (m : ℕ) [NeZero m] [IsCyclotomicExtension {m} K L]
    (χ : Character K L) (hχ : χ ≠ 1) :
    ∃ v : ℂ, v ≠ 0 ∧
      Tendsto (fun s : ℝ ↦ idealArtinSeries K L χ s) (𝓝[>] 1) (𝓝 v) := by
  obtain ⟨v, hv, hn⟩ := cyclotomic_family_boundary_nonzero K L m
  exact ⟨v ⟨χ, hχ⟩, hn ⟨χ, hχ⟩, hv ⟨χ, hχ⟩⟩

end PaperX.ConstructedArtinBoundary
