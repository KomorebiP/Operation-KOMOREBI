"""Compare repaired plot artists with inherited source functions and pin outputs.

This replays only rendering code on the inherited corpus. It does not run or
replace any hardware measurement, algorithmic proof, or scientific experiment.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parents[2]
SOURCE = PACKAGE / "source/strengthened/PSC_Paper_VIII_Strengthened_Annals_Edition_Package"
ORIGINAL_GENERATOR = SOURCE / "psc_packet/make_figures.py"
RAW = SOURCE / "verification/benchmark_results_sanitized.json"
FUNCTIONS = ["architecture", "output_contracts", "discovery", "contract_counts"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture_original(df):
    captured = {}
    def save(fig, stem):
        captured[stem] = fig
    namespace = {"plt":plt, "np":np, "pd":pd,
                 "FancyBboxPatch":FancyBboxPatch, "save":save}
    parsed = ast.parse(ORIGINAL_GENERATOR.read_text())
    chosen = [n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in FUNCTIONS]
    assert len(chosen)==4
    exec(compile(ast.Module(body=chosen,type_ignores=[]),str(ORIGINAL_GENERATOR),"exec"),namespace)
    namespace["architecture"]()
    for fn in FUNCTIONS[1:]:
        namespace[fn](df)
    return captured


def capture_repaired(df):
    captured = {}
    spec = importlib.util.spec_from_file_location("paper_viii_figure_repairs",HERE/"repair_figures.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    def save(fig,out,stem):
        captured[stem] = fig
    mod.save = save
    model = {}
    mod.architecture(HERE,model)
    mod.output_contracts(df,HERE,model)
    mod.discovery(df,HERE,model)
    mod.contract_counts(df,HERE,model)
    return captured


def main():
    data = json.loads(RAW.read_text())
    assert RAW.read_bytes() == (HERE/"raw_inputs/benchmark_results_sanitized.json").read_bytes()
    df = pd.DataFrame(data["results"])
    old,new = capture_original(df),capture_repaired(df)
    stems = sorted(old)
    assert stems == sorted(new)
    model_checks = {}
    for stem in stems:
        a,b = old[stem].axes[0],new[stem].axes[0]
        if stem.startswith("01"):
            labels_a = [t.get_text() for t in a.texts if t.get_text()]
            labels_b = [t.get_text().replace("\n"," ") for t in b.texts if t.get_text()]
            assert labels_a==labels_b
            assert len(a.patches)==len(b.patches)==6
            for x,y in zip(a.patches,b.patches):
                np.testing.assert_array_equal(x.get_path().vertices,y.get_path().vertices)
            assert len(a.texts)==len(b.texts)==11
            for x,y in zip(a.texts,b.texts):
                if x.get_text()=="":
                    assert x.xy==y.xy and x.get_position()==y.get_position()
            model_checks[stem] = {"pass":True,"six_labels_and_five_arrow_positions_identical":True,
                                  "change":"line breaks within the same six labels"}
        elif stem.startswith("17"):
            assert len(a.containers)==len(b.containers)==4
            for x,y in zip(a.containers,b.containers):
                np.testing.assert_array_equal(x.datavalues,y.datavalues)
                for p,q in zip(x.patches,y.patches):
                    assert p.get_x()==q.get_x() and p.get_width()==q.get_width()
            np.testing.assert_array_equal(a.get_xticks(),b.get_xticks())
            assert [t.get_text() for t in a.get_xticklabels()]==[t.get_text() for t in b.get_xticklabels()]
            assert a.get_yscale()==b.get_yscale()=="log"
            model_checks[stem] = {"pass":True,"all_eight_median_ms_bars_and_dimensions_identical":True,
                                  "change":"CPU/GPU prefixes retained from source method identifiers; legend above plot"}
        elif stem.startswith("18"):
            assert len(a.lines)==len(b.lines)==3
            for x,y in zip(a.lines,b.lines):
                np.testing.assert_array_equal(x.get_xdata(),y.get_xdata())
                np.testing.assert_array_equal(x.get_ydata(),y.get_ydata())
                assert x.get_label()==y.get_label()
            assert [t.get_text() for t in a.texts]==[t.get_text() for t in b.texts]
            assert a.get_yscale()==b.get_yscale()=="log"
            model_checks[stem] = {"pass":True,"all_three_numeric_series_and_reuse_counts_identical":True,
                                  "change":"reuse annotations placed inward below their points"}
        elif stem.startswith("22"):
            assert len(a.containers)==len(b.containers)==8
            for x,y in zip(a.containers,b.containers):
                np.testing.assert_array_equal(x.datavalues,y.datavalues)
                assert x.get_label()==y.get_label()
            labels_a = [t.get_text() for t in a.get_xticklabels()]
            labels_b = [t.get_text().replace("\n"," ") for t in b.get_yticklabels()]
            assert labels_a==labels_b
            assert sum(sum(x.datavalues) for x in a.containers)==len(df)
            model_checks[stem] = {"pass":True,"all_40_contract_counts_and_five_scopes_identical":True,
                                  "total_recorded_rows":len(df),
                                  "change":"horizontal stacked bars; long timing scope wrapped; legend below plot"}
    for fig in list(old.values())+list(new.values()):
        plt.close(fig)
    with tempfile.TemporaryDirectory(prefix="paper_viii_figure_replay_") as td:
        replay = Path(td)
        subprocess.run([sys.executable,str(HERE/"repair_figures.py"),"--output-dir",str(replay)],check=True)
        reproduced = {p.name:sha(p)==sha(HERE/"staged"/p.name) for p in replay.glob("*.pdf")}
        assert len(reproduced)==4 and all(reproduced.values())
        assert (replay/"plotted_models.json").read_bytes()==(HERE/"staged/plotted_models.json").read_bytes()
    report = {
        "status":"PASS",
        "scope":"presentation repair only; no newly measured benchmark timings",
        "original_source_generator":{"path":str(ORIGINAL_GENERATOR.relative_to(PACKAGE)),"sha256":sha(ORIGINAL_GENERATOR)},
        "raw_measurement_input":{"path":str(RAW.relative_to(PACKAGE)),"sha256":sha(RAW),"byte_identical_local_copy":True},
        "repair_generator_sha256":sha(HERE/"repair_figures.py"),
        "artist_model_comparisons":model_checks,
        "pdf_rebuild_byte_identity":reproduced,
        "hardware_evidence_status":"Inherited sanitized measurements on NVIDIA GeForce RTX 3070 Ti Laptop GPU; not rerun here",
    }
    (HERE/"model_preservation_audit.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"status":"PASS","source_artist_comparisons":len(model_checks),
                      "byte_identical_repaired_pdf_replays":len(reproduced),"corpus_rows":len(df)}))


if __name__=="__main__":
    main()
