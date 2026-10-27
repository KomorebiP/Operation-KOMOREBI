import KomorebiLSM.PerturbedOperatorFixture
import KomorebiLSM.RecordedBernsteinFixture

/-! Exact rational replay of robust_comparison_certificate.json: direct, chart 1, cone_gap. -/
set_option autoImplicit false
set_option maxRecDepth 4000
set_option maxHeartbeats 800000
namespace Komorebi.LSM.Section88ComparisonDirectPosGap
open TensorBernsteinCertificate RationalBernsteinMargin RationalLorentzMatrix
open PerturbedOperatorFixture RecordedBernsteinFixture
noncomputable section

def polynomial : Polynomial₂ := MvPolynomial.C (39656363/1280000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^0 +
MvPolynomial.C (40537971/640000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^2 +
MvPolynomial.C (15437009/120000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^0 +
MvPolynomial.C (92782613/480000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^1 +
MvPolynomial.C (55526301089/230400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^0 +
MvPolynomial.C (108793982311/230400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^2 +
MvPolynomial.C (39656363/1280000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^4 +
MvPolynomial.C (-61821389/480000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^4 +
MvPolynomial.C (23251403/120000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^3 +
MvPolynomial.C (55049844689/230400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^4 +
MvPolynomial.C (-319712113/38400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^1 +
MvPolynomial.C (-864703/960000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^0 +
MvPolynomial.C (-9548287/38400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^3 +
MvPolynomial.C (4309697/960000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^4 +
MvPolynomial.C (-31230493/1920000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^1 +
MvPolynomial.C (-20126407/1920000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^3 +
MvPolynomial.C (-18767/4000000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^0 +
MvPolynomial.C (2671039/1024000000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^2 +
MvPolynomial.C (2891/512000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^4 +
MvPolynomial.C (-319039/320000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^1 +
MvPolynomial.C (36309/80000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^2 +
MvPolynomial.C (319039/320000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^3 +
MvPolynomial.C (-31211089/1920000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^2 +
MvPolynomial.C (89719/6400000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^1 +
MvPolynomial.C (1732689/128000000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^3

theorem polynomial_source : polynomial=squareGapPolynomial (nominalComparison false) (1/16) false := by
  apply MvPolynomial.funext
  intro x
  norm_num [polynomial,squareGapPolynomial,orientationPolynomial,squareGapPolynomial,outputPolynomial,
    liftPolynomial,denominatorPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  ring

def cell_00 : Rectangle := ((square.quarter false false).quarter false false)
def leaf_00 : RecordedLeaf polynomial cell_00 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(41319071593/28800000000 : ℚ),(31068856339/30720000000 : ℚ),(404873800849/552960000000 : ℚ),(26637373423/49152000000 : ℚ),(60503950049/147456000000 : ℚ)],![(357410696599/307200000000 : ℚ),(200707741139/245760000000 : ℚ),(866928569773/1474560000000 : ℚ),(84925432429/196608000000 : ℚ),(63648508129/196608000000 : ℚ)],![(5111969516807/5529600000000 : ℚ),(952110964669/1474560000000 : ℚ),(12257068188449/26542080000000 : ℚ),(396851348189/1179648000000 : ℚ),(881950278557/3538944000000 : ℚ)],![(110778033631/153600000000 : ℚ),(61596722801/122880000000 : ℚ),(131321990051/368640000000 : ℚ),(50597897957/196608000000 : ℚ),(74103625189/393216000000 : ℚ)],![(2048157664571/3686400000000 : ℚ),(126167891889/327680000000 : ℚ),(4822852560827/17694720000000 : ℚ),(25674313897/131072000000 : ℚ),(10497636823/73728000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(10497636823/73728000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_00,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_01 : Rectangle := ((square.quarter false false).quarter false true)
def leaf_01 : RecordedLeaf polynomial cell_01 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(60503950049/147456000000 : ℚ),(41095779829/147456000000 : ℚ),(113751247549/552960000000 : ℚ),(29692160119/184320000000 : ℚ),(32151938669/230400000000 : ℚ)],![(63648508129/196608000000 : ℚ),(42371583829/196608000000 : ℚ),(228620840773/1474560000000 : ℚ),(9608141163/81920000000 : ℚ),(9972405283/102400000000 : ℚ)],![(881950278557/3538944000000 : ℚ),(573346512547/3538944000000 : ℚ),(2998955208149/26542080000000 : ℚ),(361927411507/4423680000000 : ℚ),(355036254557/5529600000000 : ℚ)],![(74103625189/393216000000 : ℚ),(91819247/768000000 : ℚ),(118905399329/1474560000000 : ℚ),(568507133/10240000000 : ℚ),(8307886183/204800000000 : ℚ)],![(10497636823/73728000000 : ℚ),(104855553263/1179648000000 : ℚ),(1036454406527/17694720000000 : ℚ),(28630141249/737280000000 : ℚ),(24634287449/921600000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(24634287449/921600000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_01,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_02 : Rectangle := ((square.quarter false false).quarter true false)
def leaf_02 : RecordedLeaf polynomial cell_02 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(2048157664571/3686400000000 : ℚ),(126167891889/327680000000 : ℚ),(4822852560827/17694720000000 : ℚ),(25674313897/131072000000 : ℚ),(10497636823/73728000000 : ℚ)],![(718821260999/1843200000000 : ℚ),(132116784463/491520000000 : ℚ),(1671124799603/8847360000000 : ℚ),(13212521867/98304000000 : ℚ),(113613502769/1179648000000 : ℚ)],![(1448878661369/5529600000000 : ℚ),(266490324223/1474560000000 : ℚ),(3373450418723/26542080000000 : ℚ),(106777097513/1179648000000 : ℚ),(229766041769/3538944000000 : ℚ)],![(5209451/30000000 : ℚ),(752230691/6144000000 : ℚ),(90653017/1024000000 : ℚ),(80268169/1228800000 : ℚ),(60392203/1228800000 : ℚ)],![(40097167/320000000 : ℚ),(6030527/64000000 : ℚ),(37586059/512000000 : ℚ),(3021413/51200000 : ℚ),(8048951/163840000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(8048951/163840000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_02,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_03 : Rectangle := ((square.quarter false false).quarter true true)
def leaf_03 : RecordedLeaf polynomial cell_03 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(10497636823/73728000000 : ℚ),(104855553263/1179648000000 : ℚ),(1036454406527/17694720000000 : ℚ),(28630141249/737280000000 : ℚ),(24634287449/921600000000 : ℚ)],![(113613502769/1179648000000 : ℚ),(34338371567/589824000000 : ℚ),(323022010553/8847360000000 : ℚ),(8163884461/368640000000 : ℚ),(23766174149/1843200000000 : ℚ)],![(229766041769/3538944000000 : ℚ),(139200790999/3538944000000 : ℚ),(656492895623/26542080000000 : ℚ),(66670475659/4423680000000 : ℚ),(49007445569/5529600000000 : ℚ)],![(60392203/1228800000 : ℚ),(40516237/1228800000 : ℚ),(24399797/1024000000 : ℚ),(110875901/6144000000 : ℚ),(57221053/3840000000 : ℚ)],![(8048951/163840000 : ℚ),(16073451/409600000 : ℚ),(34682853/1024000000 : ℚ),(15926353/512000000 : ℚ),(39656363/1280000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(49007445569/5529600000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_03,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_10 : Rectangle := ((square.quarter false true).quarter false false)
def leaf_10 : RecordedLeaf polynomial cell_10 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(32151938669/230400000000 : ℚ),(108754708757/921600000000 : ℚ),(330519686717/2764800000000 : ℚ),(511985127307/3686400000000 : ℚ),(721556216369/3686400000000 : ℚ)],![(9972405283/102400000000 : ℚ),(31738536449/409600000000 : ℚ),(556226106689/7372800000000 : ℚ),(424669211047/4915200000000 : ℚ),(617739423649/4915200000000 : ℚ)],![(355036254557/5529600000000 : ℚ),(1030652978921/22118400000000 : ℚ),(5646967097377/132710400000000 : ℚ),(4227503170921/88473600000000 : ℚ),(6551608908557/88473600000000 : ℚ)],![(8307886183/204800000000 : ℚ),(2622814853/102400000000 : ℚ),(153562063957/7372800000000 : ℚ),(27744466709/1228800000000 : ℚ),(391081092349/9830400000000 : ℚ)],![(24634287449/921600000000 : ℚ),(53923593347/3686400000000 : ℚ),(899370613531/88473600000000 : ℚ),(307065021119/29491200000000 : ℚ),(40768419553/1843200000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(899370613531/88473600000000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 5 → Fin 5 → ℚ := ![![(721556216369/3686400000000 : ℚ),(310375768477/1228800000000 : ℚ),(959232953903/2764800000000 : ℚ),(76573619249/153600000000 : ℚ),(21658482043/28800000000 : ℚ)],![(617739423649/4915200000000 : ℚ),(810809636251/4915200000000 : ℚ),(1714647382301/7372800000000 : ℚ),(422481711499/1228800000000 : ℚ),(164113105399/307200000000 : ℚ)],![(6551608908557/88473600000000 : ℚ),(2958571548731/29491200000000 : ℚ),(19591601523193/132710400000000 : ℚ),(1679007474269/7372800000000 : ℚ),(2037299960807/5529600000000 : ℚ)],![(391081092349/9830400000000 : ℚ),(280103225513/4915200000000 : ℚ),(165234534997/1843200000000 : ℚ),(90117888781/614400000000 : ℚ),(38330574631/153600000000 : ℚ)],![(40768419553/1843200000000 : ℚ),(110836044953/3276800000000 : ℚ),(5042126914279/88473600000000 : ℚ),(161162773869/1638400000000 : ℚ),(642848357771/3686400000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(40768419553/1843200000000 : ℚ),?_,?_,?_⟩
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

def cell_120 : Rectangle := (((square.quarter false true).quarter true false).quarter false false)
def leaf_120 : RecordedLeaf polynomial cell_120 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(24634287449/921600000000 : ℚ),(152460743143/7372800000000 : ℚ),(5852594689291/353894400000000 : ℚ),(1644449536673/117964800000000 : ℚ),(3096574104929/235929600000000 : ℚ)],![(24344916349/1228800000000 : ℚ),(71139647809/4915200000000 : ℚ),(281252163087/26214400000000 : ℚ),(649272934699/78643200000000 : ℚ),(759936076943/104857600000000 : ℚ)],![(339410215157/22118400000000 : ℚ),(1900999830799/176947200000000 : ℚ),(31739840557019/4246732800000000 : ℚ),(14891055152789/2831155200000000 : ℚ),(24115160515997/5662310400000000 : ℚ)],![(32840108059/2457600000000 : ℚ),(373983280201/39321600000000 : ℚ),(711290081509/104857600000000 : ℚ),(3113639958811/629145600000000 : ℚ),(868630062813/209715200000000 : ℚ)],![(51164718389/3686400000000 : ℚ),(318019028923/29491200000000 : ℚ),(49015872616879/5662310400000000 : ℚ),(862765427957/117964800000000 : ℚ),(6488668836869/943718400000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(868630062813/209715200000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_120,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_121 : Rectangle := (((square.quarter false true).quarter true false).quarter false true)
def leaf_121 : RecordedLeaf polynomial cell_121 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(3096574104929/235929600000000 : ℚ),(7563148793/614400000000 : ℚ),(4698644878789/353894400000000 : ℚ),(319786577989/19660800000000 : ℚ),(40768419553/1843200000000 : ℚ)],![(759936076943/104857600000000 : ℚ),(981262361431/157286400000000 : ℚ),(263236490647/39321600000000 : ℚ),(173161453973/19660800000000 : ℚ),(87071206833/6553600000000 : ℚ)],![(24115160515997/5662310400000000 : ℚ),(128112574489/39321600000000 : ℚ),(3684747797069/1061683200000000 : ℚ),(132512455239/26214400000000 : ℚ),(3045187168607/353894400000000 : ℚ)],![(868630062813/209715200000000 : ℚ),(2098140418067/629145600000000 : ℚ),(1118370703783/314572800000000 : ℚ),(388269056611/78643200000000 : ℚ),(52299415289/6553600000000 : ℚ)],![(6488668836869/943718400000000 : ℚ),(1012535708347/157286400000000 : ℚ),(39092962533991/5662310400000000 : ℚ),(2641044434141/314572800000000 : ℚ),(2674884700931/235929600000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(128112574489/39321600000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_121,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_122 : Rectangle := (((square.quarter false true).quarter true false).quarter true false)
def leaf_122 : RecordedLeaf polynomial cell_122 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(51164718389/3686400000000 : ℚ),(318019028923/29491200000000 : ℚ),(49015872616879/5662310400000000 : ℚ),(862765427957/117964800000000 : ℚ),(6488668836869/943718400000000 : ℚ)],![(106138549379/7372800000000 : ℚ),(1422202390781/117964800000000 : ℚ),(3726380052017/353894400000000 : ℚ),(18267573818191/1887436800000000 : ℚ),(18137004782159/1887436800000000 : ℚ)],![(385119566369/22118400000000 : ℚ),(2801757481333/176947200000000 : ℚ),(31779232601599/2123366400000000 : ℚ),(41671016978063/2831155200000000 : ℚ),(86031165817049/5662310400000000 : ℚ)],![(88095071/3840000000 : ℚ),(2718602723/122880000000 : ℚ),(899734269/40960000000 : ℚ),(11022032927/491520000000 : ℚ),(46414714847/1966080000000 : ℚ)],![(39656363/1280000000 : ℚ),(158306413/5120000000 : ℚ),(645462153/20480000000 : ℚ),(2685164283/81920000000 : ℚ),(11412331003/327680000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(6488668836869/943718400000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_122,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_123 : Rectangle := (((square.quarter false true).quarter true false).quarter true true)
def leaf_123 : RecordedLeaf polynomial cell_123 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(6488668836869/943718400000000 : ℚ),(1012535708347/157286400000000 : ℚ),(39092962533991/5662310400000000 : ℚ),(2641044434141/314572800000000 : ℚ),(2674884700931/235929600000000 : ℚ)],![(18137004782159/1887436800000000 : ℚ),(2000715082903/209715200000000 : ℚ),(3628453274993/353894400000000 : ℚ),(621502106973/52428800000000 : ℚ),(1733495225729/117964800000000 : ℚ)],![(86031165817049/5662310400000000 : ℚ),(821484237759/52428800000000 : ℚ),(71625860785967/4246732800000000 : ℚ),(742752786707/39321600000000 : ℚ),(7797821671769/353894400000000 : ℚ)],![(46414714847/1966080000000 : ℚ),(24370648993/983040000000 : ℚ),(4374464789/163840000000 : ℚ),(7235745523/245760000000 : ℚ),(4089539287/122880000000 : ℚ)],![(11412331003/327680000000 : ℚ),(6042002437/163840000000 : ℚ),(3253522483/81920000000 : ℚ),(1780439837/40960000000 : ℚ),(990805003/20480000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(1012535708347/157286400000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_123,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_13 : Rectangle := ((square.quarter false true).quarter true true)
def leaf_13 : RecordedLeaf polynomial cell_13 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(40768419553/1843200000000 : ℚ),(110836044953/3276800000000 : ℚ),(5042126914279/88473600000000 : ℚ),(161162773869/1638400000000 : ℚ),(642848357771/3686400000000 : ℚ)],![(131346148649/29491200000000 : ℚ),(26202454673/2457600000000 : ℚ),(1076498074351/44236800000000 : ℚ),(123016766483/2457600000000 : ℚ),(182881462199/1843200000000 : ℚ)],![(300226138169/88473600000000 : ℚ),(226191754727/29491200000000 : ℚ),(2256816929731/132710400000000 : ℚ),(254278742423/7372800000000 : ℚ),(374787360569/5529600000000 : ℚ)],![(558562139/30720000000 : ℚ),(728473411/30720000000 : ℚ),(170865779/5120000000 : ℚ),(1516826881/30720000000 : ℚ),(147616639/1920000000 : ℚ)],![(990805003/20480000000 : ℚ),(297993793/5120000000 : ℚ),(186016061/2560000000 : ℚ),(59986231/640000000 : ℚ),(40097167/320000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(300226138169/88473600000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_13,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_2 : Rectangle := (square.quarter true false)
def leaf_2 : RecordedLeaf polynomial cell_2 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(40097167/320000000 : ℚ),(20208103/320000000 : ℚ),(26903549/640000000 : ℚ),(19987701/640000000 : ℚ),(39656363/1280000000 : ℚ)],![(27469639/960000000 : ℚ),(120356291/2560000000 : ℚ),(192207371/3840000000 : ℚ),(131353981/2560000000 : ℚ),(242465161/3840000000 : ℚ)],![(127238489369/1382400000000 : ℚ),(308124217007/2764800000000 : ℚ),(929372454559/8294400000000 : ℚ),(309389469157/2764800000000 : ℚ),(187272344969/1382400000000 : ℚ)],![(147044277629/460800000000 : ℚ),(237673101887/921600000000 : ℚ),(633554102119/2764800000000 : ℚ),(197038845187/921600000000 : ℚ),(114157413329/460800000000 : ℚ)],![(19852898683/28800000000 : ℚ),(108406813621/230400000000 : ℚ),(270414077327/691200000000 : ℚ),(161095042417/460800000000 : ℚ),(91014995789/230400000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(27469639/960000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_2,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_3 : Rectangle := (square.quarter true true)
def leaf_3 : RecordedLeaf polynomial cell_3 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(39656363/1280000000 : ℚ),(9834331/320000000 : ℚ),(26265471/640000000 : ℚ),(2486133/40000000 : ℚ),(40097167/320000000 : ℚ)],![(242465161/3840000000 : ℚ),(575798701/7680000000 : ℚ),(124648043/1280000000 : ℚ),(1096118839/7680000000 : ℚ),(26657233/120000000 : ℚ)],![(187272344969/1382400000000 : ℚ),(439699910719/2764800000000 : ℚ),(1711235103931/8294400000000 : ℚ),(834304581731/2764800000000 : ℚ),(658357452569/1382400000000 : ℚ)],![(114157413329/460800000000 : ℚ),(259590808129/921600000000 : ℚ),(1008865879771/2764800000000 : ℚ),(491487573371/921600000000 : ℚ),(404465368829/460800000000 : ℚ)],![(91014995789/230400000000 : ℚ),(202964940739/460800000000 : ℚ),(396023772293/691200000000 : ℚ),(193971052843/230400000000 : ℚ),(41700069133/28800000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(9834331/320000000 : ℚ),?_,?_,?_⟩
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
  | false,false => .of_quarters (fun
  | false,false => .leaf leaf_00.certificate
  | false,true => .leaf leaf_01.certificate
  | true,false => .leaf leaf_02.certificate
  | true,true => .leaf leaf_03.certificate)
  | false,true => .of_quarters (fun
  | false,false => .leaf leaf_10.certificate
  | false,true => .leaf leaf_11.certificate
  | true,false => .of_quarters (fun
  | false,false => .leaf leaf_120.certificate
  | false,true => .leaf leaf_121.certificate
  | true,false => .leaf leaf_122.certificate
  | true,true => .leaf leaf_123.certificate)
  | true,true => .leaf leaf_13.certificate)
  | true,false => .leaf leaf_2.certificate
  | true,true => .leaf leaf_3.certificate)

def certifiedWitness : SubdivisionWitness (squareGapPolynomial (nominalComparison false) (1/16) false) square :=
  polynomial_source ▸ witness

end
end Komorebi.LSM.Section88ComparisonDirectPosGap
