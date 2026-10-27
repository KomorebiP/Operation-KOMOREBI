module
public import Mathlib.Data.ZMod.Basic
public import Mathlib.Data.Nat.Log
public import Mathlib.GroupTheory.Coset.Card
public import Mathlib.LinearAlgebra.Finsupp.LinearCombination
public import Mathlib.Tactic

@[expose] public section
namespace Komorebi.Discovery

#check AddSubgroup.card_addSubgroup_dvd_card
#check AddSubgroup.card_subgroup_dvd_card
#check Nat.dvd_prime_pow
#check Nat.card_fun
#check Nat.card_pi
#check ZMod.card
#check Nat.log_pow
#check Nat.card_lt_card
#check Set.ncard_lt_ncard
#check Nat.card_le_card_of_injective
#check Fintype.card_lt_of_injective_not_surjective
#check Submodule.mem_span_range_iff_exists_fun
#check Submodule.span_induction
#check Submodule.span_insert
#check Submodule.span_insert_eq_span
#check SetLike.coe_ssubset_coe
#check Finset.card_lt_card

end Komorebi.Discovery
