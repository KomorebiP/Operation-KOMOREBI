module
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.FieldSimp
public import Mathlib.Tactic.NormNum
@[expose] public section
namespace H12.CMNormCertificate

/- Integer normal form of the retained Gauss/CM arithmetic candidate.
Conversion from the retained formulas is checked separately in two exact
implementations. No gamma value is used to construct these coefficients. -/

def u21 {K : Type*} [CommRing K] (b x w : K) : K :=
  -8 * b^2 * x^2 * w + 9 * b^2 * x^2 - 18 * b^2 * x * w - 20 * b^2 * x + 14 * b^2 * w - 14 * b^2 - 17 * b * x^2 * w - 29 * b * x^2 + 42 * b * x * w + 14 * b * w + 56 * b + 63 * x^2 * w + 21 * x^2 - 14 * x * w + 70 * x - 98 * w - 56

def unitA {K : Type*} [CommRing K] (_b x w : K) : K :=
  4 * x^2 * w + 4 * x^2 - 6 * x * w - 4 * x + 1

def unitAI7 {K : Type*} [CommRing K] (b x w : K) : K :=
  -8 * b^2 * x * w - 12 * b^2 * x + 6 * b * x^2 * w + 16 * b * x^2 + 7

def uSquare {K : Type*} [CommRing K] (b x w : K) : K :=
  -11844 * b^2 * x^2 * w - 12768 * b^2 * x^2 + 11991 * b^2 * x * w - 7665 * b^2 * x + 20580 * b^2 * w + 25872 * b^2 + 24864 * b * x^2 * w + 2016 * b * x^2 + 14259 * b * x * w + 37044 * b * x - 49392 * b * w - 9408 * b - 4116 * x^2 * w + 42924 * x^2 - 71001 * x * w - 42777 * x + 18816 * w - 77028

def uCube {K : Type*} [CommRing K] (b x w : K) : K :=
  7980336 * b^2 * x^2 * w - 4477032 * b^2 * x^2 + 12796056 * b^2 * x * w + 16675092 * b^2 * x - 17503290 * b^2 * w + 5649210 * b^2 + 8573040 * b * x^2 * w + 23806062 * b * x^2 - 31931928 * b * x * w - 7408800 * b * x - 10742760 * b * w - 44267580 * b - 45601164 * x^2 * w - 29153628 * x^2 + 14261940 * x * w - 46842138 * x + 84599235 * w + 64002771

def denProduct {K : Type*} [CommRing K] (b x w : K) : K :=
  -10 * b^2 * x^2 * w + 6 * b^2 * x^2 - 16 * b^2 * x * w - 24 * b^2 * x + 12 * b * x^2 * w + 32 * b * x^2 - 7 * b * w + 28 * x * w - 56 * x + 14

def cubeRhs {K : Type*} [CommRing K] (b x w : K) : K :=
  -259308 * b * x^2 * w - 259308 * b * x^2 + 388962 * b * x * w + 259308 * b * x - 64827 * b - 518616 * x^2 + 259308 * x * w + 777924 * x + 129654 * w

theorem square_reduction {K : Type*} [CommRing K] (b x w : K)
    (hb : b^3=7) (hx : x^3=2+3*w) (hw : w^2+w+1=0) :
    (u21 b x w)^2 = uSquare b x w := by
  apply sub_eq_zero.mp
  calc
    (u21 b x w)^2 - (uSquare b x w) = (64 * b * x^4 * w^2 - 144 * b * x^4 * w + 81 * b * x^4 + 288 * b * x^3 * w^2 - 4 * b * x^3 * w - 360 * b * x^3 + 100 * b * x^2 * w^2 + 1196 * b * x^2 * w + 148 * b * x^2 - 504 * b * x * w^2 - 56 * b * x * w + 560 * b * x + 196 * b * w^2 - 392 * b * w + 196 * b + 272 * x^4 * w^2 + 158 * x^4 * w - 522 * x^4 - 60 * x^3 * w^2 + 2480 * x^3 * w + 1160 * x^3 - 2212 * x^2 * w^2 - 2660 * x^2 * w + 1820 * x^2 + 672 * x * w^2 - 3752 * x * w - 2240 * x + 392 * w^2 + 1176 * w - 1568) * (b^3-7) + (-719 * b^2 * x * w^2 + 1784 * b^2 * x * w + 1219 * b^2 * x - 3472 * b^2 * w^2 - 7084 * b^2 * w + 420 * b^2 - 1694 * b * x * w^2 - 5376 * b * x * w - 651 * b * x + 7784 * b * w^2 + 168 * b * w - 6580 * b + 5873 * x * w^2 + 3752 * x * w - 3213 * x - 2184 * w^2 + 25592 * w + 11060) * (x^3-(2+3*w)) + (5124 * b^2 * x^2 - 2157 * b^2 * x * w + 10383 * b^2 * x - 10416 * b^2 * w - 20328 * b^2 + 4620 * b * x^2 - 5082 * b * x * w - 26586 * b * x + 23352 * b * w - 8652 * b - 27636 * x^2 + 17619 * x * w + 12831 * x - 6552 * w + 91308) * (w^2+w+1) := by
      unfold u21 uSquare
      ring
    _ = 0 := by rw [hb, hx, hw]; ring

