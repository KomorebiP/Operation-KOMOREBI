module
public import KomorebiPadic.FiniteGenerators
public import Mathlib.Data.ZMod.Basic

@[expose] public section
set_option autoImplicit false
set_option linter.unusedSimpArgs false
set_option backward.isDefEq.respectTransparency false
namespace KomorebiPadic
open scoped BigOperators

abbrev PrincipalFamily {R I : Type*} [CommRing R] (w : I → R) :=
  (i : I) → Ideal.span ({w i} : Set R)

/-- Transfer a free finite basis along a surjective synthesis map. -/
theorem generators_of_free_surjection {R M I : Type*} [CommRing R] [AddCommGroup M]
    [Module R M] [Fintype I] (f : (I → R) →ₗ[R] M) (hf : Function.Surjective f) :
    HasGenerators R M (Fintype.card I) := by
  classical
  let b := (Pi.basisFun R I).reindex (Fintype.equivFin I)
  refine ⟨fun j => f (b j),?_⟩
  intro y
  obtain ⟨x,rfl⟩ := hf y
  refine ⟨fun j => b.repr x j,?_⟩
  change (∑ j, b.repr x j • f (b j))=f x
  calc
    _ = f (∑ j, b.repr x j • b j) := by simp only [map_sum,map_smul]
    _ = f x := congrArg f (b.sum_repr x)

noncomputable def dyadicResidue (r : ℕ) (hr : 0<r) : ZMod (2^r) →+* ZMod 2 :=
  ZMod.castHom (dvd_pow_self 2 (by omega : r≠0)) (ZMod 2)

/-- An annihilator of a nonzero element must have zero residue in the field.
This uses units, not the rank of an ambient reduction of the ideal. -/
theorem dyadic_annihilator_residue (r : ℕ) (hr : 0<r) {w x : ZMod (2^r)}
    (hw : w≠0) (h : w*x=0) : dyadicResidue r hr x=0 := by
  let : NeZero (2^r) := ⟨by positivity⟩
  by_contra hx
  have hval : ¬2 ∣ x.val := by
    intro hd
    apply hx
    have he : dyadicResidue r hr x=(x.val:ZMod 2) := by
      calc
        _ = dyadicResidue r hr (x.val:ZMod (2^r)) := congrArg (dyadicResidue r hr) (ZMod.natCast_zmod_val x).symm
        _ = _ := map_natCast (dyadicResidue r hr) x.val
    rw [he,ZMod.natCast_eq_zero_iff]
    exact hd
  have hu : IsUnit x := by
    have hh := (ZMod.isUnit_natCast_iff_not_dvd_pow Nat.prime_two hr (a:=x.val)).mpr hval
    simpa using hh
  apply hw
  exact hu.mul_right_cancel (by simpa using h)

