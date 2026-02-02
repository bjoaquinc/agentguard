import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from agentguard import no_egress, EgressEvent
    import sentry_sdk
    return EgressEvent, mo, no_egress, sentry_sdk


@app.cell
def _(mo):
    mo.md("""
    ## Scenario: Read-only tool unexpectedly has telemetry egress

    An **agent-callable function** is documented to only call `api.weather.com`. In production it is wired with Sentry; that dependency can **silently perform outbound network calls** (telemetry), so the **capability exceeds the documented purpose**.

    We use **no_egress** for **deterministic CI gating**: in-process enforcement (not OS/network-level isolation). If any uncontrolled egress occurs, the test **fails with evidence** (host + stack).
    """)
    return


@app.cell
def _(sentry_sdk):
    def fetch_weather(city: str) -> dict:
        result = {"city": city}
        sentry_sdk.init(
            dsn="https://key@o0.ingest.sentry.io/0",
            traces_sample_rate=0.0,
        )
        sentry_sdk.capture_message("fetch_weather called")
        sentry_sdk.flush(timeout=2)
        return result
    return (fetch_weather,)


@app.cell
def _(EgressEvent, fetch_weather, no_egress):
    try:
        with no_egress(allow_hosts={"api.weather.com"}):
            fetch_weather("London")
    except EgressEvent as e:
        lines = [
            "--- Egress blocked (CI) ---",
            f"host: {e.host}",
            f"port: {e.port}",
            "destination: " + (e.host or "") + (f":{e.port}" if e.port is not None else ""),
        ]
        if e.stack_trace:
            lines.append("stack excerpt:")
            lines.append(e.stack_trace.strip()[-1200:])
        lines.append("---")
        print("\n".join(lines))
    return


@app.cell
def _(mo):
    mo.md("""
    We are **not** asserting the weather API works; we are asserting **no other hosts are contacted**. The only allowed host was `api.weather.com`; the tool's dependency (Sentry transport) tried to reach another host → blocked with evidence.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### This is what a pytest would look like

    Deterministic gating lives in **tests/**; notebooks are for exploration and pressure-testing.

    ```python
    def test_fetch_weather_no_egress():
        from agentguard import no_egress
        with no_egress(allow_hosts={"api.weather.com"}):
            fetch_weather("London")
        # If any uncontrolled outbound attempt occurs,
        # the test fails with evidence (host/url + stack)
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    **Limitations (v0):** Subprocess bypass, native/C-level networking, async clients, hostname vs IP, background threads, real network flakiness. In-process only; not OS isolation. See README.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### The fix: capabilities must be explicit

    A developer can:

    * **Add `sentry.io` (or the ingest host) to the allowlist** — explicitly granting telemetry capability.
    * **Disable Sentry in that tool or in CI** — so the capability is not present when gating.
    * **Route telemetry to localhost or an internal collector** — keep egress within allowed boundaries.

    The invariant stays: only explicitly allowed network calls.
    """)
    return


if __name__ == "__main__":
    app.run()
