from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from main.models import Skill


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
        response = self.client.get(reverse("main:get_skills_json"))

        self.assertEqual(response.status_code, 200)
        fields = response.json()[0]["fields"]
        self.assertEqual(fields["title"], self.skill.title)
        self.assertEqual(fields["description"], self.skill.description)
        self.assertEqual(fields["category"], self.skill.category)

    def test_empty_skills_json(self):
        Skill.objects.all().delete()
        response = self.client.get(reverse("main:get_skills_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_editor_can_update_but_cannot_create_or_delete_skills(self):
        editor = User.objects.create_user(
            username="skill-editor",
            password="EditorPassword123!",
        )
        editor.groups.create(name="Editor")
        self.client.login(
            username="skill-editor",
            password="EditorPassword123!",
        )

        page_response = self.client.get(reverse("main:show_skills"))
        self.assertContains(page_response, 'data-editor="true"')
        self.assertContains(page_response, 'id="add-skill-modal"')
        self.assertNotContains(page_response, 'id="add-skill-button"')

        update_response = self.client.post(
            reverse("main:update_skill_ajax", args=[self.skill.id]),
            {
                "title": "Updated Skill",
                "description": "Updated description.",
                "category": "Backend",
            },
        )
        create_response = self.client.post(
            reverse("main:create_skill_ajax"),
            {
                "title": "New Skill",
                "description": "New description.",
                "category": "Backend",
            },
        )
        delete_response = self.client.post(
            reverse("main:delete_skill", args=[self.skill.id]),
        )

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(create_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.title, "Updated Skill")
        self.assertEqual(Skill.objects.count(), 1)
