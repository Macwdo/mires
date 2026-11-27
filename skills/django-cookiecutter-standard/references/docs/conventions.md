# Conventions

## Purpose and when to use it

These conventions keep ordinary Django code explicit and reviewable.

## Responsibilities and invariants

- Models declare fields and relations; they do not carry business-rule validation.
- Serializers validate and represent API data; they do not orchestrate side effects. Cross-field and business-rule validation belongs here, not on the model.
- ViewSets authorize, scope, validate, and delegate; see [view patterns](view-patterns.md) for choosing between `ModelViewSet`, `GenericViewSet` with mixins, and plain `APIView`.
- Services accept keyword-only inputs and own transactions or effects.
- Selectors return typed QuerySets and own reusable read composition for same-app callers. A service or selector consumed by another app returns Pydantic DTOs from that app's `dtos.py` instead; the consuming app imports only DTOs and functions, never models or querysets, from the app it depends on.
- Migrations are committed, forward-only history; never edit an applied migration.
- URLs use stable nouns and trailing slashes.
- Timestamps are UTC and generated with timezone-aware APIs.
- Logs are structured and must not contain access tokens, passwords, file contents, or provider prompts.

Ruff formats and lints. `ty` checks useful Python surfaces, but Django's dynamic model fields, managers, reverse relations, and some DRF generics remain imperfectly modeled. Prefer a narrow line-level suppression with a reason plus runtime tests; blanket package or project ignores are prohibited.

## Anti-patterns to avoid

Do not use `CheckConstraint` or a model `clean()` override to validate business rules such as "exactly one of these fields must be set." These are database/model-level mechanisms that duplicate logic which belongs in the serializer and produce harder-to-read errors for API consumers.

Avoid this:

```python
class TransactionLink(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name="link")
    expense = models.ForeignKey("expenses.Expense", on_delete=models.CASCADE, null=True, blank=True)
    installment = models.ForeignKey("payments.Installment", on_delete=models.CASCADE, null=True, blank=True)
    payment = models.ForeignKey("expenses.Payment", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints: ClassVar[list] = [
            models.CheckConstraint(
                condition=(
                    Q(expense__isnull=False, installment__isnull=True, payment__isnull=True)
                    | Q(expense__isnull=True, installment__isnull=False, payment__isnull=True)
                    | Q(expense__isnull=True, installment__isnull=True, payment__isnull=False)
                ),
                name="ck_transaction_links_exactly_one_target",
            ),
        ]
```

Avoid this too:

```python
class TransactionLink(models.Model):
    ...

    def clean(self) -> None:
        super().clean()
        errors = {}
        target_ids = [self.expense_id, self.installment_id, self.payment_id]
        if len([target_id for target_id in target_ids if target_id is not None]) != 1:
            errors["non_field_errors"] = "A transaction link must have exactly one target."
        if self.expense_id is not None and self.expense.type == ExpenseType.INSTALLMENT:
            errors["expense"] = "Installment expenses must be linked through an installment."
        if self.expense_id is not None and self.expense.type == ExpenseType.RECURRENT:
            errors["expense"] = "Recurrent expenses must be linked through a payment."
        if self.payment_id is not None and self.payment.expense.type != ExpenseType.RECURRENT:
            errors["payment"] = "Only recurring payments can be linked to a transaction."
        if errors:
            raise ValidationError(errors)
```

Put this validation in the serializer's `validate()` instead. Only use `CheckConstraint` or `full_clean()`/`clean()` when explicitly requested, and write them deliberately rather than by default.

Do this instead — the model declares fields only:

```python
class TransactionLink(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name="link")
    expense = models.ForeignKey("expenses.Expense", on_delete=models.CASCADE, null=True, blank=True)
    installment = models.ForeignKey("payments.Installment", on_delete=models.CASCADE, null=True, blank=True)
    payment = models.ForeignKey("expenses.Payment", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "transaction_links"
```

And the serializer owns the validation:

```python
class TransactionLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionLink
        fields = ["id", "transaction", "expense", "installment", "payment"]

    def validate(self, attrs):
        targets = [attrs.get("expense"), attrs.get("installment"), attrs.get("payment")]
        if len([target for target in targets if target is not None]) != 1:
            raise serializers.ValidationError("A transaction link must have exactly one target.")

        expense = attrs.get("expense")
        if expense is not None and expense.type == ExpenseType.INSTALLMENT:
            raise serializers.ValidationError({"expense": "Installment expenses must be linked through an installment."})
        if expense is not None and expense.type == ExpenseType.RECURRENT:
            raise serializers.ValidationError({"expense": "Recurrent expenses must be linked through a payment."})

        payment = attrs.get("payment")
        if payment is not None and payment.expense.type != ExpenseType.RECURRENT:
            raise serializers.ValidationError({"payment": "Only recurring payments can be linked to a transaction."})

        return attrs
```

## Alternatives and trade-offs

Direct ORM code is preferred until query reuse or complexity is demonstrated. A selector is not a generic data-access layer. A service is not required merely to call `Model.objects.create()`.

## Required tests

Run Ruff, `ty`, pytest, coverage, Django checks, and migration drift checks. See [testing](testing.md).