theorem cube_reduction_step {K : Type*} [CommRing K] (b x w : K)
    (hb : b^3=7) (hx : x^3=2+3*w) (hw : w^2+w+1=0) :
    uSquare b x w * u21 b x w = uCube b x w := by
  apply sub_eq_zero.mp
  calc
    uSquare b x w * u21 b x w - (uCube b x w) = (94752 * b * x^4 * w^2 - 4452 * b * x^4 * w - 114912 * b * x^4 + 117264 * b * x^3 * w^2 + 635943 * b * x^3 * w + 186375 * b * x^3 - 546294 * b * x^2 * w^2 - 136542 * b * x^2 * w + 564900 * b * x^2 - 202566 * b * x * w^2 - 1152480 * b * x * w - 410130 * b * x + 288120 * b * w^2 + 74088 * b * w - 362208 * b + 2436 * x^4 * w^2 + 768180 * x^4 * w + 388416 * x^4 - 1262919 * x^3 * w^2 - 1455279 * x^3 * w + 515361 * x^3 + 474516 * x^2 * w^2 - 3841698 * x^2 * w - 2319072 * x^2 + 2120916 * x * w^2 + 3126984 * x * w - 759696 * x - 403368 * w^2 + 2074464 * w + 1580544) * (b^3-7) + (-1135932 * b^2 * x * w^2 - 2188872 * b^2 * x * w + 59724 * b^2 * x + 2365230 * b^2 * w^2 - 2827104 * b^2 * w - 3372474 * b^2 + 2299668 * b * x * w^2 + 7644 * b * x * w - 2006844 * b * x + 2405214 * b * w^2 + 13386114 * b * w + 3464202 * b - 242256 * x * w^2 + 7995036 * x * w + 3620316 * x - 13255872 * w^2 - 15261981 * w + 5713890) * (x^3-(2+3*w)) + (5145882 * b^2 * x^2 - 3407796 * b^2 * x * w - 10101462 * b^2 * x + 7095690 * b^2 * w - 13291446 * b^2 - 12931590 * b * x^2 + 6899004 * b * x * w - 4604334 * b * x + 7215642 * b * w + 44873808 * b + 5904402 * x^2 - 726768 * x * w + 45768450 * x - 39767616 * w - 37197615) * (w^2+w+1) := by
      unfold uSquare u21 uCube
      ring
    _ = 0 := by rw [hb, hx, hw]; ring

theorem denominator_reduction {K : Type*} [CommRing K] (b x w : K)
    (hb : b^3=7) (hx : x^3=2+3*w) (hw : w^2+w+1=0) :
    (2-w*b)*unitAI7 b x w = denProduct b x w := by
  apply sub_eq_zero.mp
  calc
    (2-w*b)*unitAI7 b x w - (denProduct b x w) = (8 * x * w^2 + 12 * x * w) * (b^3-7) + (0) * (x^3-(2+3*w)) + (-6 * b^2 * x^2 + 56 * x) * (w^2+w+1) := by
      unfold unitAI7 denProduct
      ring
    _ = 0 := by rw [hb, hx, hw]; ring

theorem rhs_reduction {K : Type*} [CommRing K] (b x w : K)
    (hb : b^3=7) (hx : x^3=2+3*w) (hw : w^2+w+1=0) :
    64827*w*(2+(1+w)*b)*unitA b x w = cubeRhs b x w := by
  apply sub_eq_zero.mp
  calc
    64827*w*(2+(1+w)*b)*unitA b x w - (cubeRhs b x w) = (0) * (b^3-7) + (0) * (x^3-(2+3*w)) + (259308 * b * x^2 * w + 259308 * b * x^2 - 388962 * b * x * w - 259308 * b * x + 64827 * b + 518616 * x^2 - 777924 * x) * (w^2+w+1) := by
      unfold unitA cubeRhs
      ring
    _ = 0 := by rw [hb, hx, hw]; ring

