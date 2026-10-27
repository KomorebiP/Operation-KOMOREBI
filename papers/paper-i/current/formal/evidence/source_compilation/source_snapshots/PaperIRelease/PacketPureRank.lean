import PaperIRelease.PacketCorners

set_option autoImplicit false
set_option linter.unnecessarySimpa false
noncomputable section

namespace Komorebi.PaperIRelease

open Cardinal Set Komorebi.Foundation Komorebi.SeedRankBasics

universe u
variable {𝕜 X I : Type u} [Field 𝕜] [AddCommGroup X] [Module 𝕜 X] [Fintype I]

/-- Pure generation uses the actual ambient algebra action. -/
def PureGenerates (A : Subalgebra 𝕜 (Module.End 𝕜 X))
    (P : LinearProjectorFamily 𝕜 X I) (S : Set X) : Prop :=
  Generates A X S ∧ ∀ x ∈ S, PacketPure P x

/-- The minimum cardinality of an actual packet-pure generating set. -/
def packetPureSeedRank (A : Subalgebra 𝕜 (Module.End 𝕜 X))
    (P : LinearProjectorFamily 𝕜 X I) : Cardinal.{u} :=
  ⨅ (S : {S : Set X // PureGenerates A P S}), #S.1

theorem all_pure_generates (A : Subalgebra 𝕜 (Module.End 𝕜 X))
    (P : LinearProjectorFamily 𝕜 X I) : PureGenerates A P {x | PacketPure P x} := by
  refine ⟨?_, fun _ hx ↦ hx⟩
  apply top_unique
  intro x _
  rw [← P.complete x]
  apply Submodule.sum_mem
  intro i _
  exact Submodule.subset_span (packetPure_of_mem_range P ⟨x, rfl⟩)

theorem packetPureSeedRank_le_card {A : Subalgebra 𝕜 (Module.End 𝕜 X)}
    {P : LinearProjectorFamily 𝕜 X I} {S : Set X} (hS : PureGenerates A P S) :
    packetPureSeedRank A P ≤ #S :=
  ciInf_le' (fun T : {T : Set X // PureGenerates A P T} ↦ #T.1) ⟨S, hS⟩

theorem exists_pure_generating_set_card_eq
    (A : Subalgebra 𝕜 (Module.End 𝕜 X)) (P : LinearProjectorFamily 𝕜 X I) :
    ∃ S : Set X, PureGenerates A P S ∧ #S = packetPureSeedRank A P := by
  have hmem : packetPureSeedRank A P ∈
      Set.range (fun S : {S : Set X // PureGenerates A P S} ↦ #S.1) :=
    csInf_mem ⟨#({x | PacketPure P x} : Set X),
      ⟨⟨{x | PacketPure P x}, all_pure_generates A P⟩, rfl⟩⟩
  obtain ⟨S, hS⟩ := hmem
  exact ⟨S.1, S.2, hS⟩

theorem seedRank_le_packetPureSeedRank
    (A : Subalgebra 𝕜 (Module.End 𝕜 X)) (P : LinearProjectorFamily 𝕜 X I) :
    seedRank A X ≤ packetPureSeedRank A P := by
  obtain ⟨S, hS, hcard⟩ := exists_pure_generating_set_card_eq A P
  rw [← hcard]
  exact seedRank_le_mk_of_generates A X hS.1

/-- Union of genuinely minimal corner generating sets proves the cardinal
upper bound, with no finite-dimensional assumption on the packet spaces. -/
theorem packetPureSeedRank_le_sum_corner
    (A : Subalgebra 𝕜 (Module.End 𝕜 X)) (P : LinearProjectorFamily 𝕜 X I)
    (hPA : ∀ i, P.proj i ∈ A) :
    packetPureSeedRank A P ≤ Cardinal.sum (fun i ↦
      seedRank (packetCornerAlgebra A (P.proj i) (hPA i) (P.idempotent i))
        (LinearMap.range (P.proj i))) := by
  classical
  let C (i : I) := packetCornerAlgebra A (P.proj i) (hPA i) (P.idempotent i)
  choose S hS hcard using fun i ↦
    exists_generating_set_card_eq_seedRank (C i) (LinearMap.range (P.proj i))
  let seeds : Set X := ⋃ i, Subtype.val '' S i
  let H : Submodule A X := Submodule.span A seeds
  have hpacket (i : I) (x : LinearMap.range (P.proj i)) : (x : X) ∈ H := by
    have hx : x ∈ Submodule.span (C i) (S i) := by rw [hS i]; trivial
    refine Submodule.span_induction
      (p := fun (x : LinearMap.range (P.proj i)) _ ↦ (x : X) ∈ H) ?_ ?_ ?_ ?_ hx
    · intro y hy
      exact Submodule.subset_span (Set.mem_iUnion.mpr ⟨i, ⟨y, hy, rfl⟩⟩)
    · exact H.zero_mem
    · intro x y _ _ hx hy
      exact H.add_mem hx hy
    · intro a y _ hy
      obtain ⟨b, hb⟩ := corner_action_ambient A (P.proj i) (hPA i) (P.idempotent i) a
      rw [hb y]
      exact H.smul_mem b hy
  have hgen : PureGenerates A P seeds := by
    constructor
    · change H = ⊤
      apply top_unique
      intro x _
      rw [← P.complete x]
      apply H.sum_mem
      intro i _
      exact hpacket i ⟨P.proj i x, ⟨x, rfl⟩⟩
    · intro x hx
      obtain ⟨i, y, hy, rfl⟩ := Set.mem_iUnion.mp hx
      exact packetPure_of_mem_range P y.property
  calc
    packetPureSeedRank A P ≤ #seeds := packetPureSeedRank_le_card hgen
    _ ≤ Cardinal.sum (fun i ↦ #(Subtype.val '' S i : Set X)) := Cardinal.mk_iUnion_le_sum_mk
    _ ≤ Cardinal.sum (fun i ↦ #(S i)) :=
      Cardinal.sum_le_sum _ _ (fun _ ↦ Cardinal.mk_image_le)
    _ = _ := by simp only [hcard, C]

theorem packetPureSeedRank_bounds
    (A : Subalgebra 𝕜 (Module.End 𝕜 X)) (P : LinearProjectorFamily 𝕜 X I)
    (hPA : ∀ i, P.proj i ∈ A) :
    seedRank A X ≤ packetPureSeedRank A P ∧
      packetPureSeedRank A P ≤ Cardinal.sum (fun i ↦
        seedRank (packetCornerAlgebra A (P.proj i) (hPA i) (P.idempotent i))
          (LinearMap.range (P.proj i))) :=
  ⟨seedRank_le_packetPureSeedRank A P, packetPureSeedRank_le_sum_corner A P hPA⟩

end Komorebi.PaperIRelease

#print axioms Komorebi.PaperIRelease.packetPureSeedRank_bounds
