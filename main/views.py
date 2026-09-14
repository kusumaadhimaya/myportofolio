from django.shortcuts import render

from main.models import Experience, Skill

def show_main(request):
    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "npm": "2506656936",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada web development."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_skills(request):
    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "skills_list": Skill.objects.all(),
    }
    return render(request, "skills.html", context)