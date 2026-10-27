import Mathlib.GroupTheory.QuotientGroup.Basic
import Mathlib.SetTheory.Cardinal.Finite
import PaperXI.MoritaLattice110

/-! Actual product quotients for the entrywise Morita calculation.
The additive equivalences are constructed from coordinate quotient maps,
their proved kernels, and proved surjectivity. The cardinality conclusions
are consequences of those equivalences, with no supplied index formula. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MoritaQuotient110

variable {ι : Type*} {G : ι → Type*} [∀ i, AddCommGroup (G i)]

/-- The map to the product of the literal coordinate quotients. -/
def coordinateQuotientMap (K : ∀ i, AddSubgroup (G i)) :
    (∀ i, G i) →+ (∀ i, G i ⧸ K i) where
  toFun x i := (x i : G i ⧸ K i)
  map_zero' := by ext i; exact map_zero (QuotientAddGroup.mk' (K i))
  map_add' x y := by ext i; exact map_add (QuotientAddGroup.mk' (K i)) (x i) (y i)

@[simp] theorem coordinateQuotientMap_apply (K : ∀ i, AddSubgroup (G i))
    (x : ∀ i, G i) (i : ι) :
    coordinateQuotientMap K x i = (x i : G i ⧸ K i) := rfl

/-- Every coordinate quotient has a representative; choice assembles them. -/
theorem coordinateQuotientMap_surjective (K : ∀ i, AddSubgroup (G i)) :
    Function.Surjective (coordinateQuotientMap K) := by
  intro y
  refine ⟨fun i => Quotient.out (y i), ?_⟩
  ext i
  exact Quotient.out_eq (y i)

/-- Its kernel is exactly the product subgroup. -/
theorem coordinateQuotientMap_ker (K : ∀ i, AddSubgroup (G i)) :
    (coordinateQuotientMap K).ker = AddSubgroup.pi Set.univ K := by
  ext x
  simp only [AddMonoidHom.mem_ker, funext_iff, coordinateQuotientMap_apply,
    Pi.zero_apply, QuotientAddGroup.eq_zero_iff, AddSubgroup.mem_pi,
    Set.mem_univ, forall_const]

/-- The quotient of a dependent product is the product of its quotients. -/
def piQuotientEquiv (K : ∀ i, AddSubgroup (G i)) :
    ((∀ i, G i) ⧸ AddSubgroup.pi Set.univ K) ≃+ (∀ i, G i ⧸ K i) :=
  QuotientAddGroup.liftEquiv (AddSubgroup.pi Set.univ K)
    (coordinateQuotientMap_surjective K) (coordinateQuotientMap_ker K).symm

@[simp] theorem piQuotientEquiv_mk (K : ∀ i, AddSubgroup (G i))
    (x : ∀ i, G i) (i : ι) :
    piQuotientEquiv K (x : (∀ i, G i) ⧸ AddSubgroup.pi Set.univ K) i =
      (x i : G i ⧸ K i) := rfl

/-- The cardinality formula follows from the actual additive equivalence. -/
theorem card_pi_quotient [Fintype ι] (K : ∀ i, AddSubgroup (G i)) :
    Nat.card ((∀ i, G i) ⧸ AddSubgroup.pi Set.univ K) =
      ∏ i, Nat.card (G i ⧸ K i) := by
  rw [Nat.card_congr (piQuotientEquiv K).toEquiv, Nat.card_pi]

/-- The actual product subgroup maps to its coordinate subgroup quotients. -/
def subgroupCoordinateQuotientMap (L K : ∀ i, AddSubgroup (G i)) :
    AddSubgroup.pi Set.univ L →+ (∀ i, L i ⧸ (K i).addSubgroupOf (L i)) where
  toFun x i := (⟨x.1 i, x.2 i (Set.mem_univ i)⟩ : L i)
  map_zero' := by ext i; rfl
  map_add' x y := by ext i; rfl

@[simp] theorem subgroupCoordinateQuotientMap_apply
    (L K : ∀ i, AddSubgroup (G i)) (x : AddSubgroup.pi Set.univ L) (i : ι) :
    subgroupCoordinateQuotientMap L K x i =
      ((⟨x.1 i, x.2 i (Set.mem_univ i)⟩ : L i) : L i ⧸ (K i).addSubgroupOf (L i)) := rfl

/-- Representatives in each actual subgroup assemble to a product element. -/
theorem subgroupCoordinateQuotientMap_surjective
    (L K : ∀ i, AddSubgroup (G i)) :
    Function.Surjective (subgroupCoordinateQuotientMap L K) := by
  intro y
  let x : ∀ i, L i := fun i => Quotient.out (y i)
  refine ⟨⟨fun i => (x i : G i), fun i _ => (x i).2⟩, ?_⟩
  ext i
  exact Quotient.out_eq (y i)

/-- The kernel is the literal smaller product viewed inside the larger one. -/
theorem subgroupCoordinateQuotientMap_ker (L K : ∀ i, AddSubgroup (G i)) :
    (subgroupCoordinateQuotientMap L K).ker =
      (AddSubgroup.pi Set.univ K).addSubgroupOf (AddSubgroup.pi Set.univ L) := by
  ext x
  simp only [AddMonoidHom.mem_ker, funext_iff, subgroupCoordinateQuotientMap_apply,
    Pi.zero_apply, QuotientAddGroup.eq_zero_iff, AddSubgroup.mem_addSubgroupOf,
    AddSubgroup.mem_pi, Set.mem_univ, forall_const]

