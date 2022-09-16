from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrModerator(BasePermission):
    """Проверка доступа: контент может изменять автор или
        пользователь со статусом модератора (администратора).
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_moderator
            or request.user.is_superuser
            or obj.author == request.user
        )


class IsAdmin(BasePermission):
    """Пользователь имеет роль 'admin'."""

    def has_permission(self, request, view):
        return request.user.is_admin or request.user.is_superuser


class IsAdminOrReadOnly(BasePermission):
    """Пользователь имеет роль админ или запрос на чтение"""

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (
                request.user.is_authenticated and (
                    request.user.is_admin or request.user.is_superuser
                )
            )

        )
