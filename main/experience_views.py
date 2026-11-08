from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import ExperienceForm
from main.models import Experience
from main.permissions import is_editor


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
    if request.method == "POST" and form.is_valid():
        experience = form.save()
        messages.success(request, f'"{experience.title}" berhasil ditambahkan.')
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
    if request.method == "POST" and form.is_valid():
        experience = form.save()
        messages.success(request, f'"{experience.title}" berhasil diperbarui.')
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
        title = experience.title
        experience.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"message": f'"{title}" berhasil dihapus.'})
        messages.success(request, f'"{title}" berhasil dihapus.')
    return redirect("main:show_experience")


def get_experiences_json(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()
    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    data = []
    for experience in experiences:
        data.append(
            {
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
                    "star_count": experience.starred_by.count(),
                    "is_starred": (
                        request.user.is_authenticated
                        and experience.starred_by.filter(pk=request.user.pk).exists()
                    ),
                },
            }
        )
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def toggle_experience_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if experience.starred_by.filter(pk=request.user.pk).exists():
        experience.starred_by.remove(request.user)
        message = "Star dibatalkan."
    else:
        experience.starred_by.add(request.user)
        message = f'Anda memberi "{experience.title}" star.'
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "message": message,
                "star_count": experience.starred_by.count(),
                "is_starred": experience.starred_by.filter(pk=request.user.pk).exists(),
            }
        )
    messages.success(request, message)
    return redirect("main:show_experience")


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
                "message": f'"{experience.title}" berhasil ditambahkan.',
                "pk": str(experience.id),
                "title": experience.title,
            },
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
