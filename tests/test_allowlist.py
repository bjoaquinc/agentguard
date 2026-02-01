"""Tests that allowlist allows permitted hosts and no_egress(allow_hosts=...) permits them."""

import socket

import pytest

from agentguard import EgressEvent, no_egress
from agentguard.allowlist import Allowlist


def test_allowlist_exact_match_allows_host():
    """Allowlist.is_allowed returns True for exact host match."""
    allowlist = Allowlist(hosts=frozenset({"example.com"}))
    assert allowlist.is_allowed("example.com") is True
    assert allowlist.is_allowed("other.com") is False


def test_allowlist_suffix_allows_subdomain_and_bare():
    """Allowlist.is_allowed with *.suffix allows bare domain and subdomains."""
    allowlist = Allowlist(hosts=frozenset({"*.example.com"}))
    assert allowlist.is_allowed("example.com") is True
    assert allowlist.is_allowed("api.example.com") is True
    assert allowlist.is_allowed("other.com") is False


def test_no_egress_with_allow_hosts_allows_listed_host():
    """With no_egress(allow_hosts={...}), connect to allowed host does not raise EgressEvent."""
    with no_egress(allow_hosts={"example.com"}):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("example.com", 80))  # allowed; may raise OSError if unreachable
        except OSError:
            pass  # network unreachable is ok; we only assert no EgressEvent
    # no EgressEvent


def test_no_egress_with_allow_hosts_blocks_non_listed_host():
    """With no_egress(allow_hosts={...}), connect to non-allowed host raises EgressEvent."""
    with no_egress(allow_hosts={"example.com"}):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with pytest.raises(EgressEvent) as exc_info:
            s.connect(("other.com", 80))
    assert exc_info.value.host == "other.com"
    assert exc_info.value.port == 80
