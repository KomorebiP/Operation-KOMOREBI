module
public import KomorebiPadic.PrincipalIdealGenerators

@[expose] public section
set_option autoImplicit false
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option backward.isDefEq.respectTransparency false
namespace KomorebiPadic
open scoped BigOperators

noncomputable def primeResidue (p : ℕ) (hp : p.Prime) (r : ℕ) (hr : 0<r) : ZMod (p^r) →+* ZMod p :=
  ZMod.castHom (dvd_pow_self p (by omega : r≠0)) (ZMod p)

/-- An annihilator of a nonzero element must have zero residue in the field.
This uses units, not the rank of an ambient reduction of the ideal. -/
theorem prime_annihilator_residue (p : ℕ) (hp : p.Prime) (r : ℕ) (hr : 0<r) {w x : ZMod (p^r)}
    (hw : w≠0) (h : w*x=0) : primeResidue p hp r hr x=0 := by
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  by_contra hx
  have hval : ¬p ∣ x.val := by
    intro hd
    apply hx
    have he : primeResidue p hp r hr x=(x.val:ZMod p) := by
      calc
        _ = primeResidue p hp r hr (x.val:ZMod (p^r)) := congrArg (primeResidue p hp r hr) (ZMod.natCast_zmod_val x).symm
        _ = _ := map_natCast (primeResidue p hp r hr) x.val
    rw [he,ZMod.natCast_eq_zero_iff]
    exact hd
  have hu : IsUnit x := by
    have hh := (ZMod.isUnit_natCast_iff_not_dvd_pow hp hr (a:=x.val)).mpr hval
    simpa using hh
  apply hw
  exact hu.mul_right_cancel (by simpa using h)

/-- A product of t nonzero principal ideals requires at least t generators. -/
theorem primePrincipalFamily_generator_lower {I : Type*} [Fintype I]
    (p : ℕ) (hp : p.Prime) (r : ℕ) (hr : 0<r) (w : I → ZMod (p^r)) (hw : ∀ i, w i≠0)
    (n : ℕ) (hg : HasGenerators (ZMod (p^r)) (PrincipalFamily w) n) :
    Fintype.card I≤n := by
  let : Fact p.Prime := ⟨hp⟩
  classical
  obtain ⟨g,hg⟩ := hg
  choose b hb using fun (i : I) (j : Fin n) => Ideal.mem_span_singleton.mp (g j i).property
  let pi := primeResidue p hp r hr
  let B : (Fin n → ZMod p) →ₗ[ZMod p] (I → ZMod p) := {
    toFun a i := ∑ j, pi (b i j)*a j
    map_add' a c := by ext i; simp [mul_add,Finset.sum_add_distrib]
    map_smul' c a := by ext i; simp [Finset.mul_sum,mul_assoc,mul_left_comm] }
  have hs : Function.Surjective B := by
    intro y
    have hpi : Function.Surjective pi := ZMod.castHom_surjective _
    choose c hc using fun i => hpi (y i)
    let z : PrincipalFamily w := fun i => ⟨w i*c i,Ideal.mem_span_singleton.mpr ⟨c i,rfl⟩⟩
    obtain ⟨a,ha⟩ := hg z
    refine ⟨fun j => pi (a j),?_⟩
    funext i
    have hcoord := congrArg (fun t : PrincipalFamily w => (t i:ZMod (p^r))) ha
    have hm : w i*((∑ j, b i j*a j)-c i)=0 := by
      have hh : (∑ j, a j*(w i*b i j))=w i*c i := by
        simpa [Fintype.linearCombination_apply,z,hb] using hcoord
      rw [mul_sub,Finset.mul_sum]
      convert sub_eq_zero.mpr hh using 1
      congr 1
      apply Finset.sum_congr rfl
      intro j _
      ring
    have hz := prime_annihilator_residue p hp r hr (hw i) hm
    have he : (∑ j, pi (b i j)*pi (a j))-y i=0 := by
      simpa [pi,map_sub,map_sum,map_mul,hc] using hz
    exact sub_eq_zero.mp he
  have hdim := LinearMap.finrank_le_finrank_of_surjective hs
  simpa [Module.finrank_pi,Module.finrank_fin_fun] using hdim

/-- Exact minimum generator count; zero ideals are discarded only as zero ideals. -/
theorem primePrincipalFamily_generators_iff {I : Type*} [Fintype I]
    (p : ℕ) (hp : p.Prime) (r : ℕ) (hr : 0<r) (w : I → ZMod (p^r)) (d : ℕ) :
    (∃ n≤d, HasGenerators (ZMod (p^r)) (PrincipalFamily w) n) ↔
      Fintype.card {i // w i≠0}≤d := by
  classical
  constructor
  · rintro ⟨n,hn,hg⟩
    have h := hg.map (principalFamilyRestrict w) (principalFamilyRestrict_surjective w)
    exact (primePrincipalFamily_generator_lower p hp r hr (fun i : {i // w i≠0} => w i.val)
      (fun i => i.property) n h).trans hn
  · intro hd
    exact ⟨_,hd,generators_of_free_surjection (principalFamilyFreeSynthesis w)
      (principalFamilyFreeSynthesis_surjective w)⟩


end KomorebiPadic
