import PaperXI.OnePlusIndex110

/-! Common-ideal quotient towers for exact one-plus groups. The primary
statement stays in the original integral-order ring and only needs nested
unit groups. It does not assume that a conjugate lattice is an ideal in the
full endomorphism algebra, or that a common integral order exists. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.OnePlusIntersection110
open OnePlusIndex110

variable {R : Type*} [Ring R]

/-- The ambient units congruent to one modulo a left ideal. -/
def idealUnits (I : Ideal R) : Subgroup Rˣ :=
  (congruence I (⊤ : Subgroup Rˣ)).comap Subgroup.topEquiv.symm.toMonoidHom

@[simp] theorem mem_idealUnits (I : Ideal R) (g : Rˣ) :
    g ∈ idealUnits I ↔ (g : R) - 1 ∈ I := Iff.rfl

theorem mem_of_offset (L : AddSubgroup R) (K : Subgroup Rˣ)
    (hL : ∀ x : L, ∃ g : K, ((g : Rˣ) : R) = 1 + (x : R))
    (g : Rˣ) (hg : (g : R) - 1 ∈ L) : g ∈ K := by
  obtain ⟨u, hu⟩ := hL ⟨(g : R) - 1, hg⟩
  have he : (u : Rˣ) = g := by
    apply Units.ext
    rw [hu]
    change 1 + ((g : R) - 1) = (g : R)
    noncomm_ring
  exact he ▸ u.property

theorem idealUnits_le (I : Ideal R) (L : AddSubgroup R) (K : Subgroup Rˣ)
    (hL : ∀ x : L, ∃ g : K, ((g : Rˣ) : R) = 1 + (x : R))
    (hIL : I.toAddSubgroup ≤ L) : idealUnits I ≤ K := by
  intro g hg
  exact mem_of_offset L K hL g (hIL ((mem_idealUnits I g).mp hg))

theorem idealUnits_relIndex (I : Ideal R) (L : AddSubgroup R) (K : Subgroup Rˣ)
    (hK : ∀ g : K, ((g : Rˣ) : R) - 1 ∈ L)
    (hL : ∀ x : L, ∃ g : K, ((g : Rˣ) : R) = 1 + (x : R)) :
    (idealUnits I).relIndex K = I.toAddSubgroup.relIndex L := by
  change ((idealUnits I).subgroupOf K).index = _
  have he : (idealUnits I).subgroupOf K = congruence I K := by
    ext g
    rfl
  rw [he]
  exact index_eq_additive_relIndex I L K hK hL

/-- Nesting of exact one-plus unit groups forces nesting of offset lattices. -/
theorem offset_le_of_group_le (L M : AddSubgroup R) (K H : Subgroup Rˣ)
    (hK : ∀ g : K, ((g : Rˣ) : R) - 1 ∈ L)
    (hM : ∀ x : M, ∃ g : H, ((g : Rˣ) : R) = 1 + (x : R))
    (hHK : H ≤ K) : M ≤ L := by
  intro x hx
  obtain ⟨g, hg⟩ := hM ⟨x, hx⟩
  have h := hK ⟨g, hHK g.property⟩
  rw [hg] at h
  simpa only [add_sub_cancel_left] using h

/-- Finite positive quotient towers remove the common deep ideal. No final
multiplicative/additive index identity is an input. -/
theorem nested_relIndex_eq (I : Ideal R) (L M : AddSubgroup R)
    (K H : Subgroup Rˣ)
    (hK : ∀ g : K, ((g : Rˣ) : R) - 1 ∈ L)
    (hL : ∀ x : L, ∃ g : K, ((g : Rˣ) : R) = 1 + (x : R))
    (hH : ∀ g : H, ((g : Rˣ) : R) - 1 ∈ M)
    (hM : ∀ x : M, ∃ g : H, ((g : Rˣ) : R) = 1 + (x : R))
    (hHK : H ≤ K) (hIM : I.toAddSubgroup ≤ M)
    [Finite (L ⧸ I.toAddSubgroup.addSubgroupOf L)] :
    H.relIndex K = M.relIndex L := by
  have hML := offset_le_of_group_le L M K H hK hM hHK
  have hCH := idealUnits_le I M H hM hIM
  have hm := Subgroup.relIndex_mul_relIndex (idealUnits I) H K hCH hHK
  rw [idealUnits_relIndex I M H hH hM, idealUnits_relIndex I L K hK hL] at hm
  have ha := AddSubgroup.relIndex_mul_relIndex I.toAddSubgroup M L hIM hML
  have hIL : I.toAddSubgroup.relIndex L ≠ 0 := by
    change (I.toAddSubgroup.addSubgroupOf L).index ≠ 0
    exact AddSubgroup.index_ne_zero_of_finite
  have hIMpos : I.toAddSubgroup.relIndex M ≠ 0 := by
    intro hz
    rw [hz, zero_mul] at ha
    exact hIL ha.symm
  exact Nat.eq_of_mul_eq_mul_left (Nat.pos_of_ne_zero hIMpos) (hm.trans ha.symm)


