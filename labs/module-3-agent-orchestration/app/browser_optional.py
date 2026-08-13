"""
Optional Playwright browser track for Module 3.

Default (CI / Cloud Agent): stub DOM runtime only. Never claims Playwright ran.
Optional: ACADEMY_BROWSER=1 + pip install -r requirements-browser.txt
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import time
from typing import Any

from app.browser_agent import BrowserAgent
from app.browser_runtime import StubDomRuntime

_LAB_ROOT = pathlib.Path(__file__).resolve().parent.parent


def browser_track_requested() -> bool:
    return os.getenv("ACADEMY_BROWSER", "").strip() == "1"


def build_browser_plan() -> dict[str, Any]:
    return {
        "track": "optional-browser-playwright",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "default_runtime": "stub_dom",
        "fixture": str(_LAB_ROOT / "fixtures" / "vendor_portal.html"),
        "action_space": ["navigate", "click", "type", "scroll", "extract_a11y"],
        "rejected_tools": ["evaluate_js"],
        "gate": {
            "academy_browser": browser_track_requested(),
            "mode": "playwright" if browser_track_requested() else "stub",
        },
        "claims": {
            "browser_runtime": "stub",
            "playwright_executed": False,
            "note": (
                "Default CI uses StubDomRuntime. Set ACADEMY_BROWSER=1 and install "
                "requirements-browser.txt to attempt a real Playwright session."
            ),
        },
    }


def maybe_run_browser_track(plan: dict[str, Any] | None = None) -> dict[str, Any]:
    plan = plan or build_browser_plan()
    # Always demonstrate the stub path in the plan artifact.
    stub_agent = BrowserAgent(StubDomRuntime())
    stub_result = stub_agent.run("Renew ACME license on the vendor portal")
    plan["stub_demo"] = {
        "status": stub_result.status,
        "step_count": len(stub_result.steps),
        "ipi_detected": stub_result.claims.get("ipi_detected"),
        "hitl_required": stub_result.claims.get("hitl_required"),
    }

    if not browser_track_requested():
        plan["execution"] = {"status": "skipped", "reason": "ACADEMY_BROWSER!=1"}
        return plan

    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as exc:  # noqa: BLE001
        plan["execution"] = {
            "status": "skipped",
            "reason": f"playwright import failed: {exc}",
            "hint": "pip install -r requirements-browser.txt && playwright install chromium",
        }
        return plan

    fixture = _LAB_ROOT / "fixtures" / "vendor_portal.html"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(fixture.as_uri())
            title = page.title()
            browser.close()
        plan["execution"] = {
            "status": "ran",
            "title": title,
            "fixture": str(fixture),
        }
        plan["claims"]["playwright_executed"] = True
        plan["claims"]["browser_runtime"] = "playwright"
    except Exception as exc:  # noqa: BLE001
        plan["execution"] = {
            "status": "skipped",
            "reason": f"playwright session failed: {exc}",
        }
    return plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Browser micro-lab plan / optional Playwright")
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args()
    result = maybe_run_browser_track(build_browser_plan())
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "claims": result["claims"],
                "execution": result.get("execution"),
                "stub_demo": result.get("stub_demo"),
            },
            sort_keys=True,
        )
    )
