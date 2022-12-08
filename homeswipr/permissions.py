from core.shortcuts import get_object_or_None
from rest_framework import permissions

from .models import UserSavedSearch


class SavedSearchOwnerPermission(permissions.BasePermission):

    # Extends the pemission to check if the passed saved search is theirs
    def has_permission(self, request, view):
        saved_search_pk = request.query_params.get("saved_search_pk", None)

        if bool(
            request.user.is_authenticated
            and (request.user.is_user_manager or request.user.is_superuser)
        ):
            return True

        if saved_search_pk:
            if request.user.is_authenticated:
                saved_search = get_object_or_None(
                    UserSavedSearch.active_objects, pk=saved_search_pk
                )
                if saved_search:
                    return request.user == saved_search.user
                return False
            else:
                return False
        # If no saved search is passed, this doesn't need to  be checked
        return True
