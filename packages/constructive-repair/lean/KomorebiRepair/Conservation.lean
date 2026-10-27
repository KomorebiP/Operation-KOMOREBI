import KomorebiRepair.Menu

/-! # Conservation constraints forbid inadmissible repairs -/
namespace KomorebiRepair

variable {k U V W Z J : Type*} [CommRing k]
  [AddCommGroup U] [Module k U] [AddCommGroup V] [Module k V]
  [AddCommGroup W] [Module k W] [AddCommGroup Z] [Module k Z]

theorem invariant_preserved (D : U →ₗ[k] V) (E : W →ₗ[k] V) (L : V →ₗ[k] Z)
    (hD : L.comp D = 0) (hE : L.comp E = 0) (v : V) (u : U) (w : W) :
    L (v + D u + E w) = L v := by
  have hd : L (D u) = 0 := LinearMap.congr_fun hD u
  have he : L (E w) = 0 := LinearMap.congr_fun hE w
  simp only [map_add, hd, he, add_zero]

theorem conservation_no_go (D : U →ₗ[k] V) (E : W →ₗ[k] V) (L : V →ₗ[k] Z)
    (hD : L.comp D = 0) (hE : L.comp E = 0) (r : V) (hr : L r ≠ 0) :
    ¬ Repairable D E r := by
  rintro ⟨u, w, h⟩
  have hd : L (D u) = 0 := LinearMap.congr_fun hD u
  have he : L (E w) = 0 := LinearMap.congr_fun hE w
  have hh := congrArg L h
  have hz : L r = 0 := by
    simpa only [map_add, map_neg, hd, he, zero_add, zero_eq_neg] using hh
  exact hr hz

theorem menu_preserves_invariant (e : J → V) (S : Finset J) (L : V →ₗ[k] Z)
    (h : ∀ j ∈ S, L (e j) = 0) : L.comp (menuMap e S) = 0 := by
  ext a
  simp only [LinearMap.comp_apply, menuMap_apply, map_sum, map_smul, LinearMap.zero_apply]
  apply Finset.sum_eq_zero
  intro j _
  rw [h j j.property, smul_zero]

theorem conservation_menu_no_go (D : U →ₗ[k] V) (e : J → V) (S : Finset J)
    (L : V →ₗ[k] Z) (hD : L.comp D = 0) (he : ∀ j ∈ S, L (e j) = 0)
    (r : V) (hr : L r ≠ 0) : ¬ Repairable D (menuMap e S) r :=
  conservation_no_go D (menuMap e S) L hD (menu_preserves_invariant e S L he) r hr

end KomorebiRepair
