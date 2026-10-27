#!/usr/bin/env python3
"""Generate a small LaTeX macro file from frozen verification records."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def sci(value: float, digits: int = 6) -> str:
    if value == 0.0:
        return "0"
    mantissa, exponent = f"{value:.{digits}e}".split("e")
    return rf"{mantissa}\times 10^{{{int(exponent)}}}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    back = json.loads((args.data / "backreaction_audit.json").read_text())
    parent = json.loads((args.data / "parent_release_audit.json").read_text())
    checks = {
        row["id"]: row
        for row in csv.DictReader((args.data / "verification_checks.csv").open())
    }
    lineage = list(csv.DictReader((args.data / "cross_volume_lineage.csv").open()))
    data_lineage = sum(row["volume_ii_path"].startswith("data/") for row in lineage)
    figure_lineage = sum(row["volume_ii_path"].startswith("figures/") for row in lineage)
    macros = {
        "BridgeEta": sci(back["eta"], 10),
        "BridgeOverdraw": sci(back["unprojected_energy_over_available"], 10),
        "BridgeContinuumSlow": sci(back["continuum_slowing_factor"], 8),
        "BridgeContinuumOverdraw": sci(back["continuum_energy_over_available_at_input"], 10),
        "BridgeContinuumA": f'{back["continuum_energy_saturation_A_over_mu"]:.6f}',
        "BridgeContinuumX": f'{back["continuum_energy_saturation_Lambda_over_A"]:.6f}',
        "BridgeContinuumExponent": f'{back["continuum_lowest_level_suppression_exponent"]:.6f}',
        "BridgeDiscreteA": f'{back["discrete_energy_saturation_A_over_mu"]:.6f}',
        "BridgeDiscreteX": f'{back["discrete_energy_saturation_Lambda_over_A"]:.9f}',
        "BridgeDiscreteW": f'{back["discrete_saturation_w"]:.10f}',
        "BridgeDiscreteRest": f'{back["discrete_saturation_rest_fraction"]:.10f}',
        "BridgeDiscreteMeanMass": f'{back["discrete_saturation_mean_mass_over_A"]:.10f}',
        "BridgePeakCoupling": sci(back["benchmark_peak_quartic_coupling"], 8),
        "BridgeLowestCoupling": sci(back["saturation_lowest_level_quartic_coupling"], 8),
        "BridgeLambdaBound": sci(back["perturbative_lambda_upper_bound_at_benchmark_peak"], 8),
        "BridgeEnergyLambdaBound": sci(back["energy_control_lambda_upper_bound"], 10),
        "BridgePeakAtEnergyBound": f'{back["peak_coupling_at_energy_control_bound"]:.10f}',
        "BridgeLowestAtEnergyBound": sci(back["lowest_coupling_at_energy_control_bound"], 8),
        "BridgeSpectralResidual": sci(float(checks["ADM01"]["residual"]), 6),
        "BridgeAliasResidual": f'{float(checks["ADM02"]["residual"]):.10f}',
        "BridgeFiniteDifferenceResidual": f'{float(checks["ADM03"]["residual"]):.10f}',
        "BridgeMissingGradientResidual": f'{float(checks["ADM04"]["residual"]):.10f}',
        "BridgeWardNegativeResidual": f'{float(checks["COV04"]["residual"]):.10f}',
        "BridgeManifestEntries": str(parent["volume_ii_manifest_entries"]),
        "BridgeFrozenPasses": str(parent["frozen_internal_pass_count"]),
        "BridgeLineageData": str(data_lineage),
        "BridgeLineageFigures": str(figure_lineage),
        "BridgeStagingScripts": str(parent["scripts_requiring_staging"]),
        "BridgeMissingPaths": str(parent["missing_declared_paths"]),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(rf"\newcommand{{\{key}}}{{{value}}}" for key, value in macros.items())
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
