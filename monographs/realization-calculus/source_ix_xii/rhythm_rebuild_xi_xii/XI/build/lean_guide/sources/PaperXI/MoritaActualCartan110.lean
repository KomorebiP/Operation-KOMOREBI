import PaperXI.MoritaIndex110
import PaperXI.ActualLocalCartan106
import PaperXI.MoritaCartanTransport110
import PaperXI.MoritaScalarUpgrade110

/-! Actual centralizer matrices act in the noncommutative endomorphism ring
through explicit ring homomorphisms. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MoritaActualCartan110
open Matrix Module ValuativeRel
open PaperXI.MoritaLattice110 PaperXI.MoritaCornerRank110 PaperXI.MoritaIndex110
open PaperXI.MoritaCartanTransport110
variable (F E : Type*) [Field F] [Field E] [Algebra F E]
  [Module.Finite F E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E]
variable (m : Type*) [Fintype m] [DecidableEq m]

/-- The actual E-linear centralizer embedded in F-linear matrix endomorphisms.
Units.map is used because the target coefficient ring need not be commutative. -/
def centralizerEmbedding : GL m E →* (Matrix m m (Module.End F E))ˣ :=
  Units.map (RingHom.mapMatrix (Algebra.lmul F E).toRingHom).toMonoidHom

def scalarEmbedding : Eˣ →* (Matrix m m (Module.End F E))ˣ :=
  (centralizerEmbedding F E m).comp (GeneralLinearGroup.scalar m)

def uniformizerEndUnit : (Module.End F E)ˣ := coefficientUnit F E
  (ActualLocalUnitDecomposition.uniformizer E)
  (ActualLocalUnitDecomposition.uniformizer_ne_zero E)

omit [Module.Finite F E] [TopologicalSpace E] [IsNonarchimedeanLocalField E] in
theorem centralizerEmbedding_integral (k : GL m 𝒪[E]) :
    centralizerEmbedding F E m (ActualIntegralGeneralLinear.embedding E m k) =
      mappedMatrixUnit (coefficientMap F E) k := by
  apply Units.ext
  rfl

omit [Module.Finite F E] [TopologicalSpace E] [IsNonarchimedeanLocalField E] in
theorem scalarEmbedding_integralUnit (v : 𝒪[E]ˣ) :
    scalarEmbedding F E m (ActualLocalUnitTopology.unitEmbedding E v) =
      mappedMatrixUnit (coefficientMap F E) (GeneralLinearGroup.scalar m v) := by
  apply Units.ext
  ext i j
  have hmap (x : 𝒪[E]) : algebraMap 𝒪[E] E x = (x : E) := rfl
  by_cases hij : i = j
  · subst j
    simp [scalarEmbedding, centralizerEmbedding, GeneralLinearGroup.scalar,
      Matrix.scalar_apply, Matrix.diagonal, mappedMatrixUnit, coefficientMap,
      ActualLocalUnitTopology.unitEmbedding, hmap]
  · simp [scalarEmbedding, centralizerEmbedding, GeneralLinearGroup.scalar,
      Matrix.scalar_apply, Matrix.diagonal, mappedMatrixUnit, hij]

omit [Module.Finite F E] in
theorem scalarEmbedding_uniformizer :
    scalarEmbedding F E m (ActualLocalUnitDecomposition.uniformizerUnit E) =
      diagonalUnit (fun _ : m => coefficientUnit F E
        (ActualLocalUnitDecomposition.uniformizer E)
        (ActualLocalUnitDecomposition.uniformizer_ne_zero E)) := by
  apply Units.ext
  ext i j
  by_cases hij : i = j
  · subst j
    simp [scalarEmbedding, centralizerEmbedding, GeneralLinearGroup.scalar,
      Matrix.scalar_apply, diagonalUnit, Matrix.diagonal,
      coefficientUnit, ActualLocalUnitDecomposition.uniformizerUnit]
  · simp [scalarEmbedding, centralizerEmbedding, GeneralLinearGroup.scalar,
      Matrix.scalar_apply, diagonalUnit, Matrix.diagonal, hij]

