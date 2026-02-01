"""Socket-level egress interception: patch connect, record (host, port) + stack, raise EgressBlocked."""

import socket
import traceback
from contextlib import contextmanager
from typing import Any, Optional
from agentguard.allowlist import Allowlist


class EgressEvent(Exception):
    """Raised when an outbound connect is detected and blocked."""

    def __init__(self, host: str, port: int | None, stack_trace: str | None = None):
        self.host = host
        self.port = port
        self.stack_trace = stack_trace
        super().__init__(f"Egress blocked: {host}:{port}")


_original_connect: Any = None

@contextmanager
def no_egress(allow_hosts: Optional[set[str] | frozenset[str]] = None):
    """Context manager that blocks outbound socket connects and raises EgressEvent on detection."""
    allowlist = Allowlist(hosts=allow_hosts) if allow_hosts else None

    def _patched_connect(self: socket.socket, address: tuple[Any, ...]) -> None:
        host = address[0]
        port = address[1] if len(address) > 1 else None
        if allowlist and allowlist.is_allowed(host):
            return _original_connect(self, address)
        stack = "".join(traceback.format_stack())
        print(f"[agentguard] egress detected: host={host!r} port={port}")
        print(stack)
        raise EgressEvent(str(host), port, stack)

    global _original_connect
    _original_connect = socket.socket.connect
    socket.socket.connect = _patched_connect
    try:
        yield
    finally:
        socket.socket.connect = _original_connect
