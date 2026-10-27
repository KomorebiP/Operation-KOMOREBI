import PaperX.WeilData
import PaperX.NilpotentExponential

/-! Finite exponential reconstruction with an explicitly supplied twisted cocycle.
No arithmetic tame character or monodromy-existence theorem is assumed proved here. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.MonodromyReconstruction
open PaperX.WeilData
variable {K G : Type*} [Field K] [CharZero K] [Group G]
variable {ν : G →* Kˣ}

structure TwistedCocycle (ν : G →* Kˣ) where
  value : G → K
  mul_value : ∀ g h, value (g * h) = value g + (ν g : K) * value h

omit [CharZero K] in
@[simp] theorem cocycle_one (t : TwistedCocycle ν) : t.value 1 = 0 := by
  have h := t.mul_value 1 1
  simpa using h

variable {V : Type*} [AddCommGroup V] [Module K V]

def unipotent (D : Datum ν V) (a : K) : Module.End K V :=
  PaperX.NilpotentExponential.expN D.N a

@[simp] theorem unipotent_zero (D : Datum ν V) : unipotent D 0 = 1 := by
  simp [unipotent]

theorem unipotent_add (D : Datum ν V) (a b : K) :
    unipotent D (a + b) = unipotent D a * unipotent D b := by
  exact PaperX.NilpotentExponential.expN_add D.nilpotent a b

theorem action_unipotent (D : Datum ν V) (g : G) (a : K) :
    D.r g * unipotent D a = unipotent D ((ν g : K) * a) * D.r g := by
  have h : (((ν g : K) * a) • D.N).comp (D.r g) =
      (D.r g).comp (a • D.N) := by
    ext x
    simp [D.relation, smul_smul, mul_comm]
  let : Module ℚ V := Module.compHom V (algebraMap ℚ K)
  exact (Module.End.commute_exp_left_of_commute
    (D.nilpotent.smul a) (D.nilpotent.smul ((ν g : K) * a)) h).symm

/-- The exponential is on the left, matching the displayed cocycle law. -/
def reconstruct (D : Datum ν V) (t : TwistedCocycle ν) : Representation K G V where
  toFun g := unipotent D (t.value g) * D.r g
  map_one' := by simp
  map_mul' g h := by
    change unipotent D (t.value (g * h)) * D.r (g * h) =
      (unipotent D (t.value g) * D.r g) * (unipotent D (t.value h) * D.r h)
    rw [t.mul_value, unipotent_add, map_mul]
    simp only [mul_assoc]
    rw [← mul_assoc (unipotent D ((ν g : K) * t.value h)), ← action_unipotent]
    simp only [mul_assoc]

@[simp] theorem reconstruct_apply (D : Datum ν V) (t : TwistedCocycle ν) (g : G) (x : V) :
    reconstruct D t g x = unipotent D (t.value g) (D.r g x) := rfl

theorem reconstruct_inverse (D : Datum ν V) (t : TwistedCocycle ν) (g : G) :
    reconstruct D t g * reconstruct D t g⁻¹ = 1 := by
  rw [← map_mul, mul_inv_cancel, map_one]

theorem reconstruct_zero_cocycle (D : Datum ν V) (t : TwistedCocycle ν)
    (ht : ∀ g, t.value g = 0) : reconstruct D t = D.r := by
  ext g x
  simp [ht]

omit [CharZero K] in
theorem datum_ext {D E : Datum ν V} (hr : D.r = E.r) (hN : D.N = E.N) : D = E := by
  cases D
  cases E
  cases hr
  cases hN
  rfl

/-- With the nilpotent operator supplied, twisting stays inside the same covariance class. -/
def twist (D : Datum ν V) (t : TwistedCocycle ν) : Datum ν V where
  r := reconstruct D t
  N := D.N
  nilpotent := D.nilpotent
  relation g x := by
    have hc := PaperX.NilpotentExponential.expN_intertwines D.nilpotent D.nilpotent
      D.N (by rfl) (t.value g)
    change unipotent D (t.value g) (D.r g (D.N x)) =
      (ν g : K) • D.N (unipotent D (t.value g) (D.r g x))
    rw [D.relation, map_smul]
    exact congrArg (fun z => (ν g : K) • z) (LinearMap.congr_fun hc (D.r g x))

omit [CharZero K] in
def negCocycle (t : TwistedCocycle ν) : TwistedCocycle ν where
  value g := -t.value g
  mul_value g h := by simp [t.mul_value, add_comm]

/-- This inverse keeps N supplied; it does not extract N from an arbitrary representation. -/
theorem twist_cancel (D : Datum ν V) (t : TwistedCocycle ν) :
    twist (twist D t) (negCocycle t) = D := by
  have hr : (twist (twist D t) (negCocycle t)).r = D.r := by
    ext g x
    change (unipotent D (-t.value g) * (unipotent D (t.value g) * D.r g)) x = D.r g x
    rw [← mul_assoc, show unipotent D (-t.value g) * unipotent D (t.value g) = 1 from
      PaperX.NilpotentExponential.expN_neg_mul D.nilpotent _, one_mul]
  exact datum_ext hr rfl

theorem reconstruct_on_kernel (D : Datum ν V) (t : TwistedCocycle ν)
    (g : G) {x : V} (hx : D.N x = 0) : reconstruct D t g x = D.r g x :=
  PaperX.NilpotentExponential.expN_identity_on_kernel D.nilpotent _ (kernel_stable D g hx)

/-- The independently defined fixed kernel is unchanged by the twist. -/
theorem twist_fixedKernel (D : Datum ν V) (t : TwistedCocycle ν) (H : Subgroup G) :
    fixedKernel (twist D t) H = fixedKernel D H := by
  ext x
  simp only [mem_fixedKernel]
  constructor
  · rintro ⟨hN, hH⟩
    exact ⟨hN, fun h => (reconstruct_on_kernel D t h hN).symm.trans (hH h)⟩
  · rintro ⟨hN, hH⟩
    exact ⟨hN, fun h => (reconstruct_on_kernel D t h hN).trans (hH h)⟩

end PaperX.MonodromyReconstruction
