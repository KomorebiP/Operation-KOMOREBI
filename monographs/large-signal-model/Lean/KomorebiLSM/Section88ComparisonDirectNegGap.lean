import KomorebiLSM.PerturbedOperatorFixture
import KomorebiLSM.RecordedBernsteinFixture

/-! Exact rational replay of robust_comparison_certificate.json: direct, chart -1, cone_gap. -/
set_option autoImplicit false
set_option maxRecDepth 4000
set_option maxHeartbeats 800000
namespace Komorebi.LSM.Section88ComparisonDirectNegGap
open TensorBernsteinCertificate RationalBernsteinMargin RationalLorentzMatrix
open PerturbedOperatorFixture RecordedBernsteinFixture
noncomputable section

def polynomial : Polynomial₂ := MvPolynomial.C (39656363/1280000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^0 +
MvPolynomial.C (40537971/640000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^2 +
MvPolynomial.C (-61821389/480000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^0 +
MvPolynomial.C (-23251403/120000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^1 +
MvPolynomial.C (55049844689/230400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^0 +
MvPolynomial.C (108793982311/230400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^2 +
MvPolynomial.C (39656363/1280000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^4 +
MvPolynomial.C (15437009/120000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^4 +
MvPolynomial.C (-92782613/480000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^3 +
MvPolynomial.C (55526301089/230400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^4 +
MvPolynomial.C (9548287/38400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^1 +
MvPolynomial.C (4309697/960000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^0 +
MvPolynomial.C (319712113/38400000000 : ℚ)*MvPolynomial.X 0^2*MvPolynomial.X 1^3 +
MvPolynomial.C (-864703/960000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^4 +
MvPolynomial.C (20126407/1920000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^1 +
MvPolynomial.C (31230493/1920000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^3 +
MvPolynomial.C (2891/512000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^0 +
MvPolynomial.C (2671039/1024000000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^2 +
MvPolynomial.C (-18767/4000000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^4 +
MvPolynomial.C (-319039/320000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^1 +
MvPolynomial.C (36309/80000000 : ℚ)*MvPolynomial.X 0^1*MvPolynomial.X 1^2 +
MvPolynomial.C (319039/320000000 : ℚ)*MvPolynomial.X 0^0*MvPolynomial.X 1^3 +
MvPolynomial.C (-31211089/1920000000 : ℚ)*MvPolynomial.X 0^3*MvPolynomial.X 1^2 +
MvPolynomial.C (-1732689/128000000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^1 +
MvPolynomial.C (-89719/6400000 : ℚ)*MvPolynomial.X 0^4*MvPolynomial.X 1^3

theorem polynomial_source : polynomial=squareGapPolynomial (nominalComparison false) (1/16) true := by
  apply MvPolynomial.funext
  intro x
  norm_num [polynomial,squareGapPolynomial,orientationPolynomial,squareGapPolynomial,outputPolynomial,
    liftPolynomial,denominatorPolynomial,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  ring

def cell_0 : Rectangle := (square.quarter false false)
def leaf_0 : RecordedLeaf polynomial cell_0 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(21658482043/28800000000 : ℚ),(116814854941/230400000000 : ℚ),(281796937067/691200000000 : ℚ),(164789625757/460800000000 : ℚ),(92128879469/230400000000 : ℚ)],![(145803603509/460800000000 : ℚ),(234652710527/921600000000 : ℚ),(623556373399/2764800000000 : ℚ),(193963578727/921600000000 : ℚ),(113320371809/460800000000 : ℚ)],![(122871201689/1382400000000 : ℚ),(302482897967/2764800000000 : ℚ),(919630023679/8294400000000 : ℚ),(307499472517/2764800000000 : ℚ),(186901516889/1382400000000 : ℚ)],![(13662569/480000000 : ℚ),(120014957/2560000000 : ℚ),(95992921/1920000000 : ℚ),(32844363/640000000 : ℚ),(242611867/3840000000 : ℚ)],![(40097167/320000000 : ℚ),(20208103/320000000 : ℚ),(26903549/640000000 : ℚ),(19987701/640000000 : ℚ),(39656363/1280000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(13662569/480000000 : ℚ),?_,?_,?_⟩
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

def cell_1 : Rectangle := (square.quarter false true)
def leaf_1 : RecordedLeaf polynomial cell_1 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(92128879469/230400000000 : ℚ),(203725892119/460800000000 : ℚ),(398605736153/691200000000 : ℚ),(195072300403/230400000000 : ℚ),(41319071593/28800000000 : ℚ)],![(113320371809/460800000000 : ℚ),(259317908509/921600000000 : ℚ),(1015682352091/2764800000000 : ℚ),(498023040491/921600000000 : ℚ),(411126944309/460800000000 : ℚ)],![(186901516889/1382400000000 : ℚ),(440106595039/2764800000000 : ℚ),(1715272758811/8294400000000 : ℚ),(837207749411/2764800000000 : ℚ),(661892414489/1382400000000 : ℚ)],![(242611867/3840000000 : ℚ),(72039389/960000000 : ℚ),(62361433/640000000 : ℚ),(1095986833/7680000000 : ℚ),(213113363/960000000 : ℚ)],![(39656363/1280000000 : ℚ),(9834331/320000000 : ℚ),(26265471/640000000 : ℚ),(2486133/40000000 : ℚ),(40097167/320000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(9834331/320000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_1,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_20 : Rectangle := ((square.quarter true false).quarter false false)
def leaf_20 : RecordedLeaf polynomial cell_20 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(40097167/320000000 : ℚ),(6030527/64000000 : ℚ),(37586059/512000000 : ℚ),(3021413/51200000 : ℚ),(8048951/163840000 : ℚ)],![(66709873/384000000 : ℚ),(752666693/6144000000 : ℚ),(181427603/2048000000 : ℚ),(321292147/4915200000 : ℚ),(120857759/2457600000 : ℚ)],![(1445759862329/5529600000000 : ℚ),(265845852703/1474560000000 : ℚ),(3364218207203/26542080000000 : ℚ),(106437903833/1179648000000 : ℚ),(228901199609/3538944000000 : ℚ)],![(713827033019/1843200000000 : ℚ),(131098027423/491520000000 : ℚ),(1657287942443/8847360000000 : ℚ),(26193443029/196608000000 : ℚ),(112563911009/1179648000000 : ℚ)],![(2034486252971/3686400000000 : ℚ),(125355875649/327680000000 : ℚ),(4796146030067/17694720000000 : ℚ),(25570817567/131072000000 : ℚ),(5238083369/36864000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(8048951/163840000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_20,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_21 : Rectangle := ((square.quarter true false).quarter false true)
def leaf_21 : RecordedLeaf polynomial cell_21 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(8048951/163840000 : ℚ),(16073451/409600000 : ℚ),(34682853/1024000000 : ℚ),(15926353/512000000 : ℚ),(39656363/1280000000 : ℚ)],![(120857759/2457600000 : ℚ),(162138889/4915200000 : ℚ),(3049993/128000000 : ℚ),(1731299/96000000 : ℚ),(571477/38400000 : ℚ)],![(228901199609/3538944000000 : ℚ),(138488687719/3538944000000 : ℚ),(651842850503/26542080000000 : ℚ),(65986972699/4423680000000 : ℚ),(48319732529/5529600000000 : ℚ)],![(112563911009/1179648000000 : ℚ),(16991790961/294912000000 : ℚ),(319385527493/8847360000000 : ℚ),(16111548827/737280000000 : ℚ),(23390789069/1843200000000 : ℚ)],![(5238083369/36864000000 : ℚ),(105099977513/1179648000000 : ℚ),(1045024612367/17694720000000 : ℚ),(14524470287/368640000000 : ℚ),(25096293749/921600000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(48319732529/5529600000000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 5 → Fin 5 → ℚ := ![![(2034486252971/3686400000000 : ℚ),(125355875649/327680000000 : ℚ),(4796146030067/17694720000000 : ℚ),(25570817567/131072000000 : ℚ),(5238083369/36864000000 : ℚ)],![(9171244583/12800000000 : ℚ),(61242399881/122880000000 : ℚ),(43595251217/122880000000 : ℚ),(6314876209/24576000000 : ℚ),(24741491623/131072000000 : ℚ)],![(5086752983927/5529600000000 : ℚ),(949075285309/1474560000000 : ℚ),(12253639078289/26542080000000 : ℚ),(398344703549/1179648000000 : ℚ),(889558281197/3538944000000 : ℚ)],![(119074052773/102400000000 : ℚ),(201286274339/245760000000 : ℚ),(291210998911/491520000000 : ℚ),(86114712409/196608000000 : ℚ),(21665171403/65536000000 : ℚ)],![(41700069133/28800000000 : ℚ),(31548670219/30720000000 : ℚ),(414315554989/552960000000 : ℚ),(27512449723/49152000000 : ℚ),(63115222769/147456000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(5238083369/36864000000 : ℚ),?_,?_,?_⟩
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
  let c : Fin 5 → Fin 5 → ℚ := ![![(5238083369/36864000000 : ℚ),(105099977513/1179648000000 : ℚ),(1045024612367/17694720000000 : ℚ),(14524470287/368640000000 : ℚ),(25096293749/921600000000 : ℚ)],![(24741491623/131072000000 : ℚ),(23705465197/196608000000 : ℚ),(13437760831/163840000000 : ℚ),(13995444107/245760000000 : ℚ),(25664795309/614400000000 : ℚ)],![(889558281197/3538944000000 : ℚ),(584082451747/3538944000000 : ℚ),(3089364194789/26542080000000 : ℚ),(376484374627/4423680000000 : ℚ),(369941313677/5529600000000 : ℚ)],![(21665171403/65536000000 : ℚ),(43876316009/196608000000 : ℚ),(26673005637/163840000000 : ℚ),(30581178349/245760000000 : ℚ),(31676633369/307200000000 : ℚ)],![(63115222769/147456000000 : ℚ),(43693096369/147456000000 : ℚ),(122983658989/552960000000 : ℚ),(32431078819/184320000000 : ℚ),(34849000589/230400000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(25096293749/921600000000 : ℚ),?_,?_,?_⟩
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

def cell_300 : Rectangle := (((square.quarter true true).quarter false false).quarter false false)
def leaf_300 : RecordedLeaf polynomial cell_300 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(39656363/1280000000 : ℚ),(158306413/5120000000 : ℚ),(645462153/20480000000 : ℚ),(2685164283/81920000000 : ℚ),(11412331003/327680000000 : ℚ)],![(176116789/7680000000 : ℚ),(679301519/30720000000 : ℚ),(899218593/40960000000 : ℚ),(44062358051/1966080000000 : ℚ),(23194727257/983040000000 : ℚ)],![(384220596689/22118400000000 : ℚ),(2794911267973/176947200000000 : ℚ),(31703734248319/2123366400000000 : ℚ),(41584203705503/2831155200000000 : ℚ),(85898508160169/5662310400000000 : ℚ)],![(105554186159/7372800000000 : ℚ),(1414019343251/117964800000000 : ℚ),(1852745227291/176947200000000 : ℚ),(18179313917161/1887436800000000 : ℚ),(18078682787939/1887436800000000 : ℚ)],![(12725748611/921600000000 : ℚ),(1265335922407/117964800000000 : ℚ),(48754244345359/5662310400000000 : ℚ),(13736825289227/1887436800000000 : ℚ),(1616790646181/235929600000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(1616790646181/235929600000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_300,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_301 : Rectangle := (((square.quarter true true).quarter false false).quarter false true)
def leaf_301 : RecordedLeaf polynomial cell_301 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(11412331003/327680000000 : ℚ),(6042002437/163840000000 : ℚ),(3253522483/81920000000 : ℚ),(1780439837/40960000000 : ℚ),(990805003/20480000000 : ℚ)],![(23194727257/983040000000 : ℚ),(48716550977/1966080000000 : ℚ),(4372573193/163840000000 : ℚ),(14466749267/491520000000 : ℚ),(1022174281/30720000000 : ℚ)],![(85898508160169/5662310400000000 : ℚ),(820635267679/52428800000000 : ℚ),(71597770744127/4246732800000000 : ℚ),(742984470467/39321600000000 : ℚ),(7805579590889/353894400000000 : ℚ)],![(18078682787939/1887436800000000 : ℚ),(1997561295413/209715200000000 : ℚ),(7260034215331/707788800000000 : ℚ),(623030009783/52428800000000 : ℚ),(1740690822809/117964800000000 : ℚ)],![(1616790646181/235929600000000 : ℚ),(4043941683223/629145600000000 : ℚ),(39124242908011/5662310400000000 : ℚ),(2649301969511/314572800000000 : ℚ),(2688010413251/235929600000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(4043941683223/629145600000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_301,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_302 : Rectangle := (((square.quarter true true).quarter false false).quarter true false)
def leaf_302 : RecordedLeaf polynomial cell_302 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(12725748611/921600000000 : ℚ),(1265335922407/117964800000000 : ℚ),(48754244345359/5662310400000000 : ℚ),(13736825289227/1887436800000000 : ℚ),(1616790646181/235929600000000 : ℚ)],![(32685930539/2457600000000 : ℚ),(372217500521/39321600000000 : ℚ),(6370106902901/943718400000000 : ℚ),(1032704073477/209715200000000 : ℚ),(2596655850319/629145600000000 : ℚ)],![(339242229437/22118400000000 : ℚ),(1902810742909/176947200000000 : ℚ),(31806659712779/4246732800000000 : ℚ),(14929271937899/2831155200000000 : ℚ),(24166216738277/5662310400000000 : ℚ)],![(24527792189/1228800000000 : ℚ),(71899270799/4915200000000 : ℚ),(2563814881663/235929600000000 : ℚ),(219163700013/26214400000000 : ℚ),(2298924647869/314572800000000 : ℚ)],![(25096293749/921600000000 : ℚ),(77955411059/3686400000000 : ℚ),(5993083647691/353894400000000 : ℚ),(209888232931/14745600000000 : ℚ),(3135429336029/235929600000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(2596655850319/629145600000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_302,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_303 : Rectangle := (((square.quarter true true).quarter false false).quarter true true)
def leaf_303 : RecordedLeaf polynomial cell_303 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(1616790646181/235929600000000 : ℚ),(4043941683223/629145600000000 : ℚ),(39124242908011/5662310400000000 : ℚ),(2649301969511/314572800000000 : ℚ),(2688010413251/235929600000000 : ℚ)],![(2596655850319/629145600000000 : ℚ),(2095199480207/629145600000000 : ℚ),(3361368682229/943718400000000 : ℚ),(390105970081/78643200000000 : ℚ),(157886598407/19660800000000 : ℚ)],![(24166216738277/5662310400000000 : ℚ),(513163600021/157286400000000 : ℚ),(1841209787527/530841600000000 : ℚ),(132363617249/26214400000000 : ℚ),(3045352196687/353894400000000 : ℚ)],![(2298924647869/314572800000000 : ℚ),(983942447791/157286400000000 : ℚ),(785347812401/117964800000000 : ℚ),(171299381453/19660800000000 : ℚ),(258293620339/19660800000000 : ℚ)],![(3135429336029/235929600000000 : ℚ),(485441157527/39321600000000 : ℚ),(4656389302489/353894400000000 : ℚ),(314006854039/19660800000000 : ℚ),(39882134503/1843200000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(513163600021/157286400000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_303,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_31 : Rectangle := ((square.quarter true true).quarter false true)
def leaf_31 : RecordedLeaf polynomial cell_31 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(990805003/20480000000 : ℚ),(297993793/5120000000 : ℚ),(186016061/2560000000 : ℚ),(59986231/640000000 : ℚ),(40097167/320000000 : ℚ)],![(223256423/12288000000 : ℚ),(582716489/24576000000 : ℚ),(68378681/2048000000 : ℚ),(303622979/6144000000 : ℚ),(7388057/96000000 : ℚ)],![(310409486729/88473600000000 : ℚ),(232708946807/29491200000000 : ℚ),(2305775973571/132710400000000 : ℚ),(258530476343/7372800000000 : ℚ),(379570811129/5529600000000 : ℚ)],![(136766708969/29491200000000 : ℚ),(54087400051/4915200000000 : ℚ),(1102217817631/44236800000000 : ℚ),(125389070123/2457600000000 : ℚ),(185789483819/1843200000000 : ℚ)],![(39882134503/1843200000000 : ℚ),(108035766003/3276800000000 : ℚ),(4929101289679/88473600000000 : ℚ),(158391549469/1638400000000 : ℚ),(635391047771/3686400000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(310409486729/88473600000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_31,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_32 : Rectangle := ((square.quarter true true).quarter true false)
def leaf_32 : RecordedLeaf polynomial cell_32 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(25096293749/921600000000 : ℚ),(27762823561/1843200000000 : ℚ),(918608385931/88473600000000 : ℚ),(303906410069/29491200000000 : ℚ),(39882134503/1843200000000 : ℚ)],![(25664795309/614400000000 : ℚ),(32681960701/1228800000000 : ℚ),(17461791043/819200000000 : ℚ),(109800633751/4915200000000 : ℚ),(126606843903/3276800000000 : ℚ)],![(369941313677/5529600000000 : ℚ),(1077108636281/22118400000000 : ℚ),(5783062131697/132710400000000 : ℚ),(4181460842281/88473600000000 : ℚ),(6326578803677/88473600000000 : ℚ)],![(31676633369/307200000000 : ℚ),(100507175207/1228800000000 : ℚ),(63500072801/819200000000 : ℚ),(419359381907/4915200000000 : ℚ),(197150903723/1638400000000 : ℚ)],![(34849000589/230400000000 : ℚ),(116636610617/921600000000 : ℚ),(341805594077/2764800000000 : ℚ),(504232109167/3686400000000 : ℚ),(682100440289/3686400000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(303906410069/29491200000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_32,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def cell_33 : Rectangle := ((square.quarter true true).quarter true true)
def leaf_33 : RecordedLeaf polynomial cell_33 := by
  let c : Fin 5 → Fin 5 → ℚ := ![![(39882134503/1843200000000 : ℚ),(108035766003/3276800000000 : ℚ),(4929101289679/88473600000000 : ℚ),(158391549469/1638400000000 : ℚ),(635391047771/3686400000000 : ℚ)],![(126606843903/3276800000000 : ℚ),(135009948979/2457600000000 : ℚ),(26575579667/307200000000 : ℚ),(87446394571/614400000000 : ℚ),(3122233083/12800000000 : ℚ)],![(6326578803677/88473600000000 : ℚ),(2823898921691/29491200000000 : ℚ),(18653769900073/132710400000000 : ℚ),(1604909525309/7372800000000 : ℚ),(1962443291927/5529600000000 : ℚ)],![(197150903723/1638400000000 : ℚ),(763546040431/4915200000000 : ℚ),(534686876927/2457600000000 : ℚ),(395820756619/1228800000000 : ℚ),(51632295173/102400000000 : ℚ)],![(682100440289/3686400000000 : ℚ),(286656257137/1228800000000 : ℚ),(875410587443/2764800000000 : ℚ),(69746521769/153600000000 : ℚ),(19852898683/28800000000 : ℚ)]]
  refine ⟨⟨4,4,c,?_,?_⟩,(39882134503/1843200000000 : ℚ),?_,?_,?_⟩
  · decide +kernel
  · apply MvPolynomial.funext
    intro x
    norm_num [Rectangle.localPolynomial,cell_33,Rectangle.quarter,Rectangle.half,
      Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
      basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
    ring
  · norm_num
  · decide +kernel
  · decide +kernel

def witness : SubdivisionWitness polynomial square :=
 .of_quarters (fun
  | false,false => .leaf leaf_0.certificate
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
  | false,true => .leaf leaf_31.certificate
  | true,false => .leaf leaf_32.certificate
  | true,true => .leaf leaf_33.certificate))

def certifiedWitness : SubdivisionWitness (squareGapPolynomial (nominalComparison false) (1/16) true) square :=
  polynomial_source ▸ witness

end
end Komorebi.LSM.Section88ComparisonDirectNegGap
