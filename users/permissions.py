from rest_framework import permissions


class IsUserManager(permissions.BasePermission):

    # Extends the pemission to check for user manager
    def has_permission(self, request, view):
        return bool(
            request.user and (request.user.is_user_manager or request.user.is_superuser)
        )


class IsAgent(permissions.BasePermission):

    # Extends the pemission to check for anget
    def has_permission(self, request, view):
        return bool(
            request.user and (request.user.is_agent or request.user.is_superuser or request.user.is_user_manager)
        )


class RetrieveReferralAsOwnerOrUserManagerPermission(permissions.BasePermission):

    # Extends the permission to check for user manager or object owner permission
    def has_object_permission(self, request, view, obj):

        if view.action == "retrieve":
            bypass = bool(
                request.user
                and (request.user.is_user_manager or request.user.is_superuser)
            )
            if not bypass:
                return request.user == obj.referred_by
            return True
        return True
