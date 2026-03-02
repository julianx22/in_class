# inclass_legacy/sync.py
from typing import Optional
from django.db import transaction
from django.contrib.auth.models import User

from .models import Usuario, Programa

ROLE_MAP = {
    "aprendiz": 1,
    "instructor": 2,
    "admin": 3,
}

def _pick_programa(programa: Optional[Programa], ficha: Optional[str], jornada: Optional[str]) -> Optional[Programa]:
    """
    Si ya viene un Programa, úsalo. Si no, intenta encontrarlo por ficha y/o jornada.
    Si no encuentra nada, devuelve None y no lloramos.
    """
    if programa:
        return programa
    qs = Programa.objects.all()
    if ficha:
        qs = qs.filter(ficha=str(ficha))
    if jornada:
        qs = qs.filter(jornada__iexact=str(jornada))
    return qs.first()

def upsert_usuario_from_django(
    user: User,
    role: str,
    programa: Optional[Programa] = None,
    # Aceptamos kwargs “extra” para que nadie vuelva a romper esto.
    **kwargs,
) -> Usuario:
    """
    Sube/actualiza en dbo.Usuario usando el EMAIL como clave.
    Copia SIEMPRE el hash de Django (pbkdf2_sha256$...).
    Acepta kwargs como jornada/ficha (opcional) y los usa si sirven.
    """
    correo = (user.email or "").strip() or user.username
    jornada = kwargs.get("jornada")
    ficha = kwargs.get("ficha")

    programa = _pick_programa(programa, ficha, jornada)

    defaults = {
        "nombre": user.first_name or "",
        "apellido": user.last_name or "",
        # muy importante: guardamos el HASH actual de Django
        "contrasena": user.password,
        "estado": "Activo" if user.is_active else "Inactivo",
        "id_rol": ROLE_MAP.get((role or "aprendiz").lower(), 1),
        "programa": programa,  # puede ser None y está bien
    }

    with transaction.atomic():
        obj, created = Usuario.objects.update_or_create(
            correo=correo,
            defaults=defaults,
        )
    return obj
