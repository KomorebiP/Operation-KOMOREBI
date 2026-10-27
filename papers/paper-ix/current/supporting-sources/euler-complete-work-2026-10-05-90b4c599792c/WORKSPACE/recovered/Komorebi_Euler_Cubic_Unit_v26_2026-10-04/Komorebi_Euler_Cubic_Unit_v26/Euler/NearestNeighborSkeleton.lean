module
public import Euler.NearestNeighborArithmetic
public import Euler.FourScaledSeries
public import Euler.SkeletonLocalSeries
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

lemma series_coe_poly_prod {ι:Type*} (s:Finset ι) (f:ι→Polynomial D) :
    (↑(∏ i∈s, f i : Polynomial D):Series) = ∏i∈s,(f i:Series) := by
  exact map_prod (Polynomial.coeToPowerSeries.ringHom : Polynomial D →+* Series) f s

/-- Isolate one distinguished factor; every other factor is four-weighted. -/
lemma fourScaled_prod_extract {ι:Type*} [DecidableEq ι] (s:Finset ι)
    (f:ι→Series) (a:ι) (N:Series)
    (ha:∃e:Series, f a=N*rescale (4:D) e)
    (hf:∀i∈s, i≠a → FourScaled (f i)) :
    ∃e:Series, (∏i∈s,f i)=(if a∈s then N else 1)*rescale (4:D) e := by
  by_cases hmem:a∈s
  · obtain ⟨e,he⟩:=ha
    obtain ⟨d,hd⟩:=fourScaled_prod (s.erase a) f (by
      intro i hi
      exact hf i (Finset.mem_of_mem_erase hi) (Finset.ne_of_mem_erase hi))
    refine ⟨e*d,?_⟩
    rw [ite_eq_left hmem,←Finset.mul_prod_erase s f hmem,he,hd,map_mul]
    ring
  · obtain ⟨e,he⟩:=fourScaled_prod s f (by
      intro i hi
      exact hf i hi (by intro h;subst i;exact hmem hi))
    exact ⟨e,by simpa only [ite_eq_right hmem,one_mul] using he⟩

lemma skeletonPlusFactor_far (k n:ℕ) (hk:2≤k) (hn:0<n) (hb:n<2^k)
    (hne:n≠2^(k-1)) : FourScaled (skeletonPlusFactor k n:Series) := by
  have hv:=skeleton_far_val_gap n k (by omega) hn hb hne
  simp only [skeletonPlusFactor,Polynomial.coe_add,Polynomial.coe_mul,
    Polynomial.coe_C,Polynomial.coe_X]
  rw [two_power_split_four (k-padicValNat 2 n) (by omega)]
  exact fourScaled_linear _ _

lemma skeletonMinusFactor_far (k n:ℕ) (hk:2≤k) (hn:0<n) (hb:n<2^k)
    (hne:n≠2^(k-1)) : FourScaled (skeletonMinusFactor k n:Series) := by
  have hv:=skeleton_far_val_gap n k (by omega) hn hb hne
  simp only [skeletonMinusFactor,Polynomial.coe_add,Polynomial.coe_mul,
    Polynomial.coe_C,Polynomial.coe_X]
  rw [two_power_split_four (k-padicValNat 2 n) (by omega)]
  exact fourScaled_linear _ _

lemma skeletonPlusFactor_near (k:ℕ) (hk:0<k) :
    (skeletonPlusFactor k (2^(k-1)):Series)=1+C (2:D)*X := by
  simp [skeletonPlusFactor,skeleton_near_oddPart,
    show k-(k-1)=1 by omega]

lemma skeletonMinusFactor_near (k:ℕ) (hk:0<k) :
    (skeletonMinusFactor k (2^(k-1)):Series)=-(1-C (2:D)*X) := by
  simp [skeletonMinusFactor,skeleton_near_oddPart,
    show k-(k-1)=1 by omega]
  ring

lemma skeletonPlusProduct_near (n k:ℕ) (hk:2≤k) (hn:n<2^k) :
    ∃e:Series, (∏h∈Finset.range n,(skeletonPlusFactor k (h+1):Series))=
      (if 2^(k-1)≤n then 1+C (2:D)*X else 1)*rescale (4:D) e := by
  have hp:0<2^(k-1):=by positivity
  obtain ⟨e,he⟩:=fourScaled_prod_extract (Finset.range n)
    (fun h => (skeletonPlusFactor k (h+1):Series)) (2^(k-1)-1) (1+C (2:D)*X)
    (by
      refine ⟨1,?_⟩
      rw [Nat.sub_add_cancel hp, skeletonPlusFactor_near k (by omega),map_one,mul_one])
    (by
      intro h hh hne
      exact skeletonPlusFactor_far k (h+1) hk (by omega)
        (by have := Finset.mem_range.mp hh;omega) (by omega))
  refine ⟨e,?_⟩
  simpa only [Finset.mem_range,show 2^(k-1)-1<n ↔ 2^(k-1)≤n by omega] using he

