import Komorebi.Foundation.InternalSelection

/-! # Internally coded composition and transport of smallness -/

universe u v

namespace Komorebi.InternalGraphTransport

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces InternalSelection

variable {M : Type u} [language.Structure M]

def composeF {α : Type v} (a c f g : α) : language.Formula α :=
  exF (pairMemF (some a) none (some f) ⊓ pairMemF none (some c) (some g))

@[simp]
theorem composeF_realize {α : Type v} (a c f g : α) (e : α → M) :
    (composeF a c f g).Realize e ↔
      ∃ b : M, PairMember (e a) b (e f) ∧ PairMember b (e c) (e g) := by
  simp [composeF,assign]

/-- Composition is constructed by a bounded formula on the product, not by
external composition followed by an assumed graph-representation principle. -/
theorem composition_exists (h : AxiomSemantics M) {x y z f g : M}
    (hf : FunctionGraph x y f) (hg : FunctionGraph y z g) :
    ∃ c : M, FunctionGraph x z c ∧
      ∀ a d : M, PairMember a d c ↔
        ∃ b : M, PairMember a b f ∧ PairMember b d g := by
  let φ : language.Formula (Option (Option (Fin 2))) :=
    composeF none (some none) (some (some 0)) (some (some 1))
  obtain ⟨c,p,hp,hcp,hc⟩ := relationSet_exists h φ ![f,g] x z
  have hc' : ∀ a d : M, PairMember a d c ↔
      ∃ b : M, PairMember a b f ∧ PairMember b d g := by
    intro a d
    have hc'' : PairMember a d c ↔ member a x ∧ member d z ∧
        ∃ b : M, PairMember a b f ∧ PairMember b d g := by
      simpa [φ,assign] using hc a d
    refine hc''.trans ?_
    constructor
    · exact fun ha => ha.2.2
    · rintro ⟨b,hab,hbd⟩
      exact ⟨(functionGraph_pair_bounds hf hab).1,
        (functionGraph_pair_bounds hg hbd).2,b,hab,hbd⟩
  refine ⟨c,⟨⟨p,hp,hcp⟩,?_⟩,hc'⟩
  intro a ha
  obtain ⟨b,hab,_⟩ := hf.2 a ha
  obtain ⟨d,hbd,_⟩ := hg.2 b (functionGraph_pair_bounds hf hab).2
  refine ⟨d,(hc' a d).mpr ⟨b,hab,hbd⟩,?_⟩
  intro d' had'
  obtain ⟨b',hab',hb'd'⟩ := (hc' a d').mp had'
  have hbb' : b' = b := functionGraph_value_unique hf hab' hab
  subst b'
  exact functionGraph_value_unique hg hb'd' hbd

theorem embeds_trans (h : AxiomSemantics M) {x y z : M}
    (hxy : Embeds x y) (hyz : Embeds y z) : Embeds x z := by
  obtain ⟨f,hf,hif⟩ := hxy
  obtain ⟨g,hg,hig⟩ := hyz
  obtain ⟨c,hc,hcomp⟩ := composition_exists h hf hg
  refine ⟨c,hc,?_⟩
  intro a ha b hb d had hbd
  obtain ⟨a',haa',ha'd⟩ := (hcomp a d).mp had
  obtain ⟨b',hbb',hb'd⟩ := (hcomp b d).mp hbd
  have hab' : a' = b' := hig a' (functionGraph_pair_bounds hf haa').2
    b' (functionGraph_pair_bounds hf hbb').2 d ha'd hb'd
  subst b'
  exact hif a ha b hb a' haa' hbb'

/-- Smallness is preserved by an internal injection into a small internal set. -/
theorem small_of_embeds (h : AxiomSemantics M) {k x y : M}
    (hxy : Embeds x y) (hy : Small k y) : Small k x := by
  obtain ⟨a,hak,hya⟩ := hy
  exact ⟨a,hak,embeds_trans h hxy hya⟩

/-- Any two internally represented graphs with the same pairs are equal. -/
theorem functionGraph_ext (h : AxiomSemantics M) {x y f g : M}
    (hf : FunctionGraph x y f) (hg : FunctionGraph x y g)
    (he : ∀ a b : M, PairMember a b f ↔ PairMember a b g) : f = g := by
  apply h.extensionality f g
  intro p
  constructor
  · intro hpf
    obtain ⟨q,hq,hfq⟩ := hf.1
    obtain ⟨a,ha,b,hb,hab⟩ := (hq p).mp (hfq p hpf)
    obtain ⟨r,hr,hrg⟩ := (he a b).mp ⟨p,hab,hpf⟩
    have hpr : p = r := orderedPair_unique h hab hr
    exact hpr ▸ hrg
  · intro hpg
    obtain ⟨q,hq,hgq⟩ := hg.1
    obtain ⟨a,ha,b,hb,hab⟩ := (hq p).mp (hgq p hpg)
    obtain ⟨r,hr,hrf⟩ := (he a b).mpr ⟨p,hab,hpg⟩
    have hpr : p = r := orderedPair_unique h hab hr
    exact hpr ▸ hrf


/-- The internal image of a small set is small. A section of the inverse relation
is constructed internally and is an injection into the original domain. -/
theorem small_of_surjection (h : AxiomSemantics M) {k x y f : M}
    (hf : FunctionGraph x y f) (hx : Small k x)
    (hsurj : ∀ b : M, member b y → ∃ a : M, member a x ∧ PairMember a b f) :
    Small k y := by
  let φ : language.Formula (Option (Option (Fin 1))) :=
    pairMemF (some none) none (some (some 0))
  obtain ⟨r,_,_,_,hr⟩ := relationSet_exists h φ ![f] y x
  have hr' : ∀ b a : M, PairMember b a r ↔ member b y ∧ member a x ∧ PairMember a b f := by
    intro b a
    simpa [φ,assign] using hr b a
  have htotal : ∀ b : M, member b y → ∃ a : M, member a x ∧ PairMember b a r := by
    intro b hb
    obtain ⟨a,ha,hab⟩ := hsurj b hb
    exact ⟨a,ha,(hr' b a).mpr ⟨hb,ha,hab⟩⟩
  obtain ⟨g,hg,hgr⟩ := internal_selection h y x r htotal
  have hembed : Embeds y x := by
    refine ⟨g,hg,?_⟩
    intro b _ c _ a hba hca
    exact functionGraph_value_unique hf ((hr' b a).mp (hgr b a hba)).2.2
      ((hr' c a).mp (hgr c a hca)).2.2
  exact small_of_embeds h hembed hx


/-- Functional Replacement followed by bounded graph comprehension. This is
restricted to an actual finite-parameter formula, not an arbitrary external map. -/
theorem definable_image_function (h : AxiomSemantics M) {n : ℕ}
    (φ : language.Formula (Option (Option (Fin n)))) (e : Fin n → M) (x : M)
    (hfun : ∀ a : M, member a x → ∃! b : M, φ.Realize (assign (assign e b) a)) :
    ∃ y f : M, FunctionGraph x y f ∧
      (∀ a b : M, PairMember a b f ↔ member a x ∧ φ.Realize (assign (assign e b) a)) ∧
      (∀ b : M, member b y ↔ ∃ a : M, member a x ∧ φ.Realize (assign (assign e b) a)) := by
  obtain ⟨y,hy⟩ := h.replacement n φ e x hfun
  obtain ⟨f,p,hp,hfp,hf⟩ := relationSet_exists h φ e x y
  have hf' : ∀ a b : M, PairMember a b f ↔ member a x ∧ φ.Realize (assign (assign e b) a) := by
    intro a b
    refine (hf a b).trans ?_
    constructor
    · exact fun h => ⟨h.1,h.2.2⟩
    · exact fun h => ⟨h.1,(hy b).mpr ⟨a,h⟩,h.2⟩
  refine ⟨y,f,⟨⟨p,hp,hfp⟩,?_⟩,hf',hy⟩
  intro a ha
  obtain ⟨b,hb,hunique⟩ := hfun a ha
  exact ⟨b,(hf' a b).mpr ⟨ha,hb⟩,fun c hc => hunique c ((hf' a c).mp hc).2⟩

end Komorebi.InternalGraphTransport
