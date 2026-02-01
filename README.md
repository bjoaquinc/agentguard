# agentguard

**Detect and block outbound network *attempts* in-process.**  
Primary goal: deterministic CI gating for **no uncontrolled egress**.

This library does **not** claim OS/network-level isolation. It produces developer-actionable evidence (host/URL + stack) when an egress attempt is intercepted.

---

## Purpose

Agent-callable functions and their dependencies can silently perform outbound network calls (telemetry, redirects, model downloads) that expand what the agent is allowed to do.
This library lets you assert, in tests and CI, that agent capabilities only make explicitly allowed network calls—and fail deterministically when they don’t.

---

## Example

**Before:** hope and manual review.

```python
def fetch_weather(city: str) -> dict:
    # Does this accidentally make unintended network calls?
    # Does a dependency phone home?
    # ¯\_(ツ)_/¯
    return weather_api.get(city)
```

**With agentguard:** automated verification of one invariant.

```python
def test_fetch_weather_no_egress():
    from agentguard import no_egress
    with no_egress(allow_hosts={"api.weather.com"}):
        fetch_weather("London")
    # If any uncontrolled outbound attempt occurs,
    # the test fails with evidence (host/url + stack)
```

---

## Notebooks

The notebooks in `notebooks/` are for researchers to pressure-test assumptions (e.g. telemetry, SDK egress, edge cases). Add cells and try scenarios; deterministic coverage lives in `tests/`.

---

## Known limitations

1. **Subprocess bypass** — Child processes (`subprocess`, CLIs, browsers) are out of scope for v0.
2. **Native / C-level networking** — Rare cases may bypass Python interception; handled later via OS-level enforcement.
3. **Async networking** — Async clients may need explicit patching for richer context; socket interception still blocks.
4. **Hostname vs IP** — `connect()` may see IPs; hostname allowlists may fail unexpectedly. Record both.
5. **Background threads** — Telemetry may attempt late egress; keep the context active for the full test.
6. **Real network flakiness** — Default to blocking; tests assert interception, not successful calls.

---

## Scope (v0)

- One invariant: no uncontrolled egress.
- One repo: this library; no agent framework integration.
- Enforcement: in-process only; not OS/network-level isolation.
