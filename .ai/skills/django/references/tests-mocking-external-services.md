---
name: tests-mocking-external-services
description: "Mires Django external-service mocking guidance. Use for unittest.mock patching where functions are used, MagicMock, fake clients, and keeping mocks near the test that needs them."
---

# Django Tests Mocking External Services

Use this skill when a Django test touches email, task queues, SDK clients, HTTP APIs, storage, or other external systems.

## Rules

- Mock external services at the module where the function is used, not where it is defined.
- Use fakes or `MagicMock` only at true external boundaries.
- Keep patching near the test that needs it.
- Set return values explicitly so assertions describe the behavior.
- Do not mock the service or selector under test unless the test is for an endpoint adapter boundary.

## Example

```python
from unittest.mock import MagicMock, patch


@pytest.mark.django_db
@patch.object(external_module, "method_name")
def test_action_returns_expected_result(mock_method: MagicMock, api_client_with_common_user):
    """Action returns expected data when the external service succeeds."""
    mock_method.return_value = {"key": "value"}
```
