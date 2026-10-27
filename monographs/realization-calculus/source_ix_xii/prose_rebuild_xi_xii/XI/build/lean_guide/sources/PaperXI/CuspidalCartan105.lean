import PaperXI.CuspidalContraction105
import PaperXI.IntertwiningAlong105
import PaperXI.SplitRadical105

/-! An inflated finite cuspidal representation has no noncentral Cartan
intertwiners. The arithmetic Cartan decomposition remains a separate explicit
input; its cuspidal exclusion is proved on actual matrices. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CuspidalCartan105
open Matrix Representation
open PaperXI.SplitRadical105 PaperXI.IntertwiningAlong105
variable {ι R F k C V : Type*} [Fintype ι] [DecidableEq ι]
  [CommRing R] [Field F] [Field k] [Fintype k] [Field C] [CharZero C]
  [AddCommGroup V] [Module C V]

/-- The exact invariant-vanishing part of finite cuspidality needed here.
The parameter map covers the full radical of each coordinate maximal parabolic. -/
def Cuspidal (σ : Representation C (GL ι k) V) : Prop :=
  ∀ S : Finset ι, S.Nonempty → S ≠ Finset.univ →
    CuspidalContraction105.NoFixed (σ.comp (radicalMap (R := k) S))

theorem diagonal_intertwiner_zero (f : R →+* F) (red : R →+* k)
    (hred : Function.Surjective red) (π : R) (hπ : f π ≠ 0) (hπred : red π = 0)
    (σ : Representation C (GL ι k) V) (hσ : Cuspidal σ)
    (a : ι → ℕ) (ha0 : ∃ i, a i = 0) (ha1 : ∃ i, a i ≠ 0)
    (T : V →ₗ[C] V)
    (hT : Along (GeneralLinearGroup.map f) (σ.comp (GeneralLinearGroup.map red))
      (cartan (f π) hπ a) T) : T = 0 := by
  have hne : (zeroSet a).Nonempty := by
    obtain ⟨i, hi⟩ := ha0
    exact ⟨i, (mem_zeroSet a i).mpr hi⟩
  have hproper : zeroSet a ≠ Finset.univ := by
    obtain ⟨i, hi⟩ := ha1
    intro he
    apply hi
    exact (mem_zeroSet a i).mp (he ▸ Finset.mem_univ i)
  apply CuspidalContraction105.map_eq_zero
    (σ.comp (radicalMap (R := k) (zeroSet a))) (hσ _ hne hproper) T
  intro X v
  obtain ⟨u, w, hu, hw, he⟩ := exists_contracted_lift f red hred π hπ hπred a X.toAdd
  have ht := hT u w he.symm v
  simpa only [MonoidHom.comp_apply, hu, hw, map_one, Module.End.one_apply,
    radicalMap, MonoidHom.coe_mk, OneHom.coe_mk] using ht

/-- Normalized Cartan form. This is an arithmetic decomposition, not an
intertwining assertion: no representation occurs in its definition. -/
def HasCartan (f : R →+* F) (π : R) (hπ : f π ≠ 0) : Prop :=
  ∀ g : GL ι F, ∃ c : Fˣ, ∃ l r : GL ι R, ∃ a : ι → ℕ,
    (∃ i, a i = 0) ∧
    g = GeneralLinearGroup.scalar ι c *
      (GeneralLinearGroup.map f l * cartan (f π) hπ a * GeneralLinearGroup.map f r)

/-- Finite cuspidality forces a scalar-times-integral matrix. This does not
assume irreducibility of the inflated representation or a preproved support bound. -/
theorem intertwining_support (f : R →+* F) (red : R →+* k)
    (hred : Function.Surjective red) (π : R) (hπ : f π ≠ 0) (hπred : red π = 0)
    (hCartan : HasCartan (ι := ι) f π hπ)
    (σ : Representation C (GL ι k) V) (hσ : Cuspidal σ)
    (g : GL ι F)
    (hg : ExistsAt (GeneralLinearGroup.map f) (σ.comp (GeneralLinearGroup.map red)) g) :
    ∃ c : Fˣ, ∃ u : GL ι R,
      g = GeneralLinearGroup.scalar ι c * GeneralLinearGroup.map f u := by
  obtain ⟨c, l, r, a, ha0, he⟩ := hCartan g
  have hc : ∀ x : GL ι F, Commute (GeneralLinearGroup.scalar ι c) x := by
    intro x
    apply Units.ext
    change Matrix.scalar ι (c : F) * x.val = x.val * Matrix.scalar ι (c : F)
    exact Matrix.scalar_comm (c : F) (Commute.all _) x.val
  rw [he] at hg
  have hg' := existsAt_remove_central (GeneralLinearGroup.map f)
    (σ.comp (GeneralLinearGroup.map red)) _ _ hc hg
  obtain ⟨T, hn, ht⟩ := existsAt_of_left_right (GeneralLinearGroup.map f)
    (σ.comp (GeneralLinearGroup.map red)) l r (cartan (f π) hπ a) hg'
  have ha : ∀ i, a i = 0 := by
    by_contra h
    push Not at h
    exact hn (diagonal_intertwiner_zero f red hred π hπ hπred σ hσ a ha0 h T ht)
  refine ⟨c, l * r, ?_⟩
  rw [he, cartan_zero _ _ a ha, mul_one, map_mul]

end PaperXI.CuspidalCartan105
