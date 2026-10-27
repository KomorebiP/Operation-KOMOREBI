import KomorebiLSM.PerturbedOperatorFixture
import KomorebiLSM.RecordedBernsteinFixture

/-! Exact rational replay of robust_comparison_certificate.json: rotated, chart 1, orientation. -/
set_option autoImplicit false
set_option maxRecDepth 4000
set_option maxHeartbeats 800000
namespace Komorebi.LSM.Section88ComparisonRotatedPosOrientation
open TensorBernsteinCertificate RationalBernsteinMargin RationalLorentzMatrix
open PerturbedOperatorFixture RecordedBernsteinFixture
noncomputable section

def polynomial : Polynomial₂ := MvPolynomial.C (9/32 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^0 +
MvPolynomial.C (9/32 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^2 +
MvPolynomial.C (-21/160000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^0 +
MvPolynomial.C (21/160000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^2 +
MvPolynomial.C (420021/160000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^1 +
MvPolynomial.C (63/32 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^0 +
MvPolynomial.C (63/32 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^2

theorem polynomial_source : polynomial=orientationPolynomial (nominalComparison true) (1/16) false := by
  apply MvPolynomial.funext
  intro x
  norm_num [polynomial,orientationPolynomial,orientationPolynomial,squareGapPolynomial,outputPolynomial,
    liftPolynomial,denominatorPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  ring

def cell_0 : Rectangle := (square.quarter false false)
def leaf_0 : RecordedLeaf polynomial cell_0 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(1140021/160000 : ℚ),(1140063/320000 : ℚ),(360021/160000 : ℚ)],![(600021/320000 : ℚ),(600063/640000 : ℚ),(90021/320000 : ℚ)],![(9/16 : ℚ),(9/32 : ℚ),(9/32 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(9/32 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_0,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_10 : Rectangle := ((square.quarter false true).quarter false false)
def leaf_10 : RecordedLeaf polynomial cell_10 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(360021/160000 : ℚ),(1020063/640000 : ℚ),(960021/640000 : ℚ)],![(810063/640000 : ℚ),(1980189/2560000 : ℚ),(1530063/2560000 : ℚ)],![(247521/320000 : ℚ),(570063/1280000 : ℚ),(397521/1280000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(397521/1280000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_10,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_11 : Rectangle := ((square.quarter false true).quarter false true)
def leaf_11 : RecordedLeaf polynomial cell_11 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(960021/640000 : ℚ),(899979/640000 : ℚ),(299979/160000 : ℚ)],![(1530063/2560000 : ℚ),(1079937/2560000 : ℚ),(359937/640000 : ℚ)],![(397521/1280000 : ℚ),(224979/1280000 : ℚ),(74979/320000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(224979/1280000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_11,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_12 : Rectangle := ((square.quarter false true).quarter true false)
def leaf_12 : RecordedLeaf polynomial cell_12 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(247521/320000 : ℚ),(570063/1280000 : ℚ),(397521/1280000 : ℚ)],![(180021/640000 : ℚ),(300063/2560000 : ℚ),(60021/2560000 : ℚ)],![(9/32 : ℚ),(9/32 : ℚ),(45/128 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(60021/2560000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_12,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_130 : Rectangle := (((square.quarter false true).quarter true true).quarter false false)
def leaf_130 : RecordedLeaf polynomial cell_130 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(397521/1280000 : ℚ),(249/1024 : ℚ),(229479/1024000 : ℚ)],![(855063/5120000 : ℚ),(225/2048 : ℚ),(350937/4096000 : ℚ)],![(453771/2560000 : ℚ),(597/4096 : ℚ),(285729/2048000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(350937/4096000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_130,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_131 : Rectangle := (((square.quarter false true).quarter true true).quarter false true)
def leaf_131 : RecordedLeaf polynomial cell_131 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(229479/1024000 : ℚ),(104979/512000 : ℚ),(74979/320000 : ℚ)],![(350937/4096000 : ℚ),(125937/2048000 : ℚ),(89937/1280000 : ℚ)],![(285729/2048000 : ℚ),(136479/1024000 : ℚ),(97479/640000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(125937/2048000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_131,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_132 : Rectangle := (((square.quarter false true).quarter true true).quarter true false)
def leaf_132 : RecordedLeaf polynomial cell_132 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(453771/2560000 : ℚ),(597/4096 : ℚ),(285729/2048000 : ℚ)],![(960021/5120000 : ℚ),(93/512 : ℚ),(791979/4096000 : ℚ)],![(45/128 : ℚ),(99/256 : ℚ),(225/512 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(285729/2048000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_132,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_133 : Rectangle := (((square.quarter false true).quarter true true).quarter true true)
def leaf_133 : RecordedLeaf polynomial cell_133 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(285729/2048000 : ℚ),(136479/1024000 : ℚ),(97479/640000 : ℚ)],![(791979/4096000 : ℚ),(419979/2048000 : ℚ),(299979/1280000 : ℚ)],![(225/512 : ℚ),(63/128 : ℚ),(9/16 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(136479/1024000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_133,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_200 : Rectangle := (((square.quarter true false).quarter false false).quarter false false)
def leaf_200 : RecordedLeaf polynomial cell_200 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(9/16 : ℚ),(63/128 : ℚ),(225/512 : ℚ)],![(299979/1280000 : ℚ),(2099811/10240000 : ℚ),(3959601/20480000 : ℚ)],![(97479/640000 : ℚ),(682311/5120000 : ℚ),(1428351/10240000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(682311/5120000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_200,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_201 : Rectangle := (((square.quarter true false).quarter false false).quarter false true)
def leaf_201 : RecordedLeaf polynomial cell_201 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(225/512 : ℚ),(99/256 : ℚ),(45/128 : ℚ)],![(3959601/20480000 : ℚ),(185979/1024000 : ℚ),(191979/1024000 : ℚ)],![(1428351/10240000 : ℚ),(18651/128000 : ℚ),(90729/512000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(1428351/10240000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_201,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_202 : Rectangle := (((square.quarter true false).quarter false false).quarter true false)
def leaf_202 : RecordedLeaf polynomial cell_202 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(97479/640000 : ℚ),(682311/5120000 : ℚ),(1428351/10240000 : ℚ)],![(89937/1280000 : ℚ),(629433/10240000 : ℚ),(1753803/20480000 : ℚ)],![(74979/320000 : ℚ),(524811/2560000 : ℚ),(1147101/5120000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(629433/10240000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_202,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_203 : Rectangle := (((square.quarter true false).quarter false false).quarter true true)
def leaf_203 : RecordedLeaf polynomial cell_203 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(1428351/10240000 : ℚ),(18651/128000 : ℚ),(90729/512000 : ℚ)],![(1753803/20480000 : ℚ),(112437/1024000 : ℚ),(170937/1024000 : ℚ)],![(1147101/5120000 : ℚ),(62229/256000 : ℚ),(79479/256000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(1753803/20480000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_203,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_21 : Rectangle := ((square.quarter true false).quarter false true)
def leaf_21 : RecordedLeaf polynomial cell_21 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(45/128 : ℚ),(9/32 : ℚ),(9/32 : ℚ)],![(11979/512000 : ℚ),(59979/512000 : ℚ),(179979/640000 : ℚ)],![(79479/256000 : ℚ),(113979/256000 : ℚ),(247479/320000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(11979/512000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_21,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_22 : Rectangle := ((square.quarter true false).quarter true false)
def leaf_22 : RecordedLeaf polynomial cell_22 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(74979/320000 : ℚ),(44979/256000 : ℚ),(79479/256000 : ℚ)],![(359937/640000 : ℚ),(215937/512000 : ℚ),(305937/512000 : ℚ)],![(299979/160000 : ℚ),(179979/128000 : ℚ),(191979/128000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(44979/256000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_22,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_23 : Rectangle := ((square.quarter true false).quarter true true)
def leaf_23 : RecordedLeaf polynomial cell_23 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(79479/256000 : ℚ),(113979/256000 : ℚ),(247479/320000 : ℚ)],![(305937/512000 : ℚ),(395937/512000 : ℚ),(809937/640000 : ℚ)],![(191979/128000 : ℚ),(203979/128000 : ℚ),(359979/160000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(79479/256000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_23,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_3 : Rectangle := (square.quarter true true)
def leaf_3 : RecordedLeaf polynomial cell_3 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(9/32 : ℚ),(9/32 : ℚ),(9/16 : ℚ)],![(89979/320000 : ℚ),(599979/640000 : ℚ),(600021/320000 : ℚ)],![(359979/160000 : ℚ),(1139979/320000 : ℚ),(1140021/160000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(89979/320000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_3,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def witness : SubdivisionWitness polynomial square :=
 .of_quarters (fun
  | false,false => .leaf leaf_0.certificate
  | false,true => .of_quarters (fun
  | false,false => .leaf leaf_10.certificate
  | false,true => .leaf leaf_11.certificate
  | true,false => .leaf leaf_12.certificate
  | true,true => .of_quarters (fun
  | false,false => .leaf leaf_130.certificate
  | false,true => .leaf leaf_131.certificate
  | true,false => .leaf leaf_132.certificate
  | true,true => .leaf leaf_133.certificate))
  | true,false => .of_quarters (fun
  | false,false => .of_quarters (fun
  | false,false => .leaf leaf_200.certificate
  | false,true => .leaf leaf_201.certificate
  | true,false => .leaf leaf_202.certificate
  | true,true => .leaf leaf_203.certificate)
  | false,true => .leaf leaf_21.certificate
  | true,false => .leaf leaf_22.certificate
  | true,true => .leaf leaf_23.certificate)
  | true,true => .leaf leaf_3.certificate)

def certifiedWitness : SubdivisionWitness (orientationPolynomial (nominalComparison true) (1/16) false) square :=
  polynomial_source ▸ witness

end
end Komorebi.LSM.Section88ComparisonRotatedPosOrientation
