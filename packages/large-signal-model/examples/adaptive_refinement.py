from __future__ import annotations

import json

import numpy as np

from komorebi_pr_lasm import PacketTree, best_basis, l1_packet_cost


def main() -> int:
    t = np.linspace(0.0, 1.0, 128, endpoint=False)
    signal = np.sin(2.0 * np.pi * 5.0 * t)
    signal[48:80] += 0.75 * np.sin(2.0 * np.pi * 24.0 * t[48:80])
    tree = PacketTree.analyze(signal, maximum_depth=7)
    selected = best_basis(tree, cost=l1_packet_cost, packet_penalty=0.08)
    reconstructed = tree.synthesize(selected.paths)
    residual = float(np.max(np.abs(reconstructed - signal)))
    report = {
        "selected_packet_count": len(selected.paths),
        "selected_paths": list(selected.paths),
        "maximum_reconstruction_residual": residual,
    }
    print(json.dumps(report, indent=2))
    return 0 if residual < 1e-10 else 1


if __name__ == "__main__":
    raise SystemExit(main())
