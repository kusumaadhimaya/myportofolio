from rest_framework.permissions import SAFE_METHODS, BasePermission


def is_editor(user):
    return user.is_authenticated and user.groups.filter(name="Editor").exists()


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    message = "Editors can update data; only the owner can create or delete it."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return (
            request.method in ("PUT", "PATCH")
            and is_editor(request.user)
        )
