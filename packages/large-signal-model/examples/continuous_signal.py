"""Exact coordinates versus a deliberately lossy packet approximation."""
import json
import numpy as np
from komorebi_pr_lasm import analyze_signal, best_basis, l1_packet_cost


def main() -> None:
    t = np.arange(512) / 512.0
    signal = np.sin(2 * np.pi * 7 * t) + 0.35 * np.sin(2 * np.pi * 43 * t)
    signal += 0.8 * ((t > 0.30) & (t < 0.58))
    analysis = analyze_signal(signal, modulus=4, maximum_depth=6)
    basis = best_basis(analysis.packets, cost=l1_packet_cost, packet_penalty=0.15)
    reconstructed = analysis.packets.synthesize(basis.paths)
    # This thresholded view is an approximation, never a replacement for the archive.
    retained = {path: values * (np.abs(values) >= 0.2)
                for path, values in basis.coefficients(analysis.packets).items()}
    approximation = analysis.packets.synthesize(retained)
    error = float(np.max(np.abs(reconstructed - signal)))
    assert error < 1e-12
    assert np.array_equal(analysis.spatial, signal)
    print(json.dumps({"exact_residuals": analysis.reconstruction_residuals(),
                      "complete_basis_packets": len(basis.paths),
                      "complete_basis_max_error": error,
                      "thresholded_view_rmse": float(np.sqrt(np.mean((signal-approximation)**2))),
                      "archive_unchanged": True}, indent=2))


if __name__ == '__main__':
    main()
