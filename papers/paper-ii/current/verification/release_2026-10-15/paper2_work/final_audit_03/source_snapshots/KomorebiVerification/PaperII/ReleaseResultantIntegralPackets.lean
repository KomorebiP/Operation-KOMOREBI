import KomorebiVerification.PaperII.ReleaseResultantPackets

set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperII.ReleaseResultantIntegralPackets

open Polynomial ResultantSeparation ReleaseResultantPolynomial ReleaseResultantPackets
open scoped TensorProduct

universe u v w z
variable {R : Type u} {K : Type v} {L : Type w} {ι : Type z}
variable [CommRing R] [Field K] [Algebra R K] [AddCommGroup L] [Module R L]
variable [Module.Free R L] [Module.Finite R L] [Fintype ι] [DecidableEq ι]

/-- The several-packet theorem retains the integral resultant of each pair,
the actual tensor-extended operator, and the actual image lattice. -/
theorem integral_spectral_packets_exist (A : Module.End R L) (f : ι → R[X])
    (hf : ∀ i, (f i).Monic)
    (hc : Pairwise fun i j =>
      IsCoprime ((f i).map (algebraMap R K)) ((f j).map (algebraMap R K)))
    (hchar : A.charpoly = ∏ i, f i) :
    ∃ E : ι → Module.End K (K ⊗[R] L),
      (∀ i, E i * E i = E i) ∧
      (∀ i, LinearMap.range (E i) =
        LinearMap.ker (aeval (A.baseChange K) ((f i).map (algebraMap R K)))) ∧
      (∑ i, E i) = 1 ∧
      (∀ i j, i ≠ j → E i * E j = 0) ∧
      ∀ i x, x ∈ tensorLattice (K := K) (R := R) (L := L) →
        (algebraMap R K ((f i).resultant (∏ j ∈ Finset.univ.erase i, f j)) • E i) x ∈
          tensorLattice (K := K) (R := R) (L := L) := by
  let g (i : ι) : R[X] := ∏ j ∈ Finset.univ.erase i, f j
  let fK (i : ι) : K[X] := (f i).map (algebraMap R K)
  have hg (i : ι) : (g i).Monic := monic_prod_of_monic _ _ (fun j _ => hf j)
  have hmapg (i : ι) : (g i).map (algebraMap R K) = complementaryFactor fK i := by
    simp [g, complementaryFactor, fK, Polynomial.map_prod]
  have hcop (i : ι) : IsCoprime ((f i).map (algebraMap R K))
      ((g i).map (algebraMap R K)) := by
    rw [hmapg]
    exact coprime_complement fK hc i
  have hfact (i : ι) : A.charpoly = f i * g i := by
    rw [hchar]
    exact (Finset.mul_prod_erase _ _ (Finset.mem_univ i)).symm
  have hex (i : ι) := integral_resultant_projector A (f i) (g i) (hf i) (hg i)
    (hcop i) (hfact i)
  choose u v hb cert hidem hrange hker hcompl hclear using hex
  let E (i : ι) := separator (algebraMap R K ((f i).resultant (g i)))
    (aeval (A.baseChange K) ((v i).map (algebraMap R K)))
    (aeval (A.baseChange K) ((g i).map (algebraMap R K)))
  have hcharK : (A.baseChange K).charpoly = ∏ i, fK i := by
    simp only [LinearMap.charpoly_baseChange, hchar, Polynomial.map_prod, fK]
  have hfix (i : ι) (x : K ⊗[R] L)
      (hx : x ∈ LinearMap.ker (aeval (A.baseChange K) (fK i))) : E i x = x :=
    separator_apply_of_mem_ker_F (cert i) hx
  have hzero (i j : ι) (hij : i ≠ j) (x : K ⊗[R] L)
      (hx : x ∈ LinearMap.ker (aeval (A.baseChange K) (fK j))) : E i x = 0 := by
    apply separator_apply_of_mem_ker_G
    rw [hmapg]
    exact kernel_le_of_dvd (A.baseChange K) (factor_dvd_other_complement fK hij) hx
  have hassemble := assemble_projectors (A.baseChange K) fK hc hcharK E hrange hfix hzero
  exact ⟨E, hidem, hrange, hassemble.1, hassemble.2, hclear⟩

end Komorebi.PaperII.ReleaseResultantIntegralPackets