omit [Module.Finite F E] in
/-- Radical commutation and integral-unit stability imply that every actual
extension-field scalar normalizes the endomorphism lattice. -/
theorem scalarEmbedding_normalizes
    (L : AddSubgroup (Matrix m m (Module.End F E)))
    (hL : IsMatrixBimodule (coefficientMap F E) L)
    (hcomm : L.map (AddMonoidHom.mulLeft
        ((diagonalUnit (fun _ : m => uniformizerEndUnit F E) :
          (Matrix m m (Module.End F E))ˣ) : Matrix m m (Module.End F E))) =
      L.map (AddMonoidHom.mulRight
        ((diagonalUnit (fun _ : m => uniformizerEndUnit F E) :
          (Matrix m m (Module.End F E))ˣ) : Matrix m m (Module.End F E))))
    (c : Eˣ) : scalarEmbedding F E m c ∈ normalizingUnits L := by
  obtain ⟨⟨v, n⟩, rfl⟩ := ActualLocalUnitDecomposition.normalForm_surjective E c
  rw [ActualLocalUnitDecomposition.normalFormHom_apply, map_mul, map_zpow,
    scalarEmbedding_integralUnit F E m, scalarEmbedding_uniformizer F E m]
  exact (normalizingUnits L).mul_mem
    (mappedMatrixUnit_mem_normalizingUnits (coefficientMap F E) L hL
      (GeneralLinearGroup.scalar m v))
    ((normalizingUnits L).zpow_mem
      (normalizes_of_left_right_map_eq L (diagonalUnit (fun _ : m => uniformizerEndUnit F E))
        hcomm) n.toAdd)

omit [Module.Finite F E] in
theorem centralizerEmbedding_cartan (a : m → ℕ) :
    centralizerEmbedding F E m
      (PaperXI.SplitRadical105.cartan
        (ActualLocalUnitDecomposition.uniformizer E : E)
        (ActualLocalUnitDecomposition.uniformizer_ne_zero E) a) =
      diagonalUnit (fun i => uniformizerEndUnit F E ^ (-(a i : ℤ))) := by
  apply Units.ext
  apply Matrix.ext
  intro i j
  have hp (n : ℕ) :
      ((uniformizerEndUnit F E ^ (-(n : ℤ)) : (Module.End F E)ˣ) : Module.End F E) =
        (Algebra.lmul F E).toRingHom (((ActualLocalUnitDecomposition.uniformizer E : E) ^ n)⁻¹) := by
    change (((Units.map (Algebra.lmul F E).toRingHom)
      (ActualLocalUnitDecomposition.uniformizerUnit E) ^ (-(n : ℤ)) :
        (Module.End F E)ˣ) : Module.End F E) = _
    rw [← map_zpow]
    change (Algebra.lmul F E).toRingHom
      (((ActualLocalUnitDecomposition.uniformizerUnit E ^ (-(n : ℤ)) : Eˣ) : E)) = _
    congr 1
    simp [ActualLocalUnitDecomposition.uniformizerUnit]
  by_cases hij : i = j
  · subst j
    change (Algebra.lmul F E).toRingHom
      ((Matrix.diagonal (fun k =>
        ((ActualLocalUnitDecomposition.uniformizer E : E) ^ a k)⁻¹)) i i) =
      (Matrix.diagonal (fun k =>
        ((uniformizerEndUnit F E ^ (-(a k : ℤ)) : (Module.End F E)ˣ) : Module.End F E))) i i
    simp only [Matrix.diagonal_apply_eq]
    exact (hp (a i)).symm
  · simp [centralizerEmbedding, PaperXI.SplitRadical105.cartan,
      PaperXI.SplitRadical105.diagonalGL, diagonalUnit, Matrix.diagonal, hij]

/-- Literal equality of scalar-uniformizer images, the matrix form of radical
commutation used by this arithmetic calculation. -/
def RadicalCommutes (L : AddSubgroup (Matrix m m (Module.End F E))) : Prop :=
  L.map (AddMonoidHom.mulLeft
      ((diagonalUnit (fun _ : m => uniformizerEndUnit F E) :
        (Matrix m m (Module.End F E))ˣ) : Matrix m m (Module.End F E))) =
    L.map (AddMonoidHom.mulRight
      ((diagonalUnit (fun _ : m => uniformizerEndUnit F E) :
        (Matrix m m (Module.End F E))ˣ) : Matrix m m (Module.End F E)))

