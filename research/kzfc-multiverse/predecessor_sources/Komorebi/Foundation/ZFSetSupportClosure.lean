import Komorebi.Foundation.InternalSupportEquivalence
import Komorebi.Foundation.ZFSetZFCModel

/-!
# Concrete discharge of the support-arithmetic obligation in ZFSet

These theorems deliberately remain ZFSet-specific. They do not replace the
missing internal cardinal-arithmetic proof for arbitrary ZFC models.
-/

universe u

namespace Komorebi.ZFSetSupportClosure

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces
open InternalConstraints InternalFineCompactness InternalSmallSupports InternalConeFilter
open InternalUnionReduction InternalSupportEquivalence SetFilterCoding

/-- Exact smallness comparison, transported through the same syntax into the
concrete universe only. -/
theorem small_initial_iff (κ : Cardinal.{u}) (s : ZFSet.{u}) :
    InternalResidualSentence.Small κ.ord.toZFSet s ↔ s.card < κ := by
  have hs : InternalResidualSentence.Small κ.ord.toZFSet s ↔
      SetFilterCoding.SetSmall κ.ord.toZFSet s :=
    (smallF_internal (0 : Fin 2) 1 ![κ.ord.toZFSet,s]).symm.trans
      (realize_smallF (0 : Fin 2) 1 ![κ.ord.toZFSet,s])
  exact hs.trans (setSmall_initial_iff κ s)

theorem product_iff (p x y : ZFSet.{u}) :
    InternalResidualSentence.Product p x y ↔ p = ZFSet.prod x y :=
  (prodF_internal (0 : Fin 3) 1 2 ![p,x,y]).symm.trans
    (realize_prodF (0 : Fin 3) 1 2 ![p,x,y])

/-- A small-carrier product maps onto the actual Kuratowski product set. -/
theorem card_product_le (x y : ZFSet.{u}) :
    (ZFSet.prod x y).card ≤ x.card * y.card := by
  let f : Carrier x × Carrier y → ZFSet.{u} :=
    fun ab => ZFSet.pair (element x ab.1) (element y ab.2)
  have heq : ZFSet.range f = ZFSet.prod x y := by
    apply ZFSet.ext
    intro z
    constructor
    · intro hz
      obtain ⟨⟨a,b⟩,rfl⟩ := ZFSet.mem_range.mp hz
      exact ZFSet.pair_mem_prod.mpr ⟨element_mem x a,element_mem y b⟩
    · intro hz
      obtain ⟨a,ha,b,hb,rfl⟩ := ZFSet.mem_prod.mp hz
      obtain ⟨a',rfl⟩ := exists_element x ha
      obtain ⟨b',rfl⟩ := exists_element y hb
      exact ZFSet.mem_range.mpr ⟨(a',b'),rfl⟩
  have hcard := ZFSet.lift_card_range_le (f := f)
  rw [heq] at hcard
  simpa only [Cardinal.lift_id,Cardinal.mk_prod,Carrier,ZFSet.card] using hcard

/-- Ordinary ambient cardinal arithmetic proves the concrete small-product
property at every infinite initial cardinal. Regularity is not needed here. -/
theorem productClosed_initial (κ : Cardinal.{u}) (hκ : Cardinal.aleph0 ≤ κ) :
    SmallProductClosed (M := ZFSet.{u}) κ.ord.toZFSet := by
  intro x y p hx hy hp
  apply (small_initial_iff κ p).mpr
  have hprod : p = ZFSet.prod x y := (product_iff p x y).mp hp
  rw [hprod]
  exact (card_product_le x y).trans_lt
    (Cardinal.mul_lt_of_lt hκ ((small_initial_iff κ x).mp hx) ((small_initial_iff κ y).mp hy))

theorem guard_iff_cardinal (k : ZFSet.{u}) :
    Guard k ↔ ∃ κ : Cardinal.{u}, k = κ.ord.toZFSet ∧ κ.IsRegular ∧ Cardinal.aleph0 < κ :=
  (guardF_internal () (fun _ : Unit => k)).symm.trans
    (realize_guardF_iff_cardinal () (fun _ : Unit => k))

theorem productClosed_of_guard {k : ZFSet.{u}} (hg : Guard k) : SmallProductClosed k := by
  obtain ⟨κ,rfl,_,hunc⟩ := (guard_iff_cardinal k).mp hg
  exact productClosed_initial κ hunc.le

theorem unionClosed_of_guard {k : ZFSet.{u}} (hg : Guard k) : SmallUnionClosed k :=
  unionClosed_of_guard_productClosed ZFSetZFCModel.zfset_axiomSemantics hg
    (productClosed_of_guard hg)

/-- This discharges the support hypothesis for ZFSet, not for arbitrary models. -/
theorem fine_of_guard_extension {k : ZFSet.{u}} (hg : Guard k) (hext : Extension k) :
    InternalFinePrinciple k :=
  fine_of_extension_unionClosed ZFSetZFCModel.zfset_axiomSemantics hg.2.1
    (unionClosed_of_guard hg) hext

theorem internal_compactness_of_guard_extension {k : ZFSet.{u}}
    (hg : Guard k) (hext : Extension k) : ConstraintCompactness k :=
  internal_fine_implies_compactness ZFSetZFCModel.zfset_axiomSemantics k
    (fine_of_guard_extension hg hext)

end Komorebi.ZFSetSupportClosure
