import KomorebiPadic.LinearObservability

/-! # Exact future-output quotient
This is the greatest silent invariant quotient of a fixed linear system. Its
universal property compares quotients of that system; it is not, by itself, a
minimum-DFA or a uniqueness theorem across arbitrary different realizations.
-/
namespace KomorebiPadic
namespace LinearObservability
variable {R V A : Type*} [CommRing R] [AddCommGroup V] [Module R V]
noncomputable section

abbrev State (M : System R V A) := V ⧸ unobservable M

def projection (M : System R V A) : V →ₗ[R] State M := (unobservable M).mkQ

theorem projection_surjective (M : System R V A) : Function.Surjective (projection M) :=
  (unobservable M).mkQ_surjective

def quotientTransition (M : System R V A) (d : A) : State M →ₗ[R] State M :=
  (unobservable M).mapQ (unobservable M) (M.dynamics.transition d)
    ((unobservable_silentInvariant M).2 d)

def quotientOutput (M : System R V A) : State M →ₗ[R] R :=
  (unobservable M).liftQ M.output (unobservable_le_ker M)

def quotientSystem (M : System R V A) : System R (State M) A where
  dynamics := ⟨projection M M.dynamics.initial, quotientTransition M⟩
  output := quotientOutput M

@[simp] theorem quotientTransition_projection (M : System R V A) (d : A) (x : V) :
    quotientTransition M d (projection M x) = projection M (M.dynamics.transition d x) := rfl

@[simp] theorem quotientOutput_projection (M : System R V A) (x : V) :
    quotientOutput M (projection M x) = M.output x := rfl

theorem run_projection (M : System R V A) (ds : List A) (x : V) :
    LinearReachability.run (quotientSystem M).dynamics ds (projection M x) =
      projection M (LinearReachability.run M.dynamics ds x) := by
  induction ds generalizing x with
  | nil => rfl
  | cons d ds ih => exact ih (M.dynamics.transition d x)

@[simp] theorem observation_projection (M : System R V A) (ds : List A) (x : V) :
    observation (quotientSystem M) ds (projection M x) = observation M ds x := by
  change quotientOutput M (wordMap (quotientSystem M) ds (projection M x)) = _
  rw [wordMap_apply, run_projection, quotientOutput_projection]
  simp only [observation, LinearMap.comp_apply, wordMap_apply]

/-- Quotient equality is exactly equality of every future output, including the empty word. -/
theorem projection_eq_iff (M : System R V A) (x y : V) :
    projection M x = projection M y ↔ ∀ ds : List A, observation M ds x = observation M ds y := by
  change (Submodule.Quotient.mk x : State M) = Submodule.Quotient.mk y ↔ _
  rw [Submodule.Quotient.eq, mem_unobservable]
  simp only [map_sub, sub_eq_zero]

/-- The quotient retains no two distinct states with identical future behavior. -/
theorem quotient_observable (M : System R V A) (x y : State M)
    (h : ∀ ds : List A, observation (quotientSystem M) ds x =
      observation (quotientSystem M) ds y) : x = y := by
  obtain ⟨v,rfl⟩ := projection_surjective M x
  obtain ⟨w,rfl⟩ := projection_surjective M y
  exact (projection_eq_iff M v w).mpr (fun ds => by simpa using h ds)

theorem quotient_unobservable_eq_bot (M : System R V A) :
    unobservable (quotientSystem M) = ⊥ := by
  apply le_antisymm _ bot_le
  intro x hx
  change x = 0
  apply quotient_observable M x 0
  intro ds
  rw [(mem_unobservable _ _).mp hx ds, map_zero]

/-- Finite comparison criterion for two source states, with a stated strict length bound. -/
theorem projection_eq_iff_finite_words [Finite V] (M : System R V A) {p b : ℕ}
    (hp : p.Prime) (hV : Nat.card V = p^b) (x y : V) :
    projection M x = projection M y ↔
      ∀ ds : List A, ds.length < b → observation M ds x = observation M ds y := by
  change (Submodule.Quotient.mk x : State M) = Submodule.Quotient.mk y ↔ _
  rw [Submodule.Quotient.eq, unobservable_iff_finite_words M hp hV]
  simp only [map_sub, sub_eq_zero]

