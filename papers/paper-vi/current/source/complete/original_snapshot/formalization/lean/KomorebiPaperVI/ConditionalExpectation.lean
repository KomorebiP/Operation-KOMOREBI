import KomorebiPaperVI.Coarsening
import Mathlib.Analysis.Complex.Basic

/-! Author: Komorebi P. Literal finite complex weighted conditional expectations. -/
namespace KomorebiPaperVI.ConditionalExpectation
open KomorebiPaperVI.Coarsening
open scoped BigOperators ComplexConjugate
variable {I A B : Type*} [Fintype I]
    [DecidableEq A] [DecidableEq B]

def fiber (f : I → A) (v : I → ℂ) (a : A) : ℂ := ∑ i, if f i=a then v i else 0
noncomputable def average (f : I → A) (p : I → ℝ) (v : I → ℂ) (a : A) : ℂ :=
  fiber f (fun i => (p i:ℂ)*v i) a / (coarsen f p a:ℂ)
noncomputable def expect (f : I → A) (p : I → ℝ) (v : I → ℂ) (i : I) : ℂ :=
  average f p v (f i)

theorem fiber_mass_cast (f : I → A) (p : I → ℝ) (a : A) :
    fiber f (fun i => (p i:ℂ)) a=(coarsen f p a:ℂ) := by
  simp only [fiber,coarsen,Complex.ofReal_sum]
  apply Finset.sum_congr rfl
  intro i _; split_ifs <;> simp

theorem fiber_pull (f : I → A) (w : I → ℂ) (v : A → ℂ) (a : A) :
    fiber f (fun i => w i*v (f i)) a=fiber f w a*v a := by
  simp only [fiber,Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro i _
  by_cases hi : f i=a
  · simp [hi]
  · simp [hi]

theorem fiber_mass_ne (f : I → A) (p : I → ℝ) (hp : ∀ i, 0 < p i) (i : I) :
    (coarsen f p (f i):ℂ)≠0 := by
  intro h
  have hr : coarsen f p (f i)=0 := by exact_mod_cast h
  have hz := zero_packet_component f p (fun j => (hp j).le) (f i) hr i rfl
  exact (hp i).ne' hz

theorem expect_constant (f : I → A) (p : I → ℝ) (hp : ∀ i, 0 < p i) (v : A → ℂ) :
    expect f p (v ∘ f)=v ∘ f := by
  funext i
  dsimp [expect,average,Function.comp_def]
  rw [fiber_pull,fiber_mass_cast]
  exact mul_div_cancel_left₀ _ (fiber_mass_ne f p hp i)

theorem expect_block_constant (f : I → A) (p : I → ℝ) (v : I → ℂ) (i j : I)
    (h : f i=f j) : expect f p v i=expect f p v j := by simp only [expect,h]

theorem expect_idempotent (f : I → A) (p : I → ℝ) (hp : ∀ i, 0 < p i) (v : I → ℂ) :
    expect f p (expect f p v)=expect f p v :=
  expect_constant f p hp (average f p v)

theorem expect_fixes_iff (f : I → A) (p : I → ℝ) (hp : ∀ i, 0 < p i) (v : I → ℂ) :
    expect f p v=v ↔ ∀ i j, f i=f j → v i=v j := by
  constructor
  · intro h i j hij
    rw [← h]
    exact expect_block_constant f p v i j hij
  · intro h
    funext i
    have he : fiber f (fun j => (p j:ℂ)*v j) (f i)=
        (coarsen f p (f i):ℂ)*v i := by
      rw [← fiber_mass_cast]
      simp only [fiber,Finset.sum_mul]
      apply Finset.sum_congr rfl
      intro j _
      by_cases hj : f j=f i
      · simp [hj,h j i hj]
      · simp [hj]
    dsimp [expect,average]
    rw [he]
    exact mul_div_cancel_left₀ _ (fiber_mass_ne f p hp i)

theorem expect_range (f : I → A) (p : I → ℝ) (hp : ∀ i, 0 < p i) :
    Set.range (expect f p) = {v | ∀ i j, f i=f j → v i=v j} := by
  ext v
  constructor
  · rintro ⟨w,rfl⟩; exact expect_block_constant f p w
  · intro h; exact ⟨v,(expect_fixes_iff f p hp v).mpr h⟩

noncomputable def kernel (f : I → A) (p : I → ℝ) : Matrix I I ℂ :=
  fun i j => if f j=f i then (p j:ℂ)/(coarsen f p (f i):ℂ) else 0

theorem expect_matrix (f : I → A) (p : I → ℝ) (v : I → ℂ) :
    expect f p v=(kernel f p).mulVec v := by
  funext i
  simp only [expect,average,fiber,Matrix.mulVec,dotProduct,Finset.sum_div,kernel]
  apply Finset.sum_congr rfl
  intro j _
  by_cases hj : f j=f i
  · simp only [hj,ite_true]; ring
  · simp [hj]

theorem kernel_weighted_symmetry (f : I → A) (p : I → ℝ) (i j : I) :
    (p i:ℂ)*kernel f p i j=(p j:ℂ)*conj (kernel f p j i) := by
  by_cases hij : f j=f i
  · simp only [kernel,hij,ite_true,div_eq_mul_inv]
    simp only [map_mul,map_inv₀,Complex.conj_ofReal]
    ring
  · simp [kernel,hij,Ne.symm hij]

noncomputable def weightedInner (p : I → ℝ) (v w : I → ℂ) : ℂ :=
  ∑ i, (p i:ℂ)*v i*conj (w i)

theorem expect_self_adjoint (f : I → A) (p : I → ℝ) (v w : I → ℂ) :
    weightedInner p (expect f p v) w=weightedInner p v (expect f p w) := by
  rw [expect_matrix,expect_matrix]
  simp only [weightedInner,Matrix.mulVec,dotProduct,Finset.mul_sum,Finset.sum_mul,
    map_sum,map_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro i _
  apply Finset.sum_congr rfl
  intro j _
  have h := kernel_weighted_symmetry f p j i
  calc
    _ = ((p j:ℂ)*kernel f p j i)*v i*conj (w j) := by ring
    _ = _ := by rw [h]; ring

end KomorebiPaperVI.ConditionalExpectation