theorem final_product_reduction {K : Type*} [CommRing K] (b x w : K)
    (hb : b^3=7) (hx : x^3=2+3*w) (hw : w^2+w+1=0) :
    uCube b x w * denProduct b x w = cubeRhs b x w := by
  apply sub_eq_zero.mp
  calc
    uCube b x w * denProduct b x w - (cubeRhs b x w) = (-79803360 * b * x^4 * w^2 + 92652336 * b * x^4 * w - 26862192 * b * x^4 - 255645936 * b * x^3 * w^2 - 209870136 * b * x^3 * w + 207499320 * b * x^3 - 29703996 * b * x^2 * w^2 - 735418656 * b * x^2 * w - 366306948 * b * x^2 + 280052640 * b * x * w^2 + 329691600 * b * x * w - 135581040 * b * x + 10033632 * x^4 * w^2 + 15023988 * x^4 * w - 428652 * x^4 + 335703312 * x^3 * w^2 - 94578624 * x^3 * w - 82195344 * x^3 + 352436616 * x^2 * w^2 + 802150776 * x^2 * w + 92980440 * x^2 + 82311768 * x * w^2 + 849381876 * x * w + 1062421920 * x + 122523030 * w^2 - 39544470 * w) * (b^3-7) + (558888120 * b^2 * x * w^2 + 577939320 * b^2 * x * w + 586872216 * b^2 * x + 427265496 * b^2 * w^2 + 431895996 * b^2 * w + 432266436 * b^2 - 1105837488 * b * x * w^2 - 1160514432 * b * x * w - 1120951440 * b * x - 1378333152 * b * w^2 - 1388335032 * b * w - 1379592648 * b + 70235424 * x * w^2 + 105167916 * x * w - 3000564 * x + 1073090592 * w^2 + 1075313232 * w + 1057235760) * (x^3-(2+3*w)) + (-904818222 * b^2 * x^2 + 1676664360 * b^2 * x * w - 445226544 * b^2 * x + 1281796488 * b^2 * w + 943621812 * b^2 + 232377012 * b * x^2 - 3317512464 * b * x * w - 815968188 * b * x - 4134999456 * b * w - 3378866589 * b + 2866390632 * x^2 + 210706272 * x * w + 3190229280 * x + 3219271776 * w + 3010510314) * (w^2+w+1) := by
      unfold uCube denProduct cubeRhs
      ring
    _ = 0 := by rw [hb, hx, hw]; ring

theorem cleared_cube_relation {K : Type*} [CommRing K] (b x w : K)
    (hb : b^3=7) (hx : x^3=2+3*w) (hw : w^2+w+1=0) :
    (u21 b x w)^3 * (2-w*b) * unitAI7 b x w =
      64827*w*(2+(1+w)*b)*unitA b x w := by
  calc
    _ = (uSquare b x w * u21 b x w) * ((2-w*b)*unitAI7 b x w) := by
      rw [← square_reduction b x w hb hx hw]
      ring
    _ = uCube b x w * denProduct b x w := by
      rw [cube_reduction_step b x w hb hx hw, denominator_reduction b x w hb hx hw]
    _ = cubeRhs b x w := final_product_reduction b x w hb hx hw
    _ = _ := (rhs_reduction b x w hb hx hw).symm

theorem normalized_cube_relation {K : Type*} [Field K] [CharZero K] (b x w : K)
    (hb : b^3=7) (hx : x^3=2+3*w) (hw : w^2+w+1=0) :
    (u21 b x w / 21)^3 * (2-w*b) * (unitAI7 b x w / 7) =
      w*(2+(1+w)*b)*unitA b x w := by
  have hh := cleared_cube_relation b x w hb hx hw
  calc
    _ = ((u21 b x w)^3 * (2-w*b) * unitAI7 b x w)/64827 := by ring
    _ = _ := by rw [hh]; ring

theorem cube_as_relative_unit {K : Type*} [Field K] [CharZero K] (b x w : K)
    (hb : b^3=7) (hx : x^3=2+3*w) (hw : w^2+w+1=0)
    (he : 2-w*b ≠ 0) (ha : unitAI7 b x w / 7 ≠ 0) :
    (u21 b x w / 21)^3 =
      (w*(2+(1+w)*b)*unitA b x w) / ((2-w*b)*(unitAI7 b x w/7)) := by
  apply (eq_div_iff (mul_ne_zero he ha)).mpr
  simpa only [mul_assoc] using normalized_cube_relation b x w hb hx hw
end H12.CMNormCertificate
