import PaperXI.CycleSpan

/-! A return eigenline exhausts its packet in an actual irreducible
representation. No packet dimension or spanning conclusion is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.PacketLines
open PaperXI.CyclicAction PaperXI.PacketTransport PaperXI.FrobeniusPeriod
open PaperXI.CycleSpan PaperXI.GeneratedIrreducibility PaperXI.TameOrbitTransitivity
variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable {M : ℕ} [NeZero M]

def orbitLabel (q : (ZMod M)ˣ) (j : ZMod M) (a : Fin (period q j)) : ZMod M :=
  ((q ^ (a : ℕ) : (ZMod M)ˣ) : ZMod M) * j

theorem orbitLabel_injective (q : (ZMod M)ˣ) (j : ZMod M) :
    Function.Injective (orbitLabel q j) := by
  intro a b h
  apply (orbitEquiv q j).injective
  exact Subtype.ext h

theorem cycle_mem_packet (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (j : ZMod M) {v : V} (hv : v ∈ packet ρ j) (a : Fin (period q j)) :
    cycleVector F v a ∈ packet ρ (orbitLabel q j a) :=
  PaperXI.PacketReturn.power_mem ρ F q h j a hv

theorem inertia_cycle (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (j : ZMod M) {v : V} (hv : v ∈ packet ρ j)
    (a : Fin (period q j)) (b : ZMod M) :
    operator ρ b (cycleVector F v a) =
      ZMod.stdAddChar (orbitLabel q j a * b) • cycleVector F v a :=
  cycle_mem_packet ρ F q h j hv a b

theorem inertia_stable (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (j : ZMod M) {v : V} (hv : v ∈ packet ρ j) (b : ZMod M)
    {w : V} (hw : w ∈ cycleSpan F v (period q j)) :
    operator ρ b w ∈ cycleSpan F v (period q j) := by
  apply CycleSpan.map_mem F v (period q j) (operator ρ b) (fun a => ?_) hw
  rw [inertia_cycle ρ F q h j hv]
  exact (cycleSpan F v (period q j)).smul_mem _ (CycleSpan.power_mem F v a.isLt)

/-- Fourier projectors extract exactly one vector of the finite orbit. -/
theorem projector_cycle (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (j : ZMod M) {v : V} (hv : v ∈ packet ρ j) (a b : Fin (period q j)) :
    projector ρ (orbitLabel q j a) (cycleVector F v b) =
      if b = a then cycleVector F v a else 0 := by
  classical
  by_cases hab : b = a
  · subst b
    simp only [ite_true]
    exact (mem_iff_projector ρ _ _).mp (cycle_mem_packet ρ F q h j hv a)
  · rw [ite_eq_right hab]
    apply projector_on_other_packet ρ _ (cycle_mem_packet ρ F q h j hv b)
    intro heq
    exact hab ((orbitLabel_injective q j heq).symm)

/-- Projecting the finite cycle span onto its initial packet leaves just the chosen line. -/
theorem projection_to_line (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (j : ZMod M) {v : V} (hv : v ∈ packet ρ j) :
    cycleSpan F v (period q j) ≤ (Submodule.span ℂ {v}).comap (projector ρ j) := by
  apply Submodule.span_le.mpr
  rintro w ⟨a, rfl⟩
  change projector ρ j (cycleVector F v a) ∈ Submodule.span ℂ {v}
  by_cases ha : (a : ℕ) = 0
  · have heq : cycleVector F v a = v := by simp [cycleVector, ha]
    rw [heq, (mem_iff_projector ρ j v).mp hv]
    exact Submodule.subset_span (Set.mem_singleton v)
  · have hne : j ≠ orbitLabel q j a :=
      (no_short_return q j (Nat.pos_of_ne_zero ha) a.isLt).symm
    rw [projector_on_other_packet ρ hne (cycle_mem_packet ρ F q h j hv a)]
    exact Submodule.zero_mem _

theorem packet_eq_line_of_span_top (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (j : ZMod M) {v : V} (hv : v ∈ packet ρ j)
    (htop : cycleSpan F v (period q j) = ⊤) : packet ρ j = Submodule.span ℂ {v} := by
  apply le_antisymm
  · intro w hw
    have ht : w ∈ cycleSpan F v (period q j) := by simp [htop]
    have hm := projection_to_line ρ F q h j hv ht
    change projector ρ j w ∈ Submodule.span ℂ {v} at hm
    rwa [(mem_iff_projector ρ j w).mp hw] at hm
  · exact Submodule.span_le.mpr (by simpa using hv)

variable {G : Type*} [Group G]

theorem generators_preserve_cycleSpan (π : Representation ℂ G V)
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    (j : ZMod M) {v : V} (hv : v ∈ packet (tameRestriction π ι) j)
    {c : ℂ} (hc : c ≠ 0) (hclose : (actionEquiv π φ ^ period q j) v = c • v) :
    ∀ g ∈ generators ι φ, ∀ w ∈ cycleSpan (actionEquiv π φ) v (period q j),
      π g w ∈ cycleSpan (actionEquiv π φ) v (period q j) := by
  intro g hg w hw
  rcases hg with ⟨a, rfl⟩ | hg
  · exact inertia_stable (tameRestriction π ι) (actionEquiv π φ) q
      (geometric_relation π ι φ q hrel) j hv a.toAdd hw
  · rcases hg with hg | hg
    · have heq : g = φ := hg
      subst g
      exact CycleSpan.forward_stable (actionEquiv π φ) v (period_pos q j) hclose hw
    · have heq : g = φ⁻¹ := hg
      subst g
      exact CycleSpan.backward_stable (actionEquiv π φ) v (period_pos q j) hc hclose hw

theorem cycleSpan_eq_top (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    (j : ZMod M) {v : V} (hv : v ∈ packet (tameRestriction π ι) j) (hv0 : v ≠ 0)
    {c : ℂ} (hc : c ≠ 0) (hclose : (actionEquiv π φ ^ period q j) v = c • v) :
    cycleSpan (actionEquiv π φ) v (period q j) = ⊤ :=
  (eq_bot_or_top π (generators ι φ) hgen _
    (generators_preserve_cycleSpan π ι φ q hrel j hv hc hclose)).resolve_left
      (CycleSpan.span_ne_bot (actionEquiv π φ) hv0 (period_pos q j))

/-- Every nonzero packet is one-dimensional; this is a conclusion of irreducibility. -/
theorem nonzero_packet_finrank_one [FiniteDimensional ℂ V]
    (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    {j : ZMod M} (hj : packet (tameRestriction π ι) j ≠ ⊥) :
    Module.finrank ℂ (packet (tameRestriction π ι) j) = 1 := by
  obtain ⟨c, v, hc, hv, hv0, hclose⟩ := PaperXI.PacketReturn.exists_closing_eigenvector
    (tameRestriction π ι) (actionEquiv π φ) q (geometric_relation π ι φ q hrel) hj
  have htop := cycleSpan_eq_top π ι φ q hgen hrel j hv hv0 hc hclose
  have hline := packet_eq_line_of_span_top (tameRestriction π ι) (actionEquiv π φ) q
    (geometric_relation π ι φ q hrel) j hv htop
  rw [hline]
  exact finrank_span_singleton hv0

end PaperXI.PacketLines
