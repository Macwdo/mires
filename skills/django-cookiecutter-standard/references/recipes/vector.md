# Tenant-Scoped pgvector Search

## Purpose and when to use it

Use pgvector when semantic search belongs beside relational Django data and the
expected scale fits PostgreSQL operations. Documents and chunks remain normal
account-owned rows; vector distance only changes ranking.

## When not to use it

Use PostgreSQL full-text search for exact terminology and filters that do not
benefit from semantic similarity. Choose a dedicated vector system when
measured corpus size, recall, ingestion throughput, or independent scaling
requires one. Do not add embeddings without an evaluation set.

## Responsibilities and invariants

- The embedding model and database column use one explicit dimension: 1536.
- Ingestion validates every vector before persistence.
- Document and chunk rows both carry the owning account.
- Similarity queries scope the account before ordering by distance.
- The HNSW index uses cosine operator classes matching `CosineDistance`.
- Changing models or dimensions requires a versioned re-embedding migration.
- Raw document text is not sent to a provider without the product's data policy.

## Complete canonical artifacts

<!-- artifact: src/apps/documents/apps.py; profiles: vector-pgvector,vector-ai,full -->
```python
from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.documents"
```

<!-- artifact: src/apps/documents/migrations/__init__.py; profiles: vector-pgvector,vector-ai,full -->
```python
"""Documents schema history."""
```

<!-- artifact: src/apps/documents/migrations/0001_initial.py; profiles: vector-pgvector,vector-ai,full -->
```python
import uuid

import django.db.models.deletion
from django.db import migrations, models
from pgvector.django import HnswIndex, VectorExtension, VectorField


def create_hnsw_index(apps, schema_editor) -> None:
    if schema_editor.connection.vendor != "postgresql":
        return
    table = schema_editor.quote_name("documents_documentchunk")
    index = schema_editor.quote_name("chunk_embedding_hnsw_idx")
    schema_editor.execute(
        f"CREATE INDEX {index} ON {table} "
        "USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )


def drop_hnsw_index(apps, schema_editor) -> None:
    if schema_editor.connection.vendor != "postgresql":
        return
    index = schema_editor.quote_name("chunk_embedding_hnsw_idx")
    schema_editor.execute(f"DROP INDEX IF EXISTS {index}")


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("account", "0002_initial"),
    ]

    operations = [
        VectorExtension(),
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("source_key", models.CharField(max_length=255)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(app_label)s_%(class)s_items",
                        to="account.account",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("account", "source_key"),
                        name="document_unique_account_source",
                    )
                ]
            },
        ),
        migrations.CreateModel(
            name="DocumentChunk",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("ordinal", models.PositiveIntegerField()),
                ("content", models.TextField()),
                ("embedding_model", models.CharField(max_length=80)),
                ("embedding", VectorField(dimensions=1536)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(app_label)s_%(class)s_items",
                        to="account.account",
                    ),
                ),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chunks",
                        to="documents.document",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["account", "document", "ordinal"],
                        name="chunk_account_document_idx",
                    ),
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("document", "ordinal"),
                        name="chunk_unique_document_ordinal",
                    )
                ],
            },
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    create_hnsw_index,
                    reverse_code=drop_hnsw_index,
                )
            ],
            state_operations=[
                migrations.AddIndex(
                    model_name="documentchunk",
                    index=HnswIndex(
                        ef_construction=64,
                        fields=["embedding"],
                        m=16,
                        name="chunk_embedding_hnsw_idx",
                        opclasses=("vector_cosine_ops",),
                    ),
                )
            ],
        ),
    ]
```

<!-- artifact: src/apps/documents/models.py; profiles: vector-pgvector,vector-ai,full -->
```python
from __future__ import annotations

import uuid
from typing import ClassVar

from django.db import models
from pgvector.django import HnswIndex, VectorField

from apps.account.models import AccountOwnedModel

EMBEDDING_DIMENSIONS = 1536


class Document(AccountOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    source_key = models.CharField(max_length=255)
    objects: models.Manager[Document] = models.Manager()

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=("account", "source_key"),
                name="document_unique_account_source",
            )
        ]


class DocumentChunk(AccountOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks",
    )
    ordinal = models.PositiveIntegerField()
    content = models.TextField()
    embedding_model = models.CharField(max_length=80)
    embedding = VectorField(dimensions=EMBEDDING_DIMENSIONS)
    objects: models.Manager[DocumentChunk] = models.Manager()

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=("document", "ordinal"),
                name="chunk_unique_document_ordinal",
            )
        ]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=("account", "document", "ordinal"),
                name="chunk_account_document_idx",
            ),
            HnswIndex(
                name="chunk_embedding_hnsw_idx",
                fields=("embedding",),
                m=16,
                ef_construction=64,
                opclasses=("vector_cosine_ops",),
            ),
        ]
```

