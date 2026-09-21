from itertools import groupby

from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.models import Experience, Skill
from main.forms import ExperienceForm, SkillForm

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
    title_query = request.GET.get("title", "").strip()

    json_response = get_experiences_json(request)
    experiences = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8")
    )
    experiences = [experience.object for experience in experiences]

    if title_query:
        experiences = [
            experience
            for experience in experiences
            if title_query.lower() in experience.title.lower()
        ]

    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "experience_list": experiences,
        "title_query": title_query,
    }
    return render(request, "experience.html", context)
def create_experience(request):
    form = ExperienceForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("main:show_experience")

    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "form": form,
    }

    return render(request, "create_experience.html", context)

def update_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("main:show_experience")

    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "form": form,
        "experience": experience,
    }

    return render(request, "edit_experience.html", context)

def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")

def get_experiences_json(request):
    experiences = Experience.objects.all()
    experiences_json = serializers.serialize("json", experiences)
    return HttpResponse(experiences_json, content_type="application/json")

def show_skills(request):
    title_query = request.GET.get("title", "").strip()

    skills = Skill.objects.all().order_by("category", "title")

    if title_query:
        skills = skills.filter(title__icontains=title_query)

    grouped_skills = []

    for category, category_skills in groupby(
        skills,
        key=lambda skill: skill.category or "Uncategorized"
    ):
        grouped_skills.append({
            "category": category,
            "skills": list(category_skills),
        })

    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "skills_list": grouped_skills,
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