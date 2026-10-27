import RealizationBoundaries.PairedPrimes
import Mathlib.Computability.RE

/-!
# Native computability of the actual prime enumeration

The production `primeAt` uses Mathlib's mathematical nth-prime function. The
proof below derives a primitive recursive prime test and prime-counting
function, then identifies terminating unbounded search with that exact nth
function. No arbitrary function is declared computable merely because it is a
Lean definition.
-/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- Trial division is a primitive recursive relation. -/
theorem primrec_nat_dvd : PrimrecRel ((· ∣ ·) : ℕ → ℕ → Prop) := by
  exact (Primrec.eq.comp (Primrec.nat_mod.comp Primrec.snd Primrec.fst)
    (Primrec.const 0)).of_eq fun p => Nat.dvd_iff_mod_eq_zero.symm

/-- Primality is decided by the bounded divisor test from `Nat.prime_def_lt`. -/
theorem primrec_prime_predicate : PrimrecPred Nat.Prime := by
  have hdiv : PrimrecRel (fun m n : ℕ => m ∣ n → m = 1) :=
    (primrec_nat_dvd.not.or (Primrec.eq.comp Primrec.fst (Primrec.const 1))).of_eq
      (fun _ => by simp only [or_iff_not_imp_left, not_not])
  have hforall : PrimrecPred (fun n : ℕ => ∀ m < n, m ∣ n → m = 1) :=
    hdiv.forall_lt.comp Primrec.id Primrec.id
  exact ((Primrec.nat_le.comp (Primrec.const 2) Primrec.id).and hforall).of_eq
    fun _ => Nat.prime_def_lt.symm

/-- The Boolean prime test itself is primitive recursive. -/
theorem primrec_prime_decide : Primrec (fun n : ℕ => decide n.Prime) :=
  primrec_prime_predicate.decide

/-- Counting primes below a bound is primitive recursive, by filtering a finite
range with the proved primitive recursive primality test. -/
theorem primrec_prime_count : Primrec (Nat.count Nat.Prime) := by
  refine (Primrec.list_length.comp
    ((Primrec.listFilter primrec_prime_predicate).comp Primrec.list_range)).of_eq ?_
  intro n
  simp only [Nat.count, List.countP_eq_length_filter]

/-- The search relation means exactly: prime `p` has zero-based prime index `n`. -/
def primeIndexRelation (n p : ℕ) : Prop := p.Prime ∧ Nat.count Nat.Prime p = n

instance primeIndexRelation_decidable : DecidableRel primeIndexRelation := by
  unfold primeIndexRelation
  infer_instance

theorem primeIndexRelation_primrec : PrimrecRel primeIndexRelation := by
  exact ((primrec_prime_predicate.comp Primrec.snd).and
    (Primrec.eq.comp (primrec_prime_count.comp Primrec.snd) Primrec.fst))

theorem primeIndexRelation_total (n : ℕ) : ∃ p, primeIndexRelation n p :=
  ⟨Nat.nth Nat.Prime n,
    Nat.nth_mem_of_infinite Nat.infinite_setOfPred_prime n,
    Nat.count_nth_of_infinite Nat.infinite_setOfPred_prime n⟩

/-- The existing mathematical nth-prime enumeration is native computable. The
unbounded search terminates by infinitude of primes and is identified using
`Nat.nth_count`, so this applies to the actual production enumeration. -/
theorem computable_nth_prime : Computable (Nat.nth Nat.Prime) := by
  refine (Computable.find primeIndexRelation_primrec.computablePred
    primeIndexRelation_total).of_eq ?_
  intro n
  have ht := Nat.find_spec (primeIndexRelation_total n)
  have he := Nat.nth_count ht.1
  rw [ht.2] at he
  exact he.symm

/-- Native computability of the literal natural value of `primeAt`. -/
theorem computable_primeAt_value : Computable (fun n : ℕ => (primeAt n).val) :=
  computable_nth_prime

end RealizationBoundaries
