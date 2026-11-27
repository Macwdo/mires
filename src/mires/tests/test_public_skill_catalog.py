from __future__ import annotations

import re
import unittest
from pathlib import Path

from mires.frontmatter import read_frontmatter
from mires.state import load_state

ROOT = Path(__file__).resolve().parents[3]


class PublicSkillCatalogTests(unittest.TestCase):
    def test_public_skills_are_self_contained_packages(self) -> None:
        state = load_state(ROOT)
        public_skills = {skill.slug for skill in state.skills if skill.visibility == "public"}

        for name in sorted(public_skills):
            with self.subTest(name=name):
                package = ROOT / "skills" / name
                skill_path = package / "SKILL.md"
                metadata_path = package / "agents" / "openai.yaml"
                text = skill_path.read_text()

                self.assertEqual(read_frontmatter(skill_path)["name"], name)
                self.assertTrue(metadata_path.exists())
                self.assertIn(f"${name}", metadata_path.read_text())
                nested_skills = [path for path in package.rglob("SKILL.md") if path != skill_path]
                self.assertEqual(nested_skills, [])
                non_markdown = (
                    [path for path in (package / "references").rglob("*") if path.is_file() and path.suffix != ".md"]
                    if (package / "references").exists()
                    else []
                )
                self.assertEqual(non_markdown, [])
                self.assertIn("## Snippet-Driven Implementation", text)
                self.assertRegex(text, r"## Snippet-Driven Implementation\n\nAlways ")
                self.assertRegex(text, r"```[a-zA-Z0-9_-]*\n")
                self.assertNotIn("dict[str, Any]", text)
                self.assertNotIn("Dict[str, Any]", text)
                self.assertNotIn("Mapping[str, Any]", text)

    def test_catalog_exposes_the_intended_granular_skills(self) -> None:
        state = load_state(ROOT)
        declared_public = {skill.slug for skill in state.skills if skill.visibility == "public"}

        self.assertEqual(
            declared_public,
            {
                "mires",
                "mires-python",
                "mires-python-django",
                "mires-python-langchain",
                "mires-react",
                "mires-next",
                "mires-typescript",
                "django-cookiecutter-standard",
            },
        )

    def test_cross_skill_references_resolve_to_declared_skills(self) -> None:
        state = load_state(ROOT)
        declared = {skill.slug for skill in state.skills}

        for skill in state.skills:
            text = (ROOT / "skills" / skill.slug / "SKILL.md").read_text()
            referenced = set(re.findall(r"\$(mires(?:-[a-z0-9]+)*)", text))
            with self.subTest(skill=skill.slug):
                self.assertTrue(referenced <= declared, referenced - declared)

    def test_django_skill_has_connected_relational_drf_snippets(self) -> None:
        text = (ROOT / "skills" / "mires-python-django" / "SKILL.md").read_text()

        required_shapes = {
            "models.OneToOneField",
            "models.ForeignKey",
            '"customer_profile": {',
            '"customer_profile_id": 42',
            'source="customer_profile"',
            "class ContextPrimaryKeyRelatedField(",
            "Generic[ModelT]",
            "ContextQueryset = Callable[[SerializerContext], QuerySet[ModelT]]",
            "def get_queryset(self) -> QuerySet[ModelT] | None",
            "class SerializerContext(TypedDict, total=False)",
            "queryset=billing_profiles_for_context",
            "class InvoiceCreateDTO(BaseModel)",
            "model_config = ConfigDict(arbitrary_types_allowed=True)",
            "**data.model_dump()",
            "customer_create(owner=request.user, **validated_data)",
            "**input_serializer.validated_data",
            "notification_service: ExampleNotificationService",
            "def __init__(self, *, notification_service: ExampleNotificationService) -> None",
            "class InvoiceWriteSerializer(serializers.ModelSerializer)",
            "Provide exactly one of customer_profile or customer_profile_id.",
            "class CustomerReadSerializer(serializers.ModelSerializer)",
            "class CustomerCreateSerializer(serializers.ModelSerializer)",
            "AddressSerializer(many=True",
            "@transaction.atomic",
            "class CustomerViewSet(viewsets.ModelViewSet)",
            '.select_related("profile")',
            '.prefetch_related("addresses")',
            'router.register("customers", CustomerViewSet, basename="customer")',
            "from rest_framework_nested.routers import NestedSimpleRouter",
            'NestedSimpleRouter(router, "customers", lookup="customer")',
            'customers_router.register("addresses", AddressViewSet, basename="customer-address")',
            "class AddressViewSet(viewsets.ModelViewSet)",
            'self.kwargs["customer_pk"]',
            'reverse("customer-address-list"',
            "def given_a_customer(",
            "def given_an_address(",
            "from .helpers import given_a_customer, given_an_address",
            "# given",
            "# when",
            "# then",
        }

        missing = {shape for shape in required_shapes if shape not in text}
        self.assertFalse(missing, missing)
        self.assertNotIn("_ModelT", text)
        self.assertNotIn("def __init__(self, *, account)", text)
        self.assertNotIn("CustomerCreateDTO(name=validated_data", text)
        self.assertNotIn("class InvoiceByProfileIdSerializer", text)
        self.assertNotIn("UserScopedPrimaryKeyRelatedField", text)
        self.assertNotIn('user_lookup="owner"', text)
        self.assertNotIn(
            "def test_address_list_is_scoped_to_the_parent_customer(api_client, user):\n"
            "    api_client.force_authenticate(user)\n"
            "    customer = Customer.objects.create(",
            text,
        )

    def test_python_skills_have_connected_direct_upload_snippets(self) -> None:
        python_text = (ROOT / "skills" / "mires-python" / "SKILL.md").read_text()
        django_text = (ROOT / "skills" / "mires-python-django" / "SKILL.md").read_text()

        python_shapes = {
            "class PresignedPost(TypedDict)",
            "def generate_upload_presigned_post(",
            "s3_client.generate_presigned_post(",
            '["content-length-range", expected_size, expected_size]',
        }
        django_shapes = {
            "### Direct S3 Upload Start And Confirm",
            "def file_upload_start(",
            "def file_upload_confirm(",
            'object_key = f"files/{account.pk}/{uuid4().hex}{suffix}"',
            "file.upload_finished_at = timezone.now()",
            "class FileUploadConfirmSerializer(serializers.Serializer)",
            "file_id = serializers.IntegerField(min_value=1)",
            "permission_classes = [permissions.IsAuthenticated]",
            "class FileViewSet(viewsets.GenericViewSet)",
            '@action(detail=False, methods=["post"], url_path="upload-start")',
            '@action(detail=False, methods=["post"], url_path="confirm-upload")',
            "file = get_object_or_404(",
            'pk=input_serializer.validated_data["file_id"]',
            "confirmed = file_upload_confirm(file=file)",
            "test_file_upload_confirm_persists_timestamp",
        }

        missing_python_shapes = {shape for shape in python_shapes if shape not in python_text}
        missing_django_shapes = {shape for shape in django_shapes if shape not in django_text}

        self.assertFalse(missing_python_shapes, missing_python_shapes)
        self.assertFalse(missing_django_shapes, missing_django_shapes)

        direct_upload_text = django_text.split("### Direct S3 Upload Start And Confirm", 1)[1].split(
            "## Celery And Background Work",
            1,
        )[0]
        self.assertNotIn("head_object", direct_upload_text)
        self.assertNotIn("copy_object", direct_upload_text)

    def test_python_skills_share_the_uv_ruff_ty_toolchain(self) -> None:
        required = {
            "uv sync",
            "uv run ruff format --check",
            "uv run ruff check",
            "uv run ty check",
            "uv run pytest",
        }

        for slug in ("mires-python", "mires-python-django", "mires-python-langchain"):
            text = (ROOT / "skills" / slug / "SKILL.md").read_text()
            with self.subTest(skill=slug):
                missing = {command for command in required if command not in text}
                self.assertFalse(missing, missing)

        pyproject = (ROOT / "pyproject.toml").read_text()
        self.assertIn('"ty>=', pyproject)
        self.assertIn("[tool.ty.src]", pyproject)
        self.assertEqual((ROOT / ".python-version").read_text().strip(), "3.14")


if __name__ == "__main__":
    unittest.main()
