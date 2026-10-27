/- Exact signed half-grid geometry. No analytic special values are assumed. -/
module
public import Mathlib.Tactic.Ring.Basic
public import Mathlib.Tactic.FinCases
public import Mathlib.Data.Fintype.Fin
public import Mathlib.Tactic.NormNum
public import Mathlib.Tactic.Abel
@[expose] public section
namespace H12.SignedGeometry

def rotate (i : Fin 8) : Fin 8 :=
  ⟨4*(i.val%2)+i.val/2, by have h := i.isLt; omega⟩
def chi (k i : Fin 8) : ℤ :=
  if ((k.val/4)*(i.val/4)+((k.val/2)%2)*((i.val/2)%2)+(k.val%2)*(i.val%2))%2=0 then 1 else -1

variable {K : Type*} [CommRing K]
def walsh {A : Type*} [AddCommGroup A] (x : Fin 8 → A) (k : Fin 8) : A :=
  if k.val=0 then x ⟨0, by decide⟩ + x ⟨1, by decide⟩ + x ⟨2, by decide⟩ + x ⟨3, by decide⟩ + x ⟨4, by decide⟩ + x ⟨5, by decide⟩ + x ⟨6, by decide⟩ + x ⟨7, by decide⟩ else
  if k.val=1 then x ⟨0, by decide⟩ + -x ⟨1, by decide⟩ + x ⟨2, by decide⟩ + -x ⟨3, by decide⟩ + x ⟨4, by decide⟩ + -x ⟨5, by decide⟩ + x ⟨6, by decide⟩ + -x ⟨7, by decide⟩ else
  if k.val=2 then x ⟨0, by decide⟩ + x ⟨1, by decide⟩ + -x ⟨2, by decide⟩ + -x ⟨3, by decide⟩ + x ⟨4, by decide⟩ + x ⟨5, by decide⟩ + -x ⟨6, by decide⟩ + -x ⟨7, by decide⟩ else
  if k.val=3 then x ⟨0, by decide⟩ + -x ⟨1, by decide⟩ + -x ⟨2, by decide⟩ + x ⟨3, by decide⟩ + x ⟨4, by decide⟩ + -x ⟨5, by decide⟩ + -x ⟨6, by decide⟩ + x ⟨7, by decide⟩ else
  if k.val=4 then x ⟨0, by decide⟩ + x ⟨1, by decide⟩ + x ⟨2, by decide⟩ + x ⟨3, by decide⟩ + -x ⟨4, by decide⟩ + -x ⟨5, by decide⟩ + -x ⟨6, by decide⟩ + -x ⟨7, by decide⟩ else
  if k.val=5 then x ⟨0, by decide⟩ + -x ⟨1, by decide⟩ + x ⟨2, by decide⟩ + -x ⟨3, by decide⟩ + -x ⟨4, by decide⟩ + x ⟨5, by decide⟩ + -x ⟨6, by decide⟩ + x ⟨7, by decide⟩ else
  if k.val=6 then x ⟨0, by decide⟩ + x ⟨1, by decide⟩ + -x ⟨2, by decide⟩ + -x ⟨3, by decide⟩ + -x ⟨4, by decide⟩ + -x ⟨5, by decide⟩ + x ⟨6, by decide⟩ + x ⟨7, by decide⟩ else
  x ⟨0, by decide⟩ + -x ⟨1, by decide⟩ + -x ⟨2, by decide⟩ + x ⟨3, by decide⟩ + -x ⟨4, by decide⟩ + x ⟨5, by decide⟩ + x ⟨6, by decide⟩ + -x ⟨7, by decide⟩

def affine (u db dc da : K) (i : Fin 8) : K :=
  if i.val=0 then u else
  if i.val=1 then u + da else
  if i.val=2 then u + dc else
  if i.val=3 then u + dc + da else
  if i.val=4 then u + db else
  if i.val=5 then u + db + da else
  if i.val=6 then u + db + dc else
  u + db + dc + da

theorem rotate_cube (i : Fin 8) : rotate (rotate (rotate i))=i := by
  fin_cases i <;> decide

theorem character_transport : ∀ k i : Fin 8,
    chi (rotate k) (rotate i)=chi k i := by decide

