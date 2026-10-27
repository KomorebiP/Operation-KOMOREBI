import FiniteKernelConjugacy

/-! Local zero-cochains are exactly strict kernel conjugators. No finiteness or
order-invertibility assumptions are used in these identities. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G H A B : Type} [Group G] [Group H] [Ring A] [Ring B]
variable (D : Datum G A B)

theorem kernelUnit_add (x y : D.Kernel) :
    D.kernelUnit x*D.kernelUnit y=D.kernelUnit (x+y) := by
  apply Units.ext
  change (1+(x : A))*(1+(y : A))=1+((x : A)+(y : A))
  have hz := D.kernel_mul x y
  noncomm_ring [hz]

theorem every_residual_one_unit_is_kernelUnit (u : Aˣ) (hu : D.q u=1) :
    ∃ x : D.Kernel, D.kernelUnit x=u := by
  refine ⟨⟨(u : A)-1,by change D.q ((u : A)-1)=0; simp [hu]⟩,?_⟩
  apply Units.ext
  change 1+((u : A)-1)=(u : A)
  abel

theorem kernel_conjugation_correctedLift (b : G → D.Kernel) (x : D.Kernel) (g : G) :
    D.kernelUnit x*D.correctedLift (-b) g*(D.kernelUnit x)⁻¹=
      D.correctedLift (fun h => -(b h+(D.action h x-x))) g := by
  have he := D.kernelUnit_conjugation (D.correctedLift (-b) g) (-x)
  rw [neg_neg,map_neg,sub_neg_eq_add] at he
  rw [← D.action_eq_conjugate (D.correctedLift (-b)) (D.correctedLift_residue (-b)) g] at he
  rw [he]
  change D.kernelUnit (-D.action g x+x)*(D.kernelUnit (-b g)*D.lift g)=_
  rw [← mul_assoc,D.kernelUnit_add]
  change D.kernelUnit (-D.action g x+x+-b g)*D.lift g=
    D.kernelUnit (-(b g+(D.action g x-x)))*D.lift g
  congr 2
  abel

theorem kernel_conjugation_at_local_iff (loc : H →* G) (t : H →* Aˣ)
    (ht : ∀ h, D.q (t h)=D.rho (loc h)) (b : G → D.Kernel)
    (x : D.Kernel) (h : H) :
    D.kernelUnit x*D.correctedLift (-b) (loc h)*(D.kernelUnit x)⁻¹=t h ↔
      b (loc h)+(D.action (loc h) x-x)=D.localCorrection loc t ht h := by
  rw [D.kernel_conjugation_correctedLift]
  exact D.correctedLift_at_local_iff loc t ht (fun g => b g+(D.action g x-x)) h

variable [TopologicalSpace G]
variable [TopologicalSpace A] [DiscreteTopology A]

/-- Recover a continuous primitive and the actual corrected representation from
ANY continuous lift. This is not merely the existence of some primitive. -/
theorem continuous_lift_has_correcting_primitive (hr : Continuous D.lift)
    (t : G →* Aˣ) (ht : ∀ g, D.q (t g)=D.rho g) (htc : Continuous t) :
    ∃ b : G → D.Kernel, Continuous b ∧
      (∀ g h, D.normalizedDefect D.lift D.lift_residue (g,h)=
        D.action g (b h)-b (g*h)+b g) ∧
      ∀ g, D.correctedLift (-b) g=t g := by
  let b := D.localCorrection (MonoidHom.id G) t ht
  refine ⟨b,D.localCorrection_continuous hr (MonoidHom.id G) continuous_id t ht htc,
    fun g h => D.localCorrection_boundary (MonoidHom.id G) t ht g h,fun g => ?_⟩
  exact (D.correctedLift_at_local_iff (MonoidHom.id G) t ht b g).mpr rfl

end Komorebi.StrongArtin.SquareZeroH2.Datum
