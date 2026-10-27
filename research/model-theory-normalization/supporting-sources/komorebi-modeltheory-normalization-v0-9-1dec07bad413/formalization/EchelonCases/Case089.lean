module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case089
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^3)
def A : Fin 3 → Mat R 5 5 := ![![![101, 120, 94, 14, 114], ![41, 12, 12, 48, 97], ![78, 55, 52, 92, 34], ![46, 22, 31, 12, 90], ![44, 66, 51, 53, 121]], ![![75, 20, 44, 43, 11], ![117, 80, 29, 45, 35], ![47, 47, 123, 120, 69], ![58, 34, 51, 24, 39], ![48, 87, 116, 59, 21]], ![![19, 66, 59, 54, 73], ![102, 57, 76, 101, 66], ![106, 91, 0, 94, 117], ![89, 66, 65, 97, 51], ![74, 50, 101, 48, 72]]]
def O : Mat R 1 5 := ![![37, 85, 115, 110, 96]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0)]
theorem computed : fastPrimeDiscover 5 3 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case089
