import KomorebiPaperVI.ConditionalExpectation
import KomorebiPaperVI.Algebra
import KomorebiPaperVI.MartingalePackets

/-! Author: Komorebi P. Concrete conditional-expectation towers and martingale packets. -/
namespace KomorebiPaperVI.ConditionalTowers
open KomorebiPaperVI.ConditionalExpectation
open scoped BigOperators ComplexConjugate
variable {I A B : Type*} [Fintype I] [DecidableEq A] [DecidableEq B]

theorem weighted_inner_separates (p : I → ℝ) (hp : ∀ i, 0 < p i) (v w : I → ℂ)
    (h : ∀ z, weightedInner p v z=weightedInner p w z) : v=w := by
  classical
  funext i
  have he := h (fun j => if j=i then 1 else 0)
  simp [weightedInner] at he
  exact he.resolve_right (hp i).ne'

theorem fine_after_coarse (f : I → A) (g : A → B) (p : I → ℝ) (hp : ∀ i, 0 < p i)
    (v : I → ℂ) : expect f p (expect (g ∘ f) p v)=expect (g ∘ f) p v := by
  apply (expect_fixes_iff f p hp _).mpr
  intro i j hij
  apply expect_block_constant
  simp only [Function.comp_apply,hij]

theorem coarse_after_fine (f : I → A) (g : A → B) (p : I → ℝ) (hp : ∀ i, 0 < p i)
    (v : I → ℂ) : expect (g ∘ f) p (expect f p v)=expect (g ∘ f) p v := by
  apply weighted_inner_separates p hp
  intro w
  rw [expect_self_adjoint,expect_self_adjoint,fine_after_coarse f g p hp,
    ← expect_self_adjoint]

section Matrix
variable [DecidableEq I]

omit [DecidableEq I] in
theorem conditional_kernel_product (f : I → A) (g : A → B) (p : I → ℝ)
    (hp : ∀ i, 0 < p i) :
    kernel (g ∘ f) p*kernel f p=kernel (g ∘ f) p ∧
      kernel f p*kernel (g ∘ f) p=kernel (g ∘ f) p := by
  constructor
  · apply Matrix.mulVec_injective
    funext v
    rw [← Matrix.mulVec_mulVec,← expect_matrix,← expect_matrix,coarse_after_fine f g p hp,expect_matrix]
  · apply Matrix.mulVec_injective
    funext v
    rw [← Matrix.mulVec_mulVec,← expect_matrix,← expect_matrix,fine_after_coarse f g p hp,expect_matrix]


variable {J : ℕ → Type*} [∀ n, DecidableEq (J n)]

omit [DecidableEq I] in
theorem nested_kernel_min (f : ∀ n, I → J n) (p : I → ℝ) (hp : ∀ i, 0 < p i)
    (hf : ∀ m n, m ≤ n → ∃ g : J n → J m, f m=g ∘ f n) (m n : ℕ) :
    kernel (f m) p*kernel (f n) p=kernel (f (min m n)) p := by
  by_cases hmn : m ≤ n
  · obtain ⟨g,hg⟩ := hf m n hmn
    rw [Nat.min_eq_left hmn,hg]
    exact (conditional_kernel_product (f n) g p hp).1
  · have hnm : n ≤ m := by omega
    obtain ⟨g,hg⟩ := hf n m hnm
    rw [Nat.min_eq_right hnm,hg]
    exact (conditional_kernel_product (f m) g p hp).2

theorem martingale_packet_product (f : ∀ n, I → J n) (p : I → ℝ) (hp : ∀ i, 0 < p i)
    (hf : ∀ m n, m ≤ n → ∃ g : J n → J m, f m=g ∘ f n) (m n : ℕ) :
    MartingalePackets.packet (fun k => kernel (f k) p) m *
      MartingalePackets.packet (fun k => kernel (f k) p) n =
        if m=n then MartingalePackets.packet (fun k => kernel (f k) p) n else 0 :=
  MartingalePackets.packet_product _ (nested_kernel_min f p hp hf) m n

theorem martingale_packet_reconstruction (f : ∀ n, I → J n) (p : I → ℝ) (n : ℕ) :
    ∑ j ∈ Finset.range (n+1), MartingalePackets.packet (fun k => kernel (f k) p) j=kernel (f n) p :=
  MartingalePackets.packet_sum _ n

end Matrix
end KomorebiPaperVI.ConditionalTowers
