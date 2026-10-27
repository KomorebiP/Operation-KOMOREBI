module
public import MatrixSmith
public import KomorebiPadic.PrimeIdealGenerators

@[expose] public section

/- Compatibility with Mathlib's modules. The predecessor matrix definitions are unchanged. -/
namespace Komorebi.Representation.Matrix
open scoped BigOperators
universe u
variable {R : Type u} [CommRing R]

@[simp] theorem fsum_eq_finset_sum (n : Nat) (f : Fin n → R) :
    fsum n f = ∑ i, f i := by
  induction n with
  | zero => simp [fsum]
  | succ n ih =>
    rw [fsum, ih, Fin.sum_univ_succ]

noncomputable def matrixLinear {n m : Nat} (A : Mat R n m) :
    (Fin m → R) →ₗ[R] (Fin n → R) where
  toFun := mv A
  map_add' x y := by
    ext i
    simp [mv, mul_add, Finset.sum_add_distrib]
  map_smul' a x := by
    ext i
    simp [mv, Finset.mul_sum, mul_left_comm]

@[simp] theorem matrixLinear_apply {n m : Nat} (A : Mat R n m) (x : Fin m → R) :
    matrixLinear A x = mv A x := rfl

/-- Any sufficient initial encoding must distinguish unequal certificate images.
The competitor need not have linear transitions or observations. -/
theorem sufficient_encoding_kernel {d t k o l : Nat}
    (c : CertificateData R d t k o l) (hc : Valid c)
    {Z : Type u} (U : System Z (Fin k) (Fin o) R) (e : (Fin d → R) → Z)
    (he : ∀ x w j, behavior (sourceSystem c) x w j = behavior U (e x) w j)
    {x y : Fin d → R} (hxy : e x = e y) :
    mv c.encoding x = mv c.encoding y := by
  apply (matrix_behavior_exact c hc x y).mp
  intro w j
  rw [he x w j, he y w j, hxy]

/-- A sufficient linear initial encoding maps its actual image onto the
certificate's product of principal ideals. The construction never divides by a weight. -/
noncomputable def encodingToPrincipal {d t k o l n : Nat}
    (c : CertificateData R d t k o l) (s : SmithData R d t)
    (hs : SmithValid c.encoding s)
    (e : (Fin d → R) →ₗ[R] (Fin n → R))
    (hker : ∀ x y, e x = e y → mv c.encoding x = mv c.encoding y) :
    LinearMap.range e →ₗ[R] KomorebiPadic.PrincipalFamily s.weights := by
  classical
  let choosePre (z : LinearMap.range e) : Fin d → R := Classical.choose z.property
  have choose_eq (z : LinearMap.range e) : e (choosePre z) = z.val :=
    Classical.choose_spec z.property
  let value (z : LinearMap.range e) : KomorebiPadic.PrincipalFamily s.weights :=
    fun i => ⟨mv c.encoding (choosePre z) i,
      by
        obtain ⟨a,ha⟩ := (smith_image_iff c.encoding s hs (mv c.encoding (choosePre z))).mp
          ⟨choosePre z, rfl⟩ i
        exact Ideal.mem_span_singleton.mpr ⟨a,ha.symm⟩⟩
  refine {
    toFun := value
    map_add' := ?_
    map_smul' := ?_ }
  · intro a b
    have hz : e (choosePre (a+b)) = e (choosePre a + choosePre b) := by
      rw [map_add, choose_eq, choose_eq, choose_eq]
      rfl
    have hp := hker _ _ hz
    have hl := (matrixLinear c.encoding).map_add (choosePre a) (choosePre b)
    ext i
    change mv c.encoding (choosePre (a+b)) i =
      mv c.encoding (choosePre a) i + mv c.encoding (choosePre b) i
    rw [hp]
    exact congrFun hl i
  · intro a b
    have hz : e (choosePre (a • b)) = e (a • choosePre b) := by
      rw [map_smul, choose_eq, choose_eq]
      rfl
    have hp := hker _ _ hz
    have hl := (matrixLinear c.encoding).map_smul a (choosePre b)
    ext i
    change mv c.encoding (choosePre (a • b)) i = a * mv c.encoding (choosePre b) i
    rw [hp]
    exact congrFun hl i

@[simp] theorem encodingToPrincipal_apply {d t k o l n : Nat}
    (c : CertificateData R d t k o l) (s : SmithData R d t)
    (hs : SmithValid c.encoding s)
    (e : (Fin d → R) →ₗ[R] (Fin n → R))
    (hker : ∀ x y, e x = e y → mv c.encoding x = mv c.encoding y)
    (x : Fin d → R) (i : Fin t) :
    ((encodingToPrincipal c s hs e hker ⟨e x, ⟨x,rfl⟩⟩) i : R) =
      mv c.encoding x i := by
  change mv c.encoding (Classical.choose (show ∃ y, e y = e x from ⟨x,rfl⟩)) i = _
  exact congrFun (hker _ x (Classical.choose_spec (show ∃ y, e y = e x from ⟨x,rfl⟩))) i

theorem encodingToPrincipal_surjective {d t k o l n : Nat}
    (c : CertificateData R d t k o l) (s : SmithData R d t)
    (hs : SmithValid c.encoding s)
    (e : (Fin d → R) →ₗ[R] (Fin n → R))
    (hker : ∀ x y, e x = e y → mv c.encoding x = mv c.encoding y) :
    Function.Surjective (encodingToPrincipal c s hs e hker) := by
  intro y
  have hy : PrincipalCoordinates s.weights (fun i => (y i : R)) :=
    by
      intro i
      obtain ⟨a,ha⟩ := Ideal.mem_span_singleton.mp (y i).property
      exact ⟨a,ha.symm⟩
  obtain ⟨x,hx⟩ := (smith_image_iff c.encoding s hs _).mpr hy
  refine ⟨⟨e x, ⟨x,rfl⟩⟩, ?_⟩
  ext i
  rw [encodingToPrincipal_apply]
  exact congrFun hx i

end Komorebi.Representation.Matrix
