import RealizationBoundaries.SubgroupSpectrum
import Mathlib.Topology.Order
import Mathlib.Topology.Homeomorph.Lemmas

/-!
# Cantor topology on the actual subgroup lattice of D

The topology on Sub(D) is induced by its actual Boolean membership functions
on D. It is not a topology transported along the spectrum classification.
-/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries
attribute [local instance] Classical.propDecidable

/-- The actual membership function of an arbitrary subgroup of D. -/
def subgroupMembership (H : AddSubgroup finiteSupport) (x : finiteSupport) : Bool :=
  decide (x ∈ H)

/-- The topology inherited from {0,1}^D by actual subgroup membership. -/
instance subgroupMembershipTopology : TopologicalSpace (AddSubgroup finiteSupport) :=
  TopologicalSpace.induced subgroupMembership inferInstance

/-- Binary prime selectors interpreted in the actual subgroup lattice. -/
def binarySpectrumEquiv : (Prime → Bool) ≃ AddSubgroup finiteSupport where
  toFun a := spectrumSubgroup {p | a p = true}
  invFun H p := decide (primeSeed p ∈ H)
  left_inv a := by
    funext p
    simp only [primeSeed_mem_spectrumSubgroup, Set.mem_ofPred_eq, Bool.decide_coe]
  right_inv H := by
    have he : {p : Prime | decide (primeSeed p ∈ H) = true} = subgroupSpectrum H := by
      ext p
      simp [subgroupSpectrum]
    change spectrumSubgroup {p : Prime | decide (primeSeed p ∈ H) = true} = H
    rw [he, spectrumSubgroup_subgroupSpectrum]

/-- Every fixed vector membership question uses only its finitely many support bits. -/
theorem subgroupMembership_binarySpectrum (x : finiteSupport) (a : Prime → Bool) :
    subgroupMembership (binarySpectrumEquiv a) x =
      decide (∀ p : {p : Prime // p ∈ x.property.toFinset}, a p.val = true) := by
  change decide (support x.val ⊆ {p | a p = true}) = _
  congr 1
  apply propext
  constructor
  · intro hx p
    exact hx ((Set.Finite.mem_toFinset x.property).mp p.property)
  · intro hx p hp
    exact hx ⟨p, (Set.Finite.mem_toFinset x.property).mpr hp⟩

/-- Finite dependence makes every membership coordinate continuous on Cantor space. -/
theorem subgroupMembership_binarySpectrum_continuous (x : finiteSupport) :
    Continuous (fun a : Prime → Bool => subgroupMembership (binarySpectrumEquiv a) x) := by
  have he : (fun a : Prime → Bool => subgroupMembership (binarySpectrumEquiv a) x) =
      fun a => decide (∀ p : {p : Prime // p ∈ x.property.toFinset}, a p.val = true) := by
    funext a
    exact subgroupMembership_binarySpectrum x a
  rw [he]
  let F := {p : Prime // p ∈ x.property.toFinset}
  have hrestriction : Continuous (fun a : Prime → Bool => fun p : F => a p.val) :=
    continuous_pi (fun p => continuous_apply p.val)
  exact (continuous_of_discreteTopology : Continuous
    (fun z : F → Bool => decide (∀ p, z p = true))).comp hrestriction

/-- The subgroup membership embedding is continuous by the defining inherited topology. -/
theorem subgroupMembership_continuous : Continuous subgroupMembership :=
  continuous_induced_dom

/-- The spectrum parametrization is continuous for the independently defined
membership topology, because every vector has finite support. -/
theorem binarySpectrumEquiv_continuous : Continuous binarySpectrumEquiv := by
  apply continuous_induced_rng.mpr
  exact continuous_pi subgroupMembership_binarySpectrum_continuous

/-- Prime-seed membership recovers each bit continuously. -/
theorem binarySpectrumEquiv_symm_continuous : Continuous binarySpectrumEquiv.symm := by
  apply continuous_pi
  intro p
  exact (continuous_apply (primeSeed p)).comp subgroupMembership_continuous

/-- The printed Cantor-space homeomorphism, with the actual inherited subgroup
topology and the standard product of discrete Boolean prime coordinates. -/
def subgroupCantorHomeomorph : (Prime → Bool) ≃ₜ AddSubgroup finiteSupport where
  toEquiv := binarySpectrumEquiv
  continuous_toFun := binarySpectrumEquiv_continuous
  continuous_invFun := binarySpectrumEquiv_symm_continuous

/-- The homeomorphism reads exactly the original prime-seed membership bits. -/
theorem subgroupCantorHomeomorph_primeSeed (a : Prime → Bool) (p : Prime) :
    primeSeed p ∈ subgroupCantorHomeomorph a ↔ a p = true :=
  primeSeed_mem_spectrumSubgroup _ _

/-- The fixed increasing prime enumeration is onto every prime coordinate. -/
theorem primeAt_surjective_for_topology : Function.Surjective primeAt := by
  intro p
  obtain ⟨n, _, hn⟩ := Nat.exists_lt_card_nth_eq p.property
  exact ⟨n, Subtype.ext hn⟩

def primeEnumerationEquiv : ℕ ≃ Prime :=
  Equiv.ofBijective primeAt ⟨primeAt_injective, primeAt_surjective_for_topology⟩

/-- The same homeomorphism with the printed natural-number Cantor index. -/
def natSubgroupCantorHomeomorph : (ℕ → Bool) ≃ₜ AddSubgroup finiteSupport :=
  (Homeomorph.piCongrLeft (Y := fun _ : Prime => Bool) primeEnumerationEquiv).trans
    subgroupCantorHomeomorph

end RealizationBoundaries
