"""Use only the authenticated portable kit's application-path compatibility shim.

The shim adapts executable path discovery to this host. Lean compiler/kernel
bytes are unchanged. Arbitrary inherited LD_PRELOAD values remain discarded by
the original runtime_env. This file is integration tooling, not a proof module.
"""
from pathlib import Path
from audit_engine import AuditError, runtime_env as original_runtime_env, sha256

ADAPTER_SHA256 = 'fdcc7edf41b2c301abd13ec01041d44eee52148cbf05f2332bc39b23c5862853'

def runtime_env(runtime: Path, objects: list[Path], *, packages=()):
    lean, env = original_runtime_env(runtime, objects, packages=packages)
    adapter = runtime/'compat/app_path.so'
    if adapter.is_symlink() or not adapter.is_file() or sha256(adapter) != ADAPTER_SHA256:
        raise AuditError('Pinned portable runtime path adapter missing or digest mismatch')
    env['LD_PRELOAD'] = str(adapter.resolve())
    return lean, env
