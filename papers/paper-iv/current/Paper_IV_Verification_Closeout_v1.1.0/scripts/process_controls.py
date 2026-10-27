#!/usr/bin/env python3
"""POSIX fixture supervision with separate startup and execution deadlines.

Readiness is an explicit child-created file with exact content. This helper tests
process-group cleanup; it is not a proof checker or supervision of escaped groups.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import signal
import subprocess
import time
from typing import Any


def execute_ready(argv: list[str], cwd: Path, ready: Path, log: Path,
                  startup_timeout: float = 5.0,
                  execution_timeout: float = 1.0) -> dict[str, Any]:
    if os.name != 'posix':
        raise RuntimeError('Readiness fixture requires POSIX process groups')
    if startup_timeout <= 0 or execution_timeout <= 0:
        raise ValueError('Both deadlines must be positive')
    if ready.exists():
        raise ValueError('Readiness file must not exist before launch')
    begin = time.monotonic()
    readiness_time = None
    timeout_stage = None
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open('wb') as output:
        process = subprocess.Popen(argv, cwd=cwd, stdout=output,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            while True:
                if ready.exists() and ready.read_text() == 'READY':
                    readiness_time = time.monotonic()
                    break
                if process.poll() is not None:
                    break
                if time.monotonic() - begin >= startup_timeout:
                    timeout_stage = 'startup'
                    break
                time.sleep(0.01)
            if readiness_time is not None:
                try:
                    process.wait(timeout=execution_timeout)
                except subprocess.TimeoutExpired:
                    timeout_stage = 'execution'
        finally:
            # Clean every remaining member of the launched process group, even
            # when the direct parent exits first. Never treat a timeout as proof.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            code = process.wait()
    return {
        'argv': argv, 'returncode': code, 'ready': readiness_time is not None,
        'timed_out': timeout_stage is not None, 'timeout_stage': timeout_stage,
        'startup_seconds': None if readiness_time is None else readiness_time-begin,
        'seconds': time.monotonic()-begin,
        'startup_timeout': startup_timeout, 'execution_timeout': execution_timeout,
        'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest(),
    }
