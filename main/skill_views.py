from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import SkillForm
from main.models import Skill
from main.permissions import is_editor


def show_skills(request):
    title_query = request.GET.get("title", "").strip()
    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "title_query": title_query,
        "form": SkillForm(),
        "is_editor": is_editor(request.user),
    }
    return render(request, "skills.html", context)


@login_required
def create_skill(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = SkillForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        skill = form.save()
        messages.success(request, f'"{skill.title}" berhasil ditambahkan.')
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
        data.append(
            {
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
            }
        )
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
            {
                "message": f'"{skill.title}" berhasil ditambahkan.',
                "pk": str(skill.id),
                "title": skill.title,
            },
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@login_required
@require_POST
def update_skill_ajax(request, skill_id):
    if not (request.user.is_superuser or is_editor(request.user)):
        return JsonResponse(
            {"message": "Hanya pemilik portofolio atau editor yang dapat mengubah skill."},
            status=403,
        )

    skill = get_object_or_404(Skill, pk=skill_id)
    form = SkillForm(request.POST, instance=skill)
    if form.is_valid():
        skill = form.save()
        return JsonResponse(
            {
                "message": f'"{skill.title}" berhasil diperbarui.',
                "title": skill.title,
            }
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@login_required
def delete_skill(request, skill_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    skill = get_object_or_404(Skill, pk=skill_id)
    if request.method == "POST":
        title = skill.title
        skill.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"message": f'"{title}" berhasil dihapus.'})
        messages.success(request, f'"{title}" berhasil dihapus.')
    return redirect("main:show_skills")


@login_required
@require_POST
def toggle_skill_star(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    if skill.starred_by.filter(id=request.user.id).exists():
        skill.starred_by.remove(request.user)
        message = "Star dibatalkan."
    else:
        skill.starred_by.add(request.user)
        message = f'Anda memberi "{skill.title}" star.'
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "message": message,
                "star_count": skill.starred_by.count(),
                "is_starred": skill.starred_by.filter(pk=request.user.pk).exists(),
            }
        )
    messages.success(request, message)
    return redirect("main:show_skills")
