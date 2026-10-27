import PaperX.CyclotomicInertiaBridge

open PaperX.CyclotomicInertiaBridge

example {R : Type*} [CommRing R] [IsDomain R] [IsLocalRing R]
    (n : ℕ) [NeZero n] (hn : IsUnit (n : R))
    {x y : R} (hx : x ^ n = 1) (hy : y ^ n = 1)
    (hres : IsLocalRing.residue R x = IsLocalRing.residue R y) : x = y :=
  residue_injective_on_roots n hn hx hy hres

example : ∃ x y : PadicInt 2, x ^ 2 = 1 ∧ y ^ 2 = 1 ∧ x ≠ y ∧
    IsLocalRing.residue (PadicInt 2) x = IsLocalRing.residue (PadicInt 2) y :=
  twoAdic_distinct_roots_same_residue

example : ¬ IsUnit (2 : PadicInt 2) := twoAdic_order_not_unit

example {L : Type*} [Field L] (K : Type*) [Field K] [Algebra K L]
    (A : ValuationSubring L) (n : ℕ) [NeZero n] (hn : IsUnit (n : A))
    {x : L} (hx : x ^ n = 1)
    (σ : A.decompositionSubgroup K) (hσ : σ ∈ A.inertiaSubgroup K) :
    (σ.val : L ≃ₐ[K] L) x = x := inertia_fixes_roots K A n hn hx σ hσ
