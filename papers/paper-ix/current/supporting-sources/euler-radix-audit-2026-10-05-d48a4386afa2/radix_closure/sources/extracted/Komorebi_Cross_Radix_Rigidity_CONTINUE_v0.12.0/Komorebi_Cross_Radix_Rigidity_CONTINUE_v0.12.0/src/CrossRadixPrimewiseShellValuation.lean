import CrossRadixShellJetTransition
import Mathlib.Data.Nat.Factorization.Basic
import Mathlib.NumberTheory.Padics.PadicVal.Basic

noncomputable section

namespace KomorebiCrossRadix

/-- Prime-exponent form of shell transport on raw natural frequencies.
If `g = gcd(T, ξ)`, multiplication by a positive radix `m` sends the
`p`-exponent of the shell to truncated addition by the `p`-exponent of `m`. -/
theorem gcd_mul_factorization_truncated
    {T m ξ p : ℕ} (hT : 0 < T) (hm : 0 < m) :
    (Nat.gcd T (m * ξ)).factorization p =
      min (T.factorization p) ((Nat.gcd T ξ).factorization p + m.factorization p) := by
  by_cases hξ : ξ = 0
  · subst ξ
    simp
  · rw [Nat.factorization_gcd hT.ne' (mul_ne_zero hm.ne' hξ)]
    rw [Nat.factorization_mul hm.ne' hξ]
    rw [Nat.factorization_gcd hT.ne' hξ]
    simp only [Finsupp.inf_apply, Finsupp.add_apply]
    omega

/-- The same law in `padicValNat` notation for a prime `p`. -/
theorem gcd_mul_padicValNat_truncated
    {T m ξ p : ℕ} [Fact p.Prime]
    (hT : 0 < T) (hm : 0 < m) :
    padicValNat p (Nat.gcd T (m * ξ)) =
      min (padicValNat p T)
        (padicValNat p (Nat.gcd T ξ) + padicValNat p m) := by
  simpa only [Nat.factorization_def _ (Fact.out : p.Prime)] using
    (gcd_mul_factorization_truncated (T := T) (m := m) (ξ := ξ) (p := p) hT hm)

/-- Conductor-depth form: if a shell has prime depth `s` inside a period with
prime depth `a`, radix multiplication changes it by `s ↦ min(a,s+v_p(m))`. -/
theorem shell_prime_depth_transition
    {T m ξ p : ℕ} [Fact p.Prime]
    (hT : 0 < T) (hm : 0 < m) :
    let a := padicValNat p T
    let s := padicValNat p (Nat.gcd T ξ)
    padicValNat p (Nat.gcd T (m * ξ)) = min a (s + padicValNat p m) := by
  simpa using gcd_mul_padicValNat_truncated (T := T) (m := m) (ξ := ξ) (p := p) hT hm


/-- Taking a remainder modulo the period does not change its gcd with the period. -/
lemma gcd_mod_period (T x : ℕ) : Nat.gcd T (x % T) = Nat.gcd T x := by
  calc
    Nat.gcd T (x % T) = Nat.gcd (x % T) T := Nat.gcd_comm _ _
    _ = Nat.gcd T x := (Nat.gcd_rec T x).symm

/-- The raw natural radix action and its `ZMod T` frequency action have the same gcd shell. -/
lemma frequencyShell_natCast_mul_gcd
    {T : ℕ} [NeZero T] (m : ℕ) (ξ : ZMod T) :
    Nat.gcd T (((m : ZMod T) * ξ).val) = Nat.gcd T (m * ξ.val) := by
  rw [ZMod.val_mul, ZMod.val_natCast]
  calc
    Nat.gcd T ((m % T * ξ.val) % T) = Nat.gcd T (m % T * ξ.val) := gcd_mod_period T _
    _ = Nat.gcd T ((m % T * ξ.val) % T) := (gcd_mod_period T _).symm
    _ = Nat.gcd T ((m * ξ.val) % T) := by
      congr 1
      simp [Nat.mul_mod]
    _ = Nat.gcd T (m * ξ.val) := gcd_mod_period T _

/-- Primewise shell transport stated directly on the certified Fourier shell labels. -/
theorem frequencyShell_prime_depth_transition
    {T m p : ℕ} [NeZero T] [Fact p.Prime]
    (hT : 0 < T) (hm : 0 < m) (ξ : ZMod T) :
    padicValNat p (frequencyShellIdx hT ((m : ZMod T) * ξ)).1 =
      min (padicValNat p T)
        (padicValNat p (frequencyShellIdx hT ξ).1 + padicValNat p m) := by
  rw [frequencyShellIdx_val, frequencyShellIdx_val, frequencyShell_natCast_mul_gcd]
  exact gcd_mul_padicValNat_truncated hT hm

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.gcd_mul_factorization_truncated
#print axioms KomorebiCrossRadix.gcd_mul_padicValNat_truncated
#print axioms KomorebiCrossRadix.shell_prime_depth_transition
#print axioms KomorebiCrossRadix.frequencyShell_prime_depth_transition
