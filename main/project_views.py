from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import ProjectForm
from main.models import Project
from main.permissions import is_editor


def show_projects(request):
    title_query = request.GET.get("title", "").strip()
    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "title_query": title_query,
        "form": ProjectForm(),
        "is_editor": is_editor(request.user),
    }
    return render(request, "projects.html", context)


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = (
        Project.objects.prefetch_related("starred_by")
        .order_by("title", "id")
    )
    if title_query:
        projects = projects.filter(title__icontains=title_query)

    data = []
    for project in projects:
        data.append(
            {
                "pk": str(project.id),
                "fields": {
                    "title": project.title,
                    "description": project.description,
                    "tech_stack": project.tech_stack,
                    "project_url": project.project_url,
                    "project_image_url": project.project_image_url,
                    "star_count": project.starred_by.count(),
                    "is_starred": (
                        request.user.is_authenticated
                        and project.starred_by.filter(id=request.user.id).exists()
                    ),
                },
            }
        )
    return JsonResponse(data, safe=False)


@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan project."},
            status=403,
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {
                "message": f'"{project.title}" berhasil ditambahkan.',
                "pk": str(project.id),
            },
            status=201,
        )
    return JsonResponse(
        {"errors": form.errors.get_json_data()},
        status=400,
    )


@login_required
@require_POST
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)
    title = project.title
    project.delete()
    messages.success(request, f'"{title}" berhasil dihapus.')
    return redirect("main:show_projects")


@login_required
@require_POST
def toggle_project_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.starred_by.filter(id=request.user.id).exists():
        project.starred_by.remove(request.user)
        messages.success(request, "Star dibatalkan.")
    else:
        project.starred_by.add(request.user)
        messages.success(request, f'Anda memberi "{project.title}" star.')
    return redirect("main:show_projects")
