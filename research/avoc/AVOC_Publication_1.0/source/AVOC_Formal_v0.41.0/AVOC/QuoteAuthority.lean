import AVOC.LazyStagedControl
import Mathlib.Tactic.Linarith

namespace Komorebi.AVOC.Affine.QuoteAuthority

open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Terminal

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
abbrev F := ZMod 5

/-- Exact natural-number interval used for setup/resource costs. -/
structure NatBand where
  lower : Nat
  upper : Nat
  ordered : lower ≤ upper
  deriving Repr

/-- Exact rational interval. -/
structure RatBand where
  lower : ℚ
  upper : ℚ
  ordered : lower ≤ upper
  deriving Repr

/-- Probability interval, with the probability axioms part of the object. -/
structure ProbabilityBand extends RatBand where
  nonneg : 0 ≤ lower
  le_one : upper ≤ 1
  deriving Repr

namespace NatBand

def Contains (b : NatBand) (x : Nat) : Prop := b.lower ≤ x ∧ x ≤ b.upper

def width (b : NatBand) : ℚ := (b.upper : ℚ) - (b.lower : ℚ)

def singleton (x : Nat) : NatBand := ⟨x,x,le_rfl⟩

@[simp] theorem width_nonneg (b : NatBand) : 0 ≤ b.width := by
  unfold width
  exact sub_nonneg.mpr (by exact_mod_cast b.ordered)

@[simp] theorem singleton_width (x : Nat) : (singleton x).width = 0 := by
  simp [singleton,width]

@[simp] theorem singleton_contains_iff (x y : Nat) : (singleton x).Contains y ↔ y = x := by
  constructor
  · intro h; exact Nat.le_antisymm h.2 h.1
  · intro h; subst y; exact ⟨le_rfl,le_rfl⟩

theorem contains_upper_sub {b : NatBand} {x : Nat} (h : b.Contains x) :
    |(x : ℚ) - (b.upper : ℚ)| ≤ b.width := by
  have hlo : (b.lower : ℚ) ≤ (x : ℚ) := by exact_mod_cast h.1
  have hhi : (x : ℚ) ≤ (b.upper : ℚ) := by exact_mod_cast h.2
  rw [abs_of_nonpos (sub_nonpos.mpr hhi)]
  unfold width
  linarith

theorem contains_lower_sub {b : NatBand} {x : Nat} (h : b.Contains x) :
    |(x : ℚ) - (b.lower : ℚ)| ≤ b.width := by
  have hlo : (b.lower : ℚ) ≤ (x : ℚ) := by exact_mod_cast h.1
  have hhi : (x : ℚ) ≤ (b.upper : ℚ) := by exact_mod_cast h.2
  rw [abs_of_nonneg (sub_nonneg.mpr hlo)]
  unfold width
  linarith

end NatBand

namespace RatBand

def Contains (b : RatBand) (x : ℚ) : Prop := b.lower ≤ x ∧ x ≤ b.upper

def width (b : RatBand) : ℚ := b.upper - b.lower

def singleton (x : ℚ) : RatBand := ⟨x,x,le_rfl⟩

@[simp] theorem width_nonneg (b : RatBand) : 0 ≤ b.width := sub_nonneg.mpr b.ordered

@[simp] theorem singleton_width (x : ℚ) : (singleton x).width = 0 := by simp [singleton,width]

@[simp] theorem singleton_contains_iff (x y : ℚ) : (singleton x).Contains y ↔ y = x := by
  constructor
  · intro h; exact le_antisymm h.2 h.1
  · intro h; subst y; exact ⟨le_rfl,le_rfl⟩

theorem contains_lower_sub {b : RatBand} {x : ℚ} (h : b.Contains x) :
    |x - b.lower| ≤ b.width := by
  rw [abs_of_nonneg (sub_nonneg.mpr h.1)]
  unfold width
  linarith [h.2]

theorem contains_upper_sub {b : RatBand} {x : ℚ} (h : b.Contains x) :
    |x - b.upper| ≤ b.width := by
  rw [abs_of_nonpos (sub_nonpos.mpr h.2)]
  unfold width
  linarith [h.1]

end RatBand

namespace ProbabilityBand

def Contains (b : ProbabilityBand) (x : ℚ) : Prop := b.toRatBand.Contains x

def width (b : ProbabilityBand) : ℚ := b.upper - b.lower

def singleton (x : ℚ) (hn : 0 ≤ x) (hu : x ≤ 1) : ProbabilityBand :=
  ⟨⟨x,x,le_rfl⟩,hn,hu⟩

