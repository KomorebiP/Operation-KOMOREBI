import PaperX.WeilData

/-! Actual finite-copy group/monodromy actions and their inertia-fixed kernels. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.WeilCopies
open scoped BigOperators
open PaperX.CarrierSummands PaperX.CarrierPolynomials PaperX.WeilData
variable {K G I : Type*} [Field K] [Group G] [Fintype I]
variable {ν : G →* Kˣ} {W : I → Type*}
variable [∀ i, AddCommGroup (W i)] [∀ i, Module K (W i)]

def copiesDatum (D : ∀ i, Datum ν (W i)) (m : I → ℕ) : Datum ν (Copies W m) where
  r := copiesRep (fun i => (D i).r) m
  N := PaperX.MonodromyData.copiesN (fun i => (D i).N) m
  nilpotent := PaperX.MonodromyData.copiesN_nilpotent _ (fun i => (D i).nilpotent) m
  relation g x := by funext i k; exact (D i).relation g (x i k)

/-- Both sides use their own fixed-vector and kernel equations. -/
def fixedCopiesEquiv (D : ∀ i, Datum ν (W i)) (H : Subgroup G) (m : I → ℕ) :
    fixedKernel (copiesDatum D m) H ≃ₗ[K] Copies (fun i => fixedKernel (D i) H) m where
  toFun x i k := ⟨x.val i k, ⟨congrFun (congrFun x.property.1 i) k,
    fun h => congrFun (congrFun (x.property.2 h) i) k⟩⟩
  invFun x := ⟨fun i k => (x i k).val, ⟨by
    funext i k
    exact (x i k).property.1, by
    intro h
    funext i k
    exact (x i k).property.2 h⟩⟩
  left_inv x := by apply Subtype.ext; rfl
  right_inv x := rfl
  map_add' x y := rfl
  map_smul' a x := rfl

theorem fixed_equivariant (D : ∀ i, Datum ν (W i)) (H : Subgroup G) [H.Normal]
    (m : I → ℕ) (g : G) (x : fixedKernel (copiesDatum D m) H) :
    fixedCopiesEquiv D H m (fixedRep (copiesDatum D m) H g x) =
      copiesRep (fun i => fixedRep (D i) H) m g (fixedCopiesEquiv D H m x) := rfl

theorem fixed_conjugate (D : ∀ i, Datum ν (W i)) (H : Subgroup G) [H.Normal]
    (m : I → ℕ) (g : G) :
    (fixedCopiesEquiv D H m).conj (fixedRep (copiesDatum D m) H g) =
      piEnd (fun i => piEnd (fun _ : Fin (m i) => fixedRep (D i) H g)) := by
  apply LinearMap.ext
  intro x
  rfl

variable [∀ i, FiniteDimensional K (W i)]

theorem local_charpoly_product (D : ∀ i, Datum ν (W i)) (H : Subgroup G) [H.Normal]
    (m : I → ℕ) (φ : G) :
    localCharpoly (copiesDatum D m) H φ = ∏ i, localCharpoly (D i) H φ ^ m i := by
  unfold localCharpoly
  rw [← LinearEquiv.charpoly_conj (fixedCopiesEquiv D H m), fixed_conjugate, charpoly_piEnd]
  apply Finset.prod_congr rfl
  intro i _
  rw [charpoly_piEnd]
  simp

theorem fixed_dimension_sum (D : ∀ i, Datum ν (W i)) (H : Subgroup G) (m : I → ℕ) :
    Module.finrank K (fixedKernel (copiesDatum D m) H) =
      ∑ i, m i * Module.finrank K (fixedKernel (D i) H) := by
  rw [(fixedCopiesEquiv D H m).finrank_eq, copies_finrank]

theorem fixed_trace_sum (D : ∀ i, Datum ν (W i)) (H : Subgroup G) [H.Normal]
    (m : I → ℕ) (φ : G) :
    LinearMap.trace K _ (fixedRep (copiesDatum D m) H φ) =
      ∑ i, (m i : K) * LinearMap.trace K _ (fixedRep (D i) H φ) := by
  rw [← LinearMap.trace_conj' _ (fixedCopiesEquiv D H m), fixed_conjugate, trace_piEnd]
  apply Finset.sum_congr rfl
  intro i _
  rw [trace_piEnd]
  simp

theorem common_local_polynomial {E : Type*} [CommRing E] (σ : E →+* K)
    (D : ∀ i, Datum ν (W i)) (H : Subgroup G) [H.Normal] (m : I → ℕ) (φ : G)
    (P : I → Polynomial E) (hP : ∀ i, localCharpoly (D i) H φ = (P i).map σ) :
    localCharpoly (copiesDatum D m) H φ = (∏ i, P i ^ m i).map σ := by
  rw [local_charpoly_product]
  simp [hP, Polynomial.map_prod]

end PaperX.WeilCopies
