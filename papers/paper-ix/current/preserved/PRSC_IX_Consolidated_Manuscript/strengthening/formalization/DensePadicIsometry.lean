/-
Author: Komorebi P.

An isometric map on the natural-number points of the p-adic integers extends
uniquely to an isometric bijection of the p-adic integers.
-/
module

public import Mathlib.NumberTheory.Padics.ProperSpace
public import Mathlib.Topology.MetricSpace.Isometry
public import Mathlib.Topology.UniformSpace.UniformEmbedding
public import CompactSelfIsometry

@[expose] public section

namespace KomorebiPaperIX.DensePadicIsometry

variable (p : ℕ) [Fact p.Prime]

/-- Interpret the prescribed values as a function on the natural-cast range,
equipped with the metric induced by the p-adic integers. -/
noncomputable def onNaturalRange (f : ℕ → ℤ_[p])
    (x : Set.range (Nat.cast : ℕ → ℤ_[p])) : ℤ_[p] :=
  f x.property.choose

theorem onNaturalRange_nat (f : ℕ → ℤ_[p]) (n : ℕ) :
    onNaturalRange p f ⟨(n : ℤ_[p]), ⟨n, rfl⟩⟩ = f n := by
  unfold onNaturalRange
  congr 1
  exact Nat.cast_injective (Exists.choose_spec (show ∃ m : ℕ, (m : ℤ_[p]) = n from ⟨n, rfl⟩))

theorem onNaturalRange_isometry (f : ℕ → ℤ_[p])
    (hdist : ∀ m n : ℕ, dist (f m) (f n) = dist (m : ℤ_[p]) (n : ℤ_[p])) :
    Isometry (onNaturalRange p f) := by
  apply Isometry.of_dist_eq
  intro x y
  change dist (f x.property.choose) (f y.property.choose) = dist (x : ℤ_[p]) (y : ℤ_[p])
  rw [hdist, x.property.choose_spec, y.property.choose_spec]

/-- Continuous extension from the dense natural-cast range. -/
noncomputable def extension (f : ℕ → ℤ_[p]) : ℤ_[p] → ℤ_[p] :=
  PadicInt.denseRange_natCast.extend (onNaturalRange p f)

theorem extension_continuous (f : ℕ → ℤ_[p])
    (hdist : ∀ m n : ℕ, dist (f m) (f n) = dist (m : ℤ_[p]) (n : ℤ_[p])) :
    Continuous (extension p f) :=
  (PadicInt.denseRange_natCast.uniformContinuous_extend
    (onNaturalRange_isometry p f hdist).uniformContinuous).continuous

theorem extension_nat (f : ℕ → ℤ_[p])
    (hdist : ∀ m n : ℕ, dist (f m) (f n) = dist (m : ℤ_[p]) (n : ℤ_[p])) (n : ℕ) :
    extension p f (n : ℤ_[p]) = f n := by
  exact (PadicInt.denseRange_natCast.extend_of_ind
    (onNaturalRange_isometry p f hdist).uniformContinuous
    ⟨(n : ℤ_[p]), ⟨n, rfl⟩⟩).trans (onNaturalRange_nat p f n)

theorem extension_isometry (f : ℕ → ℤ_[p])
    (hdist : ∀ m n : ℕ, dist (f m) (f n) = dist (m : ℤ_[p]) (n : ℤ_[p])) :
    Isometry (extension p f) := by
  have hc := extension_continuous p f hdist
  have heq : (fun z : ℤ_[p] × ℤ_[p] => dist (extension p f z.1) (extension p f z.2)) =
      (fun z : ℤ_[p] × ℤ_[p] => dist z.1 z.2) := by
    apply (PadicInt.denseRange_natCast.prodMap PadicInt.denseRange_natCast).equalizer
      ((hc.comp continuous_fst).dist (hc.comp continuous_snd))
      (continuous_fst.dist continuous_snd)
    funext z
    change dist (extension p f (z.1 : ℤ_[p])) (extension p f (z.2 : ℤ_[p])) = _
    rw [extension_nat p f hdist, extension_nat p f hdist]
    exact hdist z.1 z.2
  exact Isometry.of_dist_eq (fun x y => congrFun heq (x, y))

