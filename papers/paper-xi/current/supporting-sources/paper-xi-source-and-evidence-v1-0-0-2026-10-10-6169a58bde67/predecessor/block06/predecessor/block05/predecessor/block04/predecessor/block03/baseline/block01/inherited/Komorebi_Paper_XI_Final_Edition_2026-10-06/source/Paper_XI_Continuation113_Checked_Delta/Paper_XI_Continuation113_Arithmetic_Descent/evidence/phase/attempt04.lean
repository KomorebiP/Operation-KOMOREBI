import PaperXI.GlobalHeisenbergBridge112
import Mathlib.Data.Int.GCD

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

end PaperXI.CyclicNormalization113
