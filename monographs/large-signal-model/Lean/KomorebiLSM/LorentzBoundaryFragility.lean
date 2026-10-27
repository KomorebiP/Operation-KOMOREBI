import KomorebiLSM.LorentzCylinder

/-! P72: a literal rank-one spatial perturbation of exactly prescribed
normalized base-norm size breaks every boundary image in positive dimension. -/
set_option autoImplicit false
namespace Komorebi.LSM.LorentzBoundaryFragility
open LorentzCylinder
variable {V : Type*} [NormedAddCommGroup V] [NormedSpace ℝ V]

abbrev UnitSpatial (V : Type*) [NormedAddCommGroup V] := {v : V // ‖v‖≤1}
instance : Inhabited (UnitSpatial V) := ⟨⟨0,by simp⟩⟩

/-- The supremum is over the literal normalized Lorentz base and actual cone infimum. -/
noncomputable def normalizedSize (Delta : State V →L[ℝ] State V) : ℝ :=
  sSup (Set.range (fun v : UnitSpatial V => probabilityCone.value (Delta (1,v.1))))

/-- The actual mass-row-zero outer product epsilon (0,e) lambda. -/
noncomputable def outwardPerturbation (epsilon : ℝ) (e : V) : State V →L[ℝ] State V :=
  (ContinuousLinearMap.fst ℝ ℝ V).smulRight (0,epsilon • e)

@[simp] theorem outwardPerturbation_apply (epsilon : ℝ) (e : V) (z : State V) :
    outwardPerturbation epsilon e z=z.1 • (0,epsilon • e) := rfl

@[simp] theorem outwardPerturbation_normalized (epsilon : ℝ) (e v : V) :
    outwardPerturbation epsilon e (1,v)=(0,epsilon • e) := by
  rw [outwardPerturbation_apply,one_smul]

theorem outwardPerturbation_mass (epsilon : ℝ) (e : V) :
    (ContinuousLinearMap.fst ℝ ℝ V).comp (outwardPerturbation epsilon e)=0 := by
  apply ContinuousLinearMap.ext
  intro z
  change (outwardPerturbation epsilon e z).1=0
  simp [outwardPerturbation_apply]

/-- Its range is exactly the one-dimensional spatial line it adds. -/
theorem outwardPerturbation_range (epsilon : ℝ) (e : V) :
    LinearMap.range (outwardPerturbation epsilon e).toLinearMap=
      Submodule.span ℝ {(0,epsilon • e)} := by
  apply le_antisymm
  · rintro y ⟨z,rfl⟩
    exact Submodule.smul_mem _ z.1 (Submodule.subset_span (Set.mem_singleton _))
  · apply Submodule.span_le.mpr
    intro y hy
    rw [Set.mem_singleton_iff] at hy
    subst y
    exact ⟨(1,0),by simp⟩

theorem outwardPerturbation_rank_one (epsilon : ℝ) (hepsilon : 0<epsilon)
    (e : V) (he : ‖e‖=1) :
    Module.finrank ℝ (LinearMap.range (outwardPerturbation epsilon e).toLinearMap)=1 := by
  rw [outwardPerturbation_range]
  apply finrank_span_singleton
  intro h
  have hz : epsilon • e=0 := congrArg Prod.snd h
  have hn : ‖epsilon • e‖=epsilon := by
    rw [norm_smul,Real.norm_eq_abs,abs_of_pos hepsilon,he,mul_one]
  rw [hz,norm_zero] at hn
  linarith

/-- All normalized inputs receive the same spatial vector, so the supremum is exact. -/
theorem outwardPerturbation_size (epsilon : ℝ) (hepsilon : 0≤epsilon)
    (e : V) (he : ‖e‖=1) : normalizedSize (outwardPerturbation epsilon e)=epsilon := by
  have hvalue : ∀ v : UnitSpatial V,
      probabilityCone.value (outwardPerturbation epsilon e (1,v.1))=epsilon := by
    intro v
    rw [outwardPerturbation_normalized,value_zero_mass,norm_smul,Real.norm_eq_abs,
      abs_of_nonneg hepsilon,he,mul_one]
  simp only [normalizedSize,hvalue,Set.range_const,csSup_singleton]

/-- A unit outward ray exists also when the current boundary image is zero. -/
theorem exists_aligned_unit [Nontrivial V] (w : V) :
    ∃ e : V,‖e‖=1 ∧ ∀ t : ℝ,0≤t → ‖w+t • e‖=‖w‖+t := by
  by_cases hw : w=0
  · obtain ⟨x,hx⟩ := exists_ne (0 : V)
    have hxp : 0<‖x‖ := norm_pos_iff.mpr hx
    let e : V := ‖x‖⁻¹ • x
    have he : ‖e‖=1 := by
      rw [norm_smul,Real.norm_eq_abs,abs_of_pos (inv_pos.mpr hxp),inv_mul_cancel₀ hxp.ne']
    refine ⟨e,he,?_⟩
    intro t ht
    rw [hw,zero_add,norm_zero,norm_smul,Real.norm_eq_abs,abs_of_nonneg ht,he,mul_one,zero_add]
  · have hwp : 0<‖w‖ := norm_pos_iff.mpr hw
    let e : V := ‖w‖⁻¹ • w
    have he : ‖e‖=1 := by
      rw [norm_smul,Real.norm_eq_abs,abs_of_pos (inv_pos.mpr hwp),inv_mul_cancel₀ hwp.ne']
    have hwrep : w=‖w‖ • e := by
      change w=‖w‖ • (‖w‖⁻¹ • w)
      rw [smul_smul,mul_inv_cancel₀ hwp.ne',one_smul]
    refine ⟨e,he,?_⟩
    intro t ht
    calc
      ‖w+t • e‖=‖(‖w‖+t) • e‖ := by conv_lhs => rw [hwrep,← add_smul]
      _=‖w‖+t := by rw [norm_smul,Real.norm_eq_abs,abs_of_nonneg (by positivity),he,mul_one]

/-- The exact P72 obstruction, including nonzero and zero boundary images. -/
theorem boundary_fragility [Nontrivial V] (F : State V →L[ℝ] State V)
    (_hF : ∀ z∈cone,F z∈cone) (v : V) (_hv : ‖v‖≤1)
    (hboundary : (F (1,v)).1=‖(F (1,v)).2‖) (epsilon : ℝ) (hepsilon : 0<epsilon) :
    ∃ Delta : State V →L[ℝ] State V,
      (ContinuousLinearMap.fst ℝ ℝ V).comp Delta=0 ∧
      Module.finrank ℝ (LinearMap.range Delta.toLinearMap)=1 ∧
      normalizedSize Delta=epsilon ∧ (F+Delta) (1,v)∉cone := by
  obtain ⟨e,he,halign⟩ := exists_aligned_unit (F (1,v)).2
  refine ⟨outwardPerturbation epsilon e,outwardPerturbation_mass epsilon e,
    outwardPerturbation_rank_one epsilon hepsilon e he,outwardPerturbation_size epsilon hepsilon.le e he,?_⟩
  intro hcone
  simp only [mem_cone,add_apply,outwardPerturbation_normalized,Prod.fst_add,Prod.snd_add,add_zero] at hcone
  rw [halign epsilon hepsilon.le,← hboundary] at hcone
  linarith

/-- In zero spatial dimension, a zero mass row forces the entire perturbation to vanish. -/
theorem mass_row_zero_of_subsingleton [Subsingleton V] (Delta : State V →L[ℝ] State V)
    (hm : (ContinuousLinearMap.fst ℝ ℝ V).comp Delta=0) : Delta=0 := by
  apply ContinuousLinearMap.ext
  intro z
  apply Prod.ext
  · exact congrArg (fun L : State V →L[ℝ] ℝ => L z) hm
  · exact Subsingleton.elim _ _

theorem zero_dimensional_impossibility [Subsingleton V] (epsilon : ℝ) (hepsilon : 0<epsilon) :
    ¬∃ Delta : State V →L[ℝ] State V,
      (ContinuousLinearMap.fst ℝ ℝ V).comp Delta=0 ∧ normalizedSize Delta=epsilon := by
  rintro ⟨Delta,hm,hsize⟩
  rw [mass_row_zero_of_subsingleton Delta hm] at hsize
  have hzero : normalizedSize (0 : State V →L[ℝ] State V)=0 := by
    simp [normalizedSize,probabilityCone.value_zero]
  rw [hzero] at hsize
  linarith

/-- The source's d≥1 case is the actual finite Euclidean spatial space. -/
theorem euclidean_boundary_fragility {D : Type*} [Fintype D] [Nonempty D]
    (F : State (EuclideanSpace ℝ D) →L[ℝ] State (EuclideanSpace ℝ D))
    (hF : ∀ z∈cone,F z∈cone) (v : EuclideanSpace ℝ D) (hv : ‖v‖≤1)
    (hboundary : (F (1,v)).1=‖(F (1,v)).2‖) (epsilon : ℝ) (hepsilon : 0<epsilon) :
    ∃ Delta : State (EuclideanSpace ℝ D) →L[ℝ] State (EuclideanSpace ℝ D),
      (ContinuousLinearMap.fst ℝ ℝ (EuclideanSpace ℝ D)).comp Delta=0 ∧
      Module.finrank ℝ (LinearMap.range Delta.toLinearMap)=1 ∧
      normalizedSize Delta=epsilon ∧ (F+Delta) (1,v)∉cone :=
  boundary_fragility F hF v hv hboundary epsilon hepsilon

end Komorebi.LSM.LorentzBoundaryFragility