section ExternalRing
variable {S : Type*} [Ring S]

/-- Actual unit conjugation as a ring equivalence of the external algebra. -/
def innerRing (y : Sˣ) : S ≃+* S where
  toFun x := (y : S) * x * (y⁻¹ : Sˣ)
  invFun x := (y⁻¹ : Sˣ) * x * (y : S)
  left_inv x := by simp [mul_assoc]
  right_inv x := by simp [mul_assoc]
  map_mul' x z := by simp [mul_assoc]
  map_add' x z := by simp [mul_add, add_mul]

/-- The literal image group has the literal image offset lattice. -/
theorem mapped_offsets (f : R →+* S) (L : AddSubgroup R) (K : Subgroup Rˣ)
    (hK : ∀ g : K, ((g : Rˣ) : R) - 1 ∈ L) :
    ∀ g : K.map (Units.map f.toMonoidHom),
      ((g : Sˣ) : S) - 1 ∈ L.map f.toAddMonoidHom := by
  intro g
  obtain ⟨u, hu, he⟩ := Subgroup.mem_map.mp g.property
  apply AddSubgroup.mem_map.mpr
  refine ⟨(u : R) - 1, hK ⟨u, hu⟩, ?_⟩
  change f ((u : R) - 1) = ((g : Sˣ) : S) - 1
  rw [map_sub, map_one]
  exact congrArg (fun z : Sˣ => (z : S) - 1) he

theorem mapped_onePlus (f : R →+* S) (L : AddSubgroup R) (K : Subgroup Rˣ)
    (hL : ∀ x : L, ∃ g : K, ((g : Rˣ) : R) = 1 + (x : R)) :
    ∀ x : L.map f.toAddMonoidHom,
      ∃ g : K.map (Units.map f.toMonoidHom), ((g : Sˣ) : S) = 1 + (x : S) := by
  intro x
  obtain ⟨a, ha, he⟩ := AddSubgroup.mem_map.mp x.property
  obtain ⟨u, hu⟩ := hL ⟨a, ha⟩
  refine ⟨⟨Units.map f.toMonoidHom (u : Rˣ),
    Subgroup.mem_map.mpr ⟨u, u.property, rfl⟩⟩, ?_⟩
  change f ((u : Rˣ) : R) = 1 + (x : S)
  rw [hu, map_add, map_one]
  exact congrArg (fun z : S => 1 + z) he

