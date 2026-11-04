from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from main.models import Experience

class ExperienceTest(TestCase):

    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
            started_at="2026-01-01",
        )

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(
            response,
            f'href="{reverse("main:show_main")}"'
        )

    def test_experience_is_not_shown_on_main_page(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertNotContains(response, self.experience.title)

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(
            response,
            "Belum ada pengalaman yang ditambahkan."
        )

    def test_completed_experience(self):
        self.experience.ended_at = date(2026, 9, 28)
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

    def test_create_experience_requires_login(self):
        response = self.client.get(
            reverse("main:create_experience")
        )

        self.assertRedirects(
            response,
            "/login/?next=/experience/add/",
        )

    def test_regular_user_cannot_create_experience(self):
        User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        self.client.login(
            username="testuser",
            password="TestPassword123!",
        )

        response = self.client.get(
            reverse("main:create_experience")
        )

        self.assertEqual(response.status_code, 403)

    def test_superuser_can_create_experience(self):
        User.objects.create_superuser(
            username="admin",
            password="AdminPassword123!",
            email="admin@example.com",
        )

        self.client.login(
            username="admin",
            password="AdminPassword123!",
        )

        response = self.client.get(
            reverse("main:create_experience")
        )

        self.assertEqual(response.status_code, 200)

    def test_regular_user_cannot_update_experience(self):
        user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        self.client.login(
            username="testuser",
            password="TestPassword123!",
        )

        experience = Experience.objects.create(
            title="Test Experience",
            description="Test description",
            category="part-time",
            started_at="2026-01-01",
        )

        response = self.client.get(
            reverse(
                "main:update_experience",
                args=[experience.id],
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_regular_user_cannot_delete_experience(self):
        user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        self.client.login(
            username="testuser",
            password="TestPassword123!",
        )

        experience = Experience.objects.create(
            title="Test Experience",
            description="Test description",
            category="part-time",
            started_at="2026-01-01",
        )

        response = self.client.post(
            reverse(
                "main:delete_experience",
                args=[experience.id],
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_editor_can_update_experience(self):
        user = User.objects.create_user(
            username="editor",
            password="EditorPassword123!",
        )

        user.groups.create(name="Editor")

        self.client.login(
            username="editor",
            password="EditorPassword123!",
        )

        experience = Experience.objects.create(
            title="Test Experience",
            description="Test description",
            category="part-time",
            started_at="2026-01-01",
        )

        response = self.client.get(
            reverse(
                "main:update_experience",
                args=[experience.id],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_experience.html")

    def test_editor_cannot_create_experience(self):
        user = User.objects.create_user(
            username="editor",
            password="EditorPassword123!",
        )

        user.groups.create(name="Editor")

        self.client.login(
            username="editor",
            password="EditorPassword123!",
        )

        response = self.client.get(
            reverse("main:create_experience")
        )

        self.assertEqual(response.status_code, 403)

    def test_editor_cannot_delete_experience(self):
        user = User.objects.create_user(
            username="editor",
            password="EditorPassword123!",
        )

        user.groups.create(name="Editor")

        self.client.login(
            username="editor",
            password="EditorPassword123!",
        )

        experience = Experience.objects.create(
            title="Test Experience",
            description="Test description",
            category="part-time",
            started_at="2026-01-01",
        )

        response = self.client.post(
            reverse(
                "main:delete_experience",
                args=[experience.id],
            )
        )

        self.assertEqual(response.status_code, 403)

        self.assertTrue(
            Experience.objects.filter(
                id=experience.id
            ).exists()
        )
