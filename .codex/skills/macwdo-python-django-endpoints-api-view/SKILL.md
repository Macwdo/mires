---
name: macwdo-python-django-endpoints-api-view
description: "Macwdo DRF APIView guidance. Use for bespoke workflows, RPC-like actions, webhooks, multi-step flows, thin BaseAPIView handlers, serializer validation, service calls, and explicit responses."
---

# Django Endpoints APIView

Use this skill when an endpoint is custom logic rather than standard resource CRUD.

## Rules

- Use an APIView for bespoke workflows, RPC-like actions, webhooks, or multi-step flows.
- Inspect existing `views.py`, `serializers.py`, `selectors.py`, `services.py`, `urls.py`, and tests before choosing the shape.
- Validate request data with a serializer and `raise_exception=True`.
- Call a selector for read flows and a service for write flows.
- Return `Response(..., status=...)` explicitly.
- Use the project base APIView when one exists.

## Example

```python
class ExampleAPIView(BaseAPIView):
    def post(self, request: Request) -> Response:
        input_serializer = ExampleSerializerRequest(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        example = services.do_example(**input_serializer.validated_data)
        output_serializer = ExampleSerializerResponse(example)

        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
```
