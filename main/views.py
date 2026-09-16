from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.models import Experience, Skill
from main.forms import SkillForm

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
    json_response = get_skills_json(request)

    skills = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    skills = [skill.object for skill in skills]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "skills_list": skills,
        "title_query": title_query,
    }
    return render(request, "skills.html", context)

def create_skill(request):
    form = SkillForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("main:show_skills")

    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "form": form,
    }

    return render(request, "create_skill.html", context)

def get_skills_json(request):
    title_query = request.GET.get("title", "").strip()
    skills = Skill.objects.all()

    if title_query:
        skills = skills.filter(title__icontains=title_query)

    skills_json = serializers.serialize("json", skills)
    return HttpResponse(skills_json, content_type="application/json")

def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)

    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill berhasil dihapus!")
        return redirect("main:show_skills")

    return redirect("main:show_skills")