/-- Every actual Cartan factorization gives the same index for every finite full
integer-ring bimodule commuting with the scalar radical. -/
theorem relIndex_of_actual_cartan [Nonempty m]
    (L : Submodule 𝒪[E] (Matrix m m (Module.End F E)))
    (hL : IsMatrixBimodule (coefficientMap F E) L.toAddSubgroup)
    (hfg : L.FG)
    (hfull : Submodule.span F (L : Set (Matrix m m (Module.End F E))) = ⊤)
    (hcomm : RadicalCommutes F E m L.toAddSubgroup)
    (y : GL m E) (c : Eˣ) (l r : GL m 𝒪[E]) (a : m → ℕ)
    (hy : y = GeneralLinearGroup.scalar m c *
      (ActualIntegralGeneralLinear.embedding E m l *
        PaperXI.SplitRadical105.cartan (ActualLocalUnitDecomposition.uniformizer E : E)
          (ActualLocalUnitDecomposition.uniformizer_ne_zero E) a *
            ActualIntegralGeneralLinear.embedding E m r)) :
    (L.toAddSubgroup ⊓ L.toAddSubgroup.map
      (unitConjugation (centralizerEmbedding F E m y)).toAddMonoidHom).relIndex
        L.toAddSubgroup =
      Nat.card 𝓀[E] ^ (Module.finrank F E * ∑ i, ∑ j, ((a i : ℤ) - (a j : ℤ)).toNat) := by
  let k₁ := scalarEmbedding F E m c * mappedMatrixUnit (coefficientMap F E) l
  let d := diagonalUnit (fun i => uniformizerEndUnit F E ^ (-(a i : ℤ)))
  let k₂ := mappedMatrixUnit (coefficientMap F E) r
  have he : centralizerEmbedding F E m y = k₁ * d * k₂ := by
    rw [hy]
    simp only [map_mul, centralizerEmbedding_integral, centralizerEmbedding_cartan]
    change scalarEmbedding F E m c * (_ * _ * _) = _
    simp only [k₁, d, k₂, mul_assoc]
  have hk₁ : k₁ ∈ normalizingUnits L.toAddSubgroup :=
    (normalizingUnits L.toAddSubgroup).mul_mem
      (scalarEmbedding_normalizes F E m L.toAddSubgroup hL hcomm c)
      (mappedMatrixUnit_mem_normalizingUnits (coefficientMap F E) L.toAddSubgroup hL l)
  have hk₂ : k₂ ∈ normalizingUnits L.toAddSubgroup :=
    mappedMatrixUnit_mem_normalizingUnits (coefficientMap F E) L.toAddSubgroup hL r
  rw [he, intersection_relIndex_outer_factors L.toAddSubgroup k₁ d k₂ hk₁ hk₂]
  have hd := diagonal_relIndex_of_radical_commutation F E L hL
    (Classical.choice (inferInstance : Nonempty m)) hfg hfull
    (ActualLocalUnitDecomposition.uniformizer E)
    (ActualLocalUnitDecomposition.uniformizer_irreducible E)
    (uniformizerEndUnit F E) (coefficientUnit_coe F E _ _) hcomm
    (fun i => -(a i : ℤ))
  have hs : (∑ i, ∑ j, (-(a i : ℤ) - -(a j : ℤ)).toNat) =
      ∑ i, ∑ j, ((a i : ℤ) - (a j : ℤ)).toNat := by
    simp only [neg_sub_neg]
    exact Finset.sum_comm
  simpa only [hs] using hd

/-- The Cartan factorization is obtained from the authenticated actual local
field theorem, rather than supplied as an arithmetic-index hypothesis. -/
theorem exists_actual_cartan_index [Nonempty m]
    (L : Submodule 𝒪[E] (Matrix m m (Module.End F E)))
    (hL : IsMatrixBimodule (coefficientMap F E) L.toAddSubgroup)
    (hfg : L.FG)
    (hfull : Submodule.span F (L : Set (Matrix m m (Module.End F E))) = ⊤)
    (hcomm : RadicalCommutes F E m L.toAddSubgroup) (y : GL m E) :
    ∃ c : Eˣ, ∃ l r : GL m 𝒪[E], ∃ a : m → ℕ,
      (∃ i, a i = 0) ∧
      y = GeneralLinearGroup.scalar m c *
        (ActualIntegralGeneralLinear.embedding E m l *
          PaperXI.SplitRadical105.cartan (ActualLocalUnitDecomposition.uniformizer E : E)
            (ActualLocalUnitDecomposition.uniformizer_ne_zero E) a *
              ActualIntegralGeneralLinear.embedding E m r) ∧
      (L.toAddSubgroup ⊓ L.toAddSubgroup.map
        (unitConjugation (centralizerEmbedding F E m y)).toAddMonoidHom).relIndex
          L.toAddSubgroup =
        Nat.card 𝓀[E] ^ (Module.finrank F E * ∑ i, ∑ j, ((a i : ℤ) - (a j : ℤ)).toNat) := by
  obtain ⟨c, l, r, a, ha, hy⟩ := PaperXI.ActualLocalCartan106.hasCartan E m y
  exact ⟨c, l, r, a, ha, hy,
    relIndex_of_actual_cartan F E m L hL hfg hfull hcomm y c l r a hy⟩

