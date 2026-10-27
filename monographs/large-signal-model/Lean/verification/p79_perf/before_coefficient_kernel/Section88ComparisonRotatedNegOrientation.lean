import KomorebiLSM.PerturbedOperatorFixture
import KomorebiLSM.RecordedBernsteinFixture

/-! Exact rational replay of robust_comparison_certificate.json: rotated, chart -1, orientation. -/
set_option autoImplicit false
set_option maxRecDepth 4000
set_option maxHeartbeats 800000
namespace Komorebi.LSM.Section88ComparisonRotatedNegOrientation
open TensorBernsteinCertificate RationalBernsteinMargin RationalLorentzMatrix
open PerturbedOperatorFixture RecordedBernsteinFixture
noncomputable section

def polynomial : Polynomial₂ := MvPolynomial.C (9/32 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^0 +
MvPolynomial.C (9/32 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^2 +
MvPolynomial.C (21/160000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^0 +
MvPolynomial.C (-21/160000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^2 +
MvPolynomial.C (-420021/160000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^1 +
MvPolynomial.C (63/32 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^0 +
MvPolynomial.C (63/32 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^2

theorem polynomial_source : polynomial=orientationPolynomial (nominalComparison true) (1/16) true := by
  apply MvPolynomial.funext
  intro x
  norm_num [polynomial,orientationPolynomial,orientationPolynomial,squareGapPolynomial,outputPolynomial,
    liftPolynomial,denominatorPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  ring

def cell_00 : Rectangle := ((square.quarter false false).quarter false false)
def leaf_00 : RecordedLeaf polynomial cell_00 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(299979/160000 : ℚ),(179979/128000 : ℚ),(191979/128000 : ℚ)],![(359937/640000 : ℚ),(215937/512000 : ℚ),(305937/512000 : ℚ)],![(74979/320000 : ℚ),(44979/256000 : ℚ),(79479/256000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(44979/256000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_00,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨2,1,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_01 : Rectangle := ((square.quarter false false).quarter false true)
def leaf_01 : RecordedLeaf polynomial cell_01 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(191979/128000 : ℚ),(203979/128000 : ℚ),(359979/160000 : ℚ)],![(305937/512000 : ℚ),(395937/512000 : ℚ),(809937/640000 : ℚ)],![(79479/256000 : ℚ),(113979/256000 : ℚ),(247479/320000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(79479/256000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_01,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨2,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_020 : Rectangle := (((square.quarter false false).quarter true false).quarter false false)
def leaf_020 : RecordedLeaf polynomial cell_020 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(74979/320000 : ℚ),(524811/2560000 : ℚ),(1147101/5120000 : ℚ)],![(89937/1280000 : ℚ),(629433/10240000 : ℚ),(1753803/20480000 : ℚ)],![(97479/640000 : ℚ),(682311/5120000 : ℚ),(1428351/10240000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(629433/10240000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_020,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨1,1,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_021 : Rectangle := (((square.quarter false false).quarter true false).quarter false true)
def leaf_021 : RecordedLeaf polynomial cell_021 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(1147101/5120000 : ℚ),(62229/256000 : ℚ),(79479/256000 : ℚ)],![(1753803/20480000 : ℚ),(112437/1024000 : ℚ),(170937/1024000 : ℚ)],![(1428351/10240000 : ℚ),(18651/128000 : ℚ),(90729/512000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(1753803/20480000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_021,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨1,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_022 : Rectangle := (((square.quarter false false).quarter true false).quarter true false)
def leaf_022 : RecordedLeaf polynomial cell_022 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(97479/640000 : ℚ),(682311/5120000 : ℚ),(1428351/10240000 : ℚ)],![(299979/1280000 : ℚ),(2099811/10240000 : ℚ),(3959601/20480000 : ℚ)],![(9/16 : ℚ),(63/128 : ℚ),(225/512 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(682311/5120000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_022,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨0,1,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_023 : Rectangle := (((square.quarter false false).quarter true false).quarter true true)
def leaf_023 : RecordedLeaf polynomial cell_023 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(1428351/10240000 : ℚ),(18651/128000 : ℚ),(90729/512000 : ℚ)],![(3959601/20480000 : ℚ),(185979/1024000 : ℚ),(191979/1024000 : ℚ)],![(225/512 : ℚ),(99/256 : ℚ),(45/128 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(1428351/10240000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_023,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨0,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_03 : Rectangle := ((square.quarter false false).quarter true true)
def leaf_03 : RecordedLeaf polynomial cell_03 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(79479/256000 : ℚ),(113979/256000 : ℚ),(247479/320000 : ℚ)],![(11979/512000 : ℚ),(59979/512000 : ℚ),(179979/640000 : ℚ)],![(45/128 : ℚ),(9/32 : ℚ),(9/32 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(11979/512000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_03,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨1,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_1 : Rectangle := (square.quarter false true)
def leaf_1 : RecordedLeaf polynomial cell_1 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(359979/160000 : ℚ),(1139979/320000 : ℚ),(1140021/160000 : ℚ)],![(89979/320000 : ℚ),(599979/640000 : ℚ),(600021/320000 : ℚ)],![(9/32 : ℚ),(9/32 : ℚ),(9/16 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(89979/320000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_1,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨1,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_2 : Rectangle := (square.quarter true false)
def leaf_2 : RecordedLeaf polynomial cell_2 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(9/16 : ℚ),(9/32 : ℚ),(9/32 : ℚ)],![(600021/320000 : ℚ),(600063/640000 : ℚ),(90021/320000 : ℚ)],![(1140021/160000 : ℚ),(1140063/320000 : ℚ),(360021/160000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(9/32 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_2,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨0,1,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_30 : Rectangle := ((square.quarter true true).quarter false false)
def leaf_30 : RecordedLeaf polynomial cell_30 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(9/32 : ℚ),(9/32 : ℚ),(45/128 : ℚ)],![(180021/640000 : ℚ),(300063/2560000 : ℚ),(60021/2560000 : ℚ)],![(247521/320000 : ℚ),(570063/1280000 : ℚ),(397521/1280000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(60021/2560000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_30,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨1,2,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_310 : Rectangle := (((square.quarter true true).quarter false true).quarter false false)
def leaf_310 : RecordedLeaf polynomial cell_310 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(45/128 : ℚ),(99/256 : ℚ),(225/512 : ℚ)],![(960021/5120000 : ℚ),(93/512 : ℚ),(791979/4096000 : ℚ)],![(453771/2560000 : ℚ),(597/4096 : ℚ),(285729/2048000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(285729/2048000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_310,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨2,2,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_311 : Rectangle := (((square.quarter true true).quarter false true).quarter false true)
def leaf_311 : RecordedLeaf polynomial cell_311 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(225/512 : ℚ),(63/128 : ℚ),(9/16 : ℚ)],![(791979/4096000 : ℚ),(419979/2048000 : ℚ),(299979/1280000 : ℚ)],![(285729/2048000 : ℚ),(136479/1024000 : ℚ),(97479/640000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(136479/1024000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_311,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨2,1,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_312 : Rectangle := (((square.quarter true true).quarter false true).quarter true false)
def leaf_312 : RecordedLeaf polynomial cell_312 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(453771/2560000 : ℚ),(597/4096 : ℚ),(285729/2048000 : ℚ)],![(855063/5120000 : ℚ),(225/2048 : ℚ),(350937/4096000 : ℚ)],![(397521/1280000 : ℚ),(249/1024 : ℚ),(229479/1024000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(350937/4096000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_312,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨1,2,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_313 : Rectangle := (((square.quarter true true).quarter false true).quarter true true)
def leaf_313 : RecordedLeaf polynomial cell_313 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(285729/2048000 : ℚ),(136479/1024000 : ℚ),(97479/640000 : ℚ)],![(350937/4096000 : ℚ),(125937/2048000 : ℚ),(89937/1280000 : ℚ)],![(229479/1024000 : ℚ),(104979/512000 : ℚ),(74979/320000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(125937/2048000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_313,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨1,1,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_32 : Rectangle := ((square.quarter true true).quarter true false)
def leaf_32 : RecordedLeaf polynomial cell_32 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(247521/320000 : ℚ),(570063/1280000 : ℚ),(397521/1280000 : ℚ)],![(810063/640000 : ℚ),(1980189/2560000 : ℚ),(1530063/2560000 : ℚ)],![(360021/160000 : ℚ),(1020063/640000 : ℚ),(960021/640000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(397521/1280000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_32,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨0,2,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_33 : Rectangle := ((square.quarter true true).quarter true true)
def leaf_33 : RecordedLeaf polynomial cell_33 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(397521/1280000 : ℚ),(224979/1280000 : ℚ),(74979/320000 : ℚ)],![(1530063/2560000 : ℚ),(1079937/2560000 : ℚ),(359937/640000 : ℚ)],![(960021/640000 : ℚ),(899979/640000 : ℚ),(299979/160000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(224979/1280000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_33,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨0,1,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def witness : SubdivisionWitness polynomial square :=
 .of_quarters (fun
  | false,false => .of_quarters (fun
  | false,false => .leaf leaf_00.certificate
  | false,true => .leaf leaf_01.certificate
  | true,false => .of_quarters (fun
  | false,false => .leaf leaf_020.certificate
  | false,true => .leaf leaf_021.certificate
  | true,false => .leaf leaf_022.certificate
  | true,true => .leaf leaf_023.certificate)
  | true,true => .leaf leaf_03.certificate)
  | false,true => .leaf leaf_1.certificate
  | true,false => .leaf leaf_2.certificate
  | true,true => .of_quarters (fun
  | false,false => .leaf leaf_30.certificate
  | false,true => .of_quarters (fun
  | false,false => .leaf leaf_310.certificate
  | false,true => .leaf leaf_311.certificate
  | true,false => .leaf leaf_312.certificate
  | true,true => .leaf leaf_313.certificate)
  | true,false => .leaf leaf_32.certificate
  | true,true => .leaf leaf_33.certificate))

def certifiedWitness : SubdivisionWitness (orientationPolynomial (nominalComparison true) (1/16) true) square :=
  polynomial_source ▸ witness

end
end Komorebi.LSM.Section88ComparisonRotatedNegOrientation
