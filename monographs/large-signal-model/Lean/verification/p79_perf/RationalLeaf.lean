import KomorebiLSM.PerturbedOperatorFixture
import KomorebiLSM.RecordedBernsteinFixture
set_option autoImplicit false
set_option maxRecDepth 4000
set_option maxHeartbeats 400000
namespace Komorebi.LSM.P79Performance
open TensorBernsteinCertificate RationalBernsteinMargin RationalLorentzMatrix PerturbedOperatorFixture
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


def cell_0 : Rectangle := (square.quarter false false)
def c : Fin 5 → Fin 5 → ℚ := ![![(21658482043/28800000000 : ℚ),(116814854941/230400000000 : ℚ),(281796937067/691200000000 : ℚ),(164789625757/460800000000 : ℚ),(92128879469/230400000000 : ℚ)],![(145803603509/460800000000 : ℚ),(234652710527/921600000000 : ℚ),(623556373399/2764800000000 : ℚ),(193963578727/921600000000 : ℚ),(113320371809/460800000000 : ℚ)],![(122871201689/1382400000000 : ℚ),(302482897967/2764800000000 : ℚ),(919630023679/8294400000000 : ℚ),(307499472517/2764800000000 : ℚ),(186901516889/1382400000000 : ℚ)],![(13662569/480000000 : ℚ),(120014957/2560000000 : ℚ),(95992921/1920000000 : ℚ),(32844363/640000000 : ℚ),(242611867/3840000000 : ℚ)],![(40097167/320000000 : ℚ),(20208103/320000000 : ℚ),(26903549/640000000 : ℚ),(19987701/640000000 : ℚ),(39656363/1280000000 : ℚ)]]

theorem direct_rational_leaf : cell_0.localPolynomial polynomial=tensorPolynomial c := by
  apply MvPolynomial.funext
  intro x
  norm_num [Rectangle.localPolynomial,cell_0,Rectangle.quarter,Rectangle.half,
    Rectangle.lower,Rectangle.upper,Rectangle.width,square,polynomial,c,tensorPolynomial,
    basisPolynomial,Nat.choose,Fin.sum_univ_succ,Matrix.cons_val_two,Matrix.cons_val_three,Matrix.cons_val_four]
  ring
end
end Komorebi.LSM.P79Performance
