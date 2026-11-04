from itertools import groupby

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import SkillForm
from main.models import Skill


def show_skills(request):
    title_query = request.GET.get("title", "").strip()
    skills = Skill.objects.all().order_by("category", "title")
    if title_query:
        skills = skills.filter(title__icontains=title_query)

    grouped_skills = []
    for category, category_skills in groupby(
        skills,
        key=lambda skill: skill.category or "Uncategorized",
    ):
        grouped_skills.append({
            "category": category,
            "skills": list(category_skills),
        })

    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "skills_list": grouped_skills,
        "title_query": title_query,
        "form": SkillForm(),
    }
    return render(request, "skills.html", context)


@login_required
def create_skill(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = SkillForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("main:show_skills")

    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "form": form,
    }
    return render(request, "create_skill.html", context)


def get_skills_json(request):
    title_query = request.GET.get("title", "").strip()
    skills = Skill.objects.all().order_by("category", "title")
    if title_query:
        skills = skills.filter(title__icontains=title_query)

    data = []
    for skill in skills:
        data.append({
            "pk": str(skill.id),
            "fields": {
                "title": skill.title,
                "description": skill.description,
                "category": skill.category or "Uncategorized",
                "star_count": skill.starred_by.count(),
                "is_starred": (
                    request.user.is_authenticated
                    and skill.starred_by.filter(id=request.user.id).exists()
                ),
            },
        })
    return JsonResponse(data, safe=False)


@require_POST
def create_skill_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan skill."},
            status=403,
        )

    form = SkillForm(request.POST)
    if form.is_valid():
        skill = form.save()
        return JsonResponse(
            {"message": "Skill berhasil ditambahkan.", "pk": str(skill.id)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@login_required
def delete_skill(request, skill_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    skill = get_object_or_404(Skill, pk=skill_id)
    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill berhasil dihapus!")
    return redirect("main:show_skills")


@login_required
def toggle_skill_star(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    if skill.starred_by.filter(id=request.user.id).exists():
        skill.starred_by.remove(request.user)
    else:
        skill.starred_by.add(request.user)
    return redirect("main:show_skills")