/-- The finite-generation hypothesis may start with the genuine base-ring
lattice. Scalar stability is derived from its matrix bimodule, and the larger
scalar module keeps exactly the same additive carrier and full span. -/
theorem exists_actual_cartan_index_of_base_lattice [Nonempty m]
    {R : Type*} [Ring R]
    [Module R (Matrix m m (Module.End F E))] [SMul R 𝒪[E]]
    [IsScalarTower R 𝒪[E] (Matrix m m (Module.End F E))]
    (L : Submodule R (Matrix m m (Module.End F E)))
    (hL : IsMatrixBimodule (coefficientMap F E) L.toAddSubgroup)
    (hfg : L.FG)
    (hfull : Submodule.span F (L : Set (Matrix m m (Module.End F E))) = ⊤)
    (hcomm : RadicalCommutes F E m L.toAddSubgroup) (y : GL m E) :
    ∃ a : m → ℕ,
      (L.toAddSubgroup ⊓ L.toAddSubgroup.map
        (unitConjugation (centralizerEmbedding F E m y)).toAddMonoidHom).relIndex
          L.toAddSubgroup =
        Nat.card 𝓀[E] ^ (Module.finrank F E * ∑ i, ∑ j, ((a i : ℤ) - (a j : ℤ)).toNat) := by
  have hsmul : ∀ (s : 𝒪[E]) (x : Module.End F E),
      s • x = coefficientMap F E s * x := by intro s x; ext v; rfl
  let hstable := PaperXI.MoritaScalarUpgrade110.scalar_stable_of_matrix_bimodule
    (coefficientMap F E) hsmul L.toAddSubgroup hL
  let L' := PaperXI.MoritaScalarUpgrade110.upgrade L hstable
  have hfg' : L'.FG := PaperXI.MoritaScalarUpgrade110.upgrade_fg L hstable hfg
  obtain ⟨c, l, r, a, _, _, hindex⟩ :=
    exists_actual_cartan_index F E m L' hL hfg' hfull hcomm y
  exact ⟨a, hindex⟩

omit [Module.Finite F E] [ValuativeRel E] [TopologicalSpace E] [IsNonarchimedeanLocalField E] in
/-- Matrix rank zero has trivial lattice index. -/
theorem relIndex_isEmpty [IsEmpty m]
    (L : AddSubgroup (Matrix m m (Module.End F E))) (y : GL m E) :
    (L ⊓ L.map (unitConjugation (centralizerEmbedding F E m y)).toAddMonoidHom).relIndex L = 1 := by
  let K := (L ⊓ L.map (unitConjugation (centralizerEmbedding F E m y)).toAddMonoidHom).addSubgroupOf L
  have hz (z : L) : z = 0 := Subsingleton.elim _ _
  have hx (x : L ⧸ K) : x = 0 := by
    refine Quotient.inductionOn x ?_
    intro z
    rw [hz z]
    rfl
  let : Subsingleton (L ⧸ K) := ⟨fun x z => (hx x).trans (hx z).symm⟩
  exact Nat.card_unique

/-- Matrix rank one has no nonzero Cartan difference. -/
theorem relIndex_subsingleton [Nonempty m] [Subsingleton m]
    (L : Submodule 𝒪[E] (Matrix m m (Module.End F E)))
    (hL : IsMatrixBimodule (coefficientMap F E) L.toAddSubgroup)
    (hfg : L.FG)
    (hfull : Submodule.span F (L : Set (Matrix m m (Module.End F E))) = ⊤)
    (hcomm : RadicalCommutes F E m L.toAddSubgroup) (y : GL m E) :
    (L.toAddSubgroup ⊓ L.toAddSubgroup.map
      (unitConjugation (centralizerEmbedding F E m y)).toAddMonoidHom).relIndex
        L.toAddSubgroup = 1 := by
  obtain ⟨c, l, r, a, _, _, hindex⟩ :=
    exists_actual_cartan_index F E m L hL hfg hfull hcomm y
  have hs : (∑ i, ∑ j, ((a i : ℤ) - (a j : ℤ)).toNat) = 0 := by
    apply Finset.sum_eq_zero
    intro i _
    apply Finset.sum_eq_zero
    intro j _
    rw [Subsingleton.elim i j]
    simp
  simpa only [hs, Nat.mul_zero, pow_zero] using hindex

end PaperXI.MoritaActualCartan110
