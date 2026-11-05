from django.urls import path

from main.auth_views import login_user, logout_user, register
from main.experience_views import (
    create_experience,
    create_experience_ajax,
    delete_experience,
    get_experiences_json,
    show_experience,
    toggle_experience_star,
    update_experience,
)
from main.project_views import (
    create_project_ajax,
    delete_project,
    get_projects_json,
    show_projects,
    toggle_project_star,
)
from main.skill_views import (
    create_skill,
    create_skill_ajax,
    delete_skill,
    get_skills_json,
    show_skills,
    toggle_skill_star,
    update_skill_ajax,
)
from main.views import show_main

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),

    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),

    path("experience/", show_experience, name="show_experience"),
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/<uuid:experience_id>/edit/", update_experience, name="update_experience"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    path("experience/<uuid:experience_id>/star/", toggle_experience_star, name="toggle_experience_star"),
    path("api/experiences/", get_experiences_json, name="get_experiences_json"),
    path("api/experiences/create/", create_experience_ajax, name="create_experience_ajax"),

    path("skills/", show_skills, name="show_skills"),
    path("skills/add/", create_skill, name="create_skill"),
    path("api/skills/", get_skills_json, name="get_skills_json"),
    path("api/skills/create/", create_skill_ajax, name="create_skill_ajax"),
    path("api/skills/<uuid:skill_id>/update/", update_skill_ajax, name="update_skill_ajax"),
    path("skills/<uuid:skill_id>/delete/", delete_skill, name="delete_skill"),
    path("skills/<uuid:skill_id>/star/", toggle_skill_star, name="toggle_skill_star"),

    path("projects/", show_projects, name="show_projects"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("api/projects/create/", create_project_ajax, name="create_project_ajax"),
    path("projects/<uuid:project_id>/delete/", delete_project, name="delete_project"),
    path("projects/<uuid:project_id>/star/", toggle_project_star, name="toggle_project_star"),
]
