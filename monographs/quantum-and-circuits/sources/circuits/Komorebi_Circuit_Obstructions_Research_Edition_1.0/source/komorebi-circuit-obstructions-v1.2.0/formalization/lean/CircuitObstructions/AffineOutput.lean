import CircuitObstructions.SafeDegree

/-!
# Zero-cost affine output changes and the optimized complete-cover bound

An affine function is any function with a `DegreeLE 1` certificate. Every such
function is implemented by NOT/CNOT gates on the restored boundary. The proof
constructs a legal circuit and proves that its Toffoli count is zero.
-/
namespace CircuitObstructions

theorem restores_append {X W : Type} [DecidableEq W] (e : Boundary X W)
    (c d : Circuit W) (f g : X → Bool)
    (hc : Restores e c f) (hd : Restores e d g) :
    Restores e (c ++ d) (fun x => Bool.xor (f x) (g x)) := by
  intro x b
  rw [run_append, hc, hd]
  simp only [Bool.xor_assoc]

theorem canonical_target_not (n a : Nat) (x : Fin n → Bool) (b : Bool) :
    (Gate.not (canonicalBoundary n a).target).eval ((canonicalBoundary n a).encode x b) =
      (canonicalBoundary n a).encode x (Bool.xor b true) := by
  funext i
  cases i with
  | inl j => simp [Gate.eval, write, canonicalBoundary]
  | inr j =>
      cases j with
      | inl j => simp [Gate.eval, write, canonicalBoundary]
      | inr j => simp [Gate.eval, write, canonicalBoundary]

def inputToTarget (n a : Nat) (i : Fin n) : Gate (CanonicalWire n a) :=
  .cnot (.inl i) (canonicalBoundary n a).target (by intro h; cases h)

theorem canonical_input_to_target (n a : Nat) (i : Fin n) (x : Fin n → Bool) (b : Bool) :
    (inputToTarget n a i).eval ((canonicalBoundary n a).encode x b) =
      (canonicalBoundary n a).encode x (Bool.xor b (x i)) := by
  funext j
  cases j with
  | inl j => simp [inputToTarget, Gate.eval, write, canonicalBoundary]
  | inr j =>
      cases j with
      | inl j => simp [inputToTarget, Gate.eval, write, canonicalBoundary]
      | inr j => simp [inputToTarget, Gate.eval, write, canonicalBoundary]

theorem affine_restored_exists (n a : Nat) (g : BFun n) (hg : DegreeLE 1 g) :
    ∃ d : Circuit (CanonicalWire n a), toffoliCount d = 0 ∧
      Restores (canonicalBoundary n a) d g := by
  induction hg with
  | zero =>
      refine ⟨[], rfl, ?_⟩
      intro x b
      simp
  | monomial l hl =>
      cases l with
      | nil =>
          refine ⟨[.not (canonicalBoundary n a).target], rfl, ?_⟩
          intro x b
          exact canonical_target_not n a x b
      | cons i is =>
          have his : is = [] := by
            have hlen : is.length = 0 := by simp only [List.length_cons] at hl; omega
            cases is <;> simp_all
          subst is
          refine ⟨[inputToTarget n a i], rfl, ?_⟩
          intro x b
          simpa [bprod] using canonical_input_to_target n a i x b
  | add _ _ ihf ihg =>
      obtain ⟨c, hc0, hc⟩ := ihf
      obtain ⟨d, hd0, hd⟩ := ihg
      exact ⟨c ++ d, by rw [toffoliCount_append, hc0, hd0],
        restores_append (canonicalBoundary n a) c d _ _ hc hd⟩

def AffineSafeDegreeLE {n : Nat} (f : BFun n) (d : Nat) : Prop :=
  ∀ g : BFun n, DegreeLE 1 g → beta (fun x => Bool.xor (f x) (g x)) ≤ d

theorem betaStar_exists {n : Nat} (f : BFun n) :
    ∃ r, AffineSafeDegreeLE f r ∧ ∀ k, AffineSafeDegreeLE f k → r ≤ k := by
  apply exists_least_degree (AffineSafeDegreeLE f) n
  intro g _
  exact beta_le_inputs _

noncomputable def betaStar {n : Nat} (f : BFun n) : Nat :=
  Classical.choose (betaStar_exists f)

theorem betaStar_spec {n : Nat} (f : BFun n) : AffineSafeDegreeLE f (betaStar f) :=
  (Classical.choose_spec (betaStar_exists f)).1

theorem betaStar_le_of_bound {n d : Nat} {f : BFun n}
    (h : AffineSafeDegreeLE f d) : betaStar f ≤ d :=
  (Classical.choose_spec (betaStar_exists f)).2 d h

theorem betaStar_le_inputs {n : Nat} (f : BFun n) : betaStar f ≤ n := by
  apply betaStar_le_of_bound
  intro g _
  exact beta_le_inputs _

theorem beta_le_betaStar {n : Nat} (f : BFun n) : beta f ≤ betaStar f := by
  have h := betaStar_spec f (fun _ => false) DegreeLE.zero
  simpa using h

theorem betaStar_le_half_toffoliCount (n a : Nat)
    (c : Circuit (CanonicalWire n a)) (f : BFun n)
    (hR : Restores (canonicalBoundary n a) c f) :
    betaStar f ≤ (toffoliCount c + 1) / 2 + 1 := by
  apply betaStar_le_of_bound
  intro g hg
  obtain ⟨d, hd0, hd⟩ := affine_restored_exists n a g hg
  have h := beta_le_half_toffoliCount n a (c ++ d) _
    (restores_append (canonicalBoundary n a) c d f g hR hd)
  simpa only [toffoliCount_append, hd0, Nat.add_zero] using h

theorem betaStar_restoration_bound (n a : Nat)
    (c : Circuit (CanonicalWire n a)) (f : BFun n)
    (hR : Restores (canonicalBoundary n a) c f) :
    2 * betaStar f ≤ toffoliCount c + 3 := by
  have h := betaStar_le_half_toffoliCount n a c f hR
  omega

theorem toffoliCount_ge_two_betaStar_sub_three (n a : Nat)
    (c : Circuit (CanonicalWire n a)) (f : BFun n)
    (hR : Restores (canonicalBoundary n a) c f) :
    2 * betaStar f - 3 ≤ toffoliCount c := by
  have h := betaStar_restoration_bound n a c f hR
  omega

theorem canonical_restored_output_degree (n a : Nat)
    (c : Circuit (CanonicalWire n a)) (f : BFun n)
    (hR : Restores (canonicalBoundary n a) c f) :
    DegreeLE (toffoliCount c + 1) f := by
  have h := canonical_run_coordinate_degree n a c false (canonicalBoundary n a).target
  have heq : (fun x => run c ((canonicalBoundary n a).encode x false)
      (canonicalBoundary n a).target) = f := by
    funext x
    rw [hR x false, Boundary.target_eq]
    simp
  rw [heq] at h
  exact h

/-- Joint formal endpoint for the numerical and polynomial parts of C02. -/
theorem restored_degree_and_cover_bound (n a : Nat)
    (c : Circuit (CanonicalWire n a)) (f : BFun n)
    (hR : Restores (canonicalBoundary n a) c f) :
    DegreeLE (toffoliCount c + 1) f ∧
      2 * betaStar f ≤ toffoliCount c + 3 := by
  exact ⟨canonical_restored_output_degree n a c f hR,
    betaStar_restoration_bound n a c f hR⟩

end CircuitObstructions
