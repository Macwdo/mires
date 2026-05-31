---
name: macwdo-python-django-serializers-advanced-functions
description: "Macwdo advanced DRF serializer function guidance. Use when response shaping is complex enough to need a serializer function rather than overloading selectors or model serializers."
---

# Django Serializers Advanced Functions

Use this skill when response assembly is more complex than a single serializer instantiation.

## Rules

- Move complex output assembly into a serializer function instead of overloading a selector.
- Let selectors decide what data to fetch and serializer functions decide how to shape API-ready payloads.
- Optimize related objects deliberately before serializing lists or feeds.
- Keep serializer functions close to serializer classes unless the repo has a better module convention.
- Test the response shape through the endpoint or a focused serializer test.

## Example

```python
def example_feed_serialize(feed):
    feed_ids = [item.id for item in feed]
    objects = ExampleModel.objects.filter(id__in=feed_ids).order_by("-created_at")
    return [ExampleSerializerResponse(obj).data for obj in objects]
```
