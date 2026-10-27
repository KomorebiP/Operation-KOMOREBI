import PaperXI.HeisenbergCharacterProfile111
import PaperXI.FiniteRepresentation
import PaperXI.TypeSideDescent
import PaperXI.SchurScalar
import Mathlib.LinearAlgebra.Determinant
import Mathlib.GroupTheory.OrderOfElement

/-! A literal global central lift produces the Heisenberg representation bridge;
the target representation equivalence is a conclusion. The actual quotient
endpoint retains the original theta and eta on its original carrier. Existence
of the canonical global quotient lift is not asserted here. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.GlobalHeisenbergBridge112
open Representation HeisenbergCharacterProfile111

section FiniteUniqueness
variable {P V W : Type*} [Group P] [Finite P]
  [AddCommGroup V] [Module ℂ V] [AddCommGroup W] [Module ℂ W]

/-- The common original scalar/trace profile forces a nonzero actual Hom.
Neither representation equivalence nor target Hom dimension is an input. -/
theorem equiv_of_common_profile
    (H : Subgroup P) (θ : H →* ℂˣ)
    (ρ : Representation ℂ P V) (σ : Representation ℂ P W)
    [IsIrreducible ρ] [IsIrreducible σ]
    (hρ : ∀ h : H, ρ h = (θ h : ℂ) • LinearMap.id)
    (hσ : ∀ h : H, σ h = (θ h : ℂ) • LinearMap.id)
    (hzρ : ∀ p : P, p ∉ H → Representation.character ρ p = 0)
    (hzσ : ∀ p : P, p ∉ H → Representation.character σ p = 0) :
    Nonempty (Representation.Equiv ρ σ) := by
  classical
  let : Fintype P := Fintype.ofFinite P
  let : FiniteDimensional ℂ V := FiniteRepresentation.finiteDimensional ρ
  let : FiniteDimensional ℂ W := FiniteRepresentation.finiteDimensional σ
  have he := CharacterPairing108.dimension_formula ρ σ H H θ θ hρ hσ hzρ hzσ
    (fun _ _ _ => rfl)
  have hp : 0 < Module.finrank ℂ V * Module.finrank ℂ W * Nat.card H :=
    Nat.mul_pos (Nat.mul_pos (FiniteRepresentation.finrank_pos ρ)
      (FiniteRepresentation.finrank_pos σ)) (Nat.card_pos (α := H))
  have hhom : 0 < Module.finrank ℂ (IntertwiningMap ρ σ) := by
    by_contra hn
    have hh : Module.finrank ℂ (IntertwiningMap ρ σ) = 0 := Nat.eq_zero_of_not_pos hn
    rw [hh, mul_zero, inf_idem] at he
    exact (Nat.ne_of_gt hp) he.symm
  let : Nontrivial (IntertwiningMap ρ σ) := Module.nontrivial_of_finrank_pos hhom
  obtain ⟨T, hT⟩ := exists_ne (0 : IntertwiningMap ρ σ)
  exact ⟨T.ofBijective ((IsIrreducible.bijective_or_eq_zero T).resolve_right hT)⟩

variable {k X : Type*} [Field k] [AddCommGroup X] [Module k X]

/-- Nondegenerate original commutator data derive both profiles and hence the
global representation equivalence, without separate break embeddings. -/
theorem equiv_of_common_quotient_form
    (H : Subgroup P) [H.Normal] (θ : H →* ℂˣ)
    (τ : (P ⧸ H) ≃* Multiplicative X)
    (B : X →ₗ[k] X →ₗ[k] k) (ψ : AddChar k ℂˣ) (hψ : ψ ≠ 1)
    (hnd : ∀ v : X, (∀ u : X, B u v = 0) → v = 0)
    (hform : ∀ p q : P, ψ (B (coordinate H τ p) (coordinate H τ q)) =
      characterCommutator H τ θ p q)
    (ρ : Representation ℂ P V) (σ : Representation ℂ P W)
    [IsIrreducible ρ] [IsIrreducible σ]
    (hρ : ∀ h : H, ρ h = (θ h : ℂ) • LinearMap.id)
    (hσ : ∀ h : H, σ h = (θ h : ℂ) • LinearMap.id) :
    Nonempty (Representation.Equiv ρ σ) :=
  equiv_of_common_profile H θ ρ σ hρ hσ
    (trace_support_of_nondegenerate_form H τ θ B ψ hψ hnd hform ρ hρ)
    (trace_support_of_nondegenerate_form H τ θ B ψ hψ hnd hform σ hσ)

