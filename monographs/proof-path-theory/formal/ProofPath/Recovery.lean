import ProofPath.Compression

/-!
Recovery on the attained image. This is the decoder domain used by the monograph.
The old total-codomain definition stays available and is compared explicitly.
-/
namespace ProofPath
namespace Recovery

variable {A B C D : Type*}

def Image (encode : A → B) := {b : B // ∃ a : A, encode a = b}

def observed (encode : A → B) (a : A) : Image encode := ⟨encode a, a, rfl⟩

def Sufficient (encode : A → B) (task : A → C) : Prop :=
  ∃ decode : Image encode → C, ∀ a, decode (observed encode a) = task a

def FiberConstant (encode : A → B) (task : A → C) : Prop :=
  ∀ a a', encode a = encode a' → task a = task a'

theorem sufficient_iff_fiber_constant (encode : A → B) (task : A → C) :
    Sufficient encode task ↔ FiberConstant encode task := by
  constructor
  · rintro ⟨d, hd⟩ a a' he
    have hh : observed encode a = observed encode a' := Subtype.ext he
    exact (hd a).symm.trans ((congrArg d hh).trans (hd a'))
  · intro h
    classical
    let pick : Image encode → A := fun b => Classical.choose b.property
    have hp : ∀ b : Image encode, encode (pick b) = b.val :=
      fun b => Classical.choose_spec b.property
    refine ⟨fun b => task (pick b), ?_⟩
    intro a
    exact h (pick (observed encode a)) a (hp (observed encode a))

theorem total_implies_attained (encode : A → B) (task : A → C)
    (h : ProofPath.Sufficient encode task) : Sufficient encode task := by
  rcases h with ⟨d, hd⟩
  exact ⟨fun b => d b.val, hd⟩

/-- A nonempty answer type supplies values for unattained representations. -/
theorem attained_iff_total [Nonempty C] (encode : A → B) (task : A → C) :
    Sufficient encode task ↔ ProofPath.Sufficient encode task := by
  constructor
  · rintro ⟨d, hd⟩
    classical
    refine ⟨fun b => if h : ∃ a, encode a = b then d ⟨b, h⟩ else Classical.choice inferInstance, ?_⟩
    intro a
    simp only [dite_eq_left (show ∃ a', encode a' = encode a from ⟨a, rfl⟩)]
    exact hd a
  · exact total_implies_attained encode task

theorem decoder_unique (encode : A → B) (task : A → C)
    (d e : Image encode → C)
    (hd : ∀ a, d (observed encode a) = task a)
    (he : ∀ a, e (observed encode a) = task a) : d = e := by
  funext b
  obtain ⟨a, ha⟩ := b.property
  have hb : observed encode a = b := Subtype.ext ha
  rw [← hb, hd, he]

/-- The complete obstruction is an identified pair with different task answers. -/
theorem not_sufficient_iff_collision (encode : A → B) (task : A → C) :
    ¬ Sufficient encode task ↔ ∃ a a', encode a = encode a' ∧ task a ≠ task a' := by
  rw [sufficient_iff_fiber_constant]
  unfold FiberConstant
  push Not
  rfl

def Recovers (coarse : A → B) (fine : A → C) : Prop := Sufficient fine coarse

theorem recovers_refl (encode : A → B) : Recovers encode encode := by
  apply (sufficient_iff_fiber_constant _ _).mpr
  exact fun _ _ h => h

theorem task_transport (coarse : A → B) (fine : A → C) (task : A → D)
    (hr : Recovers coarse fine) (ht : Sufficient coarse task) : Sufficient fine task := by
  apply (sufficient_iff_fiber_constant _ _).mpr
  have h1 := (sufficient_iff_fiber_constant _ _).mp hr
  have h2 := (sufficient_iff_fiber_constant _ _).mp ht
  exact fun a b h => h2 a b (h1 a b h)

theorem recovers_trans (r : A → B) (s : A → C) (t : A → D)
    (hrs : Recovers r s) (hst : Recovers s t) : Recovers r t :=
  task_transport s t r hst hrs

/-- A tagged portfolio recovers each of its coordinates. -/
theorem portfolio_left (r : A → B) (s : A → C) :
    Recovers r (fun a => (r a, s a)) := by
  apply (sufficient_iff_fiber_constant _ _).mpr
  exact fun _ _ h => congrArg Prod.fst h

theorem portfolio_right (r : A → B) (s : A → C) :
    Recovers s (fun a => (r a, s a)) := by
  apply (sufficient_iff_fiber_constant _ _).mpr
  exact fun _ _ h => congrArg Prod.snd h

/-- Joint tasks supply the least information required by the entire task family. -/
theorem joint_sufficient_iff {I : Type*} {Y : I → Type*}
    (encode : A → B) (tasks : (i : I) → A → Y i) :
    Sufficient encode (fun a i => tasks i a) ↔ ∀ i, Sufficient encode (tasks i) := by
  constructor
  · intro h i
    apply (sufficient_iff_fiber_constant _ _).mpr
    intro a b hab
    exact congrFun ((sufficient_iff_fiber_constant _ _).mp h a b hab) i
  · intro h
    apply (sufficient_iff_fiber_constant _ _).mpr
    intro a b hab
    funext i
    exact (sufficient_iff_fiber_constant _ _).mp (h i) a b hab

theorem injective_sufficient (encode : A → B) (task : A → C)
    (hi : Function.Injective encode) : Sufficient encode task := by
  apply (sufficient_iff_fiber_constant _ _).mpr
  exact fun _ _ h => congrArg task (hi h)

/-- Attained and total decoding differ when an empty archive has an empty answer type. -/
theorem empty_attained_not_total :
    Sufficient (fun a : Empty => Empty.elim a : Empty → Unit) (id : Empty → Empty) ∧
    ¬ ProofPath.Sufficient (fun a : Empty => Empty.elim a : Empty → Unit) (id : Empty → Empty) := by
  constructor
  · apply (sufficient_iff_fiber_constant _ _).mpr
    intro a
    exact Empty.elim a
  · rintro ⟨d, _⟩
    exact Empty.elim (d ())

/-- Hashing cannot repair a distinction already lost by serialization. -/
theorem serialized_collision_persists (serialize : A → B) (hash : B → C)
    {a b : A} (h : serialize a = serialize b) :
    hash (serialize a) = hash (serialize b) := congrArg hash h

/-- Every task recoverable from a digest was already recoverable from its bytes. -/
theorem hash_task_data_processing (serialize : A → B) (hash : B → C)
    (task : A → D) (h : Sufficient (hash ∘ serialize) task) :
    Sufficient serialize task := by
  apply (sufficient_iff_fiber_constant _ _).mpr
  intro a b he
  exact (sufficient_iff_fiber_constant _ _).mp h a b (congrArg hash he)

/-- Injectivity only on attained serializations is sufficient to lose no further tasks. -/
theorem hash_preserves_tasks (serialize : A → B) (hash : B → C)
    (hi : Set.InjOn hash (Set.range serialize)) (task : A → D) :
    Sufficient (hash ∘ serialize) task ↔ Sufficient serialize task := by
  constructor
  · exact hash_task_data_processing serialize hash task
  · intro h
    apply (sufficient_iff_fiber_constant _ _).mpr
    intro a b he
    apply (sufficient_iff_fiber_constant _ _).mp h a b
    exact hi ⟨a, rfl⟩ ⟨b, rfl⟩ he

end Recovery
end ProofPath
