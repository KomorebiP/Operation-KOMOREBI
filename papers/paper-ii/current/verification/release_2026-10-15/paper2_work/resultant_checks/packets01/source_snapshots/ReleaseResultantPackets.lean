import ReleaseResultantPolynomial
import Mathlib.RingTheory.Polynomial.Basic
import Mathlib.RingTheory.Coprime.Lemmas

set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperII.ReleaseResultantPackets

open Polynomial ResultantSeparation ReleaseResultantPolynomial

universe u v w
variable {K : Type u} {M : Type v} {ι : Type w}
variable [Field K] [AddCommGroup M] [Module K M] [Fintype ι] [DecidableEq ι]

/-- Coprime kernel decomposition, proved for every finite subcollection. -/
theorem zero_on_product_kernel (A T : Module.End K M) (f : ι → K[X])
    (hc : Pairwise fun i j => IsCoprime (f i) (f j))
    (s : Finset ι)
    (hT : ∀ i ∈ s, ∀ x ∈ LinearMap.ker (aeval A (f i)), T x = 0) :
    ∀ x ∈ LinearMap.ker (aeval A (∏ i ∈ s, f i)), T x = 0 := by
  induction s using Finset.induction_on with
  | empty =>
      intro x hx
      have hx0 : x = 0 := by simpa using hx
      simp [hx0]
  | @insert a s ha ih =>
      have hcop : IsCoprime (f a) (∏ i ∈ s, f i) :=
        IsCoprime.prod_right fun i hi => hc (by
          intro h
          subst i
          exact ha hi)
      intro x hx
      rw [Finset.prod_insert ha,
        ← Polynomial.sup_ker_aeval_eq_ker_aeval_mul_of_coprime A hcop] at hx
      obtain ⟨y, hy, z, hz, rfl⟩ := Submodule.mem_sup.mp hx
      rw [map_add, hT a (Finset.mem_insert_self _ _) y hy,
        ih (fun i hi => hT i (Finset.mem_insert_of_mem hi)) z hz, add_zero]

/-- A map vanishing on every primary packet vanishes on the whole module. -/
theorem eq_zero_of_packet_kernels [Module.Free K M] [Module.Finite K M]
    (A T : Module.End K M) (f : ι → K[X])
    (hc : Pairwise fun i j => IsCoprime (f i) (f j))
    (hchar : A.charpoly = ∏ i, f i)
    (hT : ∀ i, ∀ x ∈ LinearMap.ker (aeval A (f i)), T x = 0) : T = 0 := by
  ext x
  apply zero_on_product_kernel A T f hc Finset.univ (fun i _ => hT i) x
  rw [← hchar, A.aeval_self_charpoly]
  exact LinearMap.mem_ker.mpr rfl

/-- An actual polynomial divisibility witness implies inclusion of evaluated kernels. -/
theorem kernel_le_of_dvd (A : Module.End K M) {f g : K[X]} (h : f ∣ g) :
    LinearMap.ker (aeval A f) ≤ LinearMap.ker (aeval A g) := by
  obtain ⟨p, rfl⟩ := h
  intro x hx
  change aeval A (f * p) x = 0
  rw [mul_comm, map_mul, Module.End.mul_apply, LinearMap.mem_ker.mp hx, map_zero]

def complementaryFactor (f : ι → K[X]) (i : ι) : K[X] :=
  ∏ j ∈ Finset.univ.erase i, f j

theorem factor_mul_complement (f : ι → K[X]) (i : ι) :
    f i * complementaryFactor f i = ∏ j, f j := by
  exact Finset.mul_prod_erase _ _ (Finset.mem_univ i)

theorem coprime_complement (f : ι → K[X])
    (hc : Pairwise fun i j => IsCoprime (f i) (f j)) (i : ι) :
    IsCoprime (f i) (complementaryFactor f i) := by
  exact IsCoprime.prod_right fun j hj => hc (Finset.mem_erase.mp hj).1.symm

theorem factor_dvd_other_complement (f : ι → K[X]) {i j : ι} (hij : i ≠ j) :
    f j ∣ complementaryFactor f i := by
  exact Finset.dvd_prod_of_mem _ (Finset.mem_erase.mpr ⟨hij.symm, Finset.mem_univ j⟩)

end Komorebi.PaperII.ReleaseResultantPackets
