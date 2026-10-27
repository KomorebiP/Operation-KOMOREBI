import KomorebiLSM.PerturbedOperatorFixture
import KomorebiLSM.RecordedBernsteinFixture

/-! Exact rational replay of robust_comparison_certificate.json: direct, chart -1, orientation. -/
set_option autoImplicit false
set_option maxRecDepth 4000
set_option maxHeartbeats 800000
namespace Komorebi.LSM.Section88ComparisonDirectNegOrientation
open TensorBernsteinCertificate RationalBernsteinMargin RationalLorentzMatrix
open PerturbedOperatorFixture RecordedBernsteinFixture
noncomputable section

def polynomial : Polynomial₂ := MvPolynomial.C (9/32 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^0 +
MvPolynomial.C (9/32 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^2 +
MvPolynomial.C (-168021/160000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^0 +
MvPolynomial.C (168021/160000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^2 +
MvPolynomial.C (-251979/160000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^1 +
MvPolynomial.C (63/32 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^0 +
MvPolynomial.C (63/32 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^2

theorem polynomial_source : polynomial=orientationPolynomial (nominalComparison false) (1/16) true := by
  apply MvPolynomial.funext
  intro x
  norm_num [polynomial,orientationPolynomial,orientationPolynomial,squareGapPolynomial,outputPolynomial,
    liftPolynomial,denominatorPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  ring

def cell_00 : Rectangle := ((square.quarter false false).quarter false false)
def leaf_00 : RecordedLeaf polynomial cell_00 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(468021/160000 : ℚ),(348021/128000 : ℚ),(360021/128000 : ℚ)],![(864063/640000 : ℚ),(720063/512000 : ℚ),(810063/512000 : ℚ)],![(243021/320000 : ℚ),(213021/256000 : ℚ),(247521/256000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(243021/320000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨2,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_01 : Rectangle := ((square.quarter false false).quarter false true)
def leaf_01 : RecordedLeaf polynomial cell_01 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(360021/128000 : ℚ),(372021/128000 : ℚ),(528021/160000 : ℚ)],![(810063/512000 : ℚ),(900063/512000 : ℚ),(1314063/640000 : ℚ)],![(247521/256000 : ℚ),(282021/256000 : ℚ),(415521/320000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(247521/256000 : ℚ),?_,?_,?_⟩
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

def cell_02 : Rectangle := ((square.quarter false false).quarter true false)
def leaf_02 : RecordedLeaf polynomial cell_02 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(243021/320000 : ℚ),(213021/256000 : ℚ),(247521/256000 : ℚ)],![(108021/640000 : ℚ),(132021/512000 : ℚ),(180021/512000 : ℚ)],![(9/16 : ℚ),(27/64 : ℚ),(45/128 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(108021/640000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_02,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨1,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_03 : Rectangle := ((square.quarter false false).quarter true true)
def leaf_03 : RecordedLeaf polynomial cell_03 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(247521/256000 : ℚ),(282021/256000 : ℚ),(415521/320000 : ℚ)],![(180021/512000 : ℚ),(228021/512000 : ℚ),(348021/640000 : ℚ)],![(45/128 : ℚ),(9/32 : ℚ),(9/32 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(9/32 : ℚ),?_,?_,?_⟩
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
  · exact ⟨2,1,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_1 : Rectangle := (square.quarter false true)
def leaf_1 : RecordedLeaf polynomial cell_1 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(528021/160000 : ℚ),(1308021/320000 : ℚ),(971979/160000 : ℚ)],![(258021/320000 : ℚ),(768021/640000 : ℚ),(431979/320000 : ℚ)],![(9/32 : ℚ),(9/32 : ℚ),(9/16 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(9/32 : ℚ),?_,?_,?_⟩
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
  · exact ⟨2,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_20 : Rectangle := ((square.quarter true false).quarter false false)
def leaf_20 : RecordedLeaf polynomial cell_20 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(9/16 : ℚ),(27/64 : ℚ),(45/128 : ℚ)],![(611979/640000 : ℚ),(299979/512000 : ℚ),(179979/512000 : ℚ)],![(746979/320000 : ℚ),(380979/256000 : ℚ),(247479/256000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(179979/512000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_20,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨1,2,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_21 : Rectangle := ((square.quarter true false).quarter false true)
def leaf_21 : RecordedLeaf polynomial cell_21 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(45/128 : ℚ),(9/32 : ℚ),(9/32 : ℚ)],![(179979/512000 : ℚ),(59979/512000 : ℚ),(11979/640000 : ℚ)],![(247479/256000 : ℚ),(113979/256000 : ℚ),(79479/320000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(11979/640000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_21,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨1,2,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_22 : Rectangle := ((square.quarter true false).quarter true false)
def leaf_22 : RecordedLeaf polynomial cell_22 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(746979/320000 : ℚ),(380979/256000 : ℚ),(247479/256000 : ℚ)],![(2375937/640000 : ℚ),(1223937/512000 : ℚ),(809937/512000 : ℚ)],![(971979/160000 : ℚ),(515979/128000 : ℚ),(359979/128000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(247479/256000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_22,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨0,2,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_23 : Rectangle := ((square.quarter true false).quarter true true)
def leaf_23 : RecordedLeaf polynomial cell_23 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(247479/256000 : ℚ),(113979/256000 : ℚ),(79479/320000 : ℚ)],![(809937/512000 : ℚ),(395937/512000 : ℚ),(305937/640000 : ℚ)],![(359979/128000 : ℚ),(203979/128000 : ℚ),(191979/160000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(79479/320000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_23,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨0,2,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_300 : Rectangle := (((square.quarter true true).quarter false false).quarter false false)
def leaf_300 : RecordedLeaf polynomial cell_300 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(9/32 : ℚ),(9/32 : ℚ),(153/512 : ℚ)],![(191979/1280000 : ℚ),(1283853/10240000 : ℚ),(2591769/20480000 : ℚ)],![(90729/640000 : ℚ),(473853/5120000 : ℚ),(870519/10240000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(870519/10240000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_300,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨2,2,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_301 : Rectangle := (((square.quarter true true).quarter false false).quarter false true)
def leaf_301 : RecordedLeaf polynomial cell_301 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(153/512 : ℚ),(81/256 : ℚ),(45/128 : ℚ)],![(2591769/20480000 : ℚ),(326979/2560000 : ℚ),(791979/5120000 : ℚ)],![(870519/10240000 : ℚ),(198333/2560000 : ℚ),(285729/2560000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(198333/2560000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_301,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨2,1,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_302 : Rectangle := (((square.quarter true true).quarter false false).quarter true false)
def leaf_302 : RecordedLeaf polynomial cell_302 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(90729/640000 : ℚ),(473853/5120000 : ℚ),(870519/10240000 : ℚ)],![(170937/1280000 : ℚ),(611559/10240000 : ℚ),(890307/20480000 : ℚ)],![(79479/320000 : ℚ),(383853/2560000 : ℚ),(679269/5120000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(890307/20480000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_302,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨1,2,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_303 : Rectangle := (((square.quarter true true).quarter false false).quarter true true)
def leaf_303 : RecordedLeaf polynomial cell_303 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(870519/10240000 : ℚ),(198333/2560000 : ℚ),(285729/2560000 : ℚ)],![(890307/20480000 : ℚ),(69687/2560000 : ℚ),(350937/5120000 : ℚ)],![(679269/5120000 : ℚ),(36927/320000 : ℚ),(229479/1280000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(69687/2560000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_303,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨1,1,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_310 : Rectangle := (((square.quarter true true).quarter false true).quarter false false)
def leaf_310 : RecordedLeaf polynomial cell_310 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(45/128 : ℚ),(99/256 : ℚ),(225/512 : ℚ)],![(791979/5120000 : ℚ),(93/512 : ℚ),(960021/4096000 : ℚ)],![(285729/2560000 : ℚ),(597/4096 : ℚ),(453771/2048000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(285729/2560000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨2,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_311 : Rectangle := (((square.quarter true true).quarter false true).quarter false true)
def leaf_311 : RecordedLeaf polynomial cell_311 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(225/512 : ℚ),(63/128 : ℚ),(9/16 : ℚ)],![(960021/4096000 : ℚ),(588021/2048000 : ℚ),(468021/1280000 : ℚ)],![(453771/2048000 : ℚ),(304521/1024000 : ℚ),(265521/640000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(453771/2048000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨2,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_312 : Rectangle := (((square.quarter true true).quarter false true).quarter true false)
def leaf_312 : RecordedLeaf polynomial cell_312 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(285729/2560000 : ℚ),(597/4096 : ℚ),(453771/2048000 : ℚ)],![(350937/5120000 : ℚ),(225/2048 : ℚ),(855063/4096000 : ℚ)],![(229479/1280000 : ℚ),(249/1024 : ℚ),(397521/1024000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(350937/5120000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨1,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_313 : Rectangle := (((square.quarter true true).quarter false true).quarter true true)
def leaf_313 : RecordedLeaf polynomial cell_313 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(453771/2048000 : ℚ),(304521/1024000 : ℚ),(265521/640000 : ℚ)],![(855063/4096000 : ℚ),(630063/2048000 : ℚ),(594063/1280000 : ℚ)],![(397521/1024000 : ℚ),(273021/512000 : ℚ),(243021/320000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(855063/4096000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨1,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_32 : Rectangle := ((square.quarter true true).quarter true false)
def leaf_32 : RecordedLeaf polynomial cell_32 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(79479/320000 : ℚ),(65937/1280000 : ℚ),(229479/1280000 : ℚ)],![(305937/640000 : ℚ),(467811/2560000 : ℚ),(1025937/2560000 : ℚ)],![(191979/160000 : ℚ),(515937/640000 : ℚ),(791979/640000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(65937/1280000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨0,1,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_33 : Rectangle := ((square.quarter true true).quarter true true)
def leaf_33 : RecordedLeaf polynomial cell_33 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(229479/1280000 : ℚ),(393021/1280000 : ℚ),(243021/320000 : ℚ)],![(1025937/2560000 : ℚ),(1584063/2560000 : ℚ),(864063/640000 : ℚ)],![(791979/640000 : ℚ),(1068021/640000 : ℚ),(468021/160000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(229479/1280000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨0,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def witness : SubdivisionWitness polynomial square :=
 .of_quarters (fun
  | false,false => .of_quarters (fun
  | false,false => .leaf leaf_00.certificate
  | false,true => .leaf leaf_01.certificate
  | true,false => .leaf leaf_02.certificate
  | true,true => .leaf leaf_03.certificate)
  | false,true => .leaf leaf_1.certificate
  | true,false => .of_quarters (fun
  | false,false => .leaf leaf_20.certificate
  | false,true => .leaf leaf_21.certificate
  | true,false => .leaf leaf_22.certificate
  | true,true => .leaf leaf_23.certificate)
  | true,true => .of_quarters (fun
  | false,false => .of_quarters (fun
  | false,false => .leaf leaf_300.certificate
  | false,true => .leaf leaf_301.certificate
  | true,false => .leaf leaf_302.certificate
  | true,true => .leaf leaf_303.certificate)
  | false,true => .of_quarters (fun
  | false,false => .leaf leaf_310.certificate
  | false,true => .leaf leaf_311.certificate
  | true,false => .leaf leaf_312.certificate
  | true,true => .leaf leaf_313.certificate)
  | true,false => .leaf leaf_32.certificate
  | true,true => .leaf leaf_33.certificate))

def certifiedWitness : SubdivisionWitness (orientationPolynomial (nominalComparison false) (1/16) true) square :=
  polynomial_source ▸ witness

end
end Komorebi.LSM.Section88ComparisonDirectNegOrientation
