import PaperXI.InducedCycleInvariants
import PaperXI.TameConductor
import PaperXI.InvariantPolynomial

/-! All inertia and determinant data are read from the actual induced space.
The finite ramification expression is kept distinct from an arithmetically
identified Artin conductor. No irreducibility or regularity is needed here. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.InducedTameProfile
open scoped Classical BigOperators
open Polynomial PaperXI.CyclicInduced PaperXI.CyclicAction PaperXI.PacketTransport
open PaperXI.TameOrbitTransitivity PaperXI.GeneratedIrreducibility
variable {G : Type*} [Group G] {M : ℕ} [NeZero M]
variable (δ : G →* Multiplicative ℤ) (ι : Multiplicative (ZMod M) →* G)

/-- Finite inertia has degree zero in an integer degree group. -/
theorem inertia_degree (a : Multiplicative (ZMod M)) : δ (ι a) = 1 := by
  have hp : (ι a) ^ M = 1 := by
    rw [← map_pow]
    have ha : a ^ M = 1 := by
      apply Multiplicative.toAdd.injective
      simp [toAdd_pow, nsmul_eq_mul]
    rw [ha, map_one]
  have hd := congrArg (fun g => (δ g).toAdd) hp
  have hm : (M : ℤ) ≠ 0 := Nat.cast_ne_zero.mpr (NeZero.ne M)
  have hz : (M : ℤ) * (δ (ι a)).toAdd = 0 := by
    simpa [map_pow, toAdd_pow, nsmul_eq_mul] using hd
  apply Multiplicative.toAdd.injective
  exact (mul_eq_zero.mp hz).resolve_left hm

/-- The actual inclusion of finite inertia into every degree-divisibility subgroup. -/
def inertiaInDegree (n : ℕ) : Multiplicative (ZMod M) →* TameDegree.degreeSubgroup δ n where
  toFun a := ⟨ι a, by
    change TameDegree.degreeMod δ n (ι a) = 1
    simp [TameDegree.degreeMod, TameDegree.degree, inertia_degree δ ι a]⟩
  map_one' := by apply Subtype.ext; simp
  map_mul' a b := by apply Subtype.ext; simp

variable (φ : G) (hφ : δ φ = Multiplicative.ofAdd (1 : ℤ))
variable (n : ℕ) [NeZero n] (ξ : TameDegree.degreeSubgroup δ n →* ℂˣ)
variable (q : (ZMod M)ˣ) (j : ZMod M)
variable (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
  ι (Multiplicative.ofAdd (q : ZMod M)))
variable (hξ : ∀ a : ZMod M,
  (ξ (inertiaInDegree δ ι n (Multiplicative.ofAdd a)) : ℂ) = ZMod.stdAddChar (j * a))

include hξ in
/-- The zeroth basis line carries the declared inertia character, derived from
its actual inducing-character restriction. -/
theorem origin_mem : degreeBasis δ φ hφ n ξ 0 ∈
    packet (tameRestriction (degreeInduced δ n ξ) ι) j := by
  intro a
  have h := degreeBasis_action_zero δ φ hφ n ξ
    (inertiaInDegree δ ι n (Multiplicative.ofAdd a))
  change degreeInduced δ n ξ (ι (Multiplicative.ofAdd a))
    (degreeBasis δ φ hφ n ξ 0) = _ at h
  rw [hξ] at h
  exact h

include hφ hrel hξ in
/-- Each basis line lies in the computed Frobenius-rotated inertia packet. -/
theorem basis_packet (i : Fin n) :
    InducedCycleInvariants.basis δ φ hφ n ξ i ∈
      packet (tameRestriction (degreeInduced δ n ξ) ι)
        (((q ^ (i : ℕ) : (ZMod M)ˣ) : ZMod M) * j) := by
  have hn := Nat.pos_of_ne_zero (NeZero.ne n)
  rw [InducedCycleInvariants.basis_powers δ φ hφ n ξ hn i]
  have h := PacketReturn.power_mem (tameRestriction (degreeInduced δ n ξ) ι)
    (actionEquiv (degreeInduced δ n ξ) φ) q
    (geometric_relation (degreeInduced δ n ξ) ι φ q hrel) j (i : ℕ)
    (origin_mem δ ι φ hφ n ξ j hξ)
  simpa only [← PacketCycle.linear_power, InducedCycleInvariants.basis_apply,
    Fin.val_zero, Nat.cast_zero, actionEquiv] using h

/-- A general eigenbasis support theorem; repeated labels are allowed. -/
theorem support_of_basis {V : Type*} [AddCommGroup V] [Module ℂ V]
    (ρ : Action (K := ℂ) (V := V) (M := M)) {A : Type*}
    (b : Module.Basis A ℂ V) (labels : A → ZMod M)
    (hb : ∀ a, b a ∈ packet ρ (labels a)) (k : ZMod M) :
    packet ρ k ≠ ⊥ ↔ ∃ a, labels a = k := by
  constructor
  · intro hk
    by_contra hnone
    have hne : ∀ a, labels a ≠ k := by simpa using hnone
    have hp : projector ρ k = 0 := by
      apply b.ext
      intro a
      exact projector_on_other_packet ρ (Ne.symm (hne a)) (hb a)
    apply hk
    apply le_antisymm
    · intro v hv
      have he := (mem_iff_projector ρ k v).mp hv
      rw [hp] at he
      exact he.symm
    · exact bot_le
  · rintro ⟨a, rfl⟩ he
    have hv := hb a
    rw [he] at hv
    exact b.ne_zero a hv

