import Mathlib.RepresentationTheory.Rep.Basic
import Mathlib.Algebra.Ring.Hom.Defs
import Mathlib.Tactic.NoncommRing

/-! The coefficient module is the actual square-zero ring kernel.
The action is induced by residual units; it does not require a multiplicative lift. -/
namespace Komorebi.StrongArtin.SquareZeroH2

variable {G A B : Type} [Group G] [Ring A] [Ring B]

structure Datum (G A B : Type) [Group G] [Ring A] [Ring B] where
  q : A →+* B
  squareZero : ∀ a b, q a = 0 → q b = 0 → a * b = 0
  rho : G →* B
  lift : G → Aˣ
  lift_one : lift 1 = 1
  lift_residue : ∀ g, q (lift g) = rho g

namespace Datum

abbrev Kernel (D : Datum G A B) := D.q.toAddMonoidHom.ker

variable (D : Datum G A B)

theorem kernel_mul (x y : D.Kernel) : (x : A) * (y : A) = 0 :=
  D.squareZero _ _ x.property y.property

theorem same_residue_mul_kernel {a b : A} (h : D.q a = D.q b) (x : D.Kernel) :
    a * (x : A) = b * (x : A) := by
  have hz := D.squareZero (a-b) x (by simp [h]) x.property
  simpa only [sub_mul, sub_eq_zero] using hz

theorem kernel_mul_same_residue (x : D.Kernel) {a b : A} (h : D.q a = D.q b) :
    (x : A) * a = (x : A) * b := by
  have hz := D.squareZero x (a-b) x.property (by simp [h])
  simpa only [mul_sub, sub_eq_zero] using hz

theorem inverse_same_residue {u v : Aˣ} (h : D.q u = D.q v) :
    D.q (↑u⁻¹ : A) = D.q (↑v⁻¹ : A) := by
  have he : Units.map D.q.toMonoidHom u = Units.map D.q.toMonoidHom v := Units.ext h
  have hi := congrArg (fun w : Bˣ => (↑w⁻¹ : B)) he
  exact hi

def conjugate (u : Aˣ) : D.Kernel →ₗ[ℤ] D.Kernel :=
  AddMonoidHom.toIntLinearMap
  { toFun := fun x => ⟨u * (x : A) * ↑u⁻¹, by
      have hx : D.q (x : A) = 0 := x.property
      simp [hx]⟩
    map_zero' := by apply Subtype.ext; simp
    map_add' := by intro x y; apply Subtype.ext; simp [mul_add, add_mul] }

@[simp] theorem conjugate_val (u : Aˣ) (x : D.Kernel) :
    (D.conjugate u x : A) = u * (x : A) * ↑u⁻¹ := rfl

theorem conjugate_same_residue {u v : Aˣ} (h : D.q u = D.q v) :
    D.conjugate u = D.conjugate v := by
  ext x
  change (u : A) * (x : A) * ↑u⁻¹ = (v : A) * (x : A) * ↑v⁻¹
  rw [D.same_residue_mul_kernel h x]
  let y : D.Kernel := ⟨(v : A) * (x : A), by
      have hx : D.q (x : A) = 0 := x.property
      simp [hx]⟩
  exact D.kernel_mul_same_residue y (D.inverse_same_residue h)

@[simp] theorem conjugate_one : D.conjugate (1 : Aˣ) = 1 := by
  ext x
  simp

theorem conjugate_mul (u v : Aˣ) :
    D.conjugate (u*v) = D.conjugate u * D.conjugate v := by
  ext x
  simp [conjugate, mul_assoc]

def action : Representation ℤ G D.Kernel where
  toFun g := D.conjugate (D.lift g)
  map_one' := by rw [D.lift_one, D.conjugate_one]
  map_mul' g h := by
    rw [← D.conjugate_mul]
    apply D.conjugate_same_residue
    simp [D.lift_residue]

def coefficientRep : Rep ℤ G := Rep.of D.action

@[simp] theorem action_val (g : G) (x : D.Kernel) :
    (D.action g x : A) = D.lift g * (x : A) * ↑(D.lift g)⁻¹ := rfl

/-- Any other unit-valued lift induces the very same action on the kernel. -/
theorem action_eq_conjugate (s : G → Aˣ) (hs : ∀ g, D.q (s g) = D.rho g) (g : G) :
    D.action g = D.conjugate (s g) := by
  apply D.conjugate_same_residue
  rw [D.lift_residue, hs]

end Datum
end Komorebi.StrongArtin.SquareZeroH2
