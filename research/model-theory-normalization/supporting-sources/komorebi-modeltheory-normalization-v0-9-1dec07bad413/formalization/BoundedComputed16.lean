module
public import BoundedDiscovery
@[expose] public section
namespace Komorebi.BoundedRegression.BoundedComputed16
open Komorebi.Discovery Komorebi.Discovery.BoundedBackend
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
abbrev c192_R := ZMod (2^3)
def c192_A : Fin 1 → Mat c192_R 6 6 := ![![![6, 3, 5, 4, 6, 2], ![4, 1, 2, 6, 0, 1], ![7, 2, 5, 7, 4, 0], ![6, 3, 4, 1, 3, 0], ![7, 1, 4, 0, 0, 5], ![6, 4, 4, 1, 2, 7]]]
def c192_O : Mat c192_R 2 6 := ![![0, 3, 3, 3, 6, 7], ![0, 6, 0, 6, 2, 2]]
def c192_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem c192_computed : boundedPrimeDiscover 2 3 6
    (fun a => rowRight (c192_A a)) c192_O = some c192_result := by decide +kernel
theorem c192_code : FiniteCodeCertificate (linearSystem c192_A c192_O) c192_result :=
  boundedPrimeDiscover_code 2 3 6 c192_A c192_O c192_result c192_computed

abbrev c193_R := ZMod (3^3)
def c193_A : Fin 2 → Mat c193_R 6 6 := ![![![1, 2, 20, 21, 24, 15], ![11, 4, 18, 5, 19, 5], ![15, 26, 25, 5, 7, 14], ![19, 12, 8, 3, 24, 21], ![20, 21, 16, 11, 13, 20], ![11, 16, 19, 9, 23, 5]], ![![2, 24, 11, 22, 16, 22], ![13, 15, 14, 21, 1, 1], ![21, 8, 17, 12, 23, 15], ![16, 22, 25, 25, 4, 6], ![4, 12, 11, 24, 5, 21], ![12, 13, 21, 5, 6, 16]]]
def c193_O : Mat c193_R 1 6 := ![![18, 4, 10, 3, 13, 23]]
def c193_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([1,1], 0), ([0,0,0], 0)]
theorem c193_computed : boundedPrimeDiscover 3 3 6
    (fun a => rowRight (c193_A a)) c193_O = some c193_result := by decide +kernel
theorem c193_code : FiniteCodeCertificate (linearSystem c193_A c193_O) c193_result :=
  boundedPrimeDiscover_code 3 3 6 c193_A c193_O c193_result c193_computed

abbrev c194_R := ZMod (5^3)
def c194_A : Fin 3 → Mat c194_R 6 6 := ![![![24, 66, 28, 73, 108, 90], ![88, 90, 116, 100, 34, 69], ![4, 63, 8, 79, 3, 42], ![19, 81, 62, 56, 16, 50], ![105, 67, 122, 7, 104, 0], ![112, 18, 67, 52, 10, 41]], ![![64, 109, 99, 36, 122, 10], ![5, 97, 70, 31, 41, 118], ![116, 58, 122, 55, 93, 104], ![52, 4, 30, 30, 8, 93], ![48, 94, 6, 6, 10, 91], ![80, 43, 58, 0, 16, 118]], ![![54, 18, 65, 34, 111, 78], ![47, 7, 119, 5, 48, 88], ![24, 110, 95, 37, 29, 82], ![98, 124, 89, 103, 55, 2], ![49, 113, 120, 15, 88, 55], ![102, 15, 3, 109, 77, 50]]]
def c194_O : Mat c194_R 2 6 := ![![86, 71, 44, 98, 62, 37], ![97, 24, 77, 0, 105, 85]]
def c194_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1)]
theorem c194_computed : boundedPrimeDiscover 5 3 6
    (fun a => rowRight (c194_A a)) c194_O = some c194_result := by decide +kernel
theorem c194_code : FiniteCodeCertificate (linearSystem c194_A c194_O) c194_result :=
  boundedPrimeDiscover_code 5 3 6 c194_A c194_O c194_result c194_computed

abbrev c195_R := ZMod (2^4)
def c195_A : Fin 1 → Mat c195_R 6 6 := ![![![5, 9, 3, 7, 10, 3], ![1, 14, 1, 8, 1, 10], ![14, 9, 14, 10, 13, 1], ![8, 1, 8, 14, 12, 12], ![14, 14, 2, 12, 7, 13], ![15, 15, 8, 7, 13, 3]]]
def c195_O : Mat c195_R 1 6 := ![![15, 4, 1, 3, 9, 2]]
def c195_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0), ([0,0,0,0,0], 0)]
theorem c195_computed : boundedPrimeDiscover 2 4 6
    (fun a => rowRight (c195_A a)) c195_O = some c195_result := by decide +kernel
theorem c195_code : FiniteCodeCertificate (linearSystem c195_A c195_O) c195_result :=
  boundedPrimeDiscover_code 2 4 6 c195_A c195_O c195_result c195_computed

