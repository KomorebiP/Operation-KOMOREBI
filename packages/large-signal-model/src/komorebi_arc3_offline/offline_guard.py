from __future__ import annotations

import builtins
import http.client
import os
import socket
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable


class OfflineNetworkError(RuntimeError):
    """Raised when code attempts network access in the offline runner."""


@dataclass(frozen=True)
class OfflineGuardState:
    installed: bool
    strict: bool


_INSTALLED = False
_ORIGINALS: dict[str, Any] = {}


def _blocked(*args: Any, **kwargs: Any) -> Any:
    del args, kwargs
    raise OfflineNetworkError(
        "network access is disabled by the Komorebi ARC-AGI-3 offline runner"
    )


def _patch_requests() -> None:
    try:
        import requests.sessions
    except Exception:
        return
    if "requests.Session.request" not in _ORIGINALS:
        _ORIGINALS["requests.Session.request"] = requests.sessions.Session.request
        requests.sessions.Session.request = _blocked  # type: ignore[assignment]


def install_offline_guard(*, strict: bool = True) -> OfflineGuardState:
    """Disable outbound network access for the current Python process.

    The official ARC-AGI toolkit is still used, but it is constructed in
    ``OperationMode.OFFLINE`` and receives only local environment files.
    The guard is an additional defense against accidental HTTP, socket, or
    anonymous-key requests from any imported package.
    """

    global _INSTALLED
    os.environ["OPERATION_MODE"] = "OFFLINE"
    os.environ["ARC_API_KEY"] = ""
    # Fail closed even for libraries that read proxy variables before the
    # Python-level socket guard is reached.  The loopback discard port is
    # intentionally unreachable; no remote proxy can be inherited.
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        os.environ[name] = "http://127.0.0.1:9"
    os.environ["NO_PROXY"] = ""
    os.environ["no_proxy"] = ""
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["WANDB_MODE"] = "offline"
    os.environ["KOMOREBI_ARC3_OFFLINE_ONLY"] = "1"

    if _INSTALLED:
        _patch_requests()
        return OfflineGuardState(True, strict)

    _ORIGINALS.update(
        {
            "socket.socket.connect": socket.socket.connect,
            "socket.socket.connect_ex": socket.socket.connect_ex,
            "socket.create_connection": socket.create_connection,
            "socket.getaddrinfo": socket.getaddrinfo,
            "urllib.request.urlopen": urllib.request.urlopen,
            "http.client.HTTPConnection.connect": http.client.HTTPConnection.connect,
            "http.client.HTTPSConnection.connect": http.client.HTTPSConnection.connect,
        }
    )

    socket.socket.connect = _blocked  # type: ignore[assignment]
    socket.socket.connect_ex = _blocked  # type: ignore[assignment]
    socket.create_connection = _blocked  # type: ignore[assignment]
    if strict:
        socket.getaddrinfo = _blocked  # type: ignore[assignment]
    urllib.request.urlopen = _blocked  # type: ignore[assignment]
    http.client.HTTPConnection.connect = _blocked  # type: ignore[assignment]
    http.client.HTTPSConnection.connect = _blocked  # type: ignore[assignment]
    _patch_requests()
    _INSTALLED = True
    return OfflineGuardState(True, strict)


def assert_offline_guard() -> None:
    if not _INSTALLED:
        raise RuntimeError("offline network guard has not been installed")
    try:
        socket.create_connection(("example.com", 80), timeout=0.01)
    except OfflineNetworkError:
        return
    except Exception as exc:
        raise RuntimeError(f"unexpected offline-guard behavior: {exc}") from exc
    raise RuntimeError("offline network guard did not block a connection attempt")


def offline_only() -> bool:
    return _INSTALLED and os.environ.get("OPERATION_MODE", "").upper() == "OFFLINE"
