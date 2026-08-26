from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import Any

from mires.compatibility.models import AssetInventory, McpAsset, McpSecretBinding, SecretAsset

__all__ = ["bind_secret_references"]


def bind_secret_references(inventory: AssetInventory, target: str) -> AssetInventory:
    """Render secret references for one runtime without ever reading their values."""
    secrets = {secret.name: secret for secret in inventory.secrets}
    bound_mcps: list[McpAsset] = []
    for mcp in inventory.mcps:
        server = deepcopy(mcp.server)
        for binding in mcp.secrets:
            if target not in binding.targets:
                continue
            secret = secrets.get(binding.secret)
            if secret is None:
                raise ValueError(f"MCP '{mcp.name}' references unavailable secret '{binding.secret}'")
            _bind_mcp_secret(server, mcp, secret, binding, target)
        bound_mcps.append(replace(mcp, server=server))
    return replace(inventory, mcps=tuple(bound_mcps))


def _bind_mcp_secret(
    server: dict[str, Any],
    mcp: McpAsset,
    secret: SecretAsset,
    binding: McpSecretBinding,
    target: str,
) -> None:
    if target == "codex":
        _bind_codex(server, mcp, secret, binding)
    elif target == "claude":
        _bind_environment(server, binding.env, f"${{{secret.source_env}}}")
    elif target == "opencode":
        _bind_environment(server, binding.env, f"{{env:{secret.source_env}}}")
    elif target == "cursor":
        raise ValueError(
            f"target 'cursor' has no verified non-literal secret reference for '{secret.name}' on MCP '{mcp.name}'"
        )
    else:
        raise ValueError(f"unsupported secret target: {target}")


def _bind_codex(
    server: dict[str, Any],
    mcp: McpAsset,
    secret: SecretAsset,
    binding: McpSecretBinding,
) -> None:
    if mcp.is_remote:
        raise ValueError(
            f"Codex stdio env reference cannot be applied to remote MCP '{mcp.name}' for secret '{secret.name}'"
        )
    if binding.env != secret.source_env:
        raise ValueError(
            f"Codex cannot rename secret environment variable '{secret.source_env}' "
            f"to '{binding.env}' for MCP '{mcp.name}'"
        )
    existing = server.get("env_vars") or []
    if not isinstance(existing, list) or not all(isinstance(item, str) for item in existing):
        raise ValueError(f"MCP '{mcp.name}' has invalid Codex env_vars")
    server["env_vars"] = sorted({*existing, secret.source_env})


def _bind_environment(server: dict[str, Any], name: str, reference: str) -> None:
    existing = server.get("env") or {}
    if not isinstance(existing, dict):
        raise ValueError("MCP env must be a mapping before scoped secrets can be applied")
    server["env"] = {**existing, name: reference}
