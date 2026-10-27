import KomorebiLSM.PerturbedOperatorFixture
import KomorebiLSM.RecordedBernsteinFixture

/-! Exact rational replay of robust_comparison_certificate.json: rotated, chart 1, cone_gap. -/
set_option autoImplicit false
set_option maxRecDepth 4000
set_option maxHeartbeats 800000
namespace Komorebi.LSM.Section88ComparisonRotatedPosGap
open TensorBernsteinCertificate RationalBernsteinMargin RationalLorentzMatrix
open PerturbedOperatorFixture RecordedBernsteinFixture
noncomputable section

def polynomial : Polynomial₂ := MvPolynomial.C (40048363/1280000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^0 +
MvPolynomial.C (40537971/640000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^2 +
MvPolynomial.C (359387/160000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^0 +
MvPolynomial.C (9985843/30000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^1 +
MvPolynomial.C (57325581089/230400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^0 +
MvPolynomial.C (117860942311/230400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^2 +
MvPolynomial.C (40048363/1280000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^4 +
MvPolynomial.C (-142919/80000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^4 +
MvPolynomial.C (159408487/480000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^3 +
MvPolynomial.C (57978084689/230400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^4 +
MvPolynomial.C (80127887/38400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^1 +
MvPolynomial.C (-5561353/960000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^0 +
MvPolynomial.C (131571713/38400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^3 +
MvPolynomial.C (1597547/960000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^4 +
MvPolynomial.C (17323607/1920000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^1 +
MvPolynomial.C (41128493/1920000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^3 +
MvPolynomial.C (38563/4000000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^0 +
MvPolynomial.C (695359/1024000000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^2 +
MvPolynomial.C (-97069/12800000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^4 +
MvPolynomial.C (366961/320000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^1 +
MvPolynomial.C (36309/80000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^2 +
MvPolynomial.C (-366961/320000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^3 +
MvPolynomial.C (23825711/1920000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^2 +
MvPolynomial.C (3283/6400000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^1 +
MvPolynomial.C (-66591/128000000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^3

theorem polynomial_source : polynomial=squareGapPolynomial (nominalComparison true) (1/16) false := by
  apply polynomial_eq_of_value_eq
  intro x
  norm_num [value,polynomial,squareGapPolynomial,orientationPolynomial,squareGapPolynomial,outputPolynomial,
    liftPolynomial,denominatorPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  ring

def cell_0 : Rectangle := (square.quarter false false)
def leaf_0 : RecordedLeaf polynomial cell_0 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(52455119593/28800000000 : ℚ),(211088168341/230400000000 : ℚ),(384402283967/691200000000 : ℚ),(174098915257/460800000000 : ℚ),(67572722669/230400000000 : ℚ)],![(521965112309/460800000000 : ℚ),(519821152127/921600000000 : ℚ),(920467762999/2764800000000 : ℚ),(200801724727/921600000000 : ℚ),(71634078209/460800000000 : ℚ)],![(864951494489/1382400000000 : ℚ),(860343479567/2764800000000 : ℚ),(1483284169279/8294400000000 : ℚ),(312054414517/2764800000000 : ℚ),(99025261289/1382400000000 : ℚ)],![(140125619/480000000 : ℚ),(1113095071/7680000000 : ℚ),(158012921/1920000000 : ℚ),(49193657/960000000 : ℚ),(39329589/1280000000 : ℚ)],![(40293167/320000000 : ℚ),(19963103/320000000 : ℚ),(26413549/640000000 : ℚ),(19840701/640000000 : ℚ),(40048363/1280000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(39329589/1280000000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply polynomial_eq_of_value_eq
    intro x
    norm_num [value,Rectangle.localPolynomial,cell_0,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨3,4,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_10 : Rectangle := ((square.quarter false true).quarter false false)
def leaf_10 : RecordedLeaf polynomial cell_10 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(67572722669/230400000000 : ℚ),(231337420757/921600000000 : ℚ),(641975558717/2764800000000 : ℚ),(832493679307/3686400000000 : ℚ),(877873160369/3686400000000 : ℚ)],![(68926507849/307200000000 : ℚ),(230559195347/1228800000000 : ℚ),(1247393058689/7372800000000 : ℚ),(261462572349/1638400000000 : ℚ),(266895731883/1638400000000 : ℚ)],![(934266066557/5529600000000 : ℚ),(3044138144921/22118400000000 : ℚ),(15963037169377/132710400000000 : ℚ),(9635420776921/88473600000000 : ℚ),(9367686480557/88473600000000 : ℚ)],![(77205265549/614400000000 : ℚ),(61229426243/614400000000 : ℚ),(620536774957/7372800000000 : ℚ),(59436537681/819200000000 : ℚ),(216379959783/3276800000000 : ℚ)],![(86348037449/921600000000 : ℚ),(268964748347/3686400000000 : ℚ),(5319440533531/88473600000000 : ℚ),(1471626531119/29491200000000 : ℚ),(79085938303/1843200000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(79085938303/1843200000000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply polynomial_eq_of_value_eq
    intro x
    norm_num [value,Rectangle.localPolynomial,cell_10,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨4,4,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_11 : Rectangle := ((square.quarter false true).quarter false true)
def leaf_11 : RecordedLeaf polynomial cell_11 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(877873160369/3686400000000 : ℚ),(307750880477/1228800000000 : ℚ),(778114001903/2764800000000 : ℚ),(51813163249/153600000000 : ℚ),(12716850043/28800000000 : ℚ)],![(266895731883/1638400000000 : ℚ),(272328891417/1638400000000 : ℚ),(1345189930301/7372800000000 : ℚ),(88348367833/409600000000 : ℚ),(87112937399/307200000000 : ℚ)],![(9367686480557/88473600000000 : ℚ),(3033317394731/29491200000000 : ℚ),(14356631391193/132710400000000 : ℚ),(916003218269/7372800000000 : ℚ),(905871872807/5529600000000 : ℚ)],![(216379959783/3276800000000 : ℚ),(97506884421/1638400000000 : ℚ),(53530132061/921600000000 : ℚ),(12893353927/204800000000 : ℚ),(12776595131/153600000000 : ℚ)],![(79085938303/1843200000000 : ℚ),(353041164859/9830400000000 : ℚ),(2844422314279/88473600000000 : ℚ),(158440801607/4915200000000 : ℚ),(157358597771/3686400000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(2844422314279/88473600000000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply polynomial_eq_of_value_eq
    intro x
    norm_num [value,Rectangle.localPolynomial,cell_11,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨4,2,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_12 : Rectangle := ((square.quarter false true).quarter true false)
def leaf_12 : RecordedLeaf polynomial cell_12 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(86348037449/921600000000 : ℚ),(268964748347/3686400000000 : ℚ),(5319440533531/88473600000000 : ℚ),(1471626531119/29491200000000 : ℚ),(79085938303/1843200000000 : ℚ)],![(113776353149/1843200000000 : ℚ),(42638234809/921600000000 : ℚ),(1596219883789/44236800000000 : ℚ),(401768852861/14745600000000 : ℚ),(583330387649/29491200000000 : ℚ)],![(227229405569/5529600000000 : ℚ),(682254726257/22118400000000 : ℚ),(3201032573659/132710400000000 : ℚ),(1618354872157/88473600000000 : ℚ),(1183150978169/88473600000000 : ℚ)],![(2480561/80000000 : ℚ),(199291367/7680000000 : ℚ),(180699709/7680000000 : ℚ),(2753930093/122880000000 : ℚ),(1427529653/61440000000 : ℚ)],![(40048363/1280000000 : ℚ),(80463687/2560000000 : ℚ),(175173953/5120000000 : ℚ),(405499417/10240000000 : ℚ),(1013933003/20480000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(1183150978169/88473600000000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply polynomial_eq_of_value_eq
    intro x
    norm_num [value,Rectangle.localPolynomial,cell_12,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨2,4,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_13 : Rectangle := ((square.quarter false true).quarter true true)
def leaf_13 : RecordedLeaf polynomial cell_13 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(79085938303/1843200000000 : ℚ),(353041164859/9830400000000 : ℚ),(2844422314279/88473600000000 : ℚ),(158440801607/4915200000000 : ℚ),(157358597771/3686400000000 : ℚ)],![(583330387649/29491200000000 : ℚ),(15130127899/1228800000000 : ℚ),(274975975351/44236800000000 : ℚ),(3720554483/2457600000000 : ℚ),(4039456199/1843200000000 : ℚ)],![(1183150978169/88473600000000 : ℚ),(249315694727/29491200000000 : ℚ),(589809209731/132710400000000 : ℚ),(10005062423/7372800000000 : ℚ),(10193760569/5529600000000 : ℚ)],![(1427529653/61440000000 : ℚ),(985396173/40960000000 : ℚ),(274642683/10240000000 : ℚ),(329318627/10240000000 : ℚ),(20487191/480000000 : ℚ)],![(1013933003/20480000000 : ℚ),(304216793/5120000000 : ℚ),(189054061/2560000000 : ℚ),(60623231/640000000 : ℚ),(40293167/320000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(10005062423/7372800000000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply polynomial_eq_of_value_eq
    intro x
    norm_num [value,Rectangle.localPolynomial,cell_13,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨2,3,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_20 : Rectangle := ((square.quarter true false).quarter false false)
def leaf_20 : RecordedLeaf polynomial cell_20 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(40293167/320000000 : ℚ),(6025627/64000000 : ℚ),(37370459/512000000 : ℚ),(2994463/51200000 : ℚ),(7970551/163840000 : ℚ)],![(16477453/384000000 : ℚ),(65556431/2048000000 : ℚ),(54214363/2048000000 : ℚ),(7757513/327680000 : ℚ),(56368649/2457600000 : ℚ)],![(10179131129/5529600000000 : ℚ),(1916485183/1474560000000 : ℚ),(115974898403/26542080000000 : ℚ),(9965138633/1179648000000 : ℚ),(47826053609/3538944000000 : ℚ)],![(3715829819/1843200000000 : ℚ),(732515503/491520000000 : ℚ),(55398156443/8847360000000 : ℚ),(2448622909/196608000000 : ℚ),(23682792809/1179648000000 : ℚ)],![(158199143771/3686400000000 : ℚ),(31891953427/983040000000 : ℚ),(570173251067/17694720000000 : ℚ),(14112102931/393216000000 : ℚ),(3162072013/73728000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(1916485183/1474560000000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply polynomial_eq_of_value_eq
    intro x
    norm_num [value,Rectangle.localPolynomial,cell_20,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨2,1,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_21 : Rectangle := ((square.quarter true false).quarter false true)
def leaf_21 : RecordedLeaf polynomial cell_21 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(7970551/163840000 : ℚ),(15897051/409600000 : ℚ),(34447653/1024000000 : ℚ),(15945953/512000000 : ℚ),(40048363/1280000000 : ℚ)],![(56368649/2457600000 : ℚ),(109111901/4915200000 : ℚ),(18064513/768000000 : ℚ),(40280449/1536000000 : ℚ),(161631/5120000 : ℚ)],![(47826053609/3538944000000 : ℚ),(65756691319/3538944000000 : ℚ),(653894029703/26542080000000 : ℚ),(140054740459/4423680000000 : ℚ),(233439612929/5529600000000 : ℚ)],![(23682792809/1179648000000 : ℚ),(8168462041/294912000000 : ℚ),(325129817093/8847360000000 : ℚ),(34826238107/737280000000 : ℚ),(116214094469/1843200000000 : ℚ)],![(3162072013/73728000000 : ℚ),(58849995623/1179648000000 : ℚ),(1065583855967/17694720000000 : ℚ),(54067792789/737280000000 : ℚ),(87083381849/921600000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(47826053609/3538944000000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply polynomial_eq_of_value_eq
    intro x
    norm_num [value,Rectangle.localPolynomial,cell_21,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨2,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_22 : Rectangle := ((square.quarter true false).quarter true false)
def leaf_22 : RecordedLeaf polynomial cell_22 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(158199143771/3686400000000 : ℚ),(31891953427/983040000000 : ℚ),(570173251067/17694720000000 : ℚ),(14112102931/393216000000 : ℚ),(3162072013/73728000000 : ℚ)],![(1609201187/19200000000 : ℚ),(2596619827/40960000000 : ℚ),(1787413523/30720000000 : ℚ),(1943913337/32768000000 : ℚ),(25834503869/393216000000 : ℚ)],![(914784035927/5529600000000 : ℚ),(184478019709/1474560000000 : ℚ),(2872236527489/26542080000000 : ℚ),(120543423989/1179648000000 : ℚ),(370750366397/3538944000000 : ℚ)],![(88245517519/307200000000 : ℚ),(17812842433/81920000000 : ℚ),(89647715311/491520000000 : ℚ),(10791855883/65536000000 : ℚ),(31524476609/196608000000 : ℚ)],![(12929282683/28800000000 : ℚ),(10464717539/30720000000 : ℚ),(155534833489/552960000000 : ℚ),(12166030103/49152000000 : ℚ),(34397731169/147456000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(570173251067/17694720000000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply polynomial_eq_of_value_eq
    intro x
    norm_num [value,Rectangle.localPolynomial,cell_22,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨0,2,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_23 : Rectangle := ((square.quarter true false).quarter true true)
def leaf_23 : RecordedLeaf polynomial cell_23 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(3162072013/73728000000 : ℚ),(58849995623/1179648000000 : ℚ),(1065583855967/17694720000000 : ℚ),(54067792789/737280000000 : ℚ),(87083381849/921600000000 : ℚ)],![(25834503869/393216000000 : ℚ),(14171023847/196608000000 : ℚ),(13712111831/163840000000 : ℚ),(24436449157/245760000000 : ℚ),(25791048103/204800000000 : ℚ)],![(370750366397/3538944000000 : ℚ),(379870460827/3538944000000 : ℚ),(3145839360389/26542080000000 : ℚ),(601852052827/4423680000000 : ℚ),(928871643677/5529600000000 : ℚ)],![(31524476609/196608000000 : ℚ),(30673385569/196608000000 : ℚ),(27045601637/163840000000 : ℚ),(45115869989/245760000000 : ℚ),(22636502323/102400000000 : ℚ)],![(34397731169/147456000000 : ℚ),(32297372029/147456000000 : ℚ),(124029446389/552960000000 : ℚ),(44787318799/184320000000 : ℚ),(65938307789/230400000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(3162072013/73728000000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply polynomial_eq_of_value_eq
    intro x
    norm_num [value,Rectangle.localPolynomial,cell_23,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨0,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def cell_3 : Rectangle := (square.quarter true true)
def leaf_3 : RecordedLeaf polynomial cell_3 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(40048363/1280000000 : ℚ),(10103831/320000000 : ℚ),(27147471/640000000 : ℚ),(1270629/20000000 : ℚ),(40293167/320000000 : ℚ)],![(40767137/1280000000 : ℚ),(101644519/1920000000 : ℚ),(162443627/1920000000 : ℚ),(1131398839/7680000000 : ℚ),(280689739/960000000 : ℚ)],![(102130364969/1382400000000 : ℚ),(320330660719/2764800000000 : ℚ),(1514938443931/8294400000000 : ℚ),(872583381731/2764800000000 : ℚ),(868754772569/1382400000000 : ℚ)],![(71851905329/460800000000 : ℚ),(202246570129/921600000000 : ℚ),(931002667771/2764800000000 : ℚ),(526718181371/921600000000 : ℚ),(527044720829/460800000000 : ℚ)],![(65938307789/230400000000 : ℚ),(171693252739/460800000000 : ℚ),(385052196293/691200000000 : ℚ),(213914836843/230400000000 : ℚ),(53301813133/28800000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(40048363/1280000000 : ℚ),?_,?_,?_⟩
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · apply polynomial_eq_of_value_eq
    intro x
    norm_num [value,Rectangle.localPolynomial,cell_3,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  · exact ⟨0,0,by norm_num [c,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]⟩

def witness : SubdivisionWitness polynomial square :=
 .of_quarters (fun
  | false,false => .leaf leaf_0.certificate
  | false,true => .of_quarters (fun
  | false,false => .leaf leaf_10.certificate
  | false,true => .leaf leaf_11.certificate
  | true,false => .leaf leaf_12.certificate
  | true,true => .leaf leaf_13.certificate)
  | true,false => .of_quarters (fun
  | false,false => .leaf leaf_20.certificate
  | false,true => .leaf leaf_21.certificate
  | true,false => .leaf leaf_22.certificate
  | true,true => .leaf leaf_23.certificate)
  | true,true => .leaf leaf_3.certificate)

def certifiedWitness : SubdivisionWitness (squareGapPolynomial (nominalComparison true) (1/16) false) square :=
  polynomial_source ▸ witness

end
end Komorebi.LSM.Section88ComparisonRotatedPosGap
