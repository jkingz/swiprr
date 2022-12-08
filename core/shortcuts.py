from django.core.exceptions import PermissionDenied

import re


def convert_query_params_to_boolean(to_eval):
    # Since we mostly used query params, the boolean passed might be stirng
    if to_eval == "true" or to_eval == "1" or to_eval == 1 or to_eval is True:
        return True
    return False


def _get_queryset(klass):
    """
    Return a QuerySet or a Manager.
    """
    # If it is a model class or anything else with ._default_manager
    if hasattr(klass, "_default_manager"):
        return klass._default_manager.all()
    return klass


def get_object_or_None(klass, *args, **kwargs):
    """
    # Modified get_object_or_404

    Use get() to return an object, or raise a None exception if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Like with QuerySet.get(), MultipleObjectsReturned is raised if more than
    one object is found.
    """
    queryset = _get_queryset(klass)
    if not hasattr(queryset, "get"):
        klass__name = (
            klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        )
        raise ValueError(
            "First argument to get_object_or_None() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )

    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


def get_object_or_403(klass, *args, **kwargs):
    """
    # Modified get_object_or_404

    Use get() to return an object, or raise a None exception if the object
    does not exist.
    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.
    Like with QuerySet.get(), MultipleObjectsReturned is raised if more than
    one object is found.
    """
    queryset = _get_queryset(klass)
    if not hasattr(queryset, "get"):
        klass__name = (
            klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        )
        raise ValueError(
            "First argument to get_object_or_403() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )

    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise PermissionDenied

def convert_to_snakecase(word: str) -> str:
    """
    Make an underscored, lowercase form from the expression in the string.
    Example::
        >>> underscore("DeviceType")
        'device_type'
    As a rule of thumb you can think of :func:`underscore` as the inverse of
    :func:`camelize`, though there are cases where that does not hold::
        >>> camelize(underscore("IOError"))
        'IoError'
    """
    word = re.sub(r"([A-Z]+)([A-Z][a-z])", r'\1_\2', word)
    word = re.sub(r"([a-z\d])([A-Z])", r'\1_\2', word)
    word = word.replace("-", "_")
    return word.lower()
