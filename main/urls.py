from django.urls import path

from main.views import (
    show_main,
    show_experience,
    show_skills,
    create_skill,
    create_experience,
    update_experience,
    delete_experience,
    get_experiences_json,
    get_skills_json,
    delete_skill,
    register,
    login_user,
    logout_user,
    toggle_skill_star,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/<uuid:experience_id>/edit/", update_experience, name="update_experience"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    path("api/experiences/", get_experiences_json, name="get_experiences_json"),
    path("skills/", show_skills, name="show_skills"),
    path("skills/add/", create_skill, name="create_skill"),
    path("api/skills/", get_skills_json, name="get_skills_json"),
    path("skills/<uuid:skill_id>/delete/", delete_skill, name="delete_skill"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("skills/<uuid:skill_id>/star/", toggle_skill_star, name="toggle_skill_star"),
]