/-- A global central-extension group lift preserving the original scalar
character gives the desired representation bridge. No target iso is a field. -/
theorem equiv_of_global_central_lift
    {Q : Type*} [Group Q] (H : Subgroup P) [H.Normal] (N : Subgroup Q)
    (θ : H →* ℂˣ) (φ : N →* ℂˣ) (ℓ : P ≃* Q)
    (ζ : H →* N) (hℓ : ∀ h : H, ℓ (h : P) = (ζ h : Q))
    (hchar : ∀ h : H, θ h = φ (ζ h))
    (τ : (P ⧸ H) ≃* Multiplicative X)
    (B : X →ₗ[k] X →ₗ[k] k) (ψ : AddChar k ℂˣ) (hψ : ψ ≠ 1)
    (hnd : ∀ v : X, (∀ u : X, B u v = 0) → v = 0)
    (hform : ∀ p q : P, ψ (B (coordinate H τ p) (coordinate H τ q)) =
      characterCommutator H τ θ p q)
    (ρ : Representation ℂ P V) (σ : Representation ℂ Q W)
    [IsIrreducible ρ] [IsIrreducible σ]
    (hρ : ∀ h : H, ρ h = (θ h : ℂ) • LinearMap.id)
    (hσ : ∀ z : N, σ z = (φ z : ℂ) • LinearMap.id) :
    Nonempty (Representation.Equiv ρ (σ.comp ℓ.toMonoidHom)) := by
  let : IsIrreducible (σ.comp ℓ.toMonoidHom) :=
    (QuotientRepresentation.irreducible_comp_iff ℓ.toMonoidHom ℓ.surjective σ).mpr
      inferInstance
  apply equiv_of_common_quotient_form H θ τ B ψ hψ hnd hform ρ
    (σ.comp ℓ.toMonoidHom) hρ
  intro h
  change σ (ℓ (h : P)) = _
  rw [hℓ, hσ, hchar]

end FiniteUniqueness

section ActualQuotient
variable {G P V W k X : Type*} [Group G] [Group P] [Finite P]
  [AddCommGroup V] [Module ℂ V] [AddCommGroup W] [Module ℂ W]
  [Field k] [AddCommGroup X] [Module k X]

/-- The target is the literal action descended from the prescribed actual eta
to J¹/ker(theta), on the same W. Scalar action is derived from occurrence. -/
theorem actual_eta_bridge_of_global_lift
    (D : Subgroup G) [D.Normal] (θ : D →* ℂˣ)
    (hinv : TypeSideDescent.Invariant D θ)
    (η : Representation ℂ G W) [IsIrreducible η]
    (hcontains : TypeSideDescent.Contains D θ η)
    (H : Subgroup P) [H.Normal] (χ : H →* ℂˣ)
    (ℓ : P ≃* (G ⧸ TypeSideDescent.characterKernel D θ hinv))
    (ζ : H →* (D ⧸ θ.ker))
    (hℓ : ∀ h : H, ℓ (h : P) = TypeSideDescent.centerInclusion D θ hinv (ζ h))
    (hchar : ∀ h : H, χ h = TypeSideDescent.centralCharacter D θ (ζ h))
    (τ : (P ⧸ H) ≃* Multiplicative X)
    (B : X →ₗ[k] X →ₗ[k] k) (ψ : AddChar k ℂˣ) (hψ : ψ ≠ 1)
    (hnd : ∀ v : X, (∀ u : X, B u v = 0) → v = 0)
    (hform : ∀ p q : P, ψ (B (coordinate H τ p) (coordinate H τ q)) =
      characterCommutator H τ χ p q)
    (ρ : Representation ℂ P V) [IsIrreducible ρ]
    (hρ : ∀ h : H, ρ h = (χ h : ℂ) • LinearMap.id) :
    Nonempty (Representation.Equiv ρ
      ((TypeSideDescent.representation D θ hinv η hcontains).comp ℓ.toMonoidHom)) := by
  let σ := TypeSideDescent.representation D θ hinv η hcontains
  let : IsIrreducible σ := TypeSideDescent.representation_irreducible D θ hinv η hcontains
  let : IsIrreducible (σ.comp ℓ.toMonoidHom) :=
    (QuotientRepresentation.irreducible_comp_iff ℓ.toMonoidHom ℓ.surjective σ).mpr
      inferInstance
  apply equiv_of_common_quotient_form H χ τ B ψ hψ hnd hform ρ (σ.comp ℓ.toMonoidHom) hρ
  intro h
  change σ (ℓ (h : P)) = _
  rw [hℓ]
  exact (TypeSideDescent.central_action D θ hinv η hcontains (ζ h)).trans
    (by rw [hchar])

