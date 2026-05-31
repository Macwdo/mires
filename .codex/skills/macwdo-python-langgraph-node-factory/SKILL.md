---
name: macwdo-python-langgraph-node-factory
description: "Macwdo LangGraph service-node factory guidance. Use for reusable node factories that map state to service inputs, write outputs under a key, clear errors on success, and capture errors on failure."
---

# LangGraph Node Factory

Use this skill when the user wants reusable service-backed nodes.

## Rules

- Use a `service_node(service_func, input_mapper, output_key)` factory shape.
- Derive service inputs from state through `input_mapper`.
- Call the injected service function.
- Write the result back under `output_key`.
- Clear `error` on success and store `str(exc)` in `error` on failure.
- Return a fresh state dictionary.

## Signature

```python
def service_node(
    service_func: Callable[..., Any],
    input_mapper: Callable[[WorkflowState], dict[str, Any]],
    output_key: str,
) -> Callable[[WorkflowState], WorkflowState]:
    ...
```
