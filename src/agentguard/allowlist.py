"""Host allowlist: exact match + optional *.suffix (v0: host only)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Allowlist:
    """Allowed hosts. v0: host only; (host, port) and paths deferred."""

    hosts: frozenset[str]


    def is_allowed(self, host: str) -> bool:
        """True if host is allowed: exact match or *.suffix (e.g. *.example.com)."""
        host = host.lower()
        for entry in self.hosts:
            entry = entry.lower()
            if entry.startswith("*."):
                suffix = entry[1:]  # ".example.com"
                return host == entry[2:] or host.endswith(suffix)
            if host == entry:
                return True
        return False