end ActualQuotient

section GeneratorPhase
variable {P V W : Type*} [Group P]
  [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]
  [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]

omit [FiniteDimensional ℂ W] in
/-- Two actual implementers of the same lifted automorphism differ by a scalar
after the global Heisenberg bridge. Schur applies to the whole irreducible rho. -/
theorem generator_discrepancy
    (ρ : Representation ℂ P V) (σ : Representation ℂ P W) [IsIrreducible ρ]
    (U : V ≃ₗ[ℂ] W) (hU : ∀ p v, U (ρ p v) = σ p (U v))
    (α : MulAut P) (A : V ≃ₗ[ℂ] V) (B : W ≃ₗ[ℂ] W)
    (hA : ∀ p v, A (ρ p v) = ρ (α p) (A v))
    (hB : ∀ p v, B (σ p v) = σ (α p) (B v)) :
    ∃ c : ℂˣ, ∀ v, U (A v) = (c : ℂ) • B (U v) := by
  have hBi (p : P) (w : W) : B.symm (σ (α p) w) = σ p (B.symm w) := by
    apply B.injective
    rw [B.apply_symm_apply, hB, B.apply_symm_apply]
  let T := (A.trans U).trans B.symm
  have hT : ∀ p v, T (ρ p v) = σ p (T v) := by
    intro p v
    simp only [T, LinearEquiv.trans_apply, hA, hU, hBi]
  obtain ⟨c, hc, _⟩ := SchurScalar.bridge_unique ρ σ U T hU hT
  refine ⟨c, fun v => ?_⟩
  simpa only [T, LinearEquiv.trans_apply, B.apply_symm_apply, map_smul] using
    congrArg B (hc v)

omit [FiniteDimensional ℂ V] [FiniteDimensional ℂ W] in
/-- The scalar discrepancy propagates through actual powers of honest
generator operators, with the same direction as the original bridge. -/
theorem generator_discrepancy_pow
    (U : V ≃ₗ[ℂ] W) (A : V ≃ₗ[ℂ] V) (B : W ≃ₗ[ℂ] W) (c : ℂˣ)
    (hc : ∀ v, U (A v) = (c : ℂ) • B (U v)) (n : ℕ) (v : V) :
    U ((A ^ n) v) = ((c ^ n : ℂˣ) : ℂ) • (B ^ n) (U v) := by
  induction n generalizing v with
  | zero => simp
  | succ n ih =>
    rw [pow_succ, LinearEquiv.mul_apply, ih, hc, map_smul]
    simp only [pow_succ, Units.val_mul, smul_smul, LinearEquiv.mul_apply]

/-- Two coprime exact scalar power conditions eliminate every residual phase. -/
theorem unit_eq_one_of_coprime_powers (c : ℂˣ) (n d : ℕ)
    (hcop : Nat.Coprime n d) (hn : c ^ n = 1) (hd : c ^ d = 1) : c = 1 := by
  apply orderOf_eq_one_iff.mp
  exact Nat.eq_one_of_dvd_coprimes hcop (orderOf_dvd_of_pow_eq_one hn)
    (orderOf_dvd_of_pow_eq_one hd)

