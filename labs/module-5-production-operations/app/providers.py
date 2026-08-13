from __future__ import annotations

from app.deploy_optional import build_deploy_plan


def deployment_plan(provider: str, model_uri: str, environment: str) -> dict:
    if environment not in {"staging", "production"}:
        raise ValueError("environment must be staging or production")
    if provider == "azure-ai-foundry":
        return {
            "provider": provider,
            "resource": "managed-online-endpoint",
            "model_uri": model_uri,
            "identity": "managed-identity",
            "environment": environment,
        }
    if provider == "databricks":
        return {
            "provider": provider,
            "resource": "model-serving-endpoint",
            "model_uri": model_uri,
            "identity": "service-principal",
            "environment": environment,
        }
    if provider in {"huggingface", "render"}:
        return build_deploy_plan(provider, model_uri, environment)
    raise ValueError("unsupported provider")
