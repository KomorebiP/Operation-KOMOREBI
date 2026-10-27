import KomorebiLSM.PerturbedOperatorFixture
import KomorebiLSM.RecordedBernsteinFixture

/-! Exact rational replay of robust_curved_certificate.json: rotated, chart 1, orientation. -/
set_option autoImplicit false
set_option maxRecDepth 4000
set_option maxHeartbeats 800000
namespace Komorebi.LSM.Section88ProposedRotatedPosOrientation
open TensorBernsteinCertificate RationalBernsteinMargin RationalLorentzMatrix
open PerturbedOperatorFixture RecordedBernsteinFixture
noncomputable section

def polynomial : Polynomial₂ := MvPolynomial.C (9/32 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^0 +
MvPolynomial.C (9/32 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^2 +
MvPolynomial.C (-259/1968000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^0 +
MvPolynomial.C (259/1968000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^2 +
MvPolynomial.C (6888343/2616000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^1 +
MvPolynomial.C (63/32 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^0 +
MvPolynomial.C (63/32 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^2

theorem polynomial_source : polynomial=orientationPolynomial (nominalProposed true) (1/16) false := by
  apply MvPolynomial.funext
  intro x
  norm_num [polynomial,orientationPolynomial,orientationPolynomial,squareGapPolynomial,outputPolynomial,
    liftPolynomial,denominatorPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  ring

def cell_0 : Rectangle := (square.quarter false false)
def leaf_0 : RecordedLeaf polynomial cell_0 := by
  let c : Fin 3 → Fin 3 → ℚ := ![![(18660343/2616000 : ℚ),(127517049/35752000 : ℚ),(4428259/1968000 : ℚ)],![(9831343/5232000 : ℚ),(67185549/71504000 : ℚ),(1107259/3936000 : ℚ)],![(9/16 : ℚ),(9/32 : ℚ),(9/32 : ℚ)]]
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(4428259/1968000 : ℚ),(227646133/143008000 : ℚ),(1283656441/858048000 : ℚ)],![(3321259/2624000 : ℚ),(441612399/572032000 : ℚ),(680341441/1144064000 : ℚ)],![(3044509/3936000 : ℚ),(127093633/286016000 : ℚ),(529512691/1716096000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(529512691/1716096000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(1283656441/858048000 : ℚ),(300359021/214512000 : ℚ),(4883657/2616000 : ℚ)],![(680341441/1144064000 : ℚ),(119364521/286016000 : ℚ),(1940657/3488000 : ℚ)],![(529512691/1716096000 : ℚ),(9264487/53628000 : ℚ),(1204907/5232000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(9264487/53628000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(3044509/3936000 : ℚ),(127093633/286016000 : ℚ),(529512691/1716096000 : ℚ)],![(2214259/7872000 : ℚ),(66762133/572032000 : ℚ),(77026441/3432192000 : ℚ)],![(9/32 : ℚ),(9/32 : ℚ),(45/128 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(77026441/3432192000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(529512691/1716096000 : ℚ),(11013017/45762560 : ℚ),(303529871/1372876800 : ℚ)],![(378683941/2288128000 : ℚ),(19766121/183050240 : ℚ),(152701121/1830502400 : ℚ)],![(302463533/1716096000 : ℚ),(3306293/22881280 : ℚ),(189472123/1372876800 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(152701121/1830502400 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(303529871/1372876800 : ℚ),(17291827/85804800 : ℚ),(1204907/5232000 : ℚ)],![(152701121/1830502400 : ℚ),(13467629/228812800 : ℚ),(469157/6976000 : ℚ)],![(189472123/1372876800 : ℚ),(90283333/686438400 : ℚ),(786391/5232000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(13467629/228812800 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(302463533/1716096000 : ℚ),(3306293/22881280 : ℚ),(189472123/1372876800 : ℚ)],![(1283656441/6864384000 : ℚ),(33134567/183050240 : ℚ),(1057673621/5491507200 : ℚ)],![(45/128 : ℚ),(99/256 : ℚ),(225/512 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(189472123/1372876800 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(189472123/1372876800 : ℚ),(90283333/686438400 : ℚ),(786391/5232000 : ℚ)],![(1057673621/5491507200 : ℚ),(140163779/686438400 : ℚ),(4883657/20928000 : ℚ)],![(225/512 : ℚ),(63/128 : ℚ),(9/16 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(90283333/686438400 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(9/16 : ℚ),(63/128 : ℚ),(225/512 : ℚ)],![(4883657/20928000 : ℚ),(29199611/143008000 : ℚ),(5287972871/27457536000 : ℚ)],![(786391/5232000 : ℚ),(150453401/1144064000 : ℚ),(473581499/3432192000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(150453401/1144064000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(225/512 : ℚ),(99/256 : ℚ),(45/128 : ℚ)],![(5287972871/27457536000 : ℚ),(496962043/2745753600 : ℚ),(256697411/1372876800 : ℚ)],![(473581499/3432192000 : ℚ),(99160559/686438400 : ℚ),(7559471/42902400 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(473581499/3432192000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(786391/5232000 : ℚ),(150453401/1144064000 : ℚ),(473581499/3432192000 : ℚ)],![(469157/6976000 : ℚ),(33654957/572032000 : ℚ),(763110371/9152512000 : ℚ)],![(1204907/5232000 : ℚ),(57630013/286016000 : ℚ),(1517254121/6864384000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(33654957/572032000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(473581499/3432192000 : ℚ),(99160559/686438400 : ℚ),(7559471/42902400 : ℚ)],![(763110371/9152512000 : ℚ),(98774143/915251200 : ℚ),(75702911/457625600 : ℚ)],![(1517254121/6864384000 : ℚ),(165138793/686438400 : ℚ),(105868661/343219200 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(763110371/9152512000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(45/128 : ℚ),(9/32 : ℚ),(9/32 : ℚ)],![(15371411/686438400 : ℚ),(8006939/68643840 : ℚ),(2213741/7872000 : ℚ)],![(105868661/343219200 : ℚ),(15246719/34321920 : ℚ),(3043991/3936000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(15371411/686438400 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(1204907/5232000 : ℚ),(14817533/85804800 : ℚ),(105868661/343219200 : ℚ)],![(1940657/3488000 : ℚ),(11933629/28601600 : ℚ),(136034411/228812800 : ℚ)],![(4883657/2616000 : ℚ),(30033079/21451200 : ℚ),(256697411/171609600 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(14817533/85804800 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(105868661/343219200 : ℚ),(15246719/34321920 : ℚ),(3043991/3936000 : ℚ)],![(136034411/228812800 : ℚ),(17659979/22881280 : ℚ),(3320741/2624000 : ℚ)],![(256697411/171609600 : ℚ),(27313019/17160960 : ℚ),(4427741/1968000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(105868661/343219200 : ℚ),?_,?_,?_⟩
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
  let c : Fin 3 → Fin 3 → ℚ := ![![(9/32 : ℚ),(9/32 : ℚ),(9/16 : ℚ)],![(1106741/3936000 : ℚ),(6297763/6703500 : ℚ),(9831343/5232000 : ℚ)],![(4427741/1968000 : ℚ),(95630729/26814000 : ℚ),(18660343/2616000 : ℚ)]]
  refine ⟨⟨2,2,c,?_,?_⟩,(1106741/3936000 : ℚ),?_,?_,?_⟩
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

def certifiedWitness : SubdivisionWitness (orientationPolynomial (nominalProposed true) (1/16) false) square :=
  polynomial_source ▸ witness

end
end Komorebi.LSM.Section88ProposedRotatedPosOrientation
