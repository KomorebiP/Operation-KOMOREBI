from __future__ import annotations

import socket
import urllib.request

import pytest

from komorebi_arc3_offline.offline_guard import (
    OfflineNetworkError,
    assert_offline_guard,
    install_offline_guard,
)


def test_network_guard_blocks_connections() -> None:
    install_offline_guard(strict=True)
    assert_offline_guard()
    with pytest.raises(OfflineNetworkError):
        socket.create_connection(("example.com", 80), timeout=0.01)
    with pytest.raises(OfflineNetworkError):
        urllib.request.urlopen("https://example.com", timeout=0.01)


def test_requests_is_blocked_when_available() -> None:
    requests = pytest.importorskip("requests")
    install_offline_guard(strict=True)
    with pytest.raises(OfflineNetworkError):
        requests.get("https://example.com", timeout=0.01)