@[simp] theorem lower_le_one (b : ProbabilityBand) : b.lower ≤ 1 := b.ordered.trans b.le_one
@[simp] theorem upper_nonneg (b : ProbabilityBand) : 0 ≤ b.upper := b.nonneg.trans b.ordered
@[simp] theorem width_nonneg (b : ProbabilityBand) : 0 ≤ b.width := sub_nonneg.mpr b.ordered

theorem contains_bounds {b : ProbabilityBand} {x : ℚ} (h : b.Contains x) :
    0 ≤ x ∧ x ≤ 1 := ⟨b.nonneg.trans h.1, h.2.trans b.le_one⟩

theorem contains_lower_sub {b : ProbabilityBand} {x : ℚ} (h : b.Contains x) :
    |x - b.lower| ≤ b.width := RatBand.contains_lower_sub h

theorem contains_upper_sub {b : ProbabilityBand} {x : ℚ} (h : b.Contains x) :
    |x - b.upper| ≤ b.width := RatBand.contains_upper_sub h

end ProbabilityBand

/-- The exact protected identity to which quote evidence is bound. -/
structure Identity (n m : Nat) where
  kind : Kind
  source : Signature F n m
  calls : Nat
  costModel : String
  provider : String
  checker : String
  environment : String
  schema : String

noncomputable instance identityDecEq (n m : Nat) : DecidableEq (Identity n m) := Classical.decEq _

/-- Untrusted wire-level quote: exact identity plus certified ranges. -/
structure RawQuote (n m : Nat) where
  identity : Identity n m
  setup : NatBand
  gross : RatBand
  probability : ProbabilityBand

noncomputable instance rawQuoteDecEq (n m : Nat) : DecidableEq (RawQuote n m) := Classical.decEq _

/-- Protected authority.  Bounds are data, while nonnegative gross is a proved contract. -/
structure Authority (n m : Nat) (k : Kind) where
  approved : RawQuote n m
  kind_eq : approved.identity.kind = k
  gross_nonneg : 0 ≤ approved.gross.lower

structure CertifiedQuote {n m : Nat} {k : Kind} (a : Authority n m k) where
  submitted : RawQuote n m
  exact : submitted = a.approved

noncomputable def validate {n m : Nat} {k : Kind} (a : Authority n m k)
    (q : RawQuote n m) : Option (CertifiedQuote a) :=
  if h : q = a.approved then some ⟨q,h⟩ else none

@[simp] theorem validate_some_iff {n m : Nat} {k : Kind} (a : Authority n m k)
    (q : RawQuote n m) :
    (∃ c, validate a q = some c) ↔ q = a.approved := by
  unfold validate
  split <;> simp_all

@[simp] theorem changed_quote_rejected {n m : Nat} {k : Kind}
    (a : Authority n m k) (q : RawQuote n m) (h : q ≠ a.approved) :
    validate a q = none := by simp [validate,h]

@[simp] theorem identity_mismatch_rejected {n m : Nat} {k : Kind}
    (a : Authority n m k) (q : RawQuote n m)
    (h : q.identity ≠ a.approved.identity) : validate a q = none := by
  apply changed_quote_rejected a q
  intro he
  exact h (congrArg RawQuote.identity he)

@[simp] theorem setup_mismatch_rejected {n m : Nat} {k : Kind}
    (a : Authority n m k) (q : RawQuote n m)
    (h : q.setup ≠ a.approved.setup) : validate a q = none := by
  apply changed_quote_rejected a q
  intro he
  exact h (congrArg RawQuote.setup he)

@[simp] theorem gross_mismatch_rejected {n m : Nat} {k : Kind}
    (a : Authority n m k) (q : RawQuote n m)
    (h : q.gross ≠ a.approved.gross) : validate a q = none := by
  apply changed_quote_rejected a q
  intro he
  exact h (congrArg RawQuote.gross he)

@[simp] theorem probability_mismatch_rejected {n m : Nat} {k : Kind}
    (a : Authority n m k) (q : RawQuote n m)
    (h : q.probability ≠ a.approved.probability) : validate a q = none := by
  apply changed_quote_rejected a q
  intro he
  exact h (congrArg RawQuote.probability he)

/-- Robust quote model: source/workload identity plus protected warm/cold evidence. -/
structure Model (n m : Nat) where
  source : DenseProgram F n m
  calls : Nat
  warm : Authority n m .warm
  cold : Authority n m .cold
  warm_source : warm.approved.identity.source = coefficients source
  cold_source : cold.approved.identity.source = coefficients source
  warm_calls : warm.approved.identity.calls = calls
  cold_calls : cold.approved.identity.calls = calls

