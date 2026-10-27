from __future__ import annotations

import json

import numpy as np

from komorebi_pr_lasm import MultiAtlasAnalyzer, MultiAtlasConfig


def main() -> int:
    y, x = np.mgrid[0:64, 0:64]
    frame = ((3 * x + 5 * y + (x // 8) * (y // 8)) % 16).astype(np.int16)
    analysis = MultiAtlasAnalyzer(MultiAtlasConfig(haar_levels=4)).analyze(frame)
    residuals = analysis.reconstruction_residuals()
    residuals["tight_frame"] = float(
        np.max(np.abs(analysis.tight_frame_synthesis() - frame))
    )
    print(json.dumps(residuals, indent=2, sort_keys=True))
    return 0 if max(residuals.values()) < 1e-10 else 1


if __name__ == "__main__":
    raise SystemExit(main())
