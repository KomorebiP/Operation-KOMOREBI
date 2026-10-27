"""Build exact statement locators plus independently assigned audit verdicts.

Run from the paper_xii_work directory. Status dashboards are deliberately not
read. Source statements, proof blocks, and hashes are recovered from TeX.
"""

from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "source/latest_v0171/Paper_XII_Complete_v0.17.1_With_Visual_Appendix/formal_release/paper/Paper_XII_Revised_Formalization_Complete_v0.17.0.tex"
ORIGINAL = ROOT / "source/original_package/PSC_Paper_XII_Strengthened_Annals_Edition_Package/PSC_Paper_XII_Strengthened_Annals_Edition.tex"
FINAL = ROOT / "traditional/Paper_XII_Traditional_Final.tex"
INTERNAL = {"theorem", "proposition", "lemma", "corollary"}
NUMBERED = "theorem|proposition|lemma|corollary|definition|remark|standardfact|example"


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def parse(path):
    text = path.read_text()
    section = count = 0
    records = []
    for match in re.finditer(r"\\section\{|\\begin\{(" + NUMBERED + r")\}", text):
        if match.group() == r"\section{":
            section += 1
            count = 0
            continue
        count += 1
        kind = match.group(1)
        end = text.index(r"\end{" + kind + "}", match.end()) + len(r"\end{" + kind + "}")
        statement = text[match.start():end]
        label = re.search(r"\\label\{([^}]+)\}", statement)
        after = text[end:]
        proof = re.match(r"\s*\\begin\{proof\}([\s\S]*?)\\end\{proof\}", after)
        records.append({
            "number": f"{section}.{count}",
            "kind": kind,
            "label": label.group(1) if label else None,
            "line": text.count("\n", 0, match.start()) + 1,
            "statement_sha256": sha(statement),
            "statement_tex": statement,
            "proof_sha256": sha(proof.group(1)) if proof else None,
            "proof_tex": proof.group(1) if proof else None,
        })
    return text, records