def pullbackGroup (f : R →+* S) (K : Subgroup Rˣ) (K' : Subgroup Sˣ) :
    Subgroup Rˣ := K ⊓ K'.comap (Units.map f.toMonoidHom)

def pullbackLattice (f : R →+* S) (L : AddSubgroup R) (L' : AddSubgroup S) :
    AddSubgroup R := L ⊓ L'.comap f.toAddMonoidHom

theorem pullback_offsets (f : R →+* S) (L : AddSubgroup R) (L' : AddSubgroup S)
    (K : Subgroup Rˣ) (K' : Subgroup Sˣ)
    (hK : ∀ g : K, ((g : Rˣ) : R) - 1 ∈ L)
    (hK' : ∀ g : K', ((g : Sˣ) : S) - 1 ∈ L') :
    ∀ g : pullbackGroup f K K',
      ((g : Rˣ) : R) - 1 ∈ pullbackLattice f L L' := by
  intro g
  refine ⟨hK ⟨g, g.property.1⟩, ?_⟩
  have h := hK' ⟨Units.map f.toMonoidHom (g : Rˣ), g.property.2⟩
  change f (((g : Rˣ) : R)) - 1 ∈ L' at h
  change f (((g : Rˣ) : R) - 1) ∈ L'
  simpa only [map_sub, map_one] using h

theorem pullback_onePlus (f : R →+* S) (L : AddSubgroup R) (L' : AddSubgroup S)
    (K : Subgroup Rˣ) (K' : Subgroup Sˣ)
    (hL : ∀ x : L, ∃ g : K, ((g : Rˣ) : R) = 1 + (x : R))
    (hL' : ∀ x : L', ∃ g : K', ((g : Sˣ) : S) = 1 + (x : S)) :
    ∀ x : pullbackLattice f L L',
      ∃ g : pullbackGroup f K K', ((g : Rˣ) : R) = 1 + (x : R) := by
  intro x
  obtain ⟨u, hu⟩ := hL ⟨x, x.property.1⟩
  have hoff : ((Units.map f.toMonoidHom (u : Rˣ) : Sˣ) : S) - 1 = f (x : R) := by
    change f ((u : Rˣ) : R) - 1 = f (x : R)
    rw [hu, map_add, map_one]
    simp only [add_sub_cancel_left]
  have hmem : Units.map f.toMonoidHom (u : Rˣ) ∈ K' :=
    mem_of_offset L' K' hL' _ (hoff ▸ x.property.2)
  exact ⟨⟨u, ⟨u.property, hmem⟩⟩, hu⟩

/-- A common deep left ideal in the original ring suffices for an intersection
with a group in an external ring. No common ambient order is required. -/
theorem pullback_intersection_relIndex_eq (f : R →+* S) (I : Ideal R)
    (L : AddSubgroup R) (L' : AddSubgroup S) (K : Subgroup Rˣ) (K' : Subgroup Sˣ)
    (hK : ∀ g : K, ((g : Rˣ) : R) - 1 ∈ L)
    (hL : ∀ x : L, ∃ g : K, ((g : Rˣ) : R) = 1 + (x : R))
    (hK' : ∀ g : K', ((g : Sˣ) : S) - 1 ∈ L')
    (hL' : ∀ x : L', ∃ g : K', ((g : Sˣ) : S) = 1 + (x : S))
    (hI : I.toAddSubgroup ≤ pullbackLattice f L L')
    [Finite (L ⧸ I.toAddSubgroup.addSubgroupOf L)] :
    K'.relIndex (K.map (Units.map f.toMonoidHom)) =
      L'.relIndex (L.map f.toAddMonoidHom) := by
  have he := nested_relIndex_eq I L (pullbackLattice f L L') K
    (pullbackGroup f K K') hK hL (pullback_offsets f L L' K K' hK hK')
    (pullback_onePlus f L L' K K' hL hL') inf_le_left hI
  simpa only [pullbackGroup, pullbackLattice, Subgroup.inf_relIndex_left,
    AddSubgroup.inf_relIndex_left, Subgroup.relIndex_comap, AddSubgroup.relIndex_comap] using he

/-- Literal conjugation in S, with the deep ideal and finite quotient kept in
R. Both the conjugated group and conjugated lattice are constructed. -/
theorem conjugate_intersection_relIndex_eq (f : R →+* S) (y : Sˣ) (I : Ideal R)
    (L : AddSubgroup R) (K : Subgroup Rˣ)
    (hK : ∀ g : K, ((g : Rˣ) : R) - 1 ∈ L)
    (hL : ∀ x : L, ∃ g : K, ((g : Rˣ) : R) = 1 + (x : R))
    (hI : I.toAddSubgroup ≤ pullbackLattice f L
      (L.map ((innerRing y).toRingHom.comp f).toAddMonoidHom))
    [Finite (L ⧸ I.toAddSubgroup.addSubgroupOf L)] :
    (K.map (Units.map ((innerRing y).toRingHom.comp f).toMonoidHom)).relIndex
        (K.map (Units.map f.toMonoidHom)) =
      (L.map ((innerRing y).toRingHom.comp f).toAddMonoidHom).relIndex
        (L.map f.toAddMonoidHom) := by
  exact pullback_intersection_relIndex_eq f I L
    (L.map ((innerRing y).toRingHom.comp f).toAddMonoidHom) K
    (K.map (Units.map ((innerRing y).toRingHom.comp f).toMonoidHom)) hK hL
    (mapped_offsets ((innerRing y).toRingHom.comp f) L K hK)
    (mapped_onePlus ((innerRing y).toRingHom.comp f) L K hL) hI

end ExternalRing
end PaperXI.OnePlusIntersection110
