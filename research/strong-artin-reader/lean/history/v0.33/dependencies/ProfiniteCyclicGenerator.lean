import Mathlib.Topology.Algebra.Category.ProfiniteGrp.Completion
import Mathlib.Algebra.Group.TypeTags.Basic

/-! The genuine profinite completion of the infinite cyclic group.
A continuous homomorphism out of this group is determined by Frobenius. -/
namespace Komorebi.StrongArtin.Procyclic

open CategoryTheory

abbrev Integers := Multiplicative ℤ
abbrev Zhat := ProfiniteGrp.ProfiniteCompletion.completion (GrpCat.of Integers)

def integerMap : Integers →* Zhat :=
  (ProfiniteGrp.ProfiniteCompletion.eta (GrpCat.of Integers)).hom

def frobenius : Zhat := integerMap (Multiplicative.ofAdd 1)

@[simp] theorem integerMap_one : integerMap (1 : Integers) = 1 := map_one _

theorem integerMap_dense : DenseRange integerMap :=
  ProfiniteGrp.ProfiniteCompletion.denseRange _

/-- Integer powers specify an ordinary homomorphism from the infinite cyclic group. -/
def integerPowers {H : Type} [Group H] (h : H) : Integers →* H where
  toFun n := h ^ n.toAdd
  map_one' := by simp
  map_mul' a b := by simp [zpow_add]

@[simp] theorem integerPowers_generator {H : Type} [Group H] (h : H) :
    integerPowers h (Multiplicative.ofAdd 1) = h := by simp [integerPowers]

/-- Every homomorphism from the integers is determined by the generator. -/
theorem integerHom_ext {H : Type} [Group H] (f g : Integers →* H)
    (h : f (Multiplicative.ofAdd 1) = g (Multiplicative.ofAdd 1)) : f = g := by
  apply MonoidHom.ext
  intro n
  have hn : n = (Multiplicative.ofAdd 1 : Integers) ^ n.toAdd := by
    change n.toAdd = n.toAdd • (1 : ℤ)
    simp
  rw [hn, map_zpow, map_zpow, h]

/-- The universal property of Mathlib's actual profinite completion. -/
noncomputable def fromFrobenius {H : ProfiniteGrp} (h : H) : Zhat →ₜ* H :=
  (ProfiniteGrp.ProfiniteCompletion.lift (GrpCat.ofHom (integerPowers h))).hom

@[simp] theorem fromFrobenius_integer {H : ProfiniteGrp} (h : H) (n : Integers) :
    fromFrobenius h (integerMap n) = integerPowers h n := by
  have he := ProfiniteGrp.ProfiniteCompletion.lift_eta (GrpCat.ofHom (integerPowers h))
  exact ConcreteCategory.congr_hom he n

@[simp] theorem fromFrobenius_frobenius {H : ProfiniteGrp} (h : H) :
    fromFrobenius h frobenius = h := by
  simp [frobenius]

/-- No discrete topology is placed on the source. -/
theorem hom_ext {H : Type} [Group H] [TopologicalSpace H] [T2Space H]
    (f g : Zhat →ₜ* H) (h : f frobenius = g frobenius) : f = g := by
  have he : f.toMonoidHom.comp integerMap = g.toMonoidHom.comp integerMap :=
    integerHom_ext _ _ h
  have hf : (fun n => f (integerMap n)) = fun n => g (integerMap n) :=
    congrArg (fun l : Integers →* H => (l : Integers → H)) he
  have hall := integerMap_dense.equalizer f.continuous g.continuous hf
  ext x
  exact congrFun hall x

noncomputable def frobeniusEquiv (H : ProfiniteGrp) : (Zhat →ₜ* H) ≃ H where
  toFun f := f frobenius
  invFun := fromFrobenius
  left_inv _f := hom_ext _ _ (fromFrobenius_frobenius _)
  right_inv := fromFrobenius_frobenius

end Komorebi.StrongArtin.Procyclic