# These normalized statements, obligations, and verdicts were assigned after
# reading the actual raw/final proofs, not copied from release statuses.
# Columns: normalized contract; dependencies; decisive obligation; verdict.
CLAIMS = {
    "3.1": ("Finite complete Noetherian local O-algebras with common residue k and closed I_i: actual completed tensor of quotients equals actual completion modulo closed generated ideal, canonically/bicontinuously.", "Ordinary tensor quotient; completion/closed-quotient comparison; common residue maps", "Actual topology, closed relation ideal, coefficient/factor maps, inverse laws, empty/unary/unit cases", "proved as written"),
    "3.2": ("Every continuous Hausdorff-target point factors uniquely/continuously through the closed local-condition quotient iff all factor restrictions kill I_i; local factors when original point local.", "3.1 object maps; actual ideal quotient", "Closed kernel contains closure exactly when it contains factor relations; uniqueness/locality", "proved as written"),
    "3.3": ("Supplied complete Noetherian local deformation rings and continuous local O-map: actual completed global base change represents simultaneous local quotient conditions on continuous local O-test points.", "3.1;3.2;supplied represented global datum", "Tensor ideal transported to m_B; actual completed global object; coefficient/naturality/locality contract", "proved as written"),
    "3.4": ("Every idempotent in a commutative local ring is zero or one.", "Local units criterion", "One of e,1-e is a unit; cancellation", "proved as written"),
    "4.2": ("The actual faithful standard S3 representation over F7 is absolutely irreducible and adequate with specified adjoint splitting, H0/H1 vanishings and projector witnesses.", "Declared adequacy definition; displayed permutation and adjoint actions", "Actual representation/domain, averaging, absolute irreducibility, every adjoint constituent detected", "proved as written"),
    "5.1": ("Every group map induces coefficient group-algebra map; surjectivity preserved; augmentations commute.", "Group algebra basis/universal property", "Multiplicativity, coefficient preservation, arbitrary groups", "proved as written"),
    "5.2": ("For finite abelian p-group product of cyclic p-powers, residual algebra is the actual multivariate monomial quotient, local with declared augmentation generators.", "Characteristic p binomial law; group basis", "Algebra isomorphism and dimension; r=0 or trivial cyclic factors", "proved as written"),
    "5.3": ("Every finite p-group over every characteristic-p field has no nontrivial residual group-algebra idempotents, including nonabelian groups.", "Finite prime-field orbit span; orbit counting;5.2 abelian case", "Nonzero fixed vector; regular action and right multiplication; no finite-field restriction on k", "proved as written"),
    "5.4": ("A free rank-d right auxiliary group-algebra module has coinvariant/tensor recovery O^d; all coefficient primes.", "Actual balancing quotient; augmentation", "Right/left convention, basis transport, rank zero", "proved as written"),
    "6.2": ("Every finite module over any commutative ring has support V(annihilator).", "Localization; finite generators", "Product of annihilating denominators stays outside prime", "proved as written"),
    "6.3": ("Finite module over Noetherian ring has support V(Fitt_0).", "Finite presentation; local minors", "Local surjectivity iff maximal minor unit; M=0 convention", "proved as written"),
    "6.4": ("Finite Noetherian module: fiber-generator dimension at least r iff Fitt_(r-1) vanishes, every r>=1.", "Finite presentation; matrix rank", "Large-index r>n and n=0 boundary; minors for 1<=r<=n", "proved as written"),
    "6.5": ("Every higher Fitting ideal of a finitely presented module commutes with arbitrary coefficient base change.", "Finite presentation minors; intrinsic Fitting ideals", "Nonflat base change allowed; presentation still right-exact", "proved as written"),
    "6.7": ("Finite module over Noetherian ring: nilpotent annihilator iff full support iff annihilator in nilradical; reduced ring gives faithfulness.", "6.2;finite generation of ideals", "Ideal generated by finitely many nilpotents is nilpotent", "proved as written"),
    "6.8": ("Every generic component point lies in the support of a nearly faithful finite Noetherian module.", "6.7", "Correct component/generic-point quantifier", "proved as written"),
    "6.9": ("Finite Noetherian module specialized to R/I has support Supp(M) intersect V(I), including I=R.", "Localization; Nakayama", "Finite nonzero M_p remains nonzero modulo I_p in maximal ideal", "proved as written"),
    "6.11": ("Actual ordinary patched quotient/control datum with full patched support gives full finite-level support and near faithfulness; reduced quotient faithful.", "6.9;6.7;actual datum identifications", "Full support supplied only at patched level; finite/control hypotheses", "proved as written"),
    "6.12": ("Each finite-level irreducible component is contained in full supported locus under ordinary descent.", "6.11", "Corrected containment direction", "proved as written"),
    "6.16": ("Every perfect complex over a commutative ring has quotient derived support equal to original support intersect V(I).", "Bounded finite-projective model; tensor associativity; faithful field extension", "Actual derived fibers; model independence; quotient spectrum; I=R", "proved as written"),
    "6.18": ("Full patched derived support and actual derived control imply full finite-level derived support and nonzero fiber at every field point.", "6.16;actual derived datum", "Kernel residue field factorization and faithful extension for any field point", "proved as written"),
    "6.19": ("Every such nonzero derived field fiber has some nonzero integer cohomology degree.", "6.18;derived acyclicity criterion", "Cohomology not confused with a nonzero complex term", "proved as written"),
    "7.1": ("Ring isomorphism of Noetherian R,T and finite T-module transports support and all intrinsic Fitting ideals.", "Localization equivalence;6.5/presentation minors", "Actual spectrum homeomorphism and module action", "proved as written"),
    "7.2": ("Full support of the same finite module is invariant under actual R=T isomorphism.", "7.1", "Support carried by full homeomorphism", "proved as written"),
    "7.3": ("Node quotient R=k[[x,y]]/(xy) to R/(x)=k[[y]] misses generic point (y).", "Formal power-series quotient;6.2", "Actual two components; annihilator (x); generic point exclusion", "proved as written"),
    "7.4": ("Finite module at any field point x has nonzero actual tensor fiber iff kernel x is in support.", "Localization; Nakayama; faithful field extension", "Finite generation essential; generic/nonclosed point allowed", "proved as written"),
    "7.5": ("Supported deformation point under actual R=T and finite Hecke module has nonzero Hecke fiber.", "7.1;7.4", "Compatible transported character", "proved as written"),
    "8.2": ("Finite commutative Hecke algebra and finite module decompose by canonical Artin idempotents; packet equals actual localization and detects support.", "External Artin decomposition8.1", "Canonical localization maps; orthogonal-idempotent direct sum", "conditional on a named input"),
    "8.3": ("Over algebraically closed field, canonical packet of a finite commuting generating list is one simultaneous generalized eigenspace with uniform positive exponent.", "8.2;Artin local nilpotence;other-factor units", "Generator/eigenvalue convention, common exponent, nonsemisimple action", "conditional on a named input"),
    "8.4": ("Characteristic-zero idempotent projector trace equals dimension cast; occupancy iff positive rank iff nonzero trace.", "Idempotent splitting;8.2 packet", "Coefficient cast; characteristic-zero restriction essential", "conditional on a named input"),
    "8.7": ("Nonzero nested idempotent ranges in one finite-dimensional carrier stabilize with nonzero intersection.", "Finite dimension;descending ranges", "No inference for infinite carrier", "proved as written"),
    "8.8": ("In the same finite carrier, zero intersection has finite empty packet witness.", "8.7 contrapositive", "Same finite carrier retained", "proved as written"),
    "8.10": ("Every transition of a coherent finite-dimensional vector inverse system surjects on stable cores.", "Descending nonempty affine fibers", "Actual coherent images and all preimage constraints", "proved as written"),
    "8.11": ("Nonzero stable cores give a nonzero actual inverse-limit sequence with any prescribed nonzero first stable vector.", "8.10;recursive choice", "Strict compatibility and nonzero first coordinate", "proved as written"),
    "8.12": ("Surjective transitions of nonzero finite-dimensional carriers give nonzero inverse limit.", "8.11;stable images equal whole level", "Nonzero and surjectivity, not level occupancy alone", "proved as written"),
    "9.3": ("Supported finite Hecke carrier under R=T gives actual nonzero scalar fiber with every Hecke element acting through x.", "7.5;tensor balancing", "Actual vector in specialized fiber", "proved as written"),
    "9.4": ("Continuous specialization and attached semisimple representation over Hausdorff char-zero field with same dense Frobenius polynomials are isomorphic after semisimplification; irreducible specialization directly.", "9.3;supplied realization;density;semisimplification;Brauer-Nesbitt", "Same polynomials and normalization; equality extends by Hausdorff continuity; intertwiner over E'", "conditional on a named input"),
    "9.5": ("Full ordinary support gives pointwise automorphy on a locus for which all realization/topology/comparison inputs apply.", "9.3;9.4", "Locus only includes points satisfying named hypotheses", "conditional on a named input"),
    "9.6": ("Full derived Hecke support gives scalar nonzero cohomology in model interval; applicable classicality on that interval and comparison inputs give automorphy after semisimplification.", "6.18;bounded projective model;supplied realization/density/BN", "Surviving degree lies in classicality range; actual cohomology scalar action", "conditional on a named input"),
    "10.3": ("Finite nonempty levels and total reductions to fixed residual root admit a compatible branch.", "Finite rooted forest;König compactness", "Total maps, no transition-surjectivity assumption", "proved as written"),
    "10.4": ("An empty declared admissible finite level obstructs a complete realization reducing into all declared levels.", "Definition of admissible completion", "Admissibility coverage rather than arbitrary omitted realizations", "proved as written"),
    "10.5": ("Explicit finite occupied continuous class forests over complete separated finitely generated-adic coefficients give actual continuous integral representations with residual class, integral Frobenius/inertia relations and every-frame polynomial-ideal effectivity.", "10.3;finite coefficient quotients/frames;adic matrix reconstruction;separatedness", "Compatible actual frames without conjugator lifts; continuity; integral polynomial data; every frame", "proved as written"),
    "10.7": ("Two existing semisimple compatible systems with same Frobenius spine, one linked to an automorphic object, agree at each coefficient place.", "External density/semisimplification/BN;existing attached family", "Both families exist and use same field/normalization/spine", "conditional on a named input"),
    "10.9": ("r independent field-valued functions have r evaluation points with invertible matrix; known semisimple carrier multiplicities recovered when trace independence supplied.", "Finite-dimensional duality", "Independence on full sample set; r=0; no arbitrary finite-prime classification", "proved as written"),
    "11.1": ("Unique two sign idempotents over Q2 are not integral in Z2[C2]; residual F2[C2] is dual numbers and local.", "Group basis;5.2;3.4", "Coefficient denominators; actual residual quotient", "proved as written"),
    "11.2": ("Finite free right module over any finite two-group algebra has free augmentation coinvariants of the same rank.", "Actual balancing quotient;5.4 basis proof", "Nonabelian right-module convention; no character projectors", "proved as written"),
    "12.2": ("Actual ordinary completion datum, full patched support, comparison, and all explicit pointwise inputs give nonzero fiber and classical automorphic realization after semisimplification.", "6.11;7.1;9.3;9.4;all datum12.1 inputs", "Universal-specialization polynomial match explicitly supplied; topology/continuity retained", "conditional on a named input"),
    "12.4": ("Actual derived completion datum gives nonzero scalar cohomological eigensystem; realization applicable to that selected eigensystem gives automorphy after semisimplification.", "6.18;6.19;9.6 comparison portion;pointwise realization", "No uniform classicality in irrelevant degrees; same polynomial/density inputs", "conditional on a named input"),
    "12.5": ("An already identified automorphic member and an existing same-spine attached family identify an existing semisimple system memberwise.", "12.2/12.4;10.7;both existing families", "Same automorphic object; same algebraic spine; no member construction", "conditional on a named input"),
    "12.6": ("Five supplied gates with actual source/target support inclusion and compatible Hecke point produce realized scalar eigensystem and representation intertwiner; two existing same-spine families propagate it.", "Support descent;compatible point;actual fiber/cohomology;particular realization;density/BN;existing families", "Point y with y∘f=x; actual support comparison; realization on chosen vector; exact family linkage", "conditional on a named input"),
}