theorem walsh_transport {A : Type*} [AddCommGroup A] (x : Fin 8 → A) (k : Fin 8) :
    walsh (fun i => x (rotate i)) k=walsh x (rotate k) := by
  fin_cases k <;> norm_num [walsh,rotate] <;> abel

theorem walsh_inversion {A : Type*} [AddCommGroup A] (x : Fin 8 → A) (k : Fin 8) :
    walsh (walsh x) k=8 • x k := by
  fin_cases k <;> norm_num [walsh] <;> abel

theorem affine_spectrum (u db dc da : K) (k : Fin 8) :
    walsh (affine u db dc da) k =
      if k.val=0 then 8*u+4*db+4*dc+4*da else
      if k.val=1 then -4*da else
      if k.val=2 then -4*dc else
      if k.val=4 then -4*db else 0 := by
  fin_cases k <;> norm_num [walsh,affine] <;> ring1

theorem quadratic_top_cancellation (u db dc da : K) :
    walsh (fun i => (affine u db dc da i)^2) 7=0 := by
  norm_num [walsh,affine]; ring1

theorem quadratic_pair_011 (u db dc da : K) :
    walsh (fun i => (affine u db dc da i)^2) 3=4*dc*da := by
  norm_num [walsh,affine]; ring1

theorem quadratic_pair_101 (u db dc da : K) :
    walsh (fun i => (affine u db dc da i)^2) 5=4*db*da := by
  norm_num [walsh,affine]; ring1

theorem quadratic_pair_110 (u db dc da : K) :
    walsh (fun i => (affine u db dc da i)^2) 6=4*db*dc := by
  norm_num [walsh,affine]; ring1

theorem cubic_top_coefficient (u db dc da : K) :
    walsh (fun i => (affine u db dc da i)^3) 7= -6*db*dc*da := by
  norm_num [walsh,affine]; ring1

theorem one_step_gain (k : Fin 8) :
    walsh (affine (5:ℤ) 4 (-2) 7) k =
    if k.val=0 then 76 else if k.val=1 then -28 else
    if k.val=2 then 8 else if k.val=4 then -16 else 0 := by
  fin_cases k <;> decide

theorem three_step_gain (k : Fin 8) :
    walsh (affine (630:ℤ) 471 (-246) 945) k =
    if k.val=0 then 9720 else if k.val=1 then -3780 else
    if k.val=2 then 984 else if k.val=4 then -1884 else 0 := by
  fin_cases k <;> decide

theorem affine_gauge_spectrum (k : Fin 8) :
    walsh (affine (-4:ℤ) 3 3 3) k =
    if k.val=0 then 4 else if k.val=1 ∨ k.val=2 ∨ k.val=4 then -12 else 0 := by
  fin_cases k <;> decide

theorem gauge_rotation_invariant (i : Fin 8) :
    affine (-4:ℤ) 3 3 3 (rotate i)=affine (-4:ℤ) 3 3 3 i := by
  fin_cases i <;> decide

theorem high_subspace_rotation : ∀ k : Fin 8,
    (k.val=3 ∨ k.val=5 ∨ k.val=6 ∨ k.val=7) ↔
    ((rotate k).val=3 ∨ (rotate k).val=5 ∨ (rotate k).val=6 ∨ (rotate k).val=7) := by decide


theorem walsh_add {A : Type*} [AddCommGroup A] (x y : Fin 8 → A) (k : Fin 8) :
    walsh (fun i => x i+y i) k=walsh x k+walsh y k := by
  fin_cases k <;> norm_num [walsh] <;> abel

theorem walsh_zsmul {A : Type*} [AddCommGroup A] (n : Fin 8 → ℤ) (a : A) (k : Fin 8) :
    walsh (fun i => n i • a) k=walsh n k • a := by
  fin_cases k <;> norm_num [walsh] <;> simp only [add_zsmul,neg_zsmul]

theorem walsh_aggregate {A : Type*} [AddCommGroup A] (x : Fin 8 → A) :
    walsh x 0+(walsh x 1+walsh x 2+walsh x 4)+
      (walsh x 3+walsh x 5+walsh x 6)+walsh x 7=8 • x 0 := by
  norm_num [walsh]; abel

end H12.SignedGeometry