variable {n m : Nat}

def rawQuote : (md : Model n m) → (k : Kind) → RawQuote n m
  | md, .warm => md.warm.approved
  | md, .cold => md.cold.approved

def setupBand (md : Model n m) (k : Kind) : NatBand := (rawQuote md k).setup
def grossBand (md : Model n m) (k : Kind) : RatBand := (rawQuote md k).gross
def probBand (md : Model n m) (k : Kind) : ProbabilityBand := (rawQuote md k).probability

def quoteIdentity (md : Model n m) (k : Kind) : Identity n m := (rawQuote md k).identity

/-- Conservative exact model: reserve upper setup, credit lower gross, use lower success. -/
def nominalQuote : (md : Model n m) → (k : Kind) → LazyStaged.Quote k
  | md, .warm =>
      { fee := md.warm.approved.setup.upper,
        gross := md.warm.approved.gross.lower,
        gross_nonneg := md.warm.gross_nonneg,
        successProb := md.warm.approved.probability.lower,
        prob_nonneg := md.warm.approved.probability.nonneg,
        prob_le_one := md.warm.approved.probability.lower_le_one }
  | md, .cold =>
      { fee := md.cold.approved.setup.upper,
        gross := md.cold.approved.gross.lower,
        gross_nonneg := md.cold.gross_nonneg,
        successProb := md.cold.approved.probability.lower,
        prob_nonneg := md.cold.approved.probability.nonneg,
        prob_le_one := md.cold.approved.probability.lower_le_one }

@[simp] theorem nominalQuote_warm_fee (md : Model n m) :
    (nominalQuote md .warm).fee = md.warm.approved.setup.upper := rfl
@[simp] theorem nominalQuote_cold_fee (md : Model n m) :
    (nominalQuote md .cold).fee = md.cold.approved.setup.upper := rfl
@[simp] theorem nominalQuote_warm_gross (md : Model n m) :
    (nominalQuote md .warm).gross = md.warm.approved.gross.lower := rfl
@[simp] theorem nominalQuote_cold_gross (md : Model n m) :
    (nominalQuote md .cold).gross = md.cold.approved.gross.lower := rfl
@[simp] theorem nominalQuote_warm_probability (md : Model n m) :
    (nominalQuote md .warm).successProb = md.warm.approved.probability.lower := rfl
@[simp] theorem nominalQuote_cold_probability (md : Model n m) :
    (nominalQuote md .cold).successProb = md.cold.approved.probability.lower := rfl

def nominal (md : Model n m) : LazyStaged.Model n m where
  source := md.source
  calls := md.calls
  warm := nominalQuote md .warm
  cold := nominalQuote md .cold

/-- One exact but unknown realization consistent with the certified intervals. -/
structure ExactQuote (md : Model n m) (k : Kind) where
  setup : Nat
  gross : ℚ
  probability : ℚ
  setup_mem : (setupBand md k).Contains setup
  gross_mem : (grossBand md k).Contains gross
  probability_mem : (probBand md k).Contains probability

structure Realization (md : Model n m) where
  warm : ExactQuote md .warm
  cold : ExactQuote md .cold

def exactQuote (r : Realization md) : (k : Kind) → ExactQuote md k
  | .warm => r.warm
  | .cold => r.cold

/-- Deterministic fields refined by a returned artifact. Probability evidence is retained. -/
structure RefinedQuote (md : Model n m) (k : Kind) where
  setup : Nat
  gross : ℚ
  setup_mem : (setupBand md k).Contains setup
  gross_mem : (grossBand md k).Contains gross

def RefinedQuote.setupBand (q : RefinedQuote md k) : NatBand := NatBand.singleton q.setup
def RefinedQuote.grossBand (q : RefinedQuote md k) : RatBand := RatBand.singleton q.gross
def RefinedQuote.probabilityBand (_q : RefinedQuote md k) : ProbabilityBand := probBand md k

@[simp] theorem refined_setup_singleton (q : RefinedQuote md k) :
    q.setupBand.Contains x ↔ x = q.setup := NatBand.singleton_contains_iff _ _

@[simp] theorem refined_gross_singleton (q : RefinedQuote md k) :
    q.grossBand.Contains x ↔ x = q.gross := RatBand.singleton_contains_iff _ _

end Komorebi.AVOC.Affine.QuoteAuthority