abbrev c196_R := ZMod (3^4)
def c196_A : Fin 2 → Mat c196_R 6 6 := ![![![8, 19, 44, 66, 42, 8], ![21, 68, 61, 80, 63, 50], ![42, 67, 13, 43, 30, 70], ![79, 23, 37, 29, 17, 80], ![30, 33, 27, 67, 73, 47], ![68, 3, 45, 46, 22, 50]], ![![53, 76, 44, 41, 10, 52], ![34, 31, 8, 12, 32, 71], ![76, 54, 7, 69, 25, 39], ![28, 40, 40, 26, 72, 1], ![26, 76, 44, 65, 35, 28], ![47, 68, 67, 26, 57, 33]]]
def c196_O : Mat c196_R 2 6 := ![![27, 27, 0, 27, 0, 27], ![0, 0, 0, 27, 27, 0]]
def c196_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([1,0], 0)]
theorem c196_computed : boundedPrimeDiscover 3 4 6
    (fun a => rowRight (c196_A a)) c196_O = some c196_result := by decide +kernel
theorem c196_code : FiniteCodeCertificate (linearSystem c196_A c196_O) c196_result :=
  boundedPrimeDiscover_code 3 4 6 c196_A c196_O c196_result c196_computed

abbrev c197_R := ZMod (5^4)
def c197_A : Fin 3 → Mat c197_R 6 6 := ![![![429, 206, 273, 402, 204, 349], ![282, 379, 580, 539, 276, 265], ![382, 104, 517, 231, 468, 18], ![484, 523, 367, 118, 187, 596], ![437, 365, 540, 560, 341, 274], ![433, 86, 196, 433, 551, 393]], ![![366, 34, 563, 282, 62, 163], ![583, 449, 60, 491, 356, 580], ![464, 239, 440, 181, 116, 138], ![226, 306, 457, 151, 390, 418], ![104, 295, 24, 536, 485, 70], ![424, 248, 363, 585, 102, 357]], ![![263, 161, 442, 343, 105, 225], ![333, 425, 11, 474, 170, 561], ![411, 355, 334, 334, 125, 145], ![445, 145, 515, 334, 471, 455], ![358, 432, 289, 359, 525, 174], ![596, 128, 71, 584, 271, 63]]]
def c197_O : Mat c197_R 1 6 := ![![134, 345, 136, 619, 577, 579]]
def c197_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0), ([1,0], 0)]
theorem c197_computed : boundedPrimeDiscover 5 4 6
    (fun a => rowRight (c197_A a)) c197_O = some c197_result := by decide +kernel
theorem c197_code : FiniteCodeCertificate (linearSystem c197_A c197_O) c197_result :=
  boundedPrimeDiscover_code 5 4 6 c197_A c197_O c197_result c197_computed

abbrev c198_R := ZMod (2^5)
def c198_A : Fin 1 → Mat c198_R 6 6 := ![![![27, 8, 24, 27, 3, 0], ![29, 18, 26, 18, 29, 18], ![3, 21, 12, 22, 10, 6], ![31, 15, 4, 28, 11, 23], ![19, 24, 14, 31, 26, 31], ![25, 11, 17, 25, 15, 7]]]
def c198_O : Mat c198_R 2 6 := ![![11, 13, 19, 21, 3, 26], ![10, 14, 5, 3, 31, 16]]
def c198_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0), ([0,0], 1), ([0,0,0], 0)]
theorem c198_computed : boundedPrimeDiscover 2 5 6
    (fun a => rowRight (c198_A a)) c198_O = some c198_result := by decide +kernel
theorem c198_code : FiniteCodeCertificate (linearSystem c198_A c198_O) c198_result :=
  boundedPrimeDiscover_code 2 5 6 c198_A c198_O c198_result c198_computed

abbrev c199_R := ZMod (3^5)
def c199_A : Fin 2 → Mat c199_R 6 6 := ![![![242, 109, 5, 6, 147, 34], ![147, 58, 207, 197, 156, 219], ![142, 172, 72, 188, 195, 173], ![99, 209, 29, 163, 85, 3], ![123, 122, 208, 228, 2, 39], ![241, 118, 23, 199, 115, 20]], ![![226, 231, 182, 184, 127, 210], ![135, 157, 143, 221, 174, 164], ![174, 87, 27, 36, 135, 32], ![48, 182, 0, 231, 100, 12], ![114, 22, 46, 185, 157, 91], ![118, 211, 135, 156, 131, 76]]]
def c199_O : Mat c199_R 1 6 := ![![171, 184, 158, 224, 142, 55]]
def c199_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([0,1], 0)]
theorem c199_computed : boundedPrimeDiscover 3 5 6
    (fun a => rowRight (c199_A a)) c199_O = some c199_result := by decide +kernel
theorem c199_code : FiniteCodeCertificate (linearSystem c199_A c199_O) c199_result :=
  boundedPrimeDiscover_code 3 5 6 c199_A c199_O c199_result c199_computed

