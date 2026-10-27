import PaperXI.GlobalHeisenbergBridge112
import Mathlib.Data.Int.GCD
import Mathlib.GroupTheory.SpecificGroups.Cyclic

/-! Same-carrier existence and uniqueness of determinant-one cyclic
implementers. The full automorphism and prescribed central character are
retained. No arithmetic realization or identification of the original kappa
is asserted. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CyclicNormalization113
open Representation GlobalHeisenbergBridge112

section ScalarCorrection
variable {V : Type*} [AddCommGroup V] [Module ℂ V]

/-- Scalar correction of an actual implementer on its original carrier. -/
def scale (c : ℂˣ) (A : V ≃ₗ[ℂ] V) : V ≃ₗ[ℂ] V :=
  A.trans (LinearEquiv.smulOfUnit c)

@[simp] theorem scale_apply (c : ℂˣ) (A : V ≃ₗ[ℂ] V) (v : V) :
    scale c A v = (c : ℂ) • A v := rfl

@[simp] theorem scale_pow_apply (c : ℂˣ) (A : V ≃ₗ[ℂ] V) (m : ℕ) (v : V) :
    (scale c A ^ m) v = ((c ^ m : ℂˣ) : ℂ) • (A ^ m) v := by
  induction m generalizing v with
  | zero => simp
  | succ m ih =>
    rw [pow_succ, LinearEquiv.mul_apply, ih, scale_apply, map_smul]
    simp only [pow_succ, Units.val_mul, smul_smul, LinearEquiv.mul_apply]