/-- A product of t nonzero principal ideals requires at least t generators. -/
theorem principalFamily_generator_lower {I : Type*} [Fintype I]
    (r : ℕ) (hr : 0<r) (w : I → ZMod (2^r)) (hw : ∀ i, w i≠0)
    (n : ℕ) (hg : HasGenerators (ZMod (2^r)) (PrincipalFamily w) n) :
    Fintype.card I≤n := by
  classical
  obtain ⟨g,hg⟩ := hg
  choose b hb using fun (i : I) (j : Fin n) => Ideal.mem_span_singleton.mp (g j i).property
  let pi := dyadicResidue r hr
  let B : (Fin n → ZMod 2) →ₗ[ZMod 2] (I → ZMod 2) := {
    toFun a i := ∑ j, pi (b i j)*a j
    map_add' a c := by ext i; simp [mul_add,Finset.sum_add_distrib]
    map_smul' c a := by ext i; simp [Finset.mul_sum,mul_assoc,mul_left_comm] }
  have hs : Function.Surjective B := by
    intro y
    have hp : Function.Surjective pi := ZMod.castHom_surjective _
    choose c hc using fun i => hp (y i)
    let z : PrincipalFamily w := fun i => ⟨w i*c i,Ideal.mem_span_singleton.mpr ⟨c i,rfl⟩⟩
    obtain ⟨a,ha⟩ := hg z
    refine ⟨fun j => pi (a j),?_⟩
    funext i
    have hcoord := congrArg (fun t : PrincipalFamily w => (t i:ZMod (2^r))) ha
    have hm : w i*((∑ j, b i j*a j)-c i)=0 := by
      have hh : (∑ j, a j*(w i*b i j))=w i*c i := by
        simpa [Fintype.linearCombination_apply,z,hb] using hcoord
      rw [mul_sub,Finset.mul_sum]
      convert sub_eq_zero.mpr hh using 1
      congr 1
      apply Finset.sum_congr rfl
      intro j _
      ring
    have hz := dyadic_annihilator_residue r hr (hw i) hm
    have he : (∑ j, pi (b i j)*pi (a j))-y i=0 := by
      simpa [pi,map_sub,map_sum,map_mul,hc] using hz
    exact sub_eq_zero.mp he
  have hdim := LinearMap.finrank_le_finrank_of_surjective hs
  simpa [Module.finrank_pi,Module.finrank_fin_fun] using hdim

/-- Restriction to nonzero factors is surjective: zero factors are filled by zero. -/
noncomputable def principalFamilyRestrict {R I : Type*} [CommRing R] (w : I → R) :
    PrincipalFamily w →ₗ[R] PrincipalFamily (fun i : {i // w i≠0} => w i.val) where
  toFun a i := a i.val
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

theorem principalFamilyRestrict_surjective {R I : Type*} [CommRing R] (w : I → R) :
    Function.Surjective (principalFamilyRestrict w) := by
  classical
  intro a
  let b : PrincipalFamily w := fun i => if h:w i≠0 then a ⟨i,h⟩ else 0
  refine ⟨b,?_⟩
  funext i
  simp [principalFamilyRestrict,b,i.property]

/-- An explicit free synthesis indexed by the nonzero ideals. -/
noncomputable def principalFamilyFreeSynthesis {R I : Type*} [CommRing R] (w : I → R) :
    ({i // w i≠0} → R) →ₗ[R] PrincipalFamily w := by
  classical
  exact {
    toFun a i := ⟨if h:w i≠0 then w i*a ⟨i,h⟩ else 0,by
      split_ifs
      · exact Ideal.mem_span_singleton.mpr ⟨_,rfl⟩
      · exact Ideal.zero_mem _⟩
    map_add' a b := by
      ext i
      by_cases h:w i=0 <;> simp [h,mul_add]
    map_smul' c a := by
      ext i
      by_cases h:w i=0 <;> simp [h,mul_assoc,mul_left_comm] }

theorem principalFamilyFreeSynthesis_surjective {R I : Type*} [CommRing R] (w : I → R) :
    Function.Surjective (principalFamilyFreeSynthesis w) := by
  classical
  intro a
  choose c hc using fun i => Ideal.mem_span_singleton.mp (a i).property
  refine ⟨fun i => c i.val,?_⟩
  ext i
  by_cases h:w i≠0
  · simpa [principalFamilyFreeSynthesis,h] using (hc i).symm
  · have he : w i=0 := by simpa using h
    simp [principalFamilyFreeSynthesis,h,hc,he]

/-- Exact minimum generator count; zero ideals are discarded only as zero ideals. -/
theorem principalFamily_generators_iff {I : Type*} [Fintype I]
    (r : ℕ) (hr : 0<r) (w : I → ZMod (2^r)) (d : ℕ) :
    (∃ n≤d, HasGenerators (ZMod (2^r)) (PrincipalFamily w) n) ↔
      Fintype.card {i // w i≠0}≤d := by
  classical
  constructor
  · rintro ⟨n,hn,hg⟩
    have h := hg.map (principalFamilyRestrict w) (principalFamilyRestrict_surjective w)
    exact (principalFamily_generator_lower r hr (fun i : {i // w i≠0} => w i.val)
      (fun i => i.property) n h).trans hn
  · intro hd
    exact ⟨_,hd,generators_of_free_surjection (principalFamilyFreeSynthesis w)
      (principalFamilyFreeSynthesis_surjective w)⟩

end KomorebiPadic
