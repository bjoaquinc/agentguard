import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium")


@app.cell
def _():
    from agentguard import no_egress, EgressEvent
    import socket
    return EgressEvent, no_egress, socket


@app.cell
def _(socket):
    # With no_egress active, any connect is blocked and we get evidence (host, port, stack).
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Control: no hook to block egress and throw an error
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("example.com", 80))
        print("Control: connect attempted (no EgressEvent).")
    except OSError as e:
        print("Control: connect attempted; network error:", e)
    return (s,)


@app.cell
def _(EgressEvent, no_egress, s):
    # With no_egress hook and egress
    try:
        with no_egress():
            s.connect(("example.com", 80))
    except EgressEvent as e:
        print("Evidence:", e.host, e.port)
        if e.stack_trace:
            print("Stack (last 3 lines):", e.stack_trace.strip().split("\n")[-3:])
    return


@app.cell
def _(no_egress):
    # With no_egress hook and no egress
    with no_egress():
        pass  # No connect attempted
    print("OK: no egress attempted, so no exception.")
    return


if __name__ == "__main__":
    app.run()