/-- Bézout gives the unique d-th root among n-torsion scalars. -/
theorem scalar_correction_exists (u : ℂˣ) (n d : ℕ)
    (hcop : Nat.Coprime n d) (hu : u ^ n = 1) :
    ∃ c : ℂˣ, c ^ n = 1 ∧ c ^ d = u := by
  refine ⟨u ^ Nat.gcdB n d, ?_, ?_⟩
  · rw [← zpow_natCast, ← zpow_mul, mul_comm, zpow_mul, zpow_natCast, hu, one_zpow]
  · have he : (1 : ℤ) = (n : ℤ) * Nat.gcdA n d + (d : ℤ) * Nat.gcdB n d := by
      simpa only [hcop, Nat.cast_one] using Nat.gcd_eq_gcd_ab n d
    have hu' : u ^ (n : ℤ) = 1 := by simpa using hu
    have h := congrArg (fun a : ℤ => u ^ a) he
    rw [zpow_one, zpow_add, zpow_mul, zpow_mul, hu', one_zpow, one_mul] at h
    rw [← zpow_natCast, ← zpow_mul, mul_comm, zpow_mul]
    exact h.symm

variable [FiniteDimensional ℂ V]

@[simp] theorem det_scale (c : ℂˣ) (A : V ≃ₗ[ℂ] V) :
    LinearEquiv.det (scale c A) = c ^ Module.finrank ℂ V * LinearEquiv.det A := by
  apply Units.ext
  rw [LinearEquiv.coe_det]
  have he : (scale c A).toLinearMap = (c : ℂ) • A.toLinearMap := by ext v; rfl
  rw [he, LinearMap.det_smul]
  simp only [Units.val_mul, Units.val_pow_eq_pow_val, LinearEquiv.coe_det]

/-- Every honest cyclic operator has a determinant-one scalar correction
when its order is coprime to the dimension. Both operators act on V. -/
theorem normalize_honest (A : V ≃ₗ[ℂ] V) (n : ℕ) (hAn : A ^ n = 1)
    (hcop : Nat.Coprime n (Module.finrank ℂ V)) :
    ∃ c : ℂˣ, c ^ n = 1 ∧ (scale c A) ^ n = 1 ∧
      LinearEquiv.det (scale c A) = 1 := by
  have hd : (LinearEquiv.det A) ^ n = 1 := by
    rw [← map_pow, hAn, map_one]
  obtain ⟨c, hcn, hcd⟩ := scalar_correction_exists (LinearEquiv.det A)⁻¹ n
    (Module.finrank ℂ V) hcop (by rw [inv_pow, hd, inv_one])
  refine ⟨c, hcn, ?_, ?_⟩
  · ext v
    simp only [scale_pow_apply, hcn, Units.val_one, one_smul, hAn]
  · rw [det_scale, hcd, inv_mul_cancel]

end ScalarCorrection

section Implementers
variable {P V : Type*} [Group P] [AddCommGroup V] [Module ℂ V]

/-- The implementer identity propagates to actual powers of the full
lifted automorphism, not merely its action on an associated graded space. -/
theorem implements_pow (ρ : Representation ℂ P V) (α : MulAut P)
    (A : V ≃ₗ[ℂ] V)
    (hA : ∀ p v, A (ρ p v) = ρ (α p) (A v)) (m : ℕ) :
    ∀ p v, (A ^ m) (ρ p v) = ρ ((α ^ m) p) ((A ^ m) v) := by
  induction m with
  | zero => intro p v; rfl
  | succ m ih =>
    intro p v
    change (A ^ m) (A (ρ p v)) = ρ ((α ^ m) (α p)) ((A ^ m) (A v))
    rw [hA, ih]

/-- Scalar correction preserves the exact same automorphism identity. -/
theorem scale_implements (ρ : Representation ℂ P V) (α : MulAut P)
    (A : V ≃ₗ[ℂ] V) (c : ℂˣ)
    (hA : ∀ p v, A (ρ p v) = ρ (α p) (A v)) :
    ∀ p v, scale c A (ρ p v) = ρ (α p) (scale c A v) := by
  intro p v
  simp only [scale_apply, hA, map_smul]

variable [FiniteDimensional ℂ V]

/-- The n-th power of an arbitrary invertible implementer is scalar,
by Schur. The operator need not initially define an honest cyclic action. -/
theorem implementer_power_scalar (ρ : Representation ℂ P V) [IsIrreducible ρ]
    (α : MulAut P) (A : V ≃ₗ[ℂ] V)
    (hA : ∀ p v, A (ρ p v) = ρ (α p) (A v))
    (n : ℕ) (hα : α ^ n = 1) :
    ∃ z : ℂˣ, ∀ v, (A ^ n) v = (z : ℂ) • v := by
  apply SchurScalar.commuting_unit ρ (A ^ n)
  intro p v
  simpa only [hα, MulAut.one_apply] using implements_pow ρ α A hA n p v

/-- Nonzero complex scalars admit unit-valued n-th roots. -/
theorem unit_nth_root (z : ℂˣ) (n : ℕ) (hn : 0 < n) :
    ∃ c : ℂˣ, c ^ n = z := by
  obtain ⟨w, hw⟩ := IsAlgClosed.exists_pow_nat_eq (z : ℂ) hn
  have hw0 : w ≠ 0 := by
    intro h
    rw [h, zero_pow (Nat.ne_of_gt hn)] at hw
    exact z.ne_zero hw.symm
  refine ⟨Units.mk0 w hw0, ?_⟩
  apply Units.ext
  exact hw

/-- An arbitrary intertwining operator can be corrected on the same carrier
to an honest cyclic action. Only existence uses a complex root. -/
theorem normalize_order (ρ : Representation ℂ P V) [IsIrreducible ρ]
    (α : MulAut P) (A : V ≃ₗ[ℂ] V)
    (hA : ∀ p v, A (ρ p v) = ρ (α p) (A v))
    (n : ℕ) (hn : 0 < n) (hα : α ^ n = 1) :
    ∃ c : ℂˣ, (scale c A) ^ n = 1 ∧
      ∀ p v, scale c A (ρ p v) = ρ (α p) (scale c A v) := by
  obtain ⟨z, hz⟩ := implementer_power_scalar ρ α A hA n hα
  obtain ⟨c, hc⟩ := unit_nth_root z⁻¹ n hn
  refine ⟨c, ?_, scale_implements ρ α A c hA⟩
  ext v
  simp only [scale_pow_apply, hc, hz, smul_smul, ← Units.val_mul,
    inv_mul_cancel, Units.val_one, one_smul, LinearEquiv.coe_one, id_eq]

/-- Existence of the canonical normalized generator, obtained from an
arbitrary implementer by order correction followed by Bézout determinant
correction. The output is still an operator on the original V. -/
theorem normalized_generator_exists (ρ : Representation ℂ P V) [IsIrreducible ρ]
    (α : MulAut P) (A : V ≃ₗ[ℂ] V)
    (hA : ∀ p v, A (ρ p v) = ρ (α p) (A v))
    (n : ℕ) (hn : 0 < n) (hα : α ^ n = 1)
    (hcop : Nat.Coprime n (Module.finrank ℂ V)) :
    ∃ B : V ≃ₗ[ℂ] V, B ^ n = 1 ∧ LinearEquiv.det B = 1 ∧
      ∀ p v, B (ρ p v) = ρ (α p) (B v) := by
  obtain ⟨c, hcn, hcA⟩ := normalize_order ρ α A hA n hn hα
  obtain ⟨d, _, hdn, hd⟩ := normalize_honest (scale c A) n hcn hcop
  exact ⟨scale d (scale c A), hdn, hd, scale_implements ρ α (scale c A) d hcA⟩

/-- Two normalized implementers for the same full automorphism are equal.
The scalar ambiguity is killed by the coprime order and determinant powers. -/
theorem normalized_generator_unique (ρ : Representation ℂ P V) [IsIrreducible ρ]
    (α : MulAut P) (A B : V ≃ₗ[ℂ] V)
    (hA : ∀ p v, A (ρ p v) = ρ (α p) (A v))
    (hB : ∀ p v, B (ρ p v) = ρ (α p) (B v))
    (n : ℕ) (hAn : A ^ n = 1) (hBn : B ^ n = 1)
    (hdetA : LinearEquiv.det A = 1) (hdetB : LinearEquiv.det B = 1)
    (hcop : Nat.Coprime n (Module.finrank ℂ V)) : A = B := by
  have he := generator_equivariant_of_det_coprime ρ ρ (LinearEquiv.refl ℂ V)
    (fun _ _ => rfl) α A B hA hB n hAn hBn (hdetA.trans hdetB.symm) hcop
  ext v
  exact he v

/-- Existence and uniqueness on the original carrier from an arbitrary
initial implementer. This proves independence of every root choice. -/
theorem normalized_generator_existsUnique (ρ : Representation ℂ P V) [IsIrreducible ρ]
    (α : MulAut P) (A : V ≃ₗ[ℂ] V)
    (hA : ∀ p v, A (ρ p v) = ρ (α p) (A v))
    (n : ℕ) (hn : 0 < n) (hα : α ^ n = 1)
    (hcop : Nat.Coprime n (Module.finrank ℂ V)) :
    ∃! B : V ≃ₗ[ℂ] V, B ^ n = 1 ∧ LinearEquiv.det B = 1 ∧
      ∀ p v, B (ρ p v) = ρ (α p) (B v) := by
  obtain ⟨B, hBn, hdB, hB⟩ := normalized_generator_exists ρ α A hA n hn hα hcop
  refine ⟨B, ⟨hBn, hdB, hB⟩, ?_⟩
  intro C hC
  exact normalized_generator_unique ρ α C B hC.2.2 hB n hC.1 hBn hC.2.1 hdB hcop

end Implementers

section ActualCharacter
variable {P V : Type*} [Group P] [Finite P]
  [AddCommGroup V] [Module ℂ V]

/-- An automorphism that acts through an actual automorphism of H and
preserves its prescribed central character supplies an implementer. Its
existence follows from the literal common trace profile, not from a chosen
cyclic extension or a presumed target equivalence. -/
theorem implementer_of_actual_profile
    (H : Subgroup P) (θ : H →* ℂˣ)
    (ρ : Representation ℂ P V) [IsIrreducible ρ]
    (hρ : ∀ h : H, ρ h = (θ h : ℂ) • LinearMap.id)
    (hz : ∀ p : P, p ∉ H → Representation.character ρ p = 0)
    (α : MulAut P) (ζ : MulAut H)
    (hαH : ∀ h : H, α (h : P) = (ζ h : P))
    (hθ : ∀ h : H, θ (ζ h) = θ h) :
    ∃ A : V ≃ₗ[ℂ] V, ∀ p v, A (ρ p v) = ρ (α p) (A v) := by
  let σ := ρ.comp α.toMonoidHom
  let : IsIrreducible σ :=
    (QuotientRepresentation.irreducible_comp_iff α.toMonoidHom α.surjective ρ).mpr
      inferInstance
  have hσ : ∀ h : H, σ h = (θ h : ℂ) • LinearMap.id := by
    intro h
    change ρ (α (h : P)) = _
    rw [hαH, hρ, hθ]
  have hzσ : ∀ p : P, p ∉ H → Representation.character σ p = 0 := by
    intro p hp
    change Representation.character ρ (α p) = 0
    apply hz
    intro ha
    obtain ⟨h, hh⟩ := ζ.surjective ⟨α p, ha⟩
    have he : α (h : P) = α p := (hαH h).trans (congrArg Subtype.val hh)
    exact hp ((α.injective he) ▸ h.property)
  obtain ⟨U⟩ := equiv_of_common_profile H θ ρ σ hρ hσ hz hzσ
  exact ⟨U.toLinearEquiv, U.toIntertwiningMap.isIntertwining⟩

/-- Exact cyclic canonical-generator existence from actual finite
central-character and trace data. Finite dimensionality is derived. -/
theorem canonical_generator_of_actual_profile
    (H : Subgroup P) (θ : H →* ℂˣ)
    (ρ : Representation ℂ P V) [IsIrreducible ρ]
    (hρ : ∀ h : H, ρ h = (θ h : ℂ) • LinearMap.id)
    (hz : ∀ p : P, p ∉ H → Representation.character ρ p = 0)
    (α : MulAut P) (ζ : MulAut H)
    (hαH : ∀ h : H, α (h : P) = (ζ h : P))
    (hθ : ∀ h : H, θ (ζ h) = θ h)
    (n : ℕ) (hn : 0 < n) (hα : α ^ n = 1)
    (hcop : Nat.Coprime n (Module.finrank ℂ V)) :
    ∃! A : V ≃ₗ[ℂ] V, A ^ n = 1 ∧ LinearEquiv.det A = 1 ∧
      ∀ p v, A (ρ p v) = ρ (α p) (A v) := by
  let : FiniteDimensional ℂ V := FiniteRepresentation.finiteDimensional ρ
  obtain ⟨A, hA⟩ := implementer_of_actual_profile H θ ρ hρ hz α ζ hαH hθ
  exact normalized_generator_existsUnique ρ α A hA n hn hα hcop

variable {k X : Type*} [Field k] [AddCommGroup X] [Module k X]

/-- The trace condition itself follows from the original nondegenerate
commutator form. No implementer or action normalization is assumed. -/
theorem canonical_generator_of_actual_form
    (H : Subgroup P) [H.Normal] (θ : H →* ℂˣ)
    (τ : (P ⧸ H) ≃* Multiplicative X)
    (B : X →ₗ[k] X →ₗ[k] k) (ψ : AddChar k ℂˣ) (hψ : ψ ≠ 1)
    (hnd : ∀ v : X, (∀ u : X, B u v = 0) → v = 0)
    (hform : ∀ p q : P, ψ (B (HeisenbergCharacterProfile111.coordinate H τ p)
      (HeisenbergCharacterProfile111.coordinate H τ q)) =
      HeisenbergCharacterProfile111.characterCommutator H τ θ p q)
    (ρ : Representation ℂ P V) [IsIrreducible ρ]
    (hρ : ∀ h : H, ρ h = (θ h : ℂ) • LinearMap.id)
    (α : MulAut P) (ζ : MulAut H)
    (hαH : ∀ h : H, α (h : P) = (ζ h : P))
    (hθ : ∀ h : H, θ (ζ h) = θ h)
    (n : ℕ) (hn : 0 < n) (hα : α ^ n = 1)
    (hcop : Nat.Coprime n (Module.finrank ℂ V)) :
    ∃! A : V ≃ₗ[ℂ] V, A ^ n = 1 ∧ LinearEquiv.det A = 1 ∧
      ∀ p v, A (ρ p v) = ρ (α p) (A v) :=
  canonical_generator_of_actual_profile H θ ρ hρ
    (HeisenbergCharacterProfile111.trace_support_of_nondegenerate_form
      H τ θ B ψ hψ hnd hform ρ hρ) α ζ hαH hθ n hn hα hcop

end ActualCharacter

section CyclicActions
variable {C P V : Type*} [Group C] [Group P]
  [AddCommGroup V] [Module ℂ V]

/-- The corrected generator defines an honest action of the original cyclic
group C. Its relation is checked against the actual order of c. -/
def cyclicAction (c : C) (hgen : ∀ g : C, ∃ m : ℕ, g = c ^ m)
    (A : V ≃ₗ[ℂ] V) (hA : A ^ orderOf c = 1) : C →* (V ≃ₗ[ℂ] V) :=
  monoidHomOfForallMemZpowers
    (fun g => by
      obtain ⟨m, hm⟩ := hgen g
      exact Subgroup.mem_zpowers_iff.mpr ⟨(m : ℤ), by simpa using hm.symm⟩)
    (orderOf_dvd_of_pow_eq_one hA)

@[simp] theorem cyclicAction_generator (c : C)
    (hgen : ∀ g : C, ∃ m : ℕ, g = c ^ m)
    (A : V ≃ₗ[ℂ] V) (hA : A ^ orderOf c = 1) :
    cyclicAction c hgen A hA c = A := by
  exact monoidHomOfForallMemZpowers_apply_gen _ _

variable [FiniteDimensional ℂ V]

/-- The cyclic canonical extension exists as a homomorphism on the original
group C, rather than only as a relation for one generator. -/
theorem canonical_action_of_implementer
    (ρ : Representation ℂ P V) [IsIrreducible ρ]
    (Ω : C →* MulAut P) (c : C) (hgen : ∀ g : C, ∃ m : ℕ, g = c ^ m)
    (hn : 0 < orderOf c) (hcop : Nat.Coprime (orderOf c) (Module.finrank ℂ V))
    (A : V ≃ₗ[ℂ] V) (hA : ∀ p v, A (ρ p v) = ρ (Ω c p) (A v)) :
    ∃! Λ : C →* (V ≃ₗ[ℂ] V),
      (∀ g, LinearEquiv.det (Λ g) = 1) ∧
      (∀ g p v, Λ g (ρ p v) = ρ (Ω g p) (Λ g v)) := by
  have hΩ : (Ω c) ^ orderOf c = 1 := by rw [← map_pow, pow_orderOf_eq_one, map_one]
  obtain ⟨B, hBn, hdB, hB⟩ := normalized_generator_exists ρ (Ω c) A hA
    (orderOf c) hn hΩ hcop
  let Λ := cyclicAction c hgen B hBn
  have hΛc : Λ c = B := cyclicAction_generator c hgen B hBn
  have hdet : ∀ g, LinearEquiv.det (Λ g) = 1 := by
    intro g
    obtain ⟨m, rfl⟩ := hgen g
    rw [map_pow, map_pow, hΛc, hdB, one_pow]
  have himp : ∀ g p v, Λ g (ρ p v) = ρ (Ω g p) (Λ g v) := by
    intro g p v
    obtain ⟨m, rfl⟩ := hgen g
    rw [map_pow, map_pow, hΛc]
    exact implements_pow ρ (Ω c) B hB m p v
  refine ⟨Λ, ⟨hdet, himp⟩, ?_⟩
  intro Λ' hΛ'
  have hΛ'n : Λ' c ^ orderOf c = 1 := by rw [← map_pow, pow_orderOf_eq_one, map_one]
  have he : Λ' c = Λ c := (normalized_generator_unique ρ (Ω c) (Λ' c) B
    (hΛ'.2 c) hB (orderOf c) hΛ'n hBn (hΛ'.1 c) hdB hcop).trans hΛc.symm
  ext g
  obtain ⟨m, rfl⟩ := hgen g
  rw [map_pow, map_pow, he]

end CyclicActions

section CanonicalActualAction
variable {C P V : Type*} [Group C] [Group P] [Finite P]
  [AddCommGroup V] [Module ℂ V]

/-- A theta-preserving actual cyclic action on the finite group supplies
its unique determinant-one action on the original representation carrier. -/
theorem canonical_action_of_actual_profile
    (H : Subgroup P) (θ : H →* ℂˣ)
    (ρ : Representation ℂ P V) [IsIrreducible ρ]
    (hρ : ∀ h : H, ρ h = (θ h : ℂ) • LinearMap.id)
    (hz : ∀ p : P, p ∉ H → Representation.character ρ p = 0)
    (Ω : C →* MulAut P) (c : C) (hgen : ∀ g : C, ∃ m : ℕ, g = c ^ m)
    (ζ : MulAut H) (hΩH : ∀ h : H, Ω c (h : P) = (ζ h : P))
    (hθ : ∀ h : H, θ (ζ h) = θ h)
    (hn : 0 < orderOf c) (hcop : Nat.Coprime (orderOf c) (Module.finrank ℂ V)) :
    ∃! Λ : C →* (V ≃ₗ[ℂ] V),
      (∀ g, LinearEquiv.det (Λ g) = 1) ∧
      (∀ g p v, Λ g (ρ p v) = ρ (Ω g p) (Λ g v)) := by
  let : FiniteDimensional ℂ V := FiniteRepresentation.finiteDimensional ρ
  obtain ⟨A, hA⟩ := implementer_of_actual_profile H θ ρ hρ hz (Ω c) ζ hΩH hθ
  exact canonical_action_of_implementer ρ Ω c hgen hn hcop A hA

variable {W : Type*} [AddCommGroup W] [Module ℂ W]

/-- The original common-profile bridge becomes cyclic equivariant for the
newly constructed canonical actions. Neither action nor a target bridge is
an input. This is a finite comparison, not an identification with an
arithmetic beta-extension whose normalization has not been checked. -/
theorem canonical_equivariant_bridge_of_actual_profile
    (H : Subgroup P) (θ : H →* ℂˣ)
    (ρ : Representation ℂ P V) (σ : Representation ℂ P W)
    [IsIrreducible ρ] [IsIrreducible σ]
    (hρ : ∀ h : H, ρ h = (θ h : ℂ) • LinearMap.id)
    (hσ : ∀ h : H, σ h = (θ h : ℂ) • LinearMap.id)
    (hzρ : ∀ p : P, p ∉ H → Representation.character ρ p = 0)
    (hzσ : ∀ p : P, p ∉ H → Representation.character σ p = 0)
    (Ω : C →* MulAut P) (c : C) (hgen : ∀ g : C, ∃ m : ℕ, g = c ^ m)
    (ζ : MulAut H) (hΩH : ∀ h : H, Ω c (h : P) = (ζ h : P))
    (hθ : ∀ h : H, θ (ζ h) = θ h)
    (hn : 0 < orderOf c) (hcop : Nat.Coprime (orderOf c) (Module.finrank ℂ V)) :
    ∃ (Λρ : C →* (V ≃ₗ[ℂ] V)) (Λσ : C →* (W ≃ₗ[ℂ] W))
      (U : Representation.Equiv ρ σ),
      (∀ g, LinearEquiv.det (Λρ g) = 1) ∧
      (∀ g, LinearEquiv.det (Λσ g) = 1) ∧
      (∀ g p v, Λρ g (ρ p v) = ρ (Ω g p) (Λρ g v)) ∧
      (∀ g p w, Λσ g (σ p w) = σ (Ω g p) (Λσ g w)) ∧
      (∀ g v, U (Λρ g v) = Λσ g (U v)) := by
  let : FiniteDimensional ℂ V := FiniteRepresentation.finiteDimensional ρ
  let : FiniteDimensional ℂ W := FiniteRepresentation.finiteDimensional σ
  obtain ⟨U⟩ := equiv_of_common_profile H θ ρ σ hρ hσ hzρ hzσ
  have hdim : Module.finrank ℂ V = Module.finrank ℂ W := U.toLinearEquiv.finrank_eq
  obtain ⟨Λρ, hΛρ, _⟩ := canonical_action_of_actual_profile H θ ρ hρ hzρ Ω c hgen ζ hΩH
    hθ hn hcop
  obtain ⟨Λσ, hΛσ, _⟩ := canonical_action_of_actual_profile H θ σ hσ hzσ Ω c hgen ζ hΩH
    hθ hn (hdim ▸ hcop)
  refine ⟨Λρ, Λσ, U, hΛρ.1, hΛσ.1, hΛρ.2, hΛσ.2, ?_⟩
  apply cyclic_equivariant_of_generator Λρ Λσ c hgen U.toLinearEquiv
  apply generator_equivariant_of_det_coprime ρ σ U.toLinearEquiv
    U.toIntertwiningMap.isIntertwining (Ω c) (Λρ c) (Λσ c) (hΛρ.2 c) (hΛσ.2 c)
    (orderOf c)
  · rw [← map_pow, pow_orderOf_eq_one, map_one]
  · rw [← map_pow, pow_orderOf_eq_one, map_one]
  · exact (hΛρ.1 c).trans (hΛσ.1 c).symm
  · exact hcop

end CanonicalActualAction

end PaperXI.CyclicNormalization113
