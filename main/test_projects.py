from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from main.models import Project


class ProjectTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Portfolio Website",
            description="A Django portfolio website.",
            tech_stack="Django, PostgreSQL",
        )

    def test_projects_page_is_accessible(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    def test_editor_gets_edit_form_but_not_project_creation_control(self):
        editor = User.objects.create_user(
            username="project-editor",
            password="EditorPassword123!",
        )
        editor.groups.create(name="Editor")
        self.client.login(
            username="project-editor",
            password="EditorPassword123!",
        )

        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, 'data-editor="true"')
        self.assertContains(response, 'id="add-project-modal"')
        self.assertNotContains(response, 'id="add-project-button"')

    def test_projects_json_returns_project_data(self):
        response = self.client.get(reverse("main:get_projects_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "pk": str(self.project.id),
                    "fields": {
                        "title": self.project.title,
                        "description": self.project.description,
                        "tech_stack": self.project.tech_stack,
                        "project_url": "",
                        "project_image_url": "",
                        "star_count": 0,
                        "is_starred": False,
                    },
                }
            ],
        )

    def test_projects_json_filters_by_title(self):
        Project.objects.create(
            title="Weather App",
            description="A weather app.",
            tech_stack="Python",
        )

        response = self.client.get(
            reverse("main:get_projects_json"),
            {"title": "portfolio"},
        )

        self.assertEqual(
            [item["fields"]["title"] for item in response.json()],
            ["Portfolio Website"],
        )

    def test_anonymous_user_cannot_create_project(self):
        response = self.client.post(
            reverse("main:create_project_ajax"),
            {
                "title": "New Project",
                "description": "Project description",
                "tech_stack": "Django",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Project.objects.filter(title="New Project").exists())

    def test_regular_user_cannot_create_project(self):
        User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )
        self.client.login(username="testuser", password="TestPassword123!")

        response = self.client.post(
            reverse("main:create_project_ajax"),
            {
                "title": "New Project",
                "description": "Project description",
                "tech_stack": "Django",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Project.objects.filter(title="New Project").exists())

    def test_superuser_can_create_project(self):
        User.objects.create_superuser(
            username="admin",
            password="AdminPassword123!",
            email="admin@example.com",
        )
        self.client.login(username="admin", password="AdminPassword123!")

        response = self.client.post(
            reverse("main:create_project_ajax"),
            {
                "title": "New Project",
                "description": "Project description",
                "tech_stack": "Django",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Project.objects.filter(
                id=response.json()["pk"],
                title="New Project",
            ).exists()
        )

    def test_invalid_project_data_is_rejected(self):
        User.objects.create_superuser(
            username="admin",
            password="AdminPassword123!",
            email="admin@example.com",
        )
        self.client.login(username="admin", password="AdminPassword123!")

        response = self.client.post(
            reverse("main:create_project_ajax"),
            {"description": "Missing required fields"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.json())

    def test_superuser_can_delete_project(self):
        User.objects.create_superuser(
            username="admin",
            password="AdminPassword123!",
            email="admin@example.com",
        )
        self.client.login(username="admin", password="AdminPassword123!")

        response = self.client.post(
            reverse("main:delete_project", args=[self.project.id])
        )

        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_regular_user_cannot_delete_project(self):
        User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )
        self.client.login(username="testuser", password="TestPassword123!")

        response = self.client.post(
            reverse("main:delete_project", args=[self.project.id])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_authenticated_user_can_star_and_unstar_project(self):
        User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )
        self.client.login(username="testuser", password="TestPassword123!")
        star_url = reverse("main:toggle_project_star", args=[self.project.id])

        star_response = self.client.post(star_url)

        self.assertRedirects(star_response, reverse("main:show_projects"))
        self.assertTrue(self.project.starred_by.filter(username="testuser").exists())

        unstar_response = self.client.post(star_url)

        self.assertRedirects(unstar_response, reverse("main:show_projects"))
        self.assertFalse(self.project.starred_by.filter(username="testuser").exists())

    def test_anonymous_user_cannot_star_project(self):
        response = self.client.post(
            reverse("main:toggle_project_star", args=[self.project.id])
        )

        self.assertRedirects(
            response,
            f"/login/?next=/projects/{self.project.id}/star/",
        )
        self.assertEqual(self.project.starred_by.count(), 0)
