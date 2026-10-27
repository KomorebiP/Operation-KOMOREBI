import KomorebiLSM.PerturbedOperatorFixture
import KomorebiLSM.RecordedBernsteinFixture

/-! Exact rational replay of robust_curved_certificate.json: direct, chart -1, orientation. -/
set_option autoImplicit false
set_option maxRecDepth 4000
set_option maxHeartbeats 800000
namespace Komorebi.LSM.Section88ProposedDirectNegOrientation
open TensorBernsteinCertificate RationalBernsteinMargin RationalLorentzMatrix
open PerturbedOperatorFixture RecordedBernsteinFixture
noncomputable section

def polynomial : Polynomial₂ := MvPolynomial.C (9/32 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^0 +
MvPolynomial.C (9/32 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^2 +
MvPolynomial.C (-690753/656000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^0 +
MvPolynomial.C (690753/656000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^2 +
MvPolynomial.C (-1381219/872000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^1 +
MvPolynomial.C (63/32 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^0 +
MvPolynomial.C (63/32 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^2

theorem polynomial_source : polynomial=orientationPolynomial (nominalProposed false) (1/16) true := by
  apply MvPolynomial.funext
  intro x
  norm_num [polynomial,orientationPolynomial,orientationPolynomial,squareGapPolynomial,outputPolynomial,
    liftPolynomial,denominatorPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  ring

def cell_00 : Rectangle := ((square.quarter false false).quarter false false)
def leaf_00 : RecordedLeaf polynomial cell_00 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(2542781/872000 : ℚ),(19402707/7150400 : ℚ),(160755263/57203200 : ℚ)],![(4685343/3488000 : ℚ),(40108671/28601600 : ℚ),(361602789/228812800 : ℚ)],![(1316531/1744000 : ℚ),(23722539/28601600 : ℚ),(110479013/114406400 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(1316531/1744000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(160755263/57203200 : ℚ),(16628887/5720320 : ℚ),(2166753/656000 : ℚ)],![(361602789/228812800 : ℚ),(40233621/22881280 : ℚ),(5393259/2624000 : ℚ)],![(110479013/114406400 : ℚ),(12606787/11440640 : ℚ),(1705503/1312000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(110479013/114406400 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(1316531/1744000 : ℚ),(23722539/28601600 : ℚ),(110479013/114406400 : ℚ)],![(580781/3488000 : ℚ),(7336407/28601600 : ℚ),(80313263/228812800 : ℚ)],![(9/16 : ℚ),(27/64 : ℚ),(45/128 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(580781/3488000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(110479013/114406400 : ℚ),(12606787/11440640 : ℚ),(1705503/1312000 : ℚ)],![(80313263/228812800 : ℚ),(10193527/22881280 : ℚ),(1428753/2624000 : ℚ)],![(45/128 : ℚ),(9/32 : ℚ),(9/32 : ℚ)]]
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(2166753/656000 : ℚ),(36600757/8938000 : ℚ),(5305219/872000 : ℚ)],![(1059753/1312000 : ℚ),(10758941/8938000 : ℚ),(2362219/1744000 : ℚ)],![(9/32 : ℚ),(9/32 : ℚ),(9/16 : ℚ)]]
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(9/16 : ℚ),(27/64 : ℚ),(45/128 : ℚ)],![(3343219/3488000 : ℚ),(16796193/28601600 : ℚ),(80570737/228812800 : ℚ)],![(4078969/1744000 : ℚ),(42642111/28601600 : ℚ),(110736487/114406400 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(45/128 : ℚ),?_,?_,?_⟩
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
  · exact ⟨0,2,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_21 : Rectangle := ((square.quarter true false).quarter false true)
def leaf_21 : RecordedLeaf polynomial cell_21 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(45/128 : ℚ),(9/32 : ℚ),(9/32 : ℚ)],![(80570737/228812800 : ℚ),(2677193/22881280 : ℚ),(47247/2624000 : ℚ)],![(110736487/114406400 : ℚ),(5090453/11440640 : ℚ),(323997/1312000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(47247/2624000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(4078969/1744000 : ℚ),(42642111/28601600 : ℚ),(110736487/114406400 : ℚ)],![(12972657/3488000 : ℚ),(68488029/28601600 : ℚ),(362375211/228812800 : ℚ)],![(5305219/872000 : ℚ),(28862493/7150400 : ℚ),(161012737/57203200 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(110736487/114406400 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(110736487/114406400 : ℚ),(5090453/11440640 : ℚ),(323997/1312000 : ℚ)],![(362375211/228812800 : ℚ),(17684619/22881280 : ℚ),(1248741/2624000 : ℚ)],![(161012737/57203200 : ℚ),(9112553/5720320 : ℚ),(785247/656000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(323997/1312000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(9/32 : ℚ),(9/32 : ℚ),(153/512 : ℚ)],![(785247/5248000 : ℚ),(285737713/2288128000 : ℚ),(1152607013/9152512000 : ℚ)],![(185061/1312000 : ℚ),(104743213/1144064000 : ℚ),(95845097/1144064000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(95845097/1144064000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(153/512 : ℚ),(81/256 : ℚ),(45/128 : ℚ)],![(1152607013/9152512000 : ℚ),(581131587/4576256000 : ℚ),(352023853/2288128000 : ℚ)],![(95845097/1144064000 : ℚ),(86946981/1144064000 : ℚ),(15722591/143008000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(86946981/1144064000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(185061/1312000 : ℚ),(104743213/1144064000 : ℚ),(95845097/1144064000 : ℚ)],![(695241/5248000 : ℚ),(133235139/2288128000 : ℚ),(380914539/9152512000 : ℚ)],![(323997/1312000 : ℚ),(84632713/572032000 : ℚ),(297910763/2288128000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(380914539/9152512000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(95845097/1144064000 : ℚ),(86946981/1144064000 : ℚ),(15722591/143008000 : ℚ)],![(380914539/9152512000 : ℚ),(114444261/4576256000 : ℚ),(151099059/2288128000 : ℚ)],![(297910763/2288128000 : ℚ),(128645337/1144064000 : ℚ),(100642603/572032000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(114444261/4576256000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(45/128 : ℚ),(99/256 : ℚ),(225/512 : ℚ)],![(352023853/2288128000 : ℚ),(33078553/183050240 : ℚ),(427187193/1830502400 : ℚ)],![(15722591/143008000 : ℚ),(6584579/45762560 : ℚ),(50236017/228812800 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(15722591/143008000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(225/512 : ℚ),(63/128 : ℚ),(9/16 : ℚ)],![(427187193/1830502400 : ℚ),(65448607/228812800 : ℚ),(2542781/6976000 : ℚ)],![(50236017/228812800 : ℚ),(67549139/228812800 : ℚ),(359789/872000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(50236017/228812800 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(15722591/143008000 : ℚ),(6584579/45762560 : ℚ),(50236017/228812800 : ℚ)],![(151099059/2288128000 : ℚ),(19598079/183050240 : ℚ),(376589079/1830502400 : ℚ)],![(100642603/572032000 : ℚ),(10957003/45762560 : ℚ),(175805943/457625600 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(151099059/2288128000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(50236017/228812800 : ℚ),(67549139/228812800 : ℚ),(359789/872000 : ℚ)],![(376589079/1830502400 : ℚ),(69649671/228812800 : ℚ),(3213843/6976000 : ℚ)],![(175805943/457625600 : ℚ),(236369/446900 : ℚ),(1316531/1744000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(376589079/1830502400 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(323997/1312000 : ℚ),(14001367/286016000 : ℚ),(100642603/572032000 : ℚ)],![(1248741/2624000 : ℚ),(102335601/572032000 : ℚ),(452756559/1144064000 : ℚ)],![(785247/656000 : ℚ),(114553867/143008000 : ℚ),(352023853/286016000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(14001367/286016000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(100642603/572032000 : ℚ),(21660309/71504000 : ℚ),(1316531/1744000 : ℚ)],![(452756559/1144064000 : ℚ),(175210479/286016000 : ℚ),(4685343/3488000 : ℚ)],![(352023853/286016000 : ℚ),(118734993/71504000 : ℚ),(2542781/872000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(100642603/572032000 : ℚ),?_,?_,?_⟩
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

def certifiedWitness : SubdivisionWitness (orientationPolynomial (nominalProposed false) (1/16) true) square :=
  polynomial_source ▸ witness

end
end Komorebi.LSM.Section88ProposedDirectNegOrientation
