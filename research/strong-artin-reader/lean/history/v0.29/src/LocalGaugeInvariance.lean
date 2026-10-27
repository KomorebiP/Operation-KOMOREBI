import ContinuousGaugeLiftCriterion

/-! Replacing prescribed local lifts by kernel-conjugate lifts preserves the
actual class in the fixed continuous gauge obstruction quotient. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G H A B : Type} [Group G] [Group H] [Ring A] [Ring B]
variable (D : Datum G A B)

theorem localCorrection_kernel_conjugate (loc : H →* G)
    (t t' : H →* Aˣ)
    (ht : ∀ h, D.q (t h)=D.rho (loc h))
    (ht' : ∀ h, D.q (t' h)=D.rho (loc h))
    (x : D.Kernel) (hc : ∀ h, D.kernelUnit x*t h*(D.kernelUnit x)⁻¹=t' h) (h : H) :
    D.localCorrection loc t ht h+(D.action (loc h) x-x)=D.localCorrection loc t' ht' h := by
  let E := D.pullbackDatum loc
  let a := D.localCorrection loc t ht
  have he : E.correctedLift (-a) h=t h :=
    (E.correctedLift_at_local_iff (MonoidHom.id H) t ht a h).mpr rfl
  have hx := (E.kernel_conjugation_at_local_iff (MonoidHom.id H) t' ht' a x h).mp (by
    change D.kernelUnit x*E.correctedLift (-a) h*(D.kernelUnit x)⁻¹=t' h
    exact (congrArg (fun u : Aˣ => D.kernelUnit x*u*(D.kernelUnit x)⁻¹) he).trans (hc h))
  exact hx

variable {I : Type}
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable (L : I → Type) [∀ i, Group (L i)] [∀ i, TopologicalSpace (L i)]

theorem localConjugacyObstruction_eq_of_kernel_conjugate (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t t' : ∀ i, L i →* Aˣ)
    (ht : ∀ i h, D.q (t i h)=D.rho (loc i h))
    (ht' : ∀ i h, D.q (t' i h)=D.rho (loc i h))
    (htc : ∀ i, Continuous (t i)) (htc' : ∀ i, Continuous (t' i))
    (x : I → D.Kernel)
    (hc : ∀ i h, D.kernelUnit (x i)*t i h*(D.kernelUnit (x i))⁻¹=t' i h) :
    D.localConjugacyObstruction L hr loc hloc t ht htc=
      D.localConjugacyObstruction L hr loc hloc t' ht' htc' := by
  symm
  apply D.localGaugeClass_eq_of_boundary L hr loc hloc _ _ 0 x
  apply Subtype.ext
  apply Prod.ext
  · change D.continuousDefectOf D.lift D.lift_residue hr-
        D.continuousDefectOf D.lift D.lift_residue hr=D.continuousDifferential hr 0+0
    rw [sub_self,map_zero,add_zero]
  · apply Subtype.ext
    funext i h
    change D.localCorrection (loc i) (t' i) (ht' i) h-
      D.localCorrection (loc i) (t i) (ht i) h=0+(D.action (loc i h) (x i)-x i)
    rw [← D.localCorrection_kernel_conjugate (loc i) (t i) (t' i) (ht i) (ht' i) (x i) (hc i) h]
    abel

/-- Independence under every local conjugator reducing to one, not just a chosen parameterization. -/
theorem localConjugacyObstruction_eq_of_residual_one_conjugate (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t t' : ∀ i, L i →* Aˣ)
    (ht : ∀ i h, D.q (t i h)=D.rho (loc i h))
    (ht' : ∀ i h, D.q (t' i h)=D.rho (loc i h))
    (htc : ∀ i, Continuous (t i)) (htc' : ∀ i, Continuous (t' i))
    (u : I → Aˣ) (hu : ∀ i, D.q (u i)=1)
    (hc : ∀ i h, u i*t i h*(u i)⁻¹=t' i h) :
    D.localConjugacyObstruction L hr loc hloc t ht htc=
      D.localConjugacyObstruction L hr loc hloc t' ht' htc' := by
  classical
  choose x hx using fun i => D.every_residual_one_unit_is_kernelUnit (u i) (hu i)
  apply D.localConjugacyObstruction_eq_of_kernel_conjugate L hr loc hloc t t' ht ht' htc htc' x
  intro i h
  rw [hx i]
  exact hc i h

end Komorebi.StrongArtin.SquareZeroH2.Datum
