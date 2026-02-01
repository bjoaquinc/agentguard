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


def test_no_connect_inside_no_egress_succeeds():
    """Inside no_egress(), code that does not connect exits normally."""
    with no_egress():
        pass  # no connect attempted
    # no exception
