from __future__ import annotations


def deployment_plan(provider: str, model_uri: str, environment: str) -> dict:
    if environment not in {"staging", "production"}:
        raise ValueError("environment must be staging or production")
    if provider == "azure-ai-foundry":
        return {"provider": provider, "resource": "managed-online-endpoint", "model_uri": model_uri, "identity": "managed-identity", "environment": environment}
    if provider == "databricks":
        return {"provider": provider, "resource": "model-serving-endpoint", "model_uri": model_uri, "identity": "service-principal", "environment": environment}
    raise ValueError("unsupported provider")
