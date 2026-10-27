module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.EchelonComputed10
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
abbrev c120_R := ZMod (2^4)
def c120_A : Fin 1 → Mat c120_R 1 1 := ![![![10]]]
def c120_O : Mat c120_R 2 1 := ![![3], ![7]]
def c120_result : List (Test 1 2) := [([], 0)]
theorem c120_computed : fastPrimeDiscover 2 4 1
    (fun a => rowRight (c120_A a)) c120_O = some c120_result := by decide +kernel
theorem c120_code : FiniteCodeCertificate (linearSystem c120_A c120_O) c120_result :=
  fastPrimeDiscover_code 2 4 1 c120_A c120_O c120_result c120_computed

abbrev c121_R := ZMod (3^4)
def c121_A : Fin 2 → Mat c121_R 1 1 := ![![![61]], ![![12]]]
def c121_O : Mat c121_R 1 1 := ![![71]]
def c121_result : List (Test 2 1) := [([], 0)]
theorem c121_computed : fastPrimeDiscover 3 4 1
    (fun a => rowRight (c121_A a)) c121_O = some c121_result := by decide +kernel
theorem c121_code : FiniteCodeCertificate (linearSystem c121_A c121_O) c121_result :=
  fastPrimeDiscover_code 3 4 1 c121_A c121_O c121_result c121_computed

abbrev c122_R := ZMod (5^4)
def c122_A : Fin 3 → Mat c122_R 1 1 := ![![![420]], ![![304]], ![![259]]]
def c122_O : Mat c122_R 2 1 := ![![617], ![181]]
def c122_result : List (Test 3 2) := [([], 0)]
theorem c122_computed : fastPrimeDiscover 5 4 1
    (fun a => rowRight (c122_A a)) c122_O = some c122_result := by decide +kernel
theorem c122_code : FiniteCodeCertificate (linearSystem c122_A c122_O) c122_result :=
  fastPrimeDiscover_code 5 4 1 c122_A c122_O c122_result c122_computed

abbrev c123_R := ZMod (2^5)
def c123_A : Fin 1 → Mat c123_R 1 1 := ![![![5]]]
def c123_O : Mat c123_R 1 1 := ![![18]]
def c123_result : List (Test 1 1) := [([], 0)]
theorem c123_computed : fastPrimeDiscover 2 5 1
    (fun a => rowRight (c123_A a)) c123_O = some c123_result := by decide +kernel
theorem c123_code : FiniteCodeCertificate (linearSystem c123_A c123_O) c123_result :=
  fastPrimeDiscover_code 2 5 1 c123_A c123_O c123_result c123_computed

abbrev c124_R := ZMod (3^5)
def c124_A : Fin 2 → Mat c124_R 1 1 := ![![![97]], ![![142]]]
def c124_O : Mat c124_R 2 1 := ![![171], ![39]]
def c124_result : List (Test 2 2) := [([], 0), ([], 1)]
theorem c124_computed : fastPrimeDiscover 3 5 1
    (fun a => rowRight (c124_A a)) c124_O = some c124_result := by decide +kernel
theorem c124_code : FiniteCodeCertificate (linearSystem c124_A c124_O) c124_result :=
  fastPrimeDiscover_code 3 5 1 c124_A c124_O c124_result c124_computed

abbrev c125_R := ZMod (5^5)
def c125_A : Fin 3 → Mat c125_R 1 1 := ![![![2943]], ![![2010]], ![![2491]]]
def c125_O : Mat c125_R 1 1 := ![![0]]
def c125_result : List (Test 3 1) := []
theorem c125_computed : fastPrimeDiscover 5 5 1
    (fun a => rowRight (c125_A a)) c125_O = some c125_result := by decide +kernel
theorem c125_code : FiniteCodeCertificate (linearSystem c125_A c125_O) c125_result :=
  fastPrimeDiscover_code 5 5 1 c125_A c125_O c125_result c125_computed