/-- Agreement on every natural number determines the entire continuous map. -/
theorem extension_unique (f : ℕ → ℤ_[p])
    (hdist : ∀ m n : ℕ, dist (f m) (f n) = dist (m : ℤ_[p]) (n : ℤ_[p]))
    (g : ℤ_[p] → ℤ_[p]) (hg : Continuous g)
    (hgnat : ∀ n : ℕ, g (n : ℤ_[p]) = f n) : g = extension p f := by
  apply PadicInt.denseRange_natCast.equalizer hg (extension_continuous p f hdist)
  funext n
  exact (hgnat n).trans (extension_nat p f hdist n).symm

theorem extension_surjective (f : ℕ → ℤ_[p])
    (hdist : ∀ m n : ℕ, dist (f m) (f n) = dist (m : ℤ_[p]) (n : ℤ_[p])) :
    Function.Surjective (extension p f) :=
  CompactSelfIsometry.surjective (extension_isometry p f hdist)

/-- The prescribed isometry on natural-number points determines an isometric
bijection of the entire space of p-adic integers. -/
noncomputable def extensionEquiv (f : ℕ → ℤ_[p])
    (hdist : ∀ m n : ℕ, dist (f m) (f n) = dist (m : ℤ_[p]) (n : ℤ_[p])) :
    ℤ_[p] ≃ᵢ ℤ_[p] where
  toEquiv := Equiv.ofBijective (extension p f)
    ⟨(extension_isometry p f hdist).injective, extension_surjective p f hdist⟩
  isometry_toFun := extension_isometry p f hdist

theorem extensionEquiv_apply (f : ℕ → ℤ_[p])
    (hdist : ∀ m n : ℕ, dist (f m) (f n) = dist (m : ℤ_[p]) (n : ℤ_[p]))
    (x : ℤ_[p]) : extensionEquiv p f hdist x = extension p f x := rfl

theorem extensionEquiv_nat (f : ℕ → ℤ_[p])
    (hdist : ∀ m n : ℕ, dist (f m) (f n) = dist (m : ℤ_[p]) (n : ℤ_[p])) (n : ℕ) :
    extensionEquiv p f hdist (n : ℤ_[p]) = f n :=
  extension_nat p f hdist n

theorem extensionEquiv_unique_continuous (f : ℕ → ℤ_[p])
    (hdist : ∀ m n : ℕ, dist (f m) (f n) = dist (m : ℤ_[p]) (n : ℤ_[p]))
    (g : ℤ_[p] → ℤ_[p]) (hg : Continuous g)
    (hgnat : ∀ n : ℕ, g (n : ℤ_[p]) = f n) : g = extensionEquiv p f hdist :=
  extension_unique p f hdist g hg hgnat

theorem extensionEquiv_unique (f : ℕ → ℤ_[p])
    (hdist : ∀ m n : ℕ, dist (f m) (f n) = dist (m : ℤ_[p]) (n : ℤ_[p]))
    (e : ℤ_[p] ≃ᵢ ℤ_[p]) (henat : ∀ n : ℕ, e (n : ℤ_[p]) = f n) :
    e = extensionEquiv p f hdist := by
  apply IsometryEquiv.ext
  exact congrFun (extensionEquiv_unique_continuous p f hdist e e.continuous henat)

theorem existsUnique_extensionEquiv (f : ℕ → ℤ_[p])
    (hdist : ∀ m n : ℕ, dist (f m) (f n) = dist (m : ℤ_[p]) (n : ℤ_[p])) :
    ∃! e : ℤ_[p] ≃ᵢ ℤ_[p], ∀ n : ℕ, e (n : ℤ_[p]) = f n :=
  ⟨extensionEquiv p f hdist, extensionEquiv_nat p f hdist,
    fun e he => extensionEquiv_unique p f hdist e he⟩

end KomorebiPaperIX.DensePadicIsometry
