#!/usr/bin/env python3
"""Reproducible microbenchmark for the Stage-A strict training sampler."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.data import EpisodeGenerator, _direct_conditioned_support
from komorebi_neuralese.splits import word_products_all_in_split


def _reference_rejection(
    seed: int, lengths: np.ndarray, batch_size: int
) -> tuple[float, int]:
    """Time the prior exact proposal/reject loop, conservatively.

    This omits chunk concatenation and the redundant post-acceptance audit used
    in training, so it slightly favors the reference implementation.
    """

    generator = EpisodeGenerator(seed)
    candidates = 0
    started = time.perf_counter()
    for raw_length in lengths:
        length = int(raw_length)
        accepted = 0
        while accepted < batch_size:
            candidate_size = batch_size - accepted
            candidate = generator._sample_once(
                candidate_size,
                length,
                family="d4",
                coordinate_split="train",
            )
            keep = word_products_all_in_split(
                candidate.maps.numpy(),
                candidate.op_slots.numpy(),
                "train",
                scope="contiguous",
            )
            candidates += candidate_size
            accepted += int(keep.sum())
    return time.perf_counter() - started, candidates


def _direct(seed: int, lengths: np.ndarray, batch_size: int) -> float:
    generator = EpisodeGenerator(seed)
    started = time.perf_counter()
    for raw_length in lengths:
        batch = generator.sample(
            batch_size,
            int(raw_length),
            family="d4",
            coordinate_split="train",
            word_product_scope="contiguous",
            word_product_split="train",
            conditioned_sampler_backend="cached_exact_v1",
        )
        confined = word_products_all_in_split(
            batch.maps.numpy(), batch.op_slots.numpy(), "train", scope="contiguous"
        )
        if not bool(np.all(confined)):
            raise RuntimeError("direct sampler violated the strict boundary")
    return time.perf_counter() - started


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batches", type=int, default=400)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--seed", type=int, default=260)
    args = parser.parse_args()
    if args.batches < 1 or args.batch_size < 1:
        raise ValueError("batches and batch-size must be positive")

    length_rng = np.random.default_rng(40_000 + args.seed)
    lengths = length_rng.integers(1, 5, size=args.batches, dtype=np.int64)

    _direct_conditioned_support.cache_clear()
    cold_started = time.perf_counter()
    for length in (1, 2, 3, 4):
        support = _direct_conditioned_support(
            "d4", "train", "train", "contiguous", length, None
        )
        if support is None:
            raise RuntimeError("Stage-A exact support unexpectedly unavailable")
    cold_cache_seconds = time.perf_counter() - cold_started

    direct_seconds = _direct(10_000 + args.seed, lengths, args.batch_size)
    rejection_seconds, rejection_candidates = _reference_rejection(
        10_000 + args.seed, lengths, args.batch_size
    )
    result = {
        "batches": args.batches,
        "batch_size": args.batch_size,
        "examples": args.batches * args.batch_size,
        "cold_support_build_seconds": cold_cache_seconds,
        "warm_direct_seconds_including_strict_audit": direct_seconds,
        "reference_rejection_seconds_conservative": rejection_seconds,
        "reference_candidate_examples": rejection_candidates,
        "reference_acceptance_fraction": (
            args.batches * args.batch_size / rejection_candidates
        ),
        "warm_speedup_over_conservative_reference": rejection_seconds / direct_seconds,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
