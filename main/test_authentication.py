from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from main.models import Skill

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

    def test_editor_can_star_skill(self):
        user = User.objects.create_user(
            username="editor",
            password="EditorPassword123!",
        )

        user.groups.create(name="Editor")

        skill = Skill.objects.create(
            title="Django",
            description="Django development",
            category="Python",
        )

        self.client.login(
            username="editor",
            password="EditorPassword123!",
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
                id=user.id
            ).exists()
        )
