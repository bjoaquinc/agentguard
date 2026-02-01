"""Tests that no_egress blocks socket.connect and raises EgressEvent with evidence."""

import socket

import pytest

from agentguard import EgressEvent, no_egress


def test_connect_inside_no_egress_raises_egress_event():
    """Inside no_egress(), socket.connect is blocked and EgressEvent is raised."""
    with no_egress():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with pytest.raises(EgressEvent) as exc_info:
            s.connect(("example.com", 80))
    assert exc_info.value.host == "example.com"
    assert exc_info.value.port == 80
    assert exc_info.value.stack_trace is not None

def test_connect_inside_no_egress_with_allow_hosts_allows_host():
    """Inside no_egress(allow_hosts={...}), socket.connect is allowed (no EgressEvent)."""
    try:
        with no_egress(allow_hosts={"example.com"}):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("example.com", 80))
    except EgressEvent:
        pytest.fail("EgressEvent should not be raised for allowed host")
    except OSError:
        pass  # network unreachable is ok

def test_connect_inside_no_egress_with_allow_hosts_blocks_non_allowed_host():
    """Inside no_egress(allow_hosts={...}), socket.connect is blocked."""
    with no_egress(allow_hosts={"example.com"}):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with pytest.raises(EgressEvent) as exc_info:
            s.connect(("other.com", 80))
    assert exc_info.value.host == "other.com"
    assert exc_info.value.port == 80

def test_no_connect_inside_no_egress_succeeds():
    """Inside no_egress(), code that does not connect exits normally."""
    with no_egress():
        pass  # no connect attempted
    # no exception
