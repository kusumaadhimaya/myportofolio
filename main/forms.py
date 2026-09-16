from django.forms import ModelForm, TextInput, Textarea
from main.models import Skill


class SkillForm(ModelForm):
    class Meta:
        model = Skill
        fields = ["title", "description", "tags"]
        labels = {
            "title": "Nama Skill",
            "description": "Deskripsi Skill",
            "tags": "Tags / Kategori",
        }
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "misal: Web Development",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Jelaskan keahlian atau pengalaman kamu...",
                    "rows": 3,
                }
            ),
            "tags": TextInput(
                attrs={
                    "placeholder": "misal: Django, Python, HTML, CSS",
                    "maxlength": 255,
                }
            ),
        }