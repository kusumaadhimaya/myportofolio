from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from main.models import Experience, Skill


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
            started_at="2026-01-01",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(
            response,
            f'href="{reverse("main:show_experience")}"'
        )

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

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

class SkillTest(TestCase):
    def setUp(self):
        self.skill = Skill.objects.create(
            title="Django Web Development",
            description="Membangun aplikasi web dengan framework Django.",
            category="Python, Backend",
        )

    def test_skills_url_is_accessible(self):
        response = self.client.get(reverse("main:show_skills"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "skills.html")

    def test_skills_page_shows_data(self):
        response = self.client.get(reverse("main:show_skills"))

        self.assertContains(response, self.skill.title)
        self.assertContains(response, self.skill.description)
        self.assertContains(response, self.skill.category)

    def test_empty_skills_page(self):
        Skill.objects.all().delete()
        response = self.client.get(reverse("main:show_skills"))

        self.assertContains(
            response,
            "Belum ada skill yang ditambahkan."
        )


class AuthenticationTest(TestCase):
    def test_register_page(self):
        response = self.client.get(reverse("main:register"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

    def test_register_user(self):
        response = self.client.post(
            reverse("main:register"),
            {
                "username": "testuser",
                "password1": "TestPassword123!",
                "password2": "TestPassword123!",
            },
        )

        self.assertRedirects(
            response,
            reverse("main:login"),
        )

        self.assertTrue(
            User.objects.filter(username="testuser").exists()
        )

    def test_login(self):
        User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        response = self.client.post(
            reverse("main:login"),
            {
                "username": "testuser",
                "password": "TestPassword123!",
            },
        )

        self.assertRedirects(
            response,
            reverse("main:show_main"),
        )

    def test_logout(self):
        User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        self.client.login(
            username="testuser",
            password="TestPassword123!",
        )

        response = self.client.get(
            reverse("main:logout")
        )

        self.assertRedirects(
            response,
            reverse("main:show_main"),
        )

    def test_create_skill_requires_login(self):
        response = self.client.get(
            reverse("main:create_skill")
        )

        self.assertRedirects(
            response,
            "/login/?next=/skills/add/",
        )

    def test_create_experience_requires_login(self):
        response = self.client.get(
            reverse("main:create_experience")
        )

        self.assertRedirects(
            response,
            "/login/?next=/experience/add/",
        )

    def test_regular_user_cannot_create_skill(self):
        User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        self.client.login(
            username="testuser",
            password="TestPassword123!",
        )

        response = self.client.get(
            reverse("main:create_skill")
        )

        self.assertEqual(response.status_code, 403)

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

    def test_superuser_can_create_skill(self):
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
            reverse("main:create_skill")
        )

        self.assertEqual(response.status_code, 200)

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

    def test_regular_user_can_star_skill(self):
        skill = Skill.objects.create(
            title="Django",
            description="Django web development",
            category="Python",
        )

        User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        self.client.login(
            username="testuser",
            password="TestPassword123!",
        )

        response = self.client.post(
            reverse(
                "main:toggle_skill_star",
                args=[skill.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("main:show_skills"),
        )

        self.assertTrue(
            skill.starred_by.filter(
                username="testuser"
            ).exists()
        )

    def test_regular_user_can_unstar_skill(self):
        skill = Skill.objects.create(
            title="Django",
            description="Django web development",
            category="Python",
        )

        user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        skill.starred_by.add(user)

        self.client.login(
            username="testuser",
            password="TestPassword123!",
        )

        response = self.client.post(
            reverse(
                "main:toggle_skill_star",
                args=[skill.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("main:show_skills"),
        )

        self.assertFalse(
            skill.starred_by.filter(
                username="testuser"
            ).exists()
        )

    def test_anonymous_user_cannot_star_skill(self):
        skill = Skill.objects.create(
            title="Django",
            description="Django web development",
            category="Python",
        )

        response = self.client.post(
            reverse(
                "main:toggle_skill_star",
                args=[skill.id],
            )
        )

        self.assertRedirects(
            response,
            f"/login/?next=/skills/{skill.id}/star/",
        )

        self.assertEqual(
            skill.starred_by.count(),
            0,
        )

    def test_regular_user_cannot_delete_skill(self):
        skill = Skill.objects.create(
            title="Django",
            description="Django web development",
            category="Python",
        )

        User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        self.client.login(
            username="testuser",
            password="TestPassword123!",
        )

        response = self.client.post(
            reverse(
                "main:delete_skill",
                args=[skill.id],
            )
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Skill.objects.filter(id=skill.id).exists()
        )