/-- The actual ambient product-subgroup quotient splits by coordinates.
When `K i ≤ L i`, the denominator is exactly the intended smaller lattice;
the statement also remains valid for arbitrary `K`, via `addSubgroupOf`. -/
def subgroupPiQuotientEquiv (L K : ∀ i, AddSubgroup (G i)) :
    (AddSubgroup.pi Set.univ L ⧸
      (AddSubgroup.pi Set.univ K).addSubgroupOf (AddSubgroup.pi Set.univ L)) ≃+
        (∀ i, L i ⧸ (K i).addSubgroupOf (L i)) :=
  QuotientAddGroup.liftEquiv
    ((AddSubgroup.pi Set.univ K).addSubgroupOf (AddSubgroup.pi Set.univ L))
    (subgroupCoordinateQuotientMap_surjective L K)
    (subgroupCoordinateQuotientMap_ker L K).symm

@[simp] theorem subgroupPiQuotientEquiv_mk (L K : ∀ i, AddSubgroup (G i))
    (x : AddSubgroup.pi Set.univ L) (i : ι) :
    subgroupPiQuotientEquiv L K
      (x : AddSubgroup.pi Set.univ L ⧸
        (AddSubgroup.pi Set.univ K).addSubgroupOf (AddSubgroup.pi Set.univ L)) i =
      ((⟨x.1 i, x.2 i (Set.mem_univ i)⟩ : L i) : L i ⧸ (K i).addSubgroupOf (L i)) := rfl

/-- The index cardinality of actual product lattices is the coordinate product. -/
theorem card_subgroup_pi_quotient [Fintype ι] (L K : ∀ i, AddSubgroup (G i)) :
    Nat.card (AddSubgroup.pi Set.univ L ⧸
      (AddSubgroup.pi Set.univ K).addSubgroupOf (AddSubgroup.pi Set.univ L)) =
        ∏ i, Nat.card (L i ⧸ (K i).addSubgroupOf (L i)) := by
  rw [Nat.card_congr (subgroupPiQuotientEquiv L K).toEquiv, Nat.card_pi]

section Matrix
variable {D m : Type*} [Ring D]
open PaperXI.MoritaLattice110

/-- The quotient map on the actual matrix subgroup, evaluated entry by entry. -/
def matrixCoordinateQuotientMap (L K : m → m → AddSubgroup D) :
    entrywise L →+ (∀ i j, L i j ⧸ (K i j).addSubgroupOf (L i j)) where
  toFun x i j := (⟨x.1 i j, x.2 i j⟩ : L i j)
  map_zero' := by ext i j; rfl
  map_add' x y := by ext i j; rfl

@[simp] theorem matrixCoordinateQuotientMap_apply (L K : m → m → AddSubgroup D)
    (x : entrywise L) (i j : m) :
    matrixCoordinateQuotientMap L K x i j =
      ((⟨x.1 i j, x.2 i j⟩ : L i j) : L i j ⧸ (K i j).addSubgroupOf (L i j)) := rfl

theorem matrixCoordinateQuotientMap_surjective (L K : m → m → AddSubgroup D) :
    Function.Surjective (matrixCoordinateQuotientMap L K) := by
  intro y
  let x : ∀ i j, L i j := fun i j => Quotient.out (y i j)
  refine ⟨⟨fun i j => (x i j : D), fun i j => (x i j).2⟩, ?_⟩
  ext i j
  exact Quotient.out_eq (y i j)

/-- The kernel is the actual allowed-entry matrix subgroup in the numerator. -/
theorem matrixCoordinateQuotientMap_ker (L K : m → m → AddSubgroup D) :
    (matrixCoordinateQuotientMap L K).ker = (entrywise K).addSubgroupOf (entrywise L) := by
  ext x
  simp only [AddMonoidHom.mem_ker, funext_iff, matrixCoordinateQuotientMap_apply,
    Pi.zero_apply, QuotientAddGroup.eq_zero_iff, AddSubgroup.mem_addSubgroupOf,
    mem_entrywise]

/-- The literal matrix quotient is additively equivalent to its entry quotients. -/
def matrixQuotientEquiv (L K : m → m → AddSubgroup D) :
    (entrywise L ⧸ (entrywise K).addSubgroupOf (entrywise L)) ≃+
      (∀ i j, L i j ⧸ (K i j).addSubgroupOf (L i j)) :=
  QuotientAddGroup.liftEquiv ((entrywise K).addSubgroupOf (entrywise L))
    (matrixCoordinateQuotientMap_surjective L K) (matrixCoordinateQuotientMap_ker L K).symm

@[simp] theorem matrixQuotientEquiv_mk (L K : m → m → AddSubgroup D)
    (x : entrywise L) (i j : m) :
    matrixQuotientEquiv L K
      (x : entrywise L ⧸ (entrywise K).addSubgroupOf (entrywise L)) i j =
        ((⟨x.1 i j, x.2 i j⟩ : L i j) : L i j ⧸ (K i j).addSubgroupOf (L i j)) := rfl

/-- The matrix-lattice index cardinality is the product of the entry cardinalities. -/
theorem card_matrix_quotient [Fintype m] (L K : m → m → AddSubgroup D) :
    Nat.card (entrywise L ⧸ (entrywise K).addSubgroupOf (entrywise L)) =
      ∏ i, ∏ j, Nat.card (L i j ⧸ (K i j).addSubgroupOf (L i j)) := by
  rw [Nat.card_congr (matrixQuotientEquiv L K).toEquiv]
  simp_rw [Nat.card_pi]

end Matrix

end PaperXI.MoritaQuotient110
