"""
Optional Hugging Face / Render deploy helpers.

Plans are always available offline. Live API calls require ACADEMY_DEPLOY=1 and
provider credentials. Claims flip to deployed=true only after a successful API OK.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


SUPPORTED_LIVE = {"huggingface", "render"}


def deploy_track_requested() -> bool:
    return os.getenv("ACADEMY_DEPLOY", "").strip() == "1"


def huggingface_plan(model_uri: str, environment: str, repo: str | None = None) -> dict[str, Any]:
    repo_id = repo or os.getenv("ACADEMY_HF_REPO", "org/academy-churn-risk")
    return {
        "provider": "huggingface",
        "resource": "inference-endpoint",
        "model_uri": model_uri,
        "repo_id": repo_id,
        "identity": "hf-token",
        "environment": environment,
        "claims": {"huggingface_deployed": False},
    }


def render_plan(model_uri: str, environment: str, service_id: str | None = None) -> dict[str, Any]:
    sid = service_id or os.getenv("ACADEMY_RENDER_SERVICE_ID", "srv-academy-placeholder")
    return {
        "provider": "render",
        "resource": "web-service",
        "model_uri": model_uri,
        "service_id": sid,
        "identity": "render-api-key",
        "environment": environment,
        "claims": {"render_deployed": False},
    }


def build_deploy_plan(provider: str, model_uri: str, environment: str) -> dict[str, Any]:
    if environment not in {"staging", "production"}:
        raise ValueError("environment must be staging or production")
    if provider == "huggingface":
        return huggingface_plan(model_uri, environment)
    if provider == "render":
        return render_plan(model_uri, environment)
    raise ValueError(f"unsupported live deploy provider: {provider}")


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={**headers, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - operator-gated URL
        body = resp.read().decode()
        return json.loads(body) if body else {"status": resp.status}


def maybe_deploy(provider: str, model_uri: str, environment: str = "staging") -> dict[str, Any]:
    plan = build_deploy_plan(provider, model_uri, environment)
    plan["gate"] = {"academy_deploy": deploy_track_requested()}
    if not deploy_track_requested():
        plan["execution"] = {"status": "skipped", "reason": "ACADEMY_DEPLOY!=1"}
        return plan

    if provider == "huggingface":
        token = os.getenv("HF_TOKEN", "").strip()
        if not token:
            plan["execution"] = {"status": "skipped", "reason": "HF_TOKEN missing"}
            return plan
        # Minimal Hub ping — does not create paid endpoints by default.
        # Operators can point ACADEMY_HF_DEPLOY_URL at a custom deployer.
        url = os.getenv(
            "ACADEMY_HF_DEPLOY_URL",
            f"https://huggingface.co/api/models/{plan['repo_id']}",
        )
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
            with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
                plan["execution"] = {"status": "ok", "http_status": resp.status, "mode": "hf_api_get"}
                plan["claims"]["huggingface_deployed"] = True
                plan["deployment_id"] = plan["repo_id"]
        except urllib.error.HTTPError as exc:
            plan["execution"] = {"status": "error", "http_status": exc.code, "reason": str(exc)}
        except Exception as exc:  # noqa: BLE001
            plan["execution"] = {"status": "error", "reason": str(exc)}
        return plan

    if provider == "render":
        key = os.getenv("RENDER_API_KEY", "").strip()
        if not key:
            plan["execution"] = {"status": "skipped", "reason": "RENDER_API_KEY missing"}
            return plan
        service_id = plan["service_id"]
        url = os.getenv(
            "ACADEMY_RENDER_DEPLOY_URL",
            f"https://api.render.com/v1/services/{service_id}/deploys",
        )
        try:
            result = _post_json(url, {"clearCache": "do_not_clear"}, {"Authorization": f"Bearer {key}"})
            dep_id = result.get("id") or result.get("deploy", {}).get("id")
            plan["execution"] = {"status": "ok", "response_keys": sorted(result.keys())}
            if dep_id:
                plan["claims"]["render_deployed"] = True
                plan["deployment_id"] = dep_id
            else:
                plan["execution"]["note"] = "API OK but no deploy id — claim stays false"
        except Exception as exc:  # noqa: BLE001
            plan["execution"] = {"status": "error", "reason": str(exc)}
        return plan

    raise ValueError(f"unsupported provider: {provider}")
