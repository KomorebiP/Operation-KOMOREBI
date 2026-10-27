import ResidualLayer

/-! Exact identities with variable coefficients constrain the normalized error
on a faithful leading layer. Only the relation's reduction is frozen. -/
namespace Komorebi.StrongArtin.MovingSyzygyError
open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.ResidualLayer

variable {R k X W Z Wbar Zbar : Type*} [CommRing R] [Field k]
  [AddCommGroup W] [Module R W] [AddCommGroup Z] [Module R Z]
  [AddCommGroup Wbar] [Module k Wbar] [AddCommGroup Zbar] [Module k Zbar]

/-- An exact moving relation annihilates the residue of the normalized error. -/
theorem normalized_error_compatible
    (pi : R) (redW : Reduction pi W Wbar) (redZ : Reduction pi Z Zbar)
    (F : X → W) (B : X → W →ₗ[R] Z) (Bbar : Wbar →ₗ[k] Zbar)
    (x : X) (n : ℕ) (e : W)
    (hfaithful : FaithfulAt pi redZ n)
    (herror : (pi ^ n) • e = F x)
    (hidentity : B x (F x) = 0)
    (hcompare : ∀ w, redZ.map (B x w) = Bbar (redW.map w)) :
    Bbar (redW.map e) = 0 := by
  have hz : (pi ^ n) • B x e = 0 := by
    rw [← map_smul, herror, hidentity]
  rw [← hcompare e]
  exact hfaithful _ hz

/-- It suffices that the coefficients of the moving relation agree residually
with the coefficients at the base point. -/
theorem normalized_error_compatible_of_relation_congruence
    (pi : R) (redW : Reduction pi W Wbar) (redZ : Reduction pi Z Zbar)
    (F : X → W) (B : X → W →ₗ[R] Z) (Bbar : Wbar →ₗ[k] Zbar)
    (base x : X) (n : ℕ) (e : W)
    (hfaithful : FaithfulAt pi redZ n)
    (herror : (pi ^ n) • e = F x)
    (hidentity : B x (F x) = 0)
    (hbase : ∀ w, redZ.map (B base w) = Bbar (redW.map w))
    (hmove : ∀ w, PowDivisible pi 1 (B x w - B base w)) :
    Bbar (redW.map e) = 0 := by
  apply normalized_error_compatible pi redW redZ F B Bbar x n e
    hfaithful herror hidentity
  intro w
  rw [redZ.map_eq_of_difference_divisible (hmove w), hbase]

/-- Without normalizing, exact relations imply the expected compatibility one
filtration level higher. This statement needs no torsion cancellation. -/
theorem unnormalized_error_satisfies_next_order_relation
    (pi : R) (F : X → W) (B : X → W →ₗ[R] Z)
    (base x : X) (n : ℕ) (e : W)
    (herror : (pi ^ n) • e = F x)
    (hidentity : B x (F x) = 0)
    (hmove : PowDivisible pi 1 (B base e - B x e)) :
    PowDivisible pi (n + 1) (B base (F x)) := by
  obtain ⟨z, hz⟩ := hmove
  have hid : (pi ^ n) • B x e = 0 := by
    rw [← map_smul, herror, hidentity]
  refine ⟨z, ?_⟩
  calc
    (pi ^ (n + 1)) • z = (pi ^ n) • ((pi ^ 1) • z) := by
      rw [pow_one, pow_succ, mul_smul]
    _ = (pi ^ n) • (B base e - B x e) := by rw [hz]
    _ = B base (F x) := by rw [smul_sub, hid, sub_zero, ← map_smul, herror]

end Komorebi.StrongArtin.MovingSyzygyError
