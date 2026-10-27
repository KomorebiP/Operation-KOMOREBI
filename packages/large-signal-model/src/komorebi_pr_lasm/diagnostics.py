"""Small deterministic installation check, independent of ARC runtimes."""
from __future__ import annotations
import importlib.metadata
import platform
import numpy as np

from .signal import analyze_signal, PolyphaseFIR, StreamingFIR
from komorebi_arc3_offline.exact_atlas import MultiAtlasAnalyzer
from komorebi_arc3_offline.bayes import BayesianRegression


def self_check() -> dict[str, object]:
    rng = np.random.default_rng(20261009)
    x = rng.normal(size=96)
    taps = np.asarray([0.25, 0.5, 0.25, -0.1])
    analysis = analyze_signal(x)
    image = MultiAtlasAnalyzer().analyze(rng.normal(size=(7, 10)))
    bank = PolyphaseFIR(taps, modulus=3)
    expected = np.convolve(x, taps)
    stream = StreamingFIR(taps)
    streamed = np.concatenate([stream.process(x[:13]), stream.process(x[13:]), stream.flush()])
    design = np.column_stack([np.ones(50), np.linspace(-1, 1, 50)])
    fit = BayesianRegression().fit(design, (design @ np.array([0.3, 1.2]))[:, None])
    _, variance = fit.predict(design)
    residuals = {
        "signal_reconstruction": max(analysis.reconstruction_residuals().values()),
        "irregular_image_reconstruction": max(image.reconstruction_residuals().values()),
        "polyphase_fir": float(np.max(np.abs(bank.apply(x) - expected))),
        "streaming_fir": float(np.max(np.abs(streamed - expected))),
    }
    checks = {name: residual <= 1e-10 for name, residual in residuals.items()}
    checks["finite_predictive_variance"] = bool(np.isfinite(variance).all() and (variance > 0).all())
    versions = {"python": platform.python_version()}
    for package in ("numpy", "scipy"):
        versions[package] = importlib.metadata.version(package)
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
            "residuals": residuals, "environment": versions,
            "scope": "finite installation controls; no ARC score, trained checkpoint, or universal-model claim"}


__all__ = ["self_check"]