omit [FiniteDimensional ℂ W] in
/-- Matching determinants kill the generator phase when its honest order and
the original Heisenberg dimension are coprime. A nonzero trace is unnecessary. -/
theorem generator_phase_eq_one_of_det_coprime [Nontrivial V]
    (U : V ≃ₗ[ℂ] W) (A : V ≃ₗ[ℂ] V) (B : W ≃ₗ[ℂ] W) (c : ℂˣ)
    (hc : ∀ v, U (A v) = (c : ℂ) • B (U v))
    (n : ℕ) (hA : A ^ n = 1) (hB : B ^ n = 1)
    (hdet : LinearEquiv.det A = LinearEquiv.det B)
    (hcop : Nat.Coprime n (Module.finrank ℂ V)) : c = 1 := by
  have hcn : c ^ n = 1 := by
    obtain ⟨v, hv⟩ := exists_ne (0 : V)
    have huv : U v ≠ 0 := fun h => hv (U.injective (h.trans U.map_zero.symm))
    have hp := generator_discrepancy_pow U A B c hc n v
    rw [hA, hB] at hp
    have hs : ((c ^ n : ℂˣ) : ℂ) = 1 :=
      (smul_left_injective ℂ huv) (by simpa only [LinearEquiv.coe_one, id_eq, one_smul] using hp.symm)
    exact Units.ext hs
  let B' := (U.trans B).trans U.symm
  have ha : A.toLinearMap = (c : ℂ) • B'.toLinearMap := by
    ext v
    apply U.injective
    change U (A v) = U ((c : ℂ) • B' v)
    simp only [B', LinearEquiv.trans_apply, map_smul, U.apply_symm_apply]
    exact hc v
  have hbd : LinearMap.det B'.toLinearMap = (LinearEquiv.det B : ℂ) := by
    simpa only [B', LinearEquiv.symm_symm, LinearEquiv.coe_det] using
      congrArg Units.val (LinearEquiv.det_conj B U.symm)
  have hcd : c ^ Module.finrank ℂ V = 1 := by
    have hd := congrArg LinearMap.det ha
    rw [LinearMap.det_smul, hbd, ← LinearEquiv.coe_det A] at hd
    rw [hdet] at hd
    apply Units.ext
    exact mul_right_cancel₀ (Units.ne_zero (LinearEquiv.det B))
      (by simpa only [Units.val_one, one_mul, Units.val_pow_eq_pow_val] using hd.symm)
  exact unit_eq_one_of_coprime_powers c n (Module.finrank ℂ V) hcop hcn hcd

omit [FiniteDimensional ℂ W] in
/-- The derived Heisenberg bridge intertwines the honest generator when the
same lifted automorphism and determinant normalization have been attached. -/
theorem generator_equivariant_of_det_coprime
    (ρ : Representation ℂ P V) (σ : Representation ℂ P W) [IsIrreducible ρ]
    (U : V ≃ₗ[ℂ] W) (hU : ∀ p v, U (ρ p v) = σ p (U v))
    (α : MulAut P) (A : V ≃ₗ[ℂ] V) (B : W ≃ₗ[ℂ] W)
    (hA : ∀ p v, A (ρ p v) = ρ (α p) (A v))
    (hB : ∀ p v, B (σ p v) = σ (α p) (B v))
    (n : ℕ) (hAn : A ^ n = 1) (hBn : B ^ n = 1)
    (hdet : LinearEquiv.det A = LinearEquiv.det B)
    (hcop : Nat.Coprime n (Module.finrank ℂ V)) :
    ∀ v, U (A v) = B (U v) := by
  let : Nontrivial V := GeneratedIrreducibility.nontrivial_space ρ
  obtain ⟨c, hc⟩ := generator_discrepancy ρ σ U hU α A B hA hB
  have he := generator_phase_eq_one_of_det_coprime U A B c hc n hAn hBn hdet hcop
  simpa only [he, Units.val_one, one_smul] using hc

end GeneratorPhase

section CyclicAction
variable {C V W : Type*} [Group C]
  [AddCommGroup V] [Module ℂ V] [AddCommGroup W] [Module ℂ W]

/-- A bridge for one declared cyclic generator is a bridge for every element
of the same honest cyclic action. The cyclic generation datum is explicit. -/
theorem cyclic_equivariant_of_generator
    (Ωρ : C →* (V ≃ₗ[ℂ] V)) (Ωσ : C →* (W ≃ₗ[ℂ] W))
    (c : C) (hgen : ∀ g : C, ∃ n : ℕ, g = c ^ n)
    (U : V ≃ₗ[ℂ] W) (hU : ∀ v, U (Ωρ c v) = Ωσ c (U v)) :
    ∀ g v, U (Ωρ g v) = Ωσ g (U v) := by
  intro g v
  obtain ⟨n, rfl⟩ := hgen g
  simpa only [map_pow, one_pow, Units.val_one, one_smul] using
    generator_discrepancy_pow U (Ωρ c) (Ωσ c) 1
      (fun v => by simpa only [Units.val_one, one_smul] using hU v) n v

end CyclicAction

section GlobalEquivariantBridge
variable {P C V W k X : Type*} [Group P] [Finite P] [Group C]
  [AddCommGroup V] [Module ℂ V] [AddCommGroup W] [Module ℂ W]
  [Field k] [AddCommGroup X] [Module k X]

/-- The equivariant global bridge is derived from nondegenerate original
Heisenberg data and actual honest generator actions. Neither a representation
equivalence nor a target eta intertwiner is a premise. -/
theorem equivariant_bridge_of_common_quotient_form
    (H : Subgroup P) [H.Normal] (θ : H →* ℂˣ)
    (τ : (P ⧸ H) ≃* Multiplicative X)
    (B : X →ₗ[k] X →ₗ[k] k) (ψ : AddChar k ℂˣ) (hψ : ψ ≠ 1)
    (hnd : ∀ v : X, (∀ u : X, B u v = 0) → v = 0)
    (hform : ∀ p q : P, ψ (B (coordinate H τ p) (coordinate H τ q)) =
      characterCommutator H τ θ p q)
    (ρ : Representation ℂ P V) (σ : Representation ℂ P W)
    [IsIrreducible ρ] [IsIrreducible σ]
    (hρ : ∀ h : H, ρ h = (θ h : ℂ) • LinearMap.id)
    (hσ : ∀ h : H, σ h = (θ h : ℂ) • LinearMap.id)
    (Ωρ : C →* (V ≃ₗ[ℂ] V)) (Ωσ : C →* (W ≃ₗ[ℂ] W))
    (c : C) (hgen : ∀ g : C, ∃ n : ℕ, g = c ^ n)
    (α : MulAut P)
    (hA : ∀ p v, Ωρ c (ρ p v) = ρ (α p) (Ωρ c v))
    (hB : ∀ p v, Ωσ c (σ p v) = σ (α p) (Ωσ c v))
    (n : ℕ) (hn : c ^ n = 1)
    (hdet : LinearEquiv.det (Ωρ c) = LinearEquiv.det (Ωσ c))
    (hcop : Nat.Coprime n (Module.finrank ℂ V)) :
    ∃ U : Representation.Equiv ρ σ,
      ∀ g v, U (Ωρ g v) = Ωσ g (U v) := by
  let : FiniteDimensional ℂ V := FiniteRepresentation.finiteDimensional ρ
  obtain ⟨U⟩ := equiv_of_common_quotient_form H θ τ B ψ hψ hnd hform ρ σ hρ hσ
  have hU : ∀ p v, U.toLinearEquiv (ρ p v) = σ p (U.toLinearEquiv v) :=
    U.toIntertwiningMap.isIntertwining
  have hAn : Ωρ c ^ n = 1 := by rw [← map_pow, hn, map_one]
  have hBn : Ωσ c ^ n = 1 := by rw [← map_pow, hn, map_one]
  have hc := generator_equivariant_of_det_coprime ρ σ U.toLinearEquiv hU
    α (Ωρ c) (Ωσ c) hA hB n hAn hBn hdet hcop
  exact ⟨U, cyclic_equivariant_of_generator Ωρ Ωσ c hgen U.toLinearEquiv hc⟩

end GlobalEquivariantBridge

end PaperXI.GlobalHeisenbergBridge112
