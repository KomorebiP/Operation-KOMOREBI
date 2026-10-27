from __future__ import annotations

import csv
import sys
from pathlib import Path

import sympy as sp

from proof_atlas import arithmetic, bayes, foundations, linear, nonlinear_geometry, physics, signal

ROOT = Path(__file__).resolve().parent
TABLES = ROOT / "tables"
TABLES.mkdir(exist_ok=True)



def foundation_table() -> None:
    cert = foundations.build_certificate()
    with (TABLES / "foundation_certificate.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "exact_value"])
        writer.writerow(["ambient_dimension", cert.dimension])
        writer.writerow(["orbit_rank", cert.orbit_rank])
        writer.writerow(["seed", sp.sstr(cert.seed)])
        writer.writerow(["signal", sp.sstr(cert.signal)])
        writer.writerow(["operator_output", sp.sstr(cert.operator_output)])
        writer.writerow(["transfer_support_edges", len(cert.transfer_support)])
        writer.writerow(["blocked_obstruction", sp.sstr(cert.blocked_obstruction)])
        writer.writerow(["all_exact_reconstruction_residuals", 0])


def linear_table() -> None:
    cert = linear.build_certificate()
    with (TABLES / "linear_transfer_blocks.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["output_packet", "input_packet", "block_matrix"])
        for b, row in enumerate(cert.blocks):
            for a, block in enumerate(row):
                writer.writerow([b, a, sp.sstr(block)])


def signal_table() -> None:
    cert = signal.build_certificate()
    with (TABLES / "signal_coordinates.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["index", "signal", "haar", "fourier"])
        for i in range(cert.signal.rows):
            writer.writerow([
                i,
                sp.sstr(cert.signal[i]),
                sp.sstr(cert.haar_coefficients[i]),
                str(complex(sp.N(cert.fourier_coefficients[i], 14))),
            ])


def bayes_table() -> None:
    cert = bayes.build_certificate()
    with (TABLES / "bayesian_packets.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "packet_0", "packet_1"])
        writer.writerow(["sufficient_coarse_posterior", *map(sp.sstr, cert.sufficient_coarse_posterior)])
        writer.writerow(["nonsufficient_exact_coarse", *map(sp.sstr, cert.nonsufficient_exact_coarse)])
        writer.writerow(["nonsufficient_nominal_coarse", *map(sp.sstr, cert.nonsufficient_nominal_coarse)])
        writer.writerow(["defect", *map(sp.sstr, cert.defect)])


def arithmetic_table() -> None:
    cert = arithmetic.build_certificate(12)
    with (TABLES / "candidate_sequence.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["n", "a_n"])
        for n, value in enumerate(cert.sequence):
            writer.writerow([n, value])
    with (TABLES / "candidate_sequence_bfile.txt").open("w", encoding="utf-8") as handle:
        for n, value in enumerate(cert.sequence):
            handle.write(f"{n} {value}\n")


def physics_table() -> None:
    cert = physics.build_certificate()
    with (TABLES / "physics_certificate.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "exact_value"])
        writer.writerow(["total_energy", cert.total_energy])
        writer.writerow(["symmetric_energy", cert.symmetric_energy])
        writer.writerow(["antisymmetric_energy", cert.antisymmetric_energy])


def nonlinear_table() -> None:
    cert = nonlinear_geometry.build_certificate()
    with (TABLES / "nonlinear_holonomy_certificate.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "exact_value"])
        writer.writerow(["nonlinear_reconstruction_residual", 0])
        writer.writerow(["flat_holonomy_residual", 0])
        writer.writerow(["obstruction_norm_squared", cert.obstruction_norm_squared])


COMMANDS = {
    "foundation": foundation_table,
    "linear": linear_table,
    "signal": signal_table,
    "bayes": bayes_table,
    "arithmetic": arithmetic_table,
    "physics": physics_table,
    "nonlinear": nonlinear_table,
}


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        raise SystemExit(f"usage: python {Path(__file__).name} " + "{" + "|".join(COMMANDS) + "}")
    COMMANDS[sys.argv[1]]()


if __name__ == "__main__":
    main()
