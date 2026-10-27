import UnramifiedSquareZeroLifting

/-! Factor an inertia-trivial continuous representation through an actual
surjective procyclic quotient, then lift while preserving that kernel. -/
namespace Komorebi.StrongArtin.Procyclic

variable {G H : Type} [Group G] [TopologicalSpace G] [CompactSpace G]
variable [Group H] [TopologicalSpace H]

/-- Compact-to-Hausdorff quotient descent proves the factorization; it is not assumed. -/
theorem factor_through_procyclic_of_kernel_trivial
    (nu : G →ₜ* Zhat) (hnu : Function.Surjective nu)
    (rho : G →ₜ* H) (hin : ∀ g, nu g = 1 → rho g = 1) :
    ∃ r : Zhat →ₜ* H, r.comp nu = rho := by
  let hf : nu.toMonoidHom.ker ≤ rho.toMonoidHom.ker := hin
  let raw : Zhat →* H := nu.toMonoidHom.liftOfSurjective hnu ⟨rho.toMonoidHom,hf⟩
  have he : raw.comp nu.toMonoidHom = rho.toMonoidHom :=
    MonoidHom.liftOfRightInverse_comp _ _ _ _
  have hfun : (fun g => raw (nu g)) = fun g => rho g :=
    congrArg (fun f : G →* H => (f : G → H)) he
  have hQ : Topology.IsQuotientMap nu :=
    Topology.IsQuotientMap.of_surjective_continuous hnu nu.continuous
  have hc : Continuous raw := hQ.continuous_iff.mpr (by
    change Continuous (fun g => raw (nu g))
    rw [hfun]
    exact rho.continuous)
  refine ⟨⟨raw,hc⟩,?_⟩
  apply DFunLike.ext
  intro g
  exact congrFun hfun g

/-- The unramified condition is literal triviality on the designated inertia kernel. -/
theorem unramified_lift_preserving_inertia
    {A B : Type} [Ring A] [Ring B] [Finite A] [Finite B]
    [TopologicalSpace A] [DiscreteTopology A]
    [TopologicalSpace B] [DiscreteTopology B]
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a*b = 0)
    (nu : G →ₜ* Zhat) (hnu : Function.Surjective nu)
    (rho : G →ₜ* Bˣ) (hin : ∀ g, nu g = 1 → rho g = 1) :
    ∃ l : G →ₜ* Aˣ, (unitReduction q).comp l = rho ∧
      ∀ g, nu g = 1 → l g = 1 := by
  obtain ⟨r,hr⟩ := factor_through_procyclic_of_kernel_trivial nu hnu rho hin
  obtain ⟨l,hl,hi⟩ := unramified_pullback_lifts nu r q hq hsq
  exact ⟨l,hl.trans hr,hi⟩

end Komorebi.StrongArtin.Procyclic
