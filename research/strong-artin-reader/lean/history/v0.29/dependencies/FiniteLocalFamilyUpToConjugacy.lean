import FiniteKernelConjugacy

/-! A positive simultaneous-local sector with explicitly checked order hypotheses.
The local conjugators are independent; literal equality or a single common
conjugator is not asserted. -/
namespace Komorebi.StrongArtin.SquareZeroH2

variable {Q A B I : Type} [Group Q] [Fintype Q] [Ring A] [Ring B]
variable (H : I → Type) [∀ i, Group (H i)] [∀ i, Fintype (H i)]

theorem finite_quotient_lift_matching_local_family_up_to_conjugacy
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : Q →* Bˣ) (hn : IsUnit (Fintype.card Q : A))
    (loc : ∀ i, H i →* Q)
    (t : ∀ i, H i →* Aˣ) (ht : ∀ i h, q (t i h)=(rho (loc i h) : B))
    (hlocal : ∀ i, IsUnit (Fintype.card (H i) : A)) :
    ∃ lift : Q →* Aˣ, (∀ g, q (lift g)=(rho g : B)) ∧
      ∀ i, ∃ u : Aˣ, q u=1 ∧ ∀ h, t i h=u*lift (loc i h)*u⁻¹ := by
  obtain ⟨lift,hl⟩ := (datumOfSurjective q hq hsq rho).representation_lifts_of_groupOrder_isUnit hn
  refine ⟨lift,hl,fun i => ?_⟩
  exact same_residue_representations_kernel_conjugate q hsq (lift.comp (loc i)) (t i)
    (fun h => (ht i h).trans (hl (loc i h)).symm) (hlocal i)

/-- Pull back to arbitrary topological sources and local maps. All data factor
through the displayed finite quotients, but the sources themselves need not be
finite or discrete. -/
theorem continuous_finite_quotient_local_family_up_to_conjugacy
    {G : Type} [Group G] [TopologicalSpace G]
    [TopologicalSpace Q] [DiscreteTopology Q] [TopologicalSpace A]
    (P : I → Type) [∀ i, Group (P i)]
    (label : G →* Q) (hlabel : Continuous label)
    (localMap : ∀ i, P i →* G) (localLabel : ∀ i, P i →* H i)
    (loc : ∀ i, H i →* Q)
    (commutes : ∀ i h, label (localMap i h)=loc i (localLabel i h))
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : Q →* Bˣ) (hn : IsUnit (Fintype.card Q : A))
    (t : ∀ i, H i →* Aˣ) (ht : ∀ i h, q (t i h)=(rho (loc i h) : B))
    (hlocal : ∀ i, IsUnit (Fintype.card (H i) : A)) :
    ∃ lift : G →* Aˣ, Continuous lift ∧
      (∀ g, q (lift g)=(rho (label g) : B)) ∧
      ∀ i, ∃ u : Aˣ, q u=1 ∧ ∀ h,
        t i (localLabel i h)=u*lift (localMap i h)*u⁻¹ := by
  obtain ⟨lift,hl,hfix⟩ := finite_quotient_lift_matching_local_family_up_to_conjugacy
    H q hq hsq rho hn loc t ht hlocal
  refine ⟨lift.comp label,(continuous_of_discreteTopology : Continuous lift).comp hlabel,
    fun g => hl (label g),fun i => ?_⟩
  obtain ⟨u,hu,hui⟩ := hfix i
  refine ⟨u,hu,fun h => ?_⟩
  change t i (localLabel i h)=u*lift (label (localMap i h))*u⁻¹
  rw [commutes]
  exact hui (localLabel i h)

end Komorebi.StrongArtin.SquareZeroH2