/-- Every smaller silent kernel maps surjectively to the full behavior quotient. -/
def quotientFactor (M : System R V A) (U : Submodule R V) (hU : SilentInvariant M U) :
    (V ⧸ U) →ₗ[R] State M :=
  U.mapQ (unobservable M) LinearMap.id (by simpa using le_unobservable M U hU)

@[simp] theorem quotientFactor_projection (M : System R V A) (U : Submodule R V)
    (hU : SilentInvariant M U) (x : V) : quotientFactor M U hU (U.mkQ x) = projection M x := rfl

theorem quotientFactor_surjective (M : System R V A) (U : Submodule R V)
    (hU : SilentInvariant M U) : Function.Surjective (quotientFactor M U hU) := by
  intro y
  obtain ⟨x,rfl⟩ := projection_surjective M y
  exact ⟨U.mkQ x,rfl⟩

theorem quotientFactor_unique (M : System R V A) (U : Submodule R V)
    (hU : SilentInvariant M U) (f : (V ⧸ U) →ₗ[R] State M)
    (hf : ∀ x, f (U.mkQ x) = projection M x) : f = quotientFactor M U hU := by
  apply LinearMap.ext
  intro y
  obtain ⟨x,rfl⟩ := U.mkQ_surjective y
  exact hf x

/-- Exact first-isomorphism cardinality. It does not assume a free state module. -/
theorem quotient_card_mul (M : System R V A) :
    Nat.card (State M) * Nat.card (unobservable M) = Nat.card V :=
  by simpa only [Nat.mul_comm] using
    (Submodule.card_eq_card_quotient_mul_card (unobservable M)).symm

theorem quotient_card_le [Finite V] (M : System R V A) : Nat.card (State M) ≤ Nat.card V :=
  Nat.card_le_card_of_surjective (projection M) (projection_surjective M)

/-- Minimum cardinality among invariant silent-kernel quotients of this fixed system. -/
theorem quotient_card_le_silent_quotient [Finite V] (M : System R V A)
    (U : Submodule R V) (hU : SilentInvariant M U) :
    Nat.card (State M) ≤ Nat.card (V ⧸ U) := by
  classical
  let : Fintype V := Fintype.ofFinite V
  exact Nat.card_le_card_of_surjective (quotientFactor M U hU) (quotientFactor_surjective M U hU)

/-- Linear reachability survives the quotient. Reachability means span, not orbit enumeration. -/
theorem quotient_reachable (M : System R V A) (h : LinearReachability.reachable M.dynamics = ⊤) :
    LinearReachability.reachable (quotientSystem M).dynamics = ⊤ := by
  have he := LinearReachability.map_reachable M.dynamics (quotientSystem M).dynamics
    (projection M) rfl (fun _ _ => rfl)
  rw [h] at he
  simpa only [Submodule.map_top, projection, Submodule.range_mkQ] using he.symm

/-- A normalized seed forces the quotient output to be onto the whole coefficient ring. -/
theorem quotientOutput_surjective (M : System R V A) (h : M.output M.dynamics.initial = 1) :
    Function.Surjective (quotientOutput M) := by
  intro a
  refine ⟨projection M (a • M.dynamics.initial), ?_⟩
  simp only [quotientOutput_projection, map_smul, h, smul_eq_mul, mul_one]

/-- Restricting to the reachable span gives a linearly reachable whole state module. -/
theorem restricted_reachable (M : LinearReachability.System R V A) :
    LinearReachability.reachable
      (LinearReachability.System.mk (LinearReachability.initial M) (LinearReachability.transition M)) = ⊤ := by
  let S : LinearReachability.System R (LinearReachability.State M) A :=
    ⟨LinearReachability.initial M, LinearReachability.transition M⟩
  have he := LinearReachability.map_reachable S M (LinearReachability.reachable M).subtype
    rfl (fun _ _ => rfl)
  apply top_unique
  intro x _
  have hx : x.val ∈ (LinearReachability.reachable S).map (LinearReachability.reachable M).subtype := by
    rw [he]
    exact x.property
  obtain ⟨y,hy,hxy⟩ := Submodule.mem_map.mp hx
  have h : y = x := Subtype.ext hxy
  exact h ▸ hy

end
end LinearObservability
end KomorebiPadic
