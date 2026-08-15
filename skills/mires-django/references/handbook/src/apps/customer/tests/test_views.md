# Customer endpoint tests

## Purpose and when to use it

Verify direct CRUD behavior and the non-negotiable account-isolation boundary.

## When not to use it

Model and service rules with no HTTP behavior should use focused unit tests.

## Responsibilities and invariants

Cross-account retrieve, update, and delete all return 404 and leave the target
unchanged.

## Complete canonical artifact

<!-- artifact: src/apps/customer/tests/test_views.py; profiles: base,full -->
```python
from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.customer.models import Customer


@pytest.mark.django_db
def test_customer_crud_is_direct_and_account_scoped(
    authenticated_client: APIClient,
    user: User,
) -> None:
    # Arrange
    list_url = reverse("api:customers:customer-list")
    payload = {
        "name": "Ada Example",
        "email": "ada@example.com",
        "phone": "+1-555-0100",
        "notes": "Prefers email",
    }

    # Act
    created = authenticated_client.post(
        list_url,
        payload,
    )
    customer = Customer.objects.get(pk=created.json()["id"])
    listing = authenticated_client.get(list_url, {"search": "Ada"})
    detail_url = reverse(
        "api:customers:customer-detail",
        kwargs={"pk": customer.pk},
    )
    updated = authenticated_client.patch(detail_url, {"notes": "Call first"})
    deleted = authenticated_client.delete(detail_url)

    # Assert
    assert created.status_code == status.HTTP_201_CREATED
    assert "account" not in created.json()
    assert customer.account == user.account
    assert listing.status_code == status.HTTP_200_OK
    assert [item["id"] for item in listing.json()["results"]] == [customer.pk]
    assert updated.status_code == status.HTTP_200_OK
    assert updated.json()["notes"] == "Call first"
    assert deleted.status_code == status.HTTP_204_NO_CONTENT
    assert not Customer.objects.filter(pk=customer.pk).exists()


@pytest.mark.django_db
def test_cross_account_objects_are_not_found_for_every_detail_action(
    api_client: APIClient,
    user_factory: Any,
) -> None:
    # Arrange
    actor = user_factory(email="actor@example.com")
    other = user_factory(email="other@example.com")
    target = Customer.objects.create(account=other.account, name="Private")
    api_client.force_authenticate(user=actor)
    detail_url = reverse(
        "api:customers:customer-detail",
        kwargs={"pk": target.pk},
    )

    # Act
    retrieved = api_client.get(detail_url)
    updated = api_client.patch(detail_url, {"name": "Changed"})
    deleted = api_client.delete(detail_url)
    target.refresh_from_db()

    # Assert
    assert retrieved.status_code == status.HTTP_404_NOT_FOUND
    assert updated.status_code == status.HTTP_404_NOT_FOUND
    assert deleted.status_code == status.HTTP_404_NOT_FOUND
    assert target.name == "Private"


@pytest.mark.django_db
def test_customer_endpoints_require_authentication(api_client: APIClient) -> None:
    # Arrange
    url = reverse("api:customers:customer-list")

    # Act
    response = api_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["error"]["code"]


@pytest.mark.django_db
def test_inactive_account_is_denied(
    api_client: APIClient,
    user_factory: Any,
) -> None:
    # Arrange
    user = user_factory(email="inactive@example.com", account_active=False)
    api_client.force_authenticate(user=user)
    url = reverse("api:customers:customer-list")

    # Act
    response = api_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["error"]["details"]["detail"] == ("The account is not available.")
```

## Alternatives and trade-offs

Permission-only tests can miss an unscoped queryset. Exercising each detail
action proves the object lookup itself is tenant-scoped.

## Required tests

Keep CRUD, authentication, inactive-account, and three cross-account detail
actions mandatory.

## Related standards

- [Customer ViewSet](../views.md)
- [Account scoping](../../api/views.md)
