from django.forms import ModelForm, TextInput, Textarea
from main.models import Skill


class SkillForm(ModelForm):
    class Meta:
        model = Skill
        fields = ["title", "description", "category"]
        labels = {
            "title": "Nama Skill",
            "description": "Deskripsi Skill",
            "category": "Kategori",
        }
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "misal: Python",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Jelaskan keahlian atau pengalaman kamu...",
                    "rows": 3,
                }
            ),
            "category": TextInput(
                attrs={
                    "placeholder": "misal: Coding",
                    "maxlength": 255,
                }
            ),
        }