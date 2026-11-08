import uuid

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience, Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner",
            password="test-password",
            email="owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="visitor",
            password="test-password",
        )
        self.project = Project.objects.create(
            title="Portfolio",
            description="My website",
            tech_stack="Django",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse(
            "api:project-detail",
            args=[self.project.id],
        )
        self.star_url = reverse(
            "api:project-star",
            args=[self.project.id],
        )
        self.payload = {
            "title": "New project",
            "description": "A useful app",
            "tech_stack": "Python",
            "project_url": "https://example.com/",
            "project_image_url": "",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(
            self.client.get(self.detail_url).status_code,
            status.HTTP_200_OK,
        )

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(self.list_url, {"title": "not-found"})

        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])

        self.assertEqual(
            self.client.get(url).status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(
                    self.list_url,
                    self.payload,
                    format="json",
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(
                    self.detail_url,
                    {"title": "Changed"},
                    format="json",
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(self.detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )

        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.list_url,
            self.payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        invalid_inputs = [
            ({"title": " "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
        ]

        for changes, field in invalid_inputs:
            response = self.client.post(
                self.list_url,
                {**self.payload, **changes},
                format="json",
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
            )
            self.assertIn(field, response.data)

        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self.detail_url,
            {"title": "Changed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Changed")
        self.assertEqual(self.project.description, "My website")

        response = self.client.put(
            self.detail_url,
            {"title": "Incomplete"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(
            self.detail_url,
            self.payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(
            self.client.post(self.star_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)

        response = self.client.post(self.star_url)

        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "star_count": 99,
                "is_starred": True,
                "starred_by_names": "forged",
                "starred_by": [self.visitor.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")

    def test_editor_can_update_projects_but_cannot_create_or_delete(self):
        editor = User.objects.create_user(
            username="project-editor",
            password="test-password",
        )
        editor.groups.create(name="Editor")
        self.client.force_authenticate(user=editor)

        update_response = self.client.patch(
            self.detail_url,
            {"title": "Changed"},
            format="json",
        )
        create_response = self.client.post(
            self.list_url,
            self.payload,
            format="json",
        )
        delete_response = self.client.delete(self.detail_url)

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Changed")
        self.assertEqual(Project.objects.count(), 1)

    def test_staff_without_editor_role_cannot_update_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.client.force_authenticate(user=self.visitor)

        response = self.client.patch(
            self.detail_url,
            {"title": "Changed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)

        self.assertEqual(
            self.client.delete(self.list_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(
            client.login(username="owner", password="test-password")
        )

        response = client.post(
            self.list_url,
            self.payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value

        response = client.post(
            self.list_url,
            self.payload,
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ExperienceAPIPermissionTest(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="experience-owner",
            password="test-password",
            email="experience-owner@example.com",
        )
        self.editor = User.objects.create_user(
            username="experience-editor",
            password="test-password",
        )
        self.editor.groups.create(name="Editor")
        self.visitor = User.objects.create_user(
            username="experience-visitor",
            password="test-password",
        )
        self.experience = Experience.objects.create(
            title="Teaching Assistant",
            description="Supporting students.",
            category="part-time",
            started_at="2026-01-01",
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse(
            "api:experience-detail",
            args=[self.experience.id],
        )
        self.payload = {
            "title": "Research Assistant",
            "description": "Working on a research project.",
            "category": "research",
            "started_at": "2026-02-01",
            "ended_at": "2026-10-01",
            "thumbnail": "",
        }

    def test_experience_list_and_detail_are_public(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.experience.id))
        self.assertTrue(response.data[0]["is_ongoing"])
        self.assertEqual(
            self.client.get(self.detail_url).status_code,
            status.HTTP_200_OK,
        )

    def test_editor_can_update_experience(self):
        self.client.force_authenticate(user=self.editor)

        response = self.client.patch(
            self.detail_url,
            {"title": "Updated Experience"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Updated Experience")

    def test_regular_user_cannot_update_experience(self):
        self.client.force_authenticate(user=self.visitor)

        response = self.client.patch(
            self.detail_url,
            {"title": "Unauthorized Update"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Teaching Assistant")

    def test_editor_cannot_create_or_delete_experience(self):
        self.client.force_authenticate(user=self.editor)

        create_response = self.client.post(
            self.list_url,
            self.payload,
            format="json",
        )
        delete_response = self.client.delete(self.detail_url)

        self.assertEqual(
            create_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            delete_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(Experience.objects.count(), 1)

    def test_owner_can_create_and_delete_experience(self):
        self.client.force_authenticate(user=self.owner)

        create_response = self.client.post(
            self.list_url,
            self.payload,
            format="json",
        )

        self.assertEqual(
            create_response.status_code,
            status.HTTP_201_CREATED,
        )
        created_id = create_response.data["id"]
        created_url = reverse("api:experience-detail", args=[created_id])

        delete_response = self.client.delete(created_url)

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertEqual(delete_response.content, b"")
        self.assertFalse(Experience.objects.filter(pk=created_id).exists())

    def test_guest_cannot_write_experience(self):
        create_response = self.client.post(
            self.list_url,
            self.payload,
            format="json",
        )
        update_response = self.client.patch(
            self.detail_url,
            {"title": "Unauthorized Update"},
            format="json",
        )

        self.assertEqual(
            create_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            update_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(Experience.objects.count(), 1)