lemma skeletonMinusProduct_near (n k:ℕ) (hk:2≤k) (hn:n<2^k) :
    ∃e:Series, (∏h∈Finset.range n,(skeletonMinusFactor k (h+1):Series))=
      (if 2^(k-1)≤n then 1-C (2:D)*X else 1)*rescale (4:D) e := by
  have hp:0<2^(k-1):=by positivity
  obtain ⟨e,he⟩:=fourScaled_prod_extract (Finset.range n)
    (fun h => (skeletonMinusFactor k (h+1):Series)) (2^(k-1)-1) (1-C (2:D)*X)
    (by
      refine ⟨-1,?_⟩
      rw [Nat.sub_add_cancel hp, skeletonMinusFactor_near k (by omega),map_neg,map_one]
      ring)
    (by
      intro h hh hne
      exact skeletonMinusFactor_far k (h+1) hk (by omega)
        (by have := Finset.mem_range.mp hh;omega) (by omega))
  refine ⟨e,?_⟩
  simpa only [Finset.mem_range,show 2^(k-1)-1<n ↔ 2^(k-1)≤n by omega] using he

lemma skeletonOddCompanion_fourScaled (j i k:ℕ) (hk:1≤k) :
    FourScaled (skeletonOddCompanion j i k:Series) := by
  simp only [skeletonOddCompanion,series_coe_poly_prod]
  apply fourScaled_prod
  intro l _
  simp only [Polynomial.coe_add,Polynomial.coe_mul,Polynomial.coe_C,Polynomial.coe_X]
  rw [two_power_split_four (k+1) (by omega)]
  exact fourScaled_linear _ _

/-- Closest integer factors only; the minus sign of a right offset is absorbed
in the constant term of the four-weighted seed. -/
def nearestSkeletonFactor (j i:ℕ) : Series :=
  (if (2^(skeletonDepth j i-1) ≤ i) then 1+C (2:D)*X else 1)*
  (if (2^(skeletonDepth j i-1) ≤ j-1-i) then 1-C (2:D)*X else 1)

lemma nearestSkeletonFactor_constant (j i:ℕ) :
    coeff 0 (nearestSkeletonFactor j i)=1 := by
  unfold nearestSkeletonFactor
  split_ifs <;> simp

/-- Exact construction of the remaining four-weighted product, at every degree. -/
theorem skeletonLocalUnit_nearest (j i:ℕ) (hk:2≤skeletonDepth j i) :
    ∃e:Series, (skeletonLocalUnit j i (skeletonDepth j i):Series)=
      nearestSkeletonFactor j i*rescale (4:D) e := by
  obtain ⟨e,he⟩:=skeletonPlusProduct_near i (skeletonDepth j i) hk (skeletonDepth_bounds j i).1
  obtain ⟨f,hf⟩:=skeletonMinusProduct_near (j-1-i) (skeletonDepth j i) hk (skeletonDepth_bounds j i).2
  obtain ⟨g,hg⟩:=skeletonOddCompanion_fourScaled j i (skeletonDepth j i) (by omega)
  refine ⟨e*f*g,?_⟩
  simp only [skeletonLocalUnit,Polynomial.coe_mul,series_coe_poly_prod]
  rw [he,hf,hg,map_mul,map_mul]
  unfold nearestSkeletonFactor
  ring

/-- The ACTUAL upper chart, not just its polynomial skeleton, has the factorization. -/
theorem skeletonLocalSeries_nearest (j i:ℕ) (hk:2≤skeletonDepth j i)
    {U:Series} (hU:Restricted U) (hred:PowerSeries.map red U=1) :
    ∃e:Series, skeletonLocalSeries j i U=nearestSkeletonFactor j i*rescale (4:D) e ∧
      red (coeff 0 e)=1 := by
  obtain ⟨e,he⟩:=skeletonLocalUnit_nearest j i hk
  obtain ⟨f,hf⟩:=restrictedAffine_fourScaled U ((i:D)-(j:D)) (skeletonDepth j i) hk
  have hfac : skeletonLocalSeries j i U=nearestSkeletonFactor j i*rescale (4:D) (e*f) := by
    rw [skeletonLocalSeries,he,hf,map_mul]
    ring
  refine ⟨e*f,hfac,?_⟩
  have hc:=congrArg (coeff 0) (skeletonLocalSeries_red j i hU hred)
  rw [coeff_map,hfac] at hc
  simpa [coeff_mul,nearestSkeletonFactor_constant] using hc

end Komorebi.Euler
