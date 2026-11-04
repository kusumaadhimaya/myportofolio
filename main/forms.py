from django.core.exceptions import ValidationError
from django.forms import DateInput, ModelForm, TextInput, Textarea
from django.utils.html import strip_tags

from main.models import Experience, Project, Skill


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
                    "placeholder": "misal: Python, Java, ...",
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
                    "placeholder": "misal: Coding, Video Editing, ...",
                    "maxlength": 255,
                }
            ),
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama skill tidak boleh hanya berisi tag HTML.")
        return title

    def clean_category(self):
        return strip_tags(self.cleaned_data["category"]).strip()

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()


class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
            "started_at",
            "ended_at",
        ]
        labels = {
            "title": "Judul",
            "description": "Deskripsi",
            "category": "Kategori",
            "thumbnail": "Thumbnail URL",
            "started_at": "Mulai",
            "ended_at": "Selesai",
        }
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": (
                        "misal: Staff at Compfest, Intern in Ristek, "
                        "Mentor at DDP-0, ..."
                    ),
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Jelaskan pengalaman kamu...",
                    "rows": 5,
                }
            ),
            "thumbnail": TextInput(
                attrs={
                    "placeholder": "https://example.com/image.jpg",
                }
            ),
            "started_at": DateInput(attrs={"type": "date"}),
            "ended_at": DateInput(attrs={"type": "date"}),
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Judul experience tidak boleh hanya berisi tag HTML.")
        return title

    def clean_category(self):
        return strip_tags(self.cleaned_data["category"]).strip()

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
        ]
        labels = {
            "title": "Nama Project",
            "description": "Deskripsi",
            "tech_stack": "Teknologi yang digunakan",
            "project_url": "Link Project",
            "project_image_url": "URL Gambar",
        }
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "misal: Aplikasi Jadwal",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan tentang project ini...",
                    "rows": 4,
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "misal: Django, PostgreSQL",
                    "maxlength": 255,
                }
            ),
            "project_url": TextInput(
                attrs={"placeholder": "https://example.com/"}
            ),
            "project_image_url": TextInput(
                attrs={"placeholder": "https://example.com/image.jpg"}
            ),
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama project tidak boleh hanya berisi tag HTML.")
        return title

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()

    def clean_tech_stack(self):
        return strip_tags(self.cleaned_data["tech_stack"]).strip()
