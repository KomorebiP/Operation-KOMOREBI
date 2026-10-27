from pathlib import Path
import json

path = Path(__file__).with_name("Fermat_Hodge_K23_CM_Type_Audit.json")
data = json.loads(path.read_text())
assert data["K23_orbit_count"] == 7
assert data["total_exact_K23_certificates"] == 364
assert data["all_certificates_obey_opposite_curve_CM_sign"]
assert data["all_certificates_factor_through_a_lower_conductor"]
assert data["all_certificates_are_Galois_translates_of_an_upper_half_plane_CM_type"]
print(json.dumps({
    "K23_orbit_count": data["K23_orbit_count"],
    "total_exact_K23_certificates": data["total_exact_K23_certificates"],
    "conductor_distribution": data["conductor_distribution"],
}, indent=2))
