import KomorebiVerification.MathlibImports

/-!
# The one-block semisimple seed-rank formula

Let `k` be a division ring.  We identify the direct sum of `m` copies of `k^d` with
`d`-by-`m` matrices.  The ring `M_d(k)` acts diagonally, by multiplication
on the left.  This file proves that `r` such matrices can generate the whole
module exactly when `m ≤ r * d`.  Consequently the least possible number
of generators is the ceiling quotient `m ⌈/⌉ d` (for `0 < d`).

The proof is elementary and does not appeal to a pre-existing seed-rank
formula.  Its key step identifies module generation with spanning the space
of row vectors by the `r * d` rows of the proposed generators.
-/

set_option autoImplicit false

namespace Komorebi.PaperICompletion8.DivisionRows

open scoped BigOperators

universe u

variable {k : Type u} [DivisionRing k]
variable {r d m : ℕ}

/--
`LeftGenerates v` says that the `r` matrices `v i` generate all `d`-by-`m`
matrices under the diagonal left action of `M_d(k)`.
-/
def LeftGenerates
    (v : Fin r → Matrix (Fin d) (Fin m) k) : Prop :=
  ∀ X : Matrix (Fin d) (Fin m) k,
    ∃ A : Fin r → Matrix (Fin d) (Fin d) k,
      X = ∑ i, A i * v i

/-- The `r * d` rows of `v` span the row-vector space `k^m`. -/
def RowsSpan
    (v : Fin r → Matrix (Fin d) (Fin m) k) : Prop :=
  Submodule.span k
      (Set.range (fun p : Fin r × Fin d ↦ v p.1 p.2)) = ⊤

/--
Left module generation is exactly row spanning.  The assumption `0 < d` is
needed only in the forward direction, to read a row from a nonempty matrix.
-/
theorem leftGenerates_iff_rowsSpan
    (hd : 0 < d) (v : Fin r → Matrix (Fin d) (Fin m) k) :
    LeftGenerates v ↔ RowsSpan v := by
  classical
  constructor
  · intro hgen
    rw [RowsSpan]
    apply top_unique
    intro y _hy
    let a₀ : Fin d := ⟨0, hd⟩
    let X : Matrix (Fin d) (Fin m) k := fun _ ↦ y
    obtain ⟨A, hA⟩ := hgen X
    have hy : y = ∑ i, ∑ b, A i a₀ b • v i b := by
      funext j
      have hentry := congrFun (congrFun hA a₀) j
      simpa [X, Matrix.sum_apply, Matrix.mul_apply, smul_eq_mul] using hentry
    rw [hy]
    apply Submodule.sum_mem
    intro i _hi
    apply Submodule.sum_mem
    intro b _hb
    exact Submodule.smul_mem _ _
      (Submodule.subset_span (Set.mem_range_self (i, b)))
  · intro hrows X
    have hsurj :
        ∀ y : Fin m → k,
          ∃ c : Fin r × Fin d → k,
            ∑ p, c p • v p.1 p.2 = y := by
      have htop :
          ⊤ ≤ Submodule.span k
            (Set.range (fun p : Fin r × Fin d ↦ v p.1 p.2)) := by
        simpa [RowsSpan] using hrows.symm.le
      exact
        (Submodule.top_le_span_range_iff_forall_exists_fun
          (R := k) (v := fun p : Fin r × Fin d ↦ v p.1 p.2)).mp htop
    choose c hc using fun a : Fin d ↦ hsurj (X a)
    let A : Fin r → Matrix (Fin d) (Fin d) k :=
      fun i a b ↦ c a (i, b)
    refine ⟨A, ?_⟩
    ext a j
    have hrow := congrFun (hc a) j
    rw [Matrix.sum_apply]
    simp_rw [Matrix.mul_apply]
    change X a j = ∑ i, ∑ b, c a (i, b) * v i b j
    calc
      X a j = ∑ p : Fin r × Fin d, c a p * v p.1 p.2 j := by
        simpa [Pi.smul_apply, smul_eq_mul] using hrow.symm
      _ = ∑ i, ∑ b, c a (i, b) * v i b j :=
        Fintype.sum_prod_type _

/-- Any `r` left generators force the multiplicity bound `m ≤ r * d`. -/
theorem multiplicity_le_of_leftGenerates
    (hd : 0 < d) {v : Fin r → Matrix (Fin d) (Fin m) k}
    (hgen : LeftGenerates v) :
    m ≤ r * d := by
  have hrows := (leftGenerates_iff_rowsSpan hd v).mp hgen
  have hdim := finrank_le_of_span_eq_top (R := k) hrows
  simpa [Module.finrank_pi, Fintype.card_prod] using hdim

/--
If `m ≤ r * d`, an explicit family of `r` generators exists.  Its rows are
standard basis vectors, placed using an embedding `Fin m ↪ Fin r × Fin d`;
unused rows are zero.
-/
theorem exists_leftGenerators_of_le
    (hd : 0 < d) (h : m ≤ r * d) :
    ∃ v : Fin r → Matrix (Fin d) (Fin m) k, LeftGenerates v := by
  classical
  have he_nonempty : Nonempty (Fin m ↪ Fin r × Fin d) :=
    Function.Embedding.nonempty_of_card_le (by simpa using h)
  let e : Fin m ↪ Fin r × Fin d := Classical.choice he_nonempty
  let v : Fin r → Matrix (Fin d) (Fin m) k :=
    fun i a j ↦ if e j = (i, a) then 1 else 0
  have hv_basis (j : Fin m) :
      v (e j).1 (e j).2 = Pi.basisFun k (Fin m) j := by
    funext q
    simp [v, Pi.basisFun_apply, Pi.single_apply, e.injective.eq_iff]
  refine ⟨v, (leftGenerates_iff_rowsSpan hd v).mpr ?_⟩
  rw [RowsSpan]
  apply top_unique
  rw [← (Pi.basisFun k (Fin m)).span_eq]
  apply Submodule.span_mono
  rintro _ ⟨j, rfl⟩
  exact ⟨e j, hv_basis j⟩

/--
There exist `r` generators for `(k^d)^m` under `M_d(k)` exactly when
`m ≤ r * d`.
-/
theorem exists_leftGenerators_iff (hd : 0 < d) :
    (∃ v : Fin r → Matrix (Fin d) (Fin m) k, LeftGenerates v) ↔
      m ≤ r * d := by
  constructor
  · rintro ⟨v, hv⟩
    exact multiplicity_le_of_leftGenerates hd hv
  · exact exists_leftGenerators_of_le hd

/--
The ceiling quotient `m ⌈/⌉ d` is the least number of generators of the
one-simple-block module `(k^d)^m`.
-/
theorem ceilDiv_isLeast_generatorCount (hd : 0 < d) :
    IsLeast
      {r : ℕ |
        ∃ v : Fin r → Matrix (Fin d) (Fin m) k, LeftGenerates v}
      (m ⌈/⌉ d) := by
  constructor
  · apply (exists_leftGenerators_iff (k := k) (r := m ⌈/⌉ d) hd).mpr
    have hm : m ≤ d * (m ⌈/⌉ d) :=
      (ceilDiv_le_iff_le_mul hd).mp le_rfl
    simpa [Nat.mul_comm] using hm
  · intro r hr
    apply (ceilDiv_le_iff_le_mul hd).mpr
    have hm := (exists_leftGenerators_iff (k := k) (r := r) hd).mp hr
    simpa [Nat.mul_comm] using hm

end Komorebi.PaperICompletion8.DivisionRows

