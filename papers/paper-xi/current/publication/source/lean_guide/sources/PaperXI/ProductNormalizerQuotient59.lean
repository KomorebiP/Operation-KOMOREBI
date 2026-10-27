import PaperXI.NormalizerExtensionInducing58
import Mathlib.GroupTheory.QuotientGroup.Basic
import Mathlib.GroupTheory.Subgroup.Centralizer

/-!
# Product subgroups and the action of a centralizing normalizer

For actual subgroups `H,N` of an ambient group, with `H` normalizing `N`,
the quotient of `H ⊔ N` by `N` is the quotient of `H` by its intersection
with `N`. An ambient element centralizing `H` and normalizing `N` acts
trivially on this quotient. No identification with a simple-character group
is asserted here.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ProductNormalizerQuotient59

variable {G : Type*} [Group G]
variable (H N : Subgroup G) (t : G)
variable (hH : ∀ h ∈ H, t * h = h * t)
variable (hN : t ∈ Subgroup.normalizer (N : Set G))

include hH hN in
/-- Centralizing one factor and normalizing the other normalizes their product. -/
theorem normalizes_sup : t ∈ Subgroup.normalizer ((H ⊔ N : Subgroup G) : Set G) := by
  apply H.inf_normalizer_le_normalizer_sup N
  refine ⟨?_, hN⟩
  apply Subgroup.centralizer_le_normalizer
  exact Subgroup.mem_centralizer_iff.mpr fun h hh => (hH h hh).symm

/-- The literal ambient conjugation automorphism of the product subgroup. -/
def conjugation : MulAut (H ⊔ N : Subgroup G) :=
  NormalizerExtensionInducing58.conjugation (H ⊔ N) t (normalizes_sup H N t hH hN)

@[simp] theorem conjugation_coe (j : (H ⊔ N : Subgroup G)) :
    ((conjugation H N t hH hN j : (H ⊔ N : Subgroup G)) : G) =
      t * (j : G) * t⁻¹ := rfl

/-- Every homomorphism killing the second factor is unchanged by conjugation. -/
theorem map_conjugation {Q : Type*} [Group Q]
    (hHN : H ≤ Subgroup.normalizer (N : Set G))
    (q : (H ⊔ N : Subgroup G) →* Q)
    (hq : N.subgroupOf (H ⊔ N) ≤ q.ker)
    (j : (H ⊔ N : Subgroup G)) :
    q (conjugation H N t hH hN j) = q j := by
  have hj := j.property
  rw [← SetLike.mem_coe, Subgroup.coe_mul_of_left_le_normalizer_right H N hHN] at hj
  obtain ⟨h, hh, n, hn, he⟩ := hj
  let a : (H ⊔ N : Subgroup G) := ⟨h, (show H ≤ H ⊔ N from le_sup_left) hh⟩
  let b : (H ⊔ N : Subgroup G) := ⟨n, (show N ≤ H ⊔ N from le_sup_right) hn⟩
  have hj' : j = a * b := Subtype.ext he.symm
  have ha : conjugation H N t hH hN a = a := by
    apply Subtype.ext
    change t * h * t⁻¹ = h
    rw [hH h hh, mul_assoc, mul_inv_cancel, mul_one]
  have hb : q b = 1 := hq hn
  have hcb : q (conjugation H N t hH hN b) = 1 := by
    apply hq
    exact (Subgroup.mem_normalizer_iff.mp hN n).mp hn
  simp only [hj', map_mul, ha, hcb, hb]

/-- The actual quotient projection is unchanged by the normalizer action. -/
theorem quotient_conjugation (hHN : H ≤ Subgroup.normalizer (N : Set G))
    (j : (H ⊔ N : Subgroup G)) :
    letI := Subgroup.normal_subgroupOf_sup_of_le_normalizer hHN
    QuotientGroup.mk' (N.subgroupOf (H ⊔ N)) (conjugation H N t hH hN j) =
      QuotientGroup.mk' (N.subgroupOf (H ⊔ N)) j := by
  let := Subgroup.normal_subgroupOf_sup_of_le_normalizer hHN
  apply map_conjugation H N t hH hN hHN
  rw [QuotientGroup.ker_mk']

/-- The second isomorphism theorem gives the literal product quotient. -/
def productQuotientEquiv (hHN : H ≤ Subgroup.normalizer (N : Set G)) :
    letI := Subgroup.normal_subgroupOf_of_le_normalizer hHN
    letI := Subgroup.normal_subgroupOf_sup_of_le_normalizer hHN
    (H ⊔ N : Subgroup G) ⧸ N.subgroupOf (H ⊔ N) ≃* H ⧸ N.subgroupOf H := by
  letI := Subgroup.normal_subgroupOf_of_le_normalizer hHN
  letI := Subgroup.normal_subgroupOf_sup_of_le_normalizer hHN
  exact (QuotientGroup.quotientInfEquivProdNormalizerQuotient H N hHN).symm

/-- A concrete surjective map on the first factor identifies the full product
quotient once its kernel is the actual intersection with the second factor. -/
def quotientEquivOfKernel {Q : Type*} [Group Q]
    (hHN : H ≤ Subgroup.normalizer (N : Set G))
    (q : H →* Q) (hq : Function.Surjective q)
    (hker : N.subgroupOf H = q.ker) :
    letI := Subgroup.normal_subgroupOf_sup_of_le_normalizer hHN
    (H ⊔ N : Subgroup G) ⧸ N.subgroupOf (H ⊔ N) ≃* Q := by
  letI := Subgroup.normal_subgroupOf_of_le_normalizer hHN
  letI := Subgroup.normal_subgroupOf_sup_of_le_normalizer hHN
  exact (productQuotientEquiv H N hHN).trans
    ((QuotientGroup.quotientMulEquivOfEq hker).trans
      (QuotientGroup.quotientKerEquivOfSurjective q hq))

end PaperXI.ProductNormalizerQuotient59
