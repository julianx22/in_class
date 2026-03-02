# core/decorators.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from functools import wraps

def login_required_any(view_func):
    """
    Cualquier usuario autenticado entra (aprendiz, instructor, admin).
    Si no está logueado, lo mando al login.
    """
    return login_required(view_func)

def instructor_required(view_func):
    """
    Solo instructores o staff.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        u = request.user
        if not u.is_authenticated:
            return redirect("core:login")
        if u.is_staff or u.is_superuser or u.groups.filter(name="Instructor").exists():
            return view_func(request, *args, **kwargs)
        # si no es instructor, lo saco a home inteligente
        return redirect("core:home")
    return _wrapped

def aprendiz_required(view_func):
    """
    Solo aprendices (rol grupo 'Aprendiz')
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        u = request.user
        if not u.is_authenticated:
            return redirect("core:login")
        if u.groups.filter(name="Aprendiz").exists() and not u.is_staff and not u.is_superuser:
            return view_func(request, *args, **kwargs)
        return redirect("core:home")
    return _wrapped
