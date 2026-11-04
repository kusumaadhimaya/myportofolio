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
