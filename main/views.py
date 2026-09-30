import datetime
from itertools import groupby

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.models import Experience, Skill
from main.forms import ExperienceForm, SkillForm

def is_editor(user):
    return user.groups.filter(name="Editor").exists()

def show_main(request):
    last_login = request.COOKIES.get(
        "last_login",
        "Belum ada sesi login / Cookie tidak ditemukan"
    )

    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "npm": "2506656936",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada web development."
        ),
        "last_login": last_login,
    }

    return render(request, "index.html", context)


def show_experience(request):
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "title_query": title_query,
        "form": ExperienceForm(),
        "is_editor": is_editor(request.user),
    }
    return render(request, "experience.html", context)

@login_required
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
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

@login_required
def update_experience(request, experience_id):
    if not (request.user.is_superuser or is_editor(request.user)):
        raise PermissionDenied
    
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

@login_required
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")

def get_experiences_json(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    data = []

    for experience in experiences:
        data.append({
            "pk": str(experience.id),
            "fields": {
                "title": experience.title,
                "description": experience.description,
                "category": experience.get_category_display(),
                "thumbnail": experience.thumbnail,
                "started_at": experience.started_at.strftime("%d %b %Y"),
                "ended_at": (
                    experience.ended_at.strftime("%d %b %Y")
                    if experience.ended_at
                    else None
                ),
                "is_ongoing": experience.is_ongoing,
            }
        })

    return JsonResponse(data, safe=False)

@require_POST
def create_experience_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan experience."},
            status=403,
        )

    form = ExperienceForm(request.POST)

    if form.is_valid():
        experience = form.save()

        return JsonResponse(
            {
                "message": "Experience berhasil ditambahkan.",
                "pk": str(experience.id),
            },
            status=201,
        )

    return JsonResponse(
        {"errors": form.errors.get_json_data()},
        status=400,
    )

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

@login_required
def create_skill(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
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

    skills_json = serializers.serialize(
        "json",
        skills,
        use_natural_foreign_keys=True,
    )
    return HttpResponse(skills_json, content_type="application/json")

@login_required
def delete_skill(request, skill_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    skill = get_object_or_404(Skill, pk=skill_id)

    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill berhasil dihapus!")
        return redirect("main:show_skills")

    return redirect("main:show_skills")

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("main:login")

    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "form": form,
    }

    return render(request, "register.html", context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)

        response = redirect("main:show_main")
        response.set_cookie(
            "last_login",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        return response

    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "form": form,
    }

    return render(request, "login.html", context)


def logout_user(request):
    logout(request)

    response = redirect("main:show_main")
    response.delete_cookie("last_login")

    return response

@login_required
def toggle_skill_star(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)

    if skill.starred_by.filter(id=request.user.id).exists():
        skill.starred_by.remove(request.user)
    else:
        skill.starred_by.add(request.user)

    return redirect("main:show_skills")