include hφ hrel hξ in
/-- The support is the actual set of labels on the induced Frobenius cycle. -/
theorem inertia_support (k : ZMod M) :
    packet (tameRestriction (degreeInduced δ n ξ) ι) k ≠ ⊥ ↔
      ∃ i : Fin n, ((q ^ (i : ℕ) : (ZMod M)ˣ) : ZMod M) * j = k :=
  support_of_basis _ (InducedCycleInvariants.basis δ φ hφ n ξ) _
    (basis_packet δ ι φ hφ n ξ q j hrel hξ) k

include hφ hrel hξ in
/-- All or none of this induced cycle survives inertia invariants. -/
theorem inertia_invariants :
    (tameRestriction (degreeInduced δ n ξ) ι).invariants = if j = 0 then ⊤ else ⊥ := by
  classical
  by_cases hj : j = 0
  · rw [ite_eq_left hj]
    apply InertiaFixed.invariants_eq_top_of_basis _ (InducedCycleInvariants.basis δ φ hφ n ξ)
    intro i
    simpa [hj] using basis_packet δ ι φ hφ n ξ q j hrel hξ i
  · rw [ite_eq_right hj]
    apply InertiaFixed.invariants_eq_bot_of_basis _ (InducedCycleInvariants.basis δ φ hφ n ξ)
      (fun i => ((q ^ (i : ℕ) : (ZMod M)ˣ) : ZMod M) * j)
    · intro i hz
      exact hj ((InertiaFixed.orbit_label_eq_zero_iff q j (i : ℕ)).mp hz)
    · exact basis_packet δ ι φ hφ n ξ q j hrel hξ

include hφ hrel hξ in
theorem invariant_dimension :
    Module.finrank ℂ (tameRestriction (degreeInduced δ n ξ) ι).invariants =
      if j = 0 then n else 0 := by
  by_cases hj : j = 0
  · rw [ite_eq_left hj]
    have ht : (tameRestriction (degreeInduced δ n ξ) ι).invariants = ⊤ := by
      simpa only [ite_eq_left hj] using inertia_invariants δ ι φ hφ n ξ q j hrel hξ
    exact (LinearEquiv.ofTop _ ht).finrank_eq.trans
      (InducedCycleInvariants.dimension δ φ hφ n ξ)
  · rw [ite_eq_right hj]
    have hb : (tameRestriction (degreeInduced δ n ξ) ι).invariants = ⊥ := by
      simpa only [ite_eq_right hj] using inertia_invariants δ ι φ hφ n ξ q j hrel hξ
    have : Subsingleton (tameRestriction (degreeInduced δ n ξ) ι).invariants :=
      Submodule.subsingleton_iff_eq_bot.mpr hb
    exact Module.finrank_zero_of_subsingleton

variable [FiniteDimensional ℂ (DegreeIndSpace δ n ξ)]

include hφ hrel hξ in
/-- The local polynomial is defined by restricting the actual Frobenius map,
not by a case split. The case formula is derived afterward. -/
theorem local_polynomial :
    InvariantPolynomial.localPolynomial (tameRestriction (degreeInduced δ n ξ) ι)
      (actionEquiv (degreeInduced δ n ξ) φ) q
      (geometric_relation (degreeInduced δ n ξ) ι φ q hrel) =
      if j = 0 then 1 - C (InducedCycleInvariants.returnScalar δ φ hφ n ξ : ℂ) * X ^ n
      else 1 := by
  by_cases hj : j = 0
  · rw [ite_eq_left hj]
    have ht : (tameRestriction (degreeInduced δ n ξ) ι).invariants = ⊤ := by
      simpa [hj] using inertia_invariants δ ι φ hφ n ξ q j hrel hξ
    rw [InvariantPolynomial.localPolynomial_of_top _ _ _ _ ht]
    change ((degreeInduced δ n ξ φ).charpoly).reverse = _
    rw [(InducedCycleInvariants.cycle_invariants δ φ hφ n ξ).1,
      CyclicPolynomial.reverse_cycle_polynomial]
  · rw [ite_eq_right hj]
    have hb : (tameRestriction (degreeInduced δ n ξ) ι).invariants = ⊥ := by
      simpa [hj] using inertia_invariants δ ι φ hφ n ξ q j hrel hξ
    exact InvariantPolynomial.localPolynomial_of_bot _ _ _ _ hb

include hφ hrel hξ in
omit [FiniteDimensional ℂ (DegreeIndSpace δ n ξ)] in
/-- Uniform finite tame conductor rule, including one-dimensional ramified
characters and reducible zero-label cycles. Standard conductor identification
is a separate arithmetic interface. -/
theorem finite_conductors (P : Subgroup G)
    (hP : ∀ g ∈ P, ∀ v, degreeInduced δ n ξ g v = v)
    (S : Finset ℕ) (J : ℕ → Subgroup G) (w : ℕ → ℚ)
    (hJP : ∀ r ∈ S, J r ≤ P) :
    TameConductor.finiteSwan (degreeInduced δ n ξ) S J w = 0 ∧
    TameConductor.finiteArtin (degreeInduced δ n ξ) ι S J w =
      if j = 0 then 0 else (n : ℚ) := by
  have hs := TameConductor.finiteSwan_zero (degreeInduced δ n ξ) P hP S J w hJP
  refine ⟨hs, ?_⟩
  unfold TameConductor.finiteArtin
  rw [hs, InducedCycleInvariants.dimension δ φ hφ n ξ,
    invariant_dimension δ ι φ hφ n ξ q j hrel hξ]
  split_ifs <;> simp

end PaperXI.InducedTameProfile