abbrev c126_R := ZMod (2^1)
def c126_A : Fin 1 → Mat c126_R 2 2 := ![![![0, 0], ![0, 1]]]
def c126_O : Mat c126_R 2 2 := ![![1, 1], ![1, 1]]
def c126_result : List (Test 1 2) := [([], 0), ([0], 0)]
theorem c126_computed : fastPrimeDiscover 2 1 2
    (fun a => rowRight (c126_A a)) c126_O = some c126_result := by decide +kernel
theorem c126_code : FiniteCodeCertificate (linearSystem c126_A c126_O) c126_result :=
  fastPrimeDiscover_code 2 1 2 c126_A c126_O c126_result c126_computed

abbrev c127_R := ZMod (3^1)
def c127_A : Fin 2 → Mat c127_R 2 2 := ![![![1, 2], ![0, 1]], ![![1, 1], ![2, 1]]]
def c127_O : Mat c127_R 1 2 := ![![2, 2]]
def c127_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c127_computed : fastPrimeDiscover 3 1 2
    (fun a => rowRight (c127_A a)) c127_O = some c127_result := by decide +kernel
theorem c127_code : FiniteCodeCertificate (linearSystem c127_A c127_O) c127_result :=
  fastPrimeDiscover_code 3 1 2 c127_A c127_O c127_result c127_computed

abbrev c128_R := ZMod (5^1)
def c128_A : Fin 3 → Mat c128_R 2 2 := ![![![0, 1], ![2, 0]], ![![3, 2], ![2, 2]], ![![3, 3], ![3, 0]]]
def c128_O : Mat c128_R 2 2 := ![![0, 4], ![4, 4]]
def c128_result : List (Test 3 2) := [([], 0), ([], 1)]
theorem c128_computed : fastPrimeDiscover 5 1 2
    (fun a => rowRight (c128_A a)) c128_O = some c128_result := by decide +kernel
theorem c128_code : FiniteCodeCertificate (linearSystem c128_A c128_O) c128_result :=
  fastPrimeDiscover_code 5 1 2 c128_A c128_O c128_result c128_computed

abbrev c129_R := ZMod (2^2)
def c129_A : Fin 1 → Mat c129_R 2 2 := ![![![0, 2], ![1, 3]]]
def c129_O : Mat c129_R 1 2 := ![![3, 1]]
def c129_result : List (Test 1 1) := [([], 0), ([0], 0)]
theorem c129_computed : fastPrimeDiscover 2 2 2
    (fun a => rowRight (c129_A a)) c129_O = some c129_result := by decide +kernel
theorem c129_code : FiniteCodeCertificate (linearSystem c129_A c129_O) c129_result :=
  fastPrimeDiscover_code 2 2 2 c129_A c129_O c129_result c129_computed

abbrev c130_R := ZMod (3^2)
def c130_A : Fin 2 → Mat c130_R 2 2 := ![![![8, 7], ![3, 7]], ![![2, 0], ![8, 3]]]
def c130_O : Mat c130_R 2 2 := ![![1, 0], ![6, 6]]
def c130_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem c130_computed : fastPrimeDiscover 3 2 2
    (fun a => rowRight (c130_A a)) c130_O = some c130_result := by decide +kernel
theorem c130_code : FiniteCodeCertificate (linearSystem c130_A c130_O) c130_result :=
  fastPrimeDiscover_code 3 2 2 c130_A c130_O c130_result c130_computed

abbrev c131_R := ZMod (5^2)
def c131_A : Fin 3 → Mat c131_R 2 2 := ![![![6, 12], ![12, 5]], ![![13, 3], ![10, 22]], ![![2, 2], ![21, 19]]]
def c131_O : Mat c131_R 1 2 := ![![3, 17]]
def c131_result : List (Test 3 1) := [([], 0), ([0], 0)]
theorem c131_computed : fastPrimeDiscover 5 2 2
    (fun a => rowRight (c131_A a)) c131_O = some c131_result := by decide +kernel
theorem c131_code : FiniteCodeCertificate (linearSystem c131_A c131_O) c131_result :=
  fastPrimeDiscover_code 5 2 2 c131_A c131_O c131_result c131_computed

end Komorebi.EchelonRegression.EchelonComputed10
