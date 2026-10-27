import KomorebiSpace.SplitDefectCharts

set_option autoImplicit false

/-!
# Cochain maps and the failure of repair to commute with presentation change

The change of presentation intertwines the differentials. Chosen sections need
not intertwine. Their mismatch is an exact-valued bounded map, and it measures
precisely the discrepancy between the two orders of sampling and repair.
-/
universe u v w v' w' v'' w''
noncomputable section
namespace KomorebiSpace
namespace SplitDefect
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable {E : Type v} [NormedAddCommGroup E] [NormedSpace 𝕜 E]
variable {R : Type w} [NormedAddCommGroup R] [NormedSpace 𝕜 R]
variable {F : Type v'} [NormedAddCommGroup F] [NormedSpace 𝕜 F]
variable {T : Type w'} [NormedAddCommGroup T] [NormedSpace 𝕜 T]
variable {G : Type v''} [NormedAddCommGroup G] [NormedSpace 𝕜 G]
variable {U : Type w''} [NormedAddCommGroup U] [NormedSpace 𝕜 U]
variable (d : E →L[𝕜] R) (D : F →L[𝕜] T)

/-- A bounded change of candidate and residual coordinates that preserves the differential. -/
structure DefectMap where
  candidate : E →L[𝕜] F
  residual : R →L[𝕜] T
  commutes : ∀ f, D (candidate f) = residual (d f)

namespace DefectMap
variable {d D} (S : DefectMap d D)

/-- Exact inputs remain exact; no section is used. -/
theorem preserves_exact (f : E) (hf : d f = 0) : D (S.candidate f) = 0 := by
  rw [S.commutes, hf, map_zero]

def coreMap : Core d →L[𝕜] Core D :=
  (S.candidate.comp (Core d).subtypeL).codRestrict (Core D)
    (fun f => S.preserves_exact f.val f.property)

@[simp] theorem coreMap_apply (e : Core d) : (S.coreMap e : F) = S.candidate e.val := rfl

theorem coreMap_bound (e : Core d) : ‖S.coreMap e‖ ≤ ‖S.candidate‖*‖e‖ :=
  S.candidate.le_opNorm e.val

def comp {d' : G →L[𝕜] U} (V : DefectMap D d') : DefectMap d d' where
  candidate := V.candidate.comp S.candidate
  residual := V.residual.comp S.residual
  commutes f := by simp only [ContinuousLinearMap.comp_apply, V.commutes, S.commutes]

@[simp] theorem comp_candidate {d' : G →L[𝕜] U} (V : DefectMap D d') (f : E) :
    (S.comp V).candidate f = V.candidate (S.candidate f) := rfl

@[simp] theorem comp_residual {d' : G →L[𝕜] U} (V : DefectMap D d') (r : R) :
    (S.comp V).residual r = V.residual (S.residual r) := rfl

variable (A : Section d) (B : Section D)

/-- Choice mismatch; applying D gives zero by the cochain and section identities. -/
def mismatch : R →L[𝕜] F :=
  S.candidate.comp A.lift - B.lift.comp S.residual

@[simp] theorem mismatch_apply (r : R) :
    S.mismatch A B r = S.candidate (A.lift r) - B.lift (S.residual r) := rfl

@[simp] theorem mismatch_exact (r : R) : D (S.mismatch A B r) = 0 := by
  rw [mismatch_apply, map_sub, S.commutes, A.right_inv, B.right_inv, sub_self]

def coreMismatch : R →L[𝕜] Core D :=
  (S.mismatch A B).codRestrict (Core D) (S.mismatch_exact A B)

@[simp] theorem coreMismatch_apply (r : R) :
    (S.coreMismatch A B r : F) = S.mismatch A B r := rfl

/-- Exact formula for the noncommutativity of repair and presentation change. -/
theorem repair_change (f : E) :
    B.project (S.candidate f) - S.candidate (A.project f) = S.mismatch A B (d f) := by
  simp only [Section.project_apply, mismatch_apply, map_sub, S.commutes]
  abel

theorem repair_change_exact (f : E) :
    D (B.project (S.candidate f) - S.candidate (A.project f)) = 0 := by
  rw [repair_change]
  exact S.mismatch_exact A B (d f)

theorem repair_change_bound (f : E) :
    ‖B.project (S.candidate f) - S.candidate (A.project f)‖ ≤
      ‖S.mismatch A B‖ * ‖d f‖ := by
  rw [repair_change]
  exact (S.mismatch A B).le_opNorm _

theorem mismatch_opNorm : ‖S.mismatch A B‖ ≤
    ‖S.candidate‖*‖A.lift‖ + ‖B.lift‖*‖S.residual‖ := by
  exact (norm_sub_le _ _).trans
    (add_le_add (S.candidate.opNorm_comp_le _) (B.lift.opNorm_comp_le _))

theorem repair_change_gain_bound (f : E) :
    ‖B.project (S.candidate f) - S.candidate (A.project f)‖ ≤
      (‖S.candidate‖*‖A.lift‖ + ‖B.lift‖*‖S.residual‖) * ‖d f‖ :=
  (S.repair_change_bound A B f).trans
    (mul_le_mul_of_nonneg_right (S.mismatch_opNorm A B) (norm_nonneg _))

/-- Commutation of repair is equivalent to compatibility of the chosen sections. -/
theorem repair_natural_iff :
    (∀ f, B.project (S.candidate f) = S.candidate (A.project f)) ↔
      S.candidate.comp A.lift = B.lift.comp S.residual := by
  constructor
  · intro h
    ext r
    have hz : S.mismatch A B r = 0 := by
      have hm := S.repair_change A B (A.lift r)
      rw [A.right_inv, h, sub_self] at hm
      exact hm.symm
    exact sub_eq_zero.mp hz
  · intro h f
    apply sub_eq_zero.mp
    rw [S.repair_change]
    change (S.candidate.comp A.lift) (d f) - (B.lift.comp S.residual) (d f) = 0
    rw [h, sub_self]

/-- In coordinates, a cochain map is block triangular, not necessarily block diagonal. -/
theorem chart_formula (z : Core d × R) :
    B.chart (S.candidate (A.chart.symm z)) =
      (S.coreMap z.1 + S.coreMismatch A B z.2, S.residual z.2) := by
  apply Prod.ext
  · apply Subtype.ext
    change B.project (S.candidate (z.1.val + A.lift z.2)) =
      S.candidate z.1.val + (S.candidate (A.lift z.2) - B.lift (S.residual z.2))
    rw [map_add, map_add, B.project_fixes _ (S.preserves_exact z.1.val z.1.property),
      Section.project_apply, S.commutes, A.right_inv]
  · change D (S.candidate (z.1.val + A.lift z.2)) = S.residual z.2
    have hz : d z.1.val = 0 := z.1.property
    rw [S.commutes, map_add, hz, A.right_inv, zero_add]

/-- The mismatch satisfies an exact composition law for two presentation changes. -/
theorem mismatch_comp {d' : G →L[𝕜] U} (V : DefectMap D d')
    (C : Section d') (r : R) :
    (S.comp V).mismatch A C r =
      V.candidate (S.mismatch A B r) + V.mismatch B C (S.residual r) := by
  simp only [mismatch_apply, comp_candidate, comp_residual, map_sub]
  abel

/-- If residuals vanish along a sequence, the two repair routes approach one another. -/
theorem repair_discrepancy_tendsto_zero (f : ℕ → E)
    (hf : Filter.Tendsto (fun n => d (f n)) Filter.atTop (nhds 0)) :
    Filter.Tendsto (fun n => B.project (S.candidate (f n)) - S.candidate (A.project (f n)))
      Filter.atTop (nhds 0) := by
  have hc := ((S.mismatch A B).continuous.tendsto (0 : R)).comp hf
  simpa only [map_zero, Function.comp_def, ← S.repair_change A B] using hc

end DefectMap
end SplitDefect
end KomorebiSpace
end