abbrev c200_R := ZMod (5^5)
def c200_A : Fin 3 → Mat c200_R 6 6 := ![![![359, 2215, 2375, 2102, 1953, 1435], ![309, 1145, 1384, 530, 1804, 2344], ![2729, 173, 2574, 1085, 1277, 771], ![66, 1152, 2718, 2419, 244, 1813], ![320, 2980, 2464, 472, 2510, 2751], ![2846, 1564, 1215, 1239, 630, 579]], ![![1627, 1438, 1488, 2392, 2593, 692], ![2659, 410, 1711, 1555, 3021, 2288], ![1281, 656, 1767, 807, 242, 664], ![2354, 166, 2721, 499, 1561, 239], ![2792, 1104, 1433, 1048, 3060, 253], ![2670, 2348, 1762, 2224, 2157, 2234]], ![![1317, 697, 2576, 644, 2240, 1708], ![2485, 2313, 2357, 1837, 1253, 462], ![1454, 1472, 3058, 1872, 1942, 2856], ![2517, 1084, 1644, 222, 183, 3085], ![1615, 562, 3105, 1042, 993, 1400], ![174, 2072, 2132, 2904, 1655, 1600]]]
def c200_O : Mat c200_R 2 6 := ![![2358, 1712, 158, 579, 2077, 2544], ![2315, 331, 2650, 2342, 2649, 1444]]
def c200_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1), ([1], 1)]
theorem c200_computed : boundedPrimeDiscover 5 5 6
    (fun a => rowRight (c200_A a)) c200_O = some c200_result := by decide +kernel
theorem c200_code : FiniteCodeCertificate (linearSystem c200_A c200_O) c200_result :=
  boundedPrimeDiscover_code 5 5 6 c200_A c200_O c200_result c200_computed

abbrev c201_R := ZMod (2^16)
def c201_A : Fin 2 → Mat c201_R 8 8 := ![![![17698, 7962, 49699, 37320, 23412, 6538, 39824, 34395], ![23464, 37603, 20556, 32118, 60325, 50701, 6345, 63146], ![7061, 60025, 48800, 57289, 7901, 57423, 17450, 21611], ![57954, 1463, 43061, 61981, 12327, 24535, 55220, 20222], ![9538, 34330, 18991, 25859, 64489, 51532, 7482, 17514], ![8262, 4689, 20524, 11331, 58729, 9597, 8879, 16991], ![38245, 65480, 12079, 48575, 41217, 13059, 11905, 14025], ![40555, 32470, 51819, 35275, 34452, 61245, 54300, 32399]], ![![45667, 60993, 42044, 24680, 13027, 39737, 34859, 3988], ![10393, 29683, 38554, 51204, 39690, 4755, 35121, 61378], ![63427, 47581, 32082, 32486, 44031, 34935, 29965, 8363], ![27479, 23039, 1777, 57316, 32532, 42871, 30241, 7992], ![35244, 37369, 1342, 167, 21177, 50423, 62217, 51013], ![29874, 59333, 42924, 46108, 58455, 35340, 60778, 27268], ![52594, 11868, 27092, 9501, 44582, 25499, 5486, 41184], ![1304, 20195, 44643, 12867, 63107, 13759, 28318, 26332]]]
def c201_O : Mat c201_R 1 8 := ![![7832, 48923, 62138, 42629, 5929, 53217, 38675, 43995]]
def c201_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c201_computed : boundedPrimeDiscover 2 16 8
    (fun a => rowRight (c201_A a)) c201_O = some c201_result := by decide +kernel
theorem c201_code : FiniteCodeCertificate (linearSystem c201_A c201_O) c201_result :=
  boundedPrimeDiscover_code 2 16 8 c201_A c201_O c201_result c201_computed

abbrev c202_R := ZMod (2^24)
def c202_A : Fin 1 → Mat c202_R 1 1 := ![![![1]]]
def c202_O : Mat c202_R 24 1 := ![![8388608], ![4194304], ![2097152], ![1048576], ![524288], ![262144], ![131072], ![65536], ![32768], ![16384], ![8192], ![4096], ![2048], ![1024], ![512], ![256], ![128], ![64], ![32], ![16], ![8], ![4], ![2], ![1]]
def c202_result : List (Test 1 24) := [([], 0), ([], 1), ([], 2), ([], 3), ([], 4), ([], 5), ([], 6), ([], 7), ([], 8), ([], 9), ([], 10), ([], 11), ([], 12), ([], 13), ([], 14), ([], 15), ([], 16), ([], 17), ([], 18), ([], 19), ([], 20), ([], 21), ([], 22), ([], 23)]
theorem c202_computed : boundedPrimeDiscover 2 24 1
    (fun a => rowRight (c202_A a)) c202_O = some c202_result := by decide +kernel
theorem c202_code : FiniteCodeCertificate (linearSystem c202_A c202_O) c202_result :=
  boundedPrimeDiscover_code 2 24 1 c202_A c202_O c202_result c202_computed

end Komorebi.BoundedRegression.BoundedComputed16
