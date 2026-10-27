import PaperXII.AdicCompanions

/-! Integral Frobenius polynomials and unramifiedness survive actual adic reconstruction.
Common coefficient fields map to local fields. Integral lifts of the common
polynomials are supplied separately; no field is mapped into a valuation ring. -/
set_option autoImplicit false
namespace PaperXII.AdicSpines

open ContinuousMonoidHom Matrix AdicMatrixGroups AdicCompanions

variable {R Γ ι : Type} [CommRing R] [Group Γ] [TopologicalSpace Γ]
    [Fintype ι] [DecidableEq ι] (I : Ideal R)

/-- Equality of every reduced characteristic polynomial determines the entire integral polynomial. -/
theorem charpoly_detected [IsHausdorff I R] (B : GL ι R) (P : Polynomial R)
    (h : ∀ n, (AdicMatrixGroups.reduce I n B).val.charpoly = P.map (quotientMap I n)) :
    B.val.charpoly = P := by
  apply Polynomial.ext
  intro k
  apply PaperX.RepresentationLimits.scalar_ext I
  intro n
  have hn := congrArg (fun f : Polynomial (Coeff I n) ↦ f.coeff k) (h n)
  change ((B.val.map (Ideal.Quotient.mk (I ^ n))).charpoly).coeff k =
    (P.map (Ideal.Quotient.mk (I ^ n))).coeff k at hn
  simpa only [Matrix.charpoly_map, Polynomial.coeff_map] using hn

/-- Every prescribed integral Frobenius polynomial survives, at every declared good place. -/
theorem spine_preserved [IsHausdorff I R]
    (A : ∀ n, (Γ →ₜ* GL ι (Coeff I n)) → Prop) (ρ : AdicRealization I A)
    {Ω : Type*} (frob : Ω → Γ) (good : Ω → Prop) (P : Ω → Polynomial R)
    (hspec : ∀ n σ, A n σ → ∀ v, good v →
      (σ (frob v)).val.charpoly = (P v).map (quotientMap I n)) :
    ∀ v, good v → (ρ.val (frob v)).val.charpoly = P v := by
  intro v hv
  apply charpoly_detected I
  intro n
  exact hspec n (reduceRep I n ρ.val) (ρ.property n) v hv

/-- A supplied inertia subgroup acts trivially on the lift if it does so at every finite level. -/
theorem unramified_preserved [IsHausdorff I R]
    (A : ∀ n, (Γ →ₜ* GL ι (Coeff I n)) → Prop) (ρ : AdicRealization I A)
    (H : Subgroup Γ)
    (hspec : ∀ n σ, A n σ → ∀ g, g ∈ H → σ g = 1) :
    ∀ g, g ∈ H → ρ.val g = 1 := by
  intro g hg
  apply ext_of_reductions I
  intro n
  rw [map_one]
  exact hspec n (reduceRep I n ρ.val) (ρ.property n) g hg

/-- Actual continuous coefficient change to the declared local field or topological coefficient ring. -/
def fieldRep {K : Type*} [CommRing K] [TopologicalSpace K]
    (inc : R →+* K) (hinc : @Continuous R K I.adicTopology inferInstance inc)
    (ρ : AdicRep (Γ := Γ) (ι := ι) I) : Γ →ₜ* GL ι K := by
  let _ : TopologicalSpace R := I.adicTopology
  exact
    { __ := (GeneralLinearGroup.map inc).comp ρ.toMonoidHom
      continuous_toFun := hinc.generalLinearGroup_map.comp ρ.continuous }

/-- The local integral polynomial gives the exact common-field polynomial after coefficient change. -/
theorem fieldRep_charpoly {K L : Type*} [CommRing K] [TopologicalSpace K] [CommRing L]
    (inc : R →+* K) (hinc : @Continuous R K I.adicTopology inferInstance inc)
    (emb : L →+* K) (ρ : AdicRep (Γ := Γ) (ι := ι) I) (g : Γ)
    (localP : Polynomial R) (commonP : Polynomial L)
    (hlocal : (ρ g).val.charpoly = localP)
    (hmatch : localP.map inc = commonP.map emb) :
    (fieldRep I inc hinc ρ g).val.charpoly = commonP.map emb := by
  let _ : TopologicalSpace R := I.adicTopology
  change ((ρ g).val.map inc).charpoly = _
  rw [Matrix.charpoly_map, hlocal, hmatch]

/-- Unramifiedness survives actual coefficient change as well. -/
theorem fieldRep_unramified {K : Type*} [CommRing K] [TopologicalSpace K]
    (inc : R →+* K) (hinc : @Continuous R K I.adicTopology inferInstance inc)
    (ρ : AdicRep (Γ := Γ) (ι := ι) I) (H : Subgroup Γ)
    (hρ : ∀ g, g ∈ H → ρ g = 1) : ∀ g, g ∈ H → fieldRep I inc hinc ρ g = 1 := by
  let _ : TopologicalSpace R := I.adicTopology
  intro g hg
  change GeneralLinearGroup.map inc (ρ g) = 1
  rw [hρ g hg, map_one]

/-- Simultaneous actual adic realizations with a common algebraic Frobenius spine.
Local integrality, finite occupancy, and reduction stability remain explicit inputs. -/
theorem simultaneous_common_spine
    {Λ Ω L : Type} [Field L] (O K : Λ → Type)
    [∀ l, CommRing (O l)] [∀ l, Field (K l)] [∀ l, TopologicalSpace (K l)]
    (J : ∀ l, Ideal (O l)) [∀ l, IsAdicComplete (J l) (O l)]
    (A : ∀ l n, (Γ →ₜ* GL ι (Coeff (J l) n)) → Prop)
    (hA : ∀ l n σ, A l (n + 1) σ → A l n ((step (J l) n).comp σ))
    [∀ l n, Finite {σ : Γ →ₜ* GL ι (Coeff (J l) n) // A l n σ}]
    (hne : ∀ l n, Nonempty {σ : Γ →ₜ* GL ι (Coeff (J l) n) // A l n σ})
    (inc : ∀ l, O l →+* K l)
    (hinc : ∀ l, @Continuous (O l) (K l) (J l).adicTopology inferInstance (inc l))
    (emb : ∀ l, L →+* K l) (frob : Ω → Γ) (good : Λ → Ω → Prop)
    (P : Ω → Polynomial L) (localP : ∀ l, Ω → Polynomial (O l))
    (hmatch : ∀ l v, good l v → (localP l v).map (inc l) = (P v).map (emb l))
    (hspec : ∀ l n σ, A l n σ → ∀ v, good l v →
      (σ (frob v)).val.charpoly = (localP l v).map (quotientMap (J l) n)) :
    ∃ ρ : ∀ l, AdicRealization (J l) (A l), ∀ l v, good l v →
      (fieldRep (J l) (inc l) (hinc l) (ρ l).val (frob v)).val.charpoly =
        (P v).map (emb l) := by
  classical
  let ρ : ∀ l, AdicRealization (J l) (A l) :=
    fun l ↦ Classical.choice (exists_adic_realization (J l) (A l) (hA l) (hne l))
  refine ⟨ρ, ?_⟩
  intro l v hv
  exact fieldRep_charpoly (J l) (inc l) (hinc l) (emb l) (ρ l).val (frob v)
    (localP l v) (P v)
    (spine_preserved (J l) (A l) (ρ l) frob (good l) (localP l) (hspec l) v hv)
    (hmatch l v hv)

end PaperXII.AdicSpines