raw_text, raw_records = parse(RAW)
original_text, original_records = parse(ORIGINAL)
final_text, final_records = parse(FINAL)
raw_by_label = {r["label"]: r for r in raw_records if r["label"]}
original_by_label = {r["label"]: r for r in original_records if r["label"]}
final_internal = [r for r in final_records if r["kind"] in INTERNAL]
assert len(final_internal) == 49
assert {r["number"] for r in final_internal} == set(CLAIMS)

rows = []
INHERITED_PARTIAL = {"9.4", "9.5", "9.6", "10.5", "12.2", "12.4", "12.6"}
for record in final_internal:
    normalized, dependencies, obligation, verdict = CLAIMS[record["number"]]
    raw = raw_by_label[record["label"]]
    original = original_by_label[record["label"]]
    rows.append({
        **record,
        "normalized_claim": normalized,
        "dependencies": dependencies,
        "decisive_obligation": obligation,
        "obligation_status": "passed" if verdict == "proved as written" else "conditional",
        "primary_verdict": verdict,
        "inherited_original_compiler_label": (
            "unchecked" if record["number"] == "6.12"
            else "partial" if record["number"] in INHERITED_PARTIAL
            else "complete"
        ),
        "inherited_raw_revised_compiler_label": "complete",
        "compiler_labels_are_proof_evidence_for_this_audit": False,
        "internal_gap": None,
        "final_statement_changed_from_raw_revised": record["statement_sha256"] != raw["statement_sha256"],
        "final_proof_changed_from_raw_revised": record["proof_sha256"] != raw["proof_sha256"],
        "original_statement_sha256": original["statement_sha256"],
        "raw_revised_statement_sha256": raw["statement_sha256"],
    })