<!-- artifact: src/apps/documents/services.py; profiles: vector-pgvector,vector-ai,full -->
```python
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.account.models import Account
from apps.documents.models import (
    EMBEDDING_DIMENSIONS,
    Document,
    DocumentChunk,
)


class EmbeddingProvider(Protocol):
    model_name: str

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        pass


def validate_embedding(vector: Sequence[float]) -> list[float]:
    if len(vector) != EMBEDDING_DIMENSIONS:
        raise ValidationError(
            {"embedding": (f"Expected {EMBEDDING_DIMENSIONS} values, got {len(vector)}.")}
        )
    return [float(value) for value in vector]


@transaction.atomic
def replace_document_chunks(
    *,
    account: Account,
    document: Document,
    contents: Sequence[str],
    provider: EmbeddingProvider,
) -> list[DocumentChunk]:
    if (
        document.account_id  # ty: ignore[unresolved-attribute]  # Django creates the FK id descriptor.
        != account.pk
    ):
        raise ValidationError({"document": "Document does not belong to the account."})
    if not contents or any(not content.strip() for content in contents):
        raise ValidationError({"contents": "Every chunk must contain text."})

    embeddings = provider.embed(contents)
    if len(embeddings) != len(contents):
        raise ValidationError({"embeddings": "Provider returned an unexpected number of vectors."})

    DocumentChunk.objects.filter(account=account, document=document).delete()
    chunks = [
        DocumentChunk(
            account=account,
            document=document,
            ordinal=ordinal,
            content=content,
            embedding_model=provider.model_name,
            embedding=validate_embedding(embedding),
        )
        for ordinal, (content, embedding) in enumerate(zip(contents, embeddings, strict=True))
    ]
    return DocumentChunk.objects.bulk_create(chunks)
```

<!-- artifact: src/apps/documents/selectors.py; profiles: vector-pgvector,vector-ai,full -->
```python
from __future__ import annotations

from collections.abc import Sequence

from django.db.models import QuerySet
from pgvector.django import CosineDistance

from apps.account.models import Account
from apps.documents.models import DocumentChunk
from apps.documents.services import validate_embedding


def similar_chunks(
    *,
    account: Account,
    query_embedding: Sequence[float],
    limit: int = 10,
) -> QuerySet[DocumentChunk]:
    bounded_limit = max(1, min(limit, 50))
    vector = validate_embedding(query_embedding)
    return (
        DocumentChunk.objects.filter(account=account)
        .select_related("document")
        .annotate(distance=CosineDistance("embedding", vector))
        .order_by("distance", "id")[:bounded_limit]
    )
```

<!-- artifact: src/apps/documents/tests/test_search.py; profiles: vector-pgvector,vector-ai,full -->
```python
from collections.abc import Sequence

import pytest
from django.core.exceptions import ValidationError
from django.db import connection

from apps.account.models import Account
from apps.authentication.models import User
from apps.documents.models import EMBEDDING_DIMENSIONS, Document
from apps.documents.selectors import similar_chunks
from apps.documents.services import replace_document_chunks, validate_embedding


class DeterministicEmbeddings:
    model_name = "test-embedding-1536"

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for index, _text in enumerate(texts):
            vector = [0.0] * EMBEDDING_DIMENSIONS
            vector[index % EMBEDDING_DIMENSIONS] = 1.0
            vectors.append(vector)
        return vectors


@pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="pgvector cosine distance requires PostgreSQL",
)
@pytest.mark.django_db
def test_search_never_returns_another_accounts_chunks() -> None:
    # Arrange
    user = User.objects.create_user(email="vectors@example.test", password="safe-pass-123")
    account = Account.objects.create(user=user)
    other_user = User.objects.create_user(
        email="other-vectors@example.test",
        password="safe-pass-123",
    )
    other_account = Account.objects.create(user=other_user)
    document = Document.objects.create(
        account=account,
        title="Guide",
        source_key="guide",
    )
    other_document = Document.objects.create(
        account=other_account,
        title="Private",
        source_key="private",
    )
    provider = DeterministicEmbeddings()
    replace_document_chunks(
        account=account,
        document=document,
        contents=["customer account guidance"],
        provider=provider,
    )
    replace_document_chunks(
        account=other_account,
        document=other_document,
        contents=["another account content"],
        provider=provider,
    )

    # Act
    result = list(
        similar_chunks(
            account=account,
            query_embedding=provider.embed(["customer"])[0],
        )
    )

    # Assert
    assert len(result) == 1
    assert result[0].account_id == account.pk


def test_embedding_dimension_is_explicit() -> None:
    # Arrange
    embedding = [0.0, 1.0]

    # Assert
    with pytest.raises(ValidationError):
        validate_embedding(embedding)
```

<!-- dependency-fragment: pyproject.toml#dependencies; modules: vector-pgvector -->
```toml
  "pgvector==0.5.0",
```

## Alternatives and trade-offs

HNSW offers fast approximate search and good query latency at the cost of more
memory and slower writes. IVFFlat needs representative training data and
careful list and probe tuning. Exact search is a useful correctness baseline
for small corpora and recall evaluations. Hybrid semantic plus PostgreSQL
full-text ranking often outperforms either signal alone.

## Required tests

Run against the `pgvector` extension, not SQLite. Test dimension rejection,
cross-account denial, stable tie ordering, empty corpora, maximum result limits,
transaction rollback during replacement, index creation, query plans at
representative scale, and measured approximate recall against exact cosine
search.

## Related standards

- [OpenAI and Deep Agents](openai-deep-agents.md)
- [Architecture](../docs/architecture.md)
- [Testing](../docs/testing.md)
