import MachineTheory.PositivePackets

/-!
# Transporting the cone, mass and packets together

An invertible real-linear change of coordinates preserves mixture meaning only
when the cone and mass are transported with the operators. Coordinate signs
alone have no invariant probability meaning.
-/
namespace Komorebi.MachineTheory.PositivePackets.Transport

noncomputable section

open scoped BigOperators

universe uV uW uI
variable {V : Type uV} {W : Type uW} {I : Type uI}
variable [AddCommGroup V] [Module ℝ V] [AddCommGroup W] [Module ℝ W]

/-- The transported cone is the actual image of the original cone. -/
def cone (e : V ≃ₗ[ℝ] W) (C : ConvexCone ℝ V) : ConvexCone ℝ W :=
  C.map e.toLinearMap

/-- Mass is read after applying the inverse coordinate map. -/
def mass (e : V ≃ₗ[ℝ] W) (m : V →ₗ[ℝ] ℝ) : W →ₗ[ℝ] ℝ :=
  m.comp e.symm.toLinearMap

/-- The actual conjugated operation. -/
def operator (e : V ≃ₗ[ℝ] W) (P : V →ₗ[ℝ] V) : W →ₗ[ℝ] W :=
  e.toLinearMap.comp (P.comp e.symm.toLinearMap)

@[simp] theorem cone_mem (e : V ≃ₗ[ℝ] W) (C : ConvexCone ℝ V) (v : V) :
    e v ∈ cone e C ↔ v ∈ C := by
  simp [cone, ConvexCone.mem_map]

@[simp] theorem mass_apply (e : V ≃ₗ[ℝ] W) (m : V →ₗ[ℝ] ℝ) (v : V) :
    mass e m (e v) = m v := by simp [mass]

@[simp] theorem operator_apply (e : V ≃ₗ[ℝ] W) (P : V →ₗ[ℝ] V) (v : V) :
    operator e P (e v) = e (P v) := by simp [operator]

/-- Strict positivity survives actual coordinate transport. -/
theorem strictMass (e : V ≃ₗ[ℝ] W) (C : ConvexCone ℝ V) (m : V →ₗ[ℝ] ℝ)
    (hm : StrictMass C m) : StrictMass (cone e C) (mass e m) := by
  intro w hw hn
  obtain ⟨v, rfl⟩ := e.surjective w
  rw [mass_apply]
  apply hm v ((cone_mem e C v).mp hw)
  intro hz
  apply hn
  simp [hz]

/-- Cone preservation is transported, not replaced by coordinate nonnegativity. -/
theorem preserves (e : V ≃ₗ[ℝ] W) (C : ConvexCone ℝ V) (P : V →ₗ[ℝ] V)
    (hp : Preserves C P) : Preserves (cone e C) (operator e P) := by
  intro w hw
  obtain ⟨v, rfl⟩ := e.surjective w
  rw [operator_apply, cone_mem]
  exact hp v ((cone_mem e C v).mp hw)

/-- Normalized state membership is equivalent in the two coordinate systems. -/
theorem state_iff (e : V ≃ₗ[ℝ] W) (C : ConvexCone ℝ V) (m : V →ₗ[ℝ] ℝ) (v : V) :
    IsState (cone e C) (mass e m) (e v) ↔ IsState C m v := by
  simp [IsState]

/-- Each packet retains exactly its old weight. -/
theorem weight_eq (e : V ≃ₗ[ℝ] W) (m : V →ₗ[ℝ] ℝ)
    (P : I → V →ₗ[ℝ] V) (v : V) (i : I) :
    weight (mass e m) (fun j => operator e (P j)) (e v) i = weight m P v i := by
  simp [weight]

/-- An original active index is active after transport. -/
def index (e : V ≃ₗ[ℝ] W) (m : V →ₗ[ℝ] ℝ) (P : I → V →ₗ[ℝ] V) (v : V)
    (i : PositiveIndex m P v) : PositiveIndex (mass e m) (fun j => operator e (P j)) (e v) :=
  ⟨i.val, by simpa only [weight_eq] using i.property⟩

/-- Positive-weight normalization commutes with the coordinate transformation. -/
theorem normalized_eq (e : V ≃ₗ[ℝ] W) (m : V →ₗ[ℝ] ℝ)
    (P : I → V →ₗ[ℝ] V) (v : V) (i : PositiveIndex m P v) :
    normalized (mass e m) (fun j => operator e (P j)) (e v) (index e m P v i) =
      e (normalized m P v i) := by
  simp [normalized, index, weight_eq]

/-- Idempotence, when present, is preserved by conjugation. -/
theorem idempotent (e : V ≃ₗ[ℝ] W) (P : V →ₗ[ℝ] V) (h : P.comp P = P) :
    (operator e P).comp (operator e P) = operator e P := by
  apply LinearMap.ext
  intro w
  obtain ⟨v, rfl⟩ := e.surjective w
  simp only [LinearMap.comp_apply, operator_apply]
  exact congrArg e (LinearMap.congr_fun h v)

variable [Fintype I]

/-- Completeness is also transported as an identity of actual linear maps. -/
theorem complete (e : V ≃ₗ[ℝ] W) (P : I → V →ₗ[ℝ] V) (hc : Complete P) :
    Complete (fun i => operator e (P i)) := by
  apply LinearMap.ext
  intro w
  obtain ⟨v, rfl⟩ := e.surjective w
  simpa only [LinearMap.sum_apply, LinearMap.id_apply, operator_apply, ← map_sum] using
    congrArg e (sum_packets P hc v)

/-- Source coordinate-change clause: the complete mixture hypotheses move together. -/
theorem source_coordinate_change (e : V ≃ₗ[ℝ] W) (C : ConvexCone ℝ V)
    (m : V →ₗ[ℝ] ℝ) (hm : StrictMass C m) (P : I → V →ₗ[ℝ] V)
    (hp : ∀ i, Preserves C (P i)) (hc : Complete P) {v : V} (hv : IsState C m v) :
    StrictMass (cone e C) (mass e m) ∧
    (∀ i, Preserves (cone e C) (operator e (P i))) ∧
    Complete (fun i => operator e (P i)) ∧
    IsState (cone e C) (mass e m) (e v) ∧
    (∀ i, weight (mass e m) (fun j => operator e (P j)) (e v) i = weight m P v i) :=
  ⟨strictMass e C m hm, fun i => preserves e C (P i) (hp i), complete e P hc,
    (state_iff e C m v).mpr hv, weight_eq e m P v⟩

end
end Komorebi.MachineTheory.PositivePackets.Transport
