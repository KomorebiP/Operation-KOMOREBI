module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case202
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^24)
def A : Fin 1 → Mat R 1 1 := ![![![1]]]
def O : Mat R 24 1 := ![![8388608], ![4194304], ![2097152], ![1048576], ![524288], ![262144], ![131072], ![65536], ![32768], ![16384], ![8192], ![4096], ![2048], ![1024], ![512], ![256], ![128], ![64], ![32], ![16], ![8], ![4], ![2], ![1]]
def result : List (Test 1 24) := [([], 0), ([], 1), ([], 2), ([], 3), ([], 4), ([], 5), ([], 6), ([], 7), ([], 8), ([], 9), ([], 10), ([], 11), ([], 12), ([], 13), ([], 14), ([], 15), ([], 16), ([], 17), ([], 18), ([], 19), ([], 20), ([], 21), ([], 22), ([], 23)]
theorem computed : fastPrimeDiscover 2 24 1
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case202
