import KomorebiLSM.PerturbedOperatorFixture
import KomorebiLSM.RecordedBernsteinFixture

/-! Exact rational replay of robust_comparison_certificate.json: rotated, chart -1, cone_gap. -/
set_option autoImplicit false
set_option maxRecDepth 4000
set_option maxHeartbeats 800000
namespace Komorebi.LSM.Section88ComparisonRotatedNegGap
open TensorBernsteinCertificate RationalBernsteinMargin RationalLorentzMatrix
open PerturbedOperatorFixture RecordedBernsteinFixture
noncomputable section

def polynomial : Polynomial₂ := MvPolynomial.C (40048363/1280000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^0 +
MvPolynomial.C (40537971/640000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^2 +
MvPolynomial.C (-142919/80000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^0 +
MvPolynomial.C (-159408487/480000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^1 +
MvPolynomial.C (57978084689/230400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^0 +
MvPolynomial.C (117860942311/230400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^2 +
MvPolynomial.C (40048363/1280000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^4 +
MvPolynomial.C (359387/160000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^4 +
MvPolynomial.C (-9985843/30000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^3 +
MvPolynomial.C (57325581089/230400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^4 +
MvPolynomial.C (-131571713/38400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^1 +
MvPolynomial.C (1597547/960000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^0 +
MvPolynomial.C (-80127887/38400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^3 +
MvPolynomial.C (-5561353/960000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^4 +
MvPolynomial.C (-41128493/1920000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^1 +
MvPolynomial.C (-17323607/1920000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^3 +
MvPolynomial.C (-97069/12800000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^0 +
MvPolynomial.C (695359/1024000000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^2 +
MvPolynomial.C (38563/4000000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^4 +
MvPolynomial.C (366961/320000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^1 +
MvPolynomial.C (36309/80000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^2 +
MvPolynomial.C (-366961/320000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^3 +
MvPolynomial.C (23825711/1920000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^2 +
MvPolynomial.C (66591/128000000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^1 +
MvPolynomial.C (-3283/6400000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^3

theorem polynomial_source : polynomial=squareGapPolynomial (nominalComparison true) (1/16) true := by
  apply MvPolynomial.funext
  intro x
  norm_num [polynomial,squareGapPolynomial,orientationPolynomial,squareGapPolynomial,outputPolynomial,
    liftPolynomial,denominatorPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  ring

def cell_00 : Rectangle := ((square.quarter false false).quarter false false)
def leaf_00 : RecordedLeaf polynomial cell_00 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(12716850043/28800000000 : ℚ),(9984327419/30720000000 : ℚ),(145408559149/552960000000 : ℚ),(11271708563/49152000000 : ℚ),(31898531249/147456000000 : ℚ)],![(87112937399/307200000000 : ℚ),(17175501393/81920000000 : ℚ),(255695337373/1474560000000 : ℚ),(10219519223/65536000000 : ℚ),(9989184843/65536000000 : ℚ)],![(905871872807/5529600000000 : ℚ),(179148105469/1474560000000 : ℚ),(2761907747249/26542080000000 : ℚ),(115876832549/1179648000000 : ℚ),(358430249357/3538944000000 : ℚ)],![(12776595131/153600000000 : ℚ),(2531967267/40960000000 : ℚ),(10390777663/184320000000 : ℚ),(3778019389/65536000000 : ℚ),(8426060463/131072000000 : ℚ)],![(157358597771/3686400000000 : ℚ),(31255278787/983040000000 : ℚ),(557196661427/17694720000000 : ℚ),(13857862021/393216000000 : ℚ),(390578981/9216000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(557196661427/17694720000000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨4,2,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_01 : Rectangle := ((square.quarter false false).quarter false true)
def leaf_01 : RecordedLeaf polynomial cell_01 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(31898531249/147456000000 : ℚ),(29981936809/147456000000 : ℚ),(116659642549/552960000000 : ℚ),(42669580939/184320000000 : ℚ),(63467743469/230400000000 : ℚ)],![(9989184843/65536000000 : ℚ),(9758850463/65536000000 : ℚ),(234965243173/1474560000000 : ℚ),(43966013449/245760000000 : ℚ),(66585562249/307200000000 : ℚ)],![(358430249357/3538944000000 : ℚ),(369230001067/3538944000000 : ℚ),(3085900298549/26542080000000 : ℚ),(594308459707/4423680000000 : ℚ),(920198796557/5529600000000 : ℚ)],![(8426060463/131072000000 : ℚ),(2324020537/32768000000 : ℚ),(122277197129/1474560000000 : ℚ),(12157226071/122880000000 : ℚ),(77081239549/614400000000 : ℚ)],![(390578981/9216000000 : ℚ),(58414633073/1179648000000 : ℚ),(1062428071727/17694720000000 : ℚ),(27013179317/368640000000 : ℚ),(87007603349/921600000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(390578981/9216000000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨4,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_02 : Rectangle := ((square.quarter false false).quarter true false)
def leaf_02 : RecordedLeaf polynomial cell_02 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(157358597771/3686400000000 : ℚ),(31255278787/983040000000 : ℚ),(557196661427/17694720000000 : ℚ),(13857862021/393216000000 : ℚ),(390578981/9216000000 : ℚ)],![(4039456199/1843200000000 : ℚ),(871671583/491520000000 : ℚ),(58439333603/8847360000000 : ℚ),(1261901927/98304000000 : ℚ),(24153674969/1179648000000 : ℚ)],![(10193760569/5529600000000 : ℚ),(2076491743/1474560000000 : ℚ),(119999781923/26542080000000 : ℚ),(10153780793/1179648000000 : ℚ),(48345034169/3538944000000 : ℚ)],![(20487191/480000000 : ℚ),(65254297/2048000000 : ℚ),(27007197/1024000000 : ℚ),(4834401/204800000 : ℚ),(3514781/153600000 : ℚ)],![(40293167/320000000 : ℚ),(6025627/64000000 : ℚ),(37370459/512000000 : ℚ),(2994463/51200000 : ℚ),(7970551/163840000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(2076491743/1474560000000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨2,1,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_03 : Rectangle := ((square.quarter false false).quarter true true)
def leaf_03 : RecordedLeaf polynomial cell_03 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(390578981/9216000000 : ℚ),(58414633073/1179648000000 : ℚ),(1062428071727/17694720000000 : ℚ),(27013179317/368640000000 : ℚ),(87007603349/921600000000 : ℚ)],![(24153674969/1179648000000 : ℚ),(16582263407/589824000000 : ℚ),(328764888953/8847360000000 : ℚ),(17554680421/368640000000 : ℚ),(116786694749/1843200000000 : ℚ)],![(48345034169/3538944000000 : ℚ),(66228725959/3538944000000 : ℚ),(656510535623/26542080000000 : ℚ),(140300512699/4423680000000 : ℚ),(233456653169/5529600000000 : ℚ)],![(3514781/153600000 : ℚ),(2723009/122880000 : ℚ),(72140011/3072000000 : ℚ),(160841761/6144000000 : ℚ),(40334201/1280000000 : ℚ)],![(7970551/163840000 : ℚ),(15897051/409600000 : ℚ),(34447653/1024000000 : ℚ),(15945953/512000000 : ℚ),(40048363/1280000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(48345034169/3538944000000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨2,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_1 : Rectangle := (square.quarter false true)
def leaf_1 : RecordedLeaf polynomial cell_1 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(63467743469/230400000000 : ℚ),(167458556119/460800000000 : ℚ),(376796144153/691200000000 : ℚ),(208552788403/230400000000 : ℚ),(52455119593/28800000000 : ℚ)],![(72821199809/460800000000 : ℚ),(204132806509/921600000000 : ℚ),(933331524091/2764800000000 : ℚ),(524109072491/921600000000 : ℚ),(521965112309/460800000000 : ℚ)],![(102465136889/1382400000000 : ℚ),(320102305039/2764800000000 : ℚ),(1510932258811/8294400000000 : ℚ),(869559509411/2764800000000 : ℚ),(864951494489/1382400000000 : ℚ)],![(40620039/1280000000 : ℚ),(405330487/7680000000 : ℚ),(323935723/3840000000 : ℚ),(1128914833/7680000000 : ℚ),(140125619/480000000 : ℚ)],![(40048363/1280000000 : ℚ),(10103831/320000000 : ℚ),(27147471/640000000 : ℚ),(1270629/20000000 : ℚ),(40293167/320000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(40048363/1280000000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨4,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_2 : Rectangle := (square.quarter true false)
def leaf_2 : RecordedLeaf polynomial cell_2 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(40293167/320000000 : ℚ),(19963103/320000000 : ℚ),(26413549/640000000 : ℚ),(19840701/640000000 : ℚ),(40048363/1280000000 : ℚ)],![(280689739/960000000 : ℚ),(1114119073/7680000000 : ℚ),(316247371/3840000000 : ℚ),(394066843/7680000000 : ℚ),(39476687/1280000000 : ℚ)],![(868754772569/1382400000000 : ℚ),(864926163407/2764800000000 : ℚ),(1491966788959/8294400000000 : ℚ),(314367183157/2764800000000 : ℚ),(99995496569/1382400000000 : ℚ)],![(527044720829/460800000000 : ℚ),(527371260287/921600000000 : ℚ),(932961904519/2764800000000 : ℚ),(202690995187/921600000000 : ℚ),(71969790929/460800000000 : ℚ)],![(53301813133/28800000000 : ℚ),(212499668221/230400000000 : ℚ),(380806690427/691200000000 : ℚ),(167751128917/460800000000 : ℚ),(63411352589/230400000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(39476687/1280000000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨1,4,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_30 : Rectangle := ((square.quarter true true).quarter false false)
def leaf_30 : RecordedLeaf polynomial cell_30 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(40048363/1280000000 : ℚ),(80463687/2560000000 : ℚ),(175173953/5120000000 : ℚ),(405499417/10240000000 : ℚ),(1013933003/20480000000 : ℚ)],![(1590501/51200000 : ℚ),(159859129/6144000000 : ℚ),(2901757/122880000 : ℚ),(17292179/768000000 : ℚ),(143521349/6144000000 : ℚ)],![(228517372529/5529600000000 : ℚ),(687297096737/22118400000000 : ℚ),(3231884651419/132710400000000 : ℚ),(1638997353037/88473600000000 : ℚ),(1202366006729/88473600000000 : ℚ)],![(114508760069/1843200000000 : ℚ),(171653067391/3686400000000 : ℚ),(1607102155609/44236800000000 : ℚ),(202519214533/7372800000000 : ℚ),(588870899969/29491200000000 : ℚ)],![(85744587749/921600000000 : ℚ),(132688557061/1843200000000 : ℚ),(5218274721931/88473600000000 : ℚ),(1437061664069/29491200000000 : ℚ),(77131551253/1843200000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(1202366006729/88473600000000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨2,4,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_31 : Rectangle := ((square.quarter true true).quarter false true)
def leaf_31 : RecordedLeaf polynomial cell_31 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(1013933003/20480000000 : ℚ),(304216793/5120000000 : ℚ),(189054061/2560000000 : ℚ),(60623231/640000000 : ℚ),(40293167/320000000 : ℚ)],![(143521349/6144000000 : ℚ),(24784211/1024000000 : ℚ),(27637253/1024000000 : ℚ),(66263193/2048000000 : ℚ),(16477453/384000000 : ℚ)],![(1202366006729/88473600000000 : ℚ),(255244886807/29491200000000 : ℚ),(612096573571/132710400000000 : ℚ),(10775836343/7372800000000 : ℚ),(10179131129/5529600000000 : ℚ)],![(588870899969/29491200000000 : ℚ),(61277490301/4915200000000 : ℚ),(279866406631/44236800000000 : ℚ),(3769082123/2457600000000 : ℚ),(3715829819/1843200000000 : ℚ)],![(77131551253/1843200000000 : ℚ),(343715992009/9830400000000 : ℚ),(2782792593679/88473600000000 : ℚ),(156938520407/4915200000000 : ℚ),(158199143771/3686400000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(10775836343/7372800000000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_31,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨2,3,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_32 : Rectangle := ((square.quarter true true).quarter true false)
def leaf_32 : RecordedLeaf polynomial cell_32 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(85744587749/921600000000 : ℚ),(132688557061/1843200000000 : ℚ),(5218274721931/88473600000000 : ℚ),(1437061664069/29491200000000 : ℚ),(77131551253/1843200000000 : ℚ)],![(25385510103/204800000000 : ℚ),(119700386951/1228800000000 : ℚ),(66873566043/819200000000 : ℚ),(344007745001/4915200000000 : ℚ),(626446246709/9830400000000 : ℚ)],![(912282357677/5529600000000 : ℚ),(2936674218281/22118400000000 : ℚ),(15256307115697/132710400000000 : ℚ),(9162815024281/88473600000000 : ℚ),(8945173047677/88473600000000 : ℚ)],![(22088055123/102400000000 : ℚ),(218187241207/1228800000000 : ℚ),(129759440801/819200000000 : ℚ),(731591007907/4915200000000 : ℚ),(753702883169/4915200000000 : ℚ)],![(63411352589/230400000000 : ℚ),(212716986617/921600000000 : ℚ),(583153050077/2764800000000 : ℚ),(754773365167/3686400000000 : ℚ),(808697512289/3686400000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(77131551253/1843200000000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨0,4,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_33 : Rectangle := ((square.quarter true true).quarter true true)
def leaf_33 : RecordedLeaf polynomial cell_33 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(77131551253/1843200000000 : ℚ),(343715992009/9830400000000 : ℚ),(2782792593679/88473600000000 : ℚ),(156938520407/4915200000000 : ℚ),(158199143771/3686400000000 : ℚ)],![(626446246709/9830400000000 : ℚ),(23536541809/409600000000 : ℚ),(34762863709/614400000000 : ℚ),(12764119857/204800000000 : ℚ),(1609201187/19200000000 : ℚ)],![(8945173047677/88473600000000 : ℚ),(2909177023691/29491200000000 : ℚ),(13950455256073/132710400000000 : ℚ),(907177973309/7372800000000 : ℚ),(914784035927/5529600000000 : ℚ)],![(753702883169/4915200000000 : ℚ),(258604919477/1638400000000 : ℚ),(433502072927/2457600000000 : ℚ),(87426822873/409600000000 : ℚ),(88245517519/307200000000 : ℚ)],![(808697512289/3686400000000 : ℚ),(287540553137/1228800000000 : ℚ),(744925491443/2764800000000 : ℚ),(51110673769/153600000000 : ℚ),(12929282683/28800000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(2782792593679/88473600000000 : ℚ),?_,?_,?_⟩
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
  · exact ⟨0,2,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def witness : SubdivisionWitness polynomial square :=
 .of_quarters (fun
  | false,false => .of_quarters (fun
  | false,false => .leaf leaf_00.certificate
  | false,true => .leaf leaf_01.certificate
  | true,false => .leaf leaf_02.certificate
  | true,true => .leaf leaf_03.certificate)
  | false,true => .leaf leaf_1.certificate
  | true,false => .leaf leaf_2.certificate
  | true,true => .of_quarters (fun
  | false,false => .leaf leaf_30.certificate
  | false,true => .leaf leaf_31.certificate
  | true,false => .leaf leaf_32.certificate
  | true,true => .leaf leaf_33.certificate))

def certifiedWitness : SubdivisionWitness (squareGapPolynomial (nominalComparison true) (1/16) true) square :=
  polynomial_source ▸ witness

end
end Komorebi.LSM.Section88ComparisonRotatedNegGap