output = {
    "audit_type": "independent mathematical source audit; compiler not rerun by this auditor",
    "source_paths": {"original": str(ORIGINAL.relative_to(ROOT)), "raw_revised": str(RAW.relative_to(ROOT)), "final": str(FINAL.relative_to(ROOT))},
    "source_sha256": {"original": sha(original_text), "raw_revised": sha(raw_text), "final": sha(final_text)},
    "internal_claim_count": 49,
    "internal_partition": {kind: sum(r["kind"] == kind for r in final_internal) for kind in sorted(INTERNAL)},
    "excluded_worked_example_count": sum(r["kind"] == "example" for r in final_records),
    "external_standard_fact_count": sum(r["kind"] == "standardfact" for r in final_records),
    "inherited_amendments": ["6.12", "9.4", "9.5", "9.6", "10.5", "12.2", "12.4", "12.6"],
    "records": rows,
}
destination = ROOT / "audit/claims"
(destination / "CLAIM_OBLIGATION_MATRIX.json").write_text(json.dumps(output, indent=2) + "\n")
markdown = [
    "# Paper XII: all-49 independent obligation matrix",
    "",
    "Exact statement/proof hashes, final-source line locators, and full normalized contracts are in `CLAIM_OBLIGATION_MATRIX.json`. A passed row means the displayed internal implication was checked from definitions; a conditional row retains its named external leaf. No row infers arithmetic input validity from a compiler dashboard.",
    "",
    "| Claim | Normalized contract | Decisive obligation | Verdict |",
    "|---|---|---|---|",
]
for row in rows:
    markdown.append("| " + " | ".join([row["number"], row["normalized_claim"], row["decisive_obligation"], row["primary_verdict"]]) + " |")
markdown += ["", "There is no remaining internal gap in the reviewed final wording. Conditional rows rely on the canonical Artin decomposition or explicitly declared arithmetic realization/density/semisimplification/Brauer–Nesbitt inputs, as detailed in `INDEPENDENT_CLAIM_AUDIT.md`.", ""]
(destination / "CLAIM_OBLIGATION_MATRIX.md").write_text("\n".join(markdown))
print(json.dumps({
    "final_sha256": output["source_sha256"]["final"],
    "claim_count": len(rows),
    "proof_count": sum(r["proof_sha256"] is not None for r in final_records),
    "changed_internal_proof_numbers": [r["number"] for r in rows if r["final_proof_changed_from_raw_revised"]],
    "changed_internal_statement_numbers": [r["number"] for r in rows if r["final_statement_changed_from_raw_revised"]],
    "verdict_counts": {verdict: sum(r["primary_verdict"] == verdict for r in rows) for verdict in sorted({r["primary_verdict"] for r in rows})},
}, indent=2))
