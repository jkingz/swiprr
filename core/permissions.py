from rest_framework import permissions


class ObjectOwnerPermission(permissions.BasePermission):
    # Check if the user/owner of the object is the one requesting it

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class ObjectOwnerPermissionOrUserManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Checks if usermanager or has object permission
        if bool(
            request.user.is_authenticated
            and (request.user.is_user_manager or request.user.is_superuser)
        ):
            return True
        return request.user == obj.user


class IsSuperUser(permissions.BasePermission):
    # Extends the permission to check for superuser
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsAgentUser(permissions.BasePermission):
    # Extends the permission to check for agentuser
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_agent and request.user.is_superuser)


class IsAdmin(permissions.BasePermission):
    # Extends the permission to check for admin/team member
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_user_manager and request.user.is_superuser)


class IsMortgageBroker(permissions.BasePermission):
    # Extends the permission to check for mortgage broker
    def has_permission(self, request, view):
        return bool(request.user and request.user.user_type and request.user.uset_type.type == 'Mortgage Broker' and request.user.is_user_manager and request.user.is_superuser)


class IsSalesAgent(permissions.BasePermission):
    # Extends the permission to check for mortgage broker
    def has_permission(self, request, view):
        return bool(request.user and request.user.user_type and request.user.uset_type.type == 'Sales Agent' and request.user.is_user_manager and request.user.is_superuser)
