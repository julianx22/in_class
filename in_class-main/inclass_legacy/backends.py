# inclass_legacy/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db import transaction
from inclass_legacy.models import Usuario

# libs opcionales (si no están instaladas, el código hace fallback)
try:
    from passlib.hash import bcrypt, argon2, django_pbkdf2_sha256
except Exception:  # passlib no instalada o parcial
    bcrypt = argon2 = django_pbkdf2_sha256 = None

import hashlib
import re


def verify_legacy_password(plain: str, stored: str) -> bool:
    """
    Intenta validar 'plain' contra 'stored' detectando formato:
    - bcrypt: $2a$ / $2b$ / $2y$
    - argon2: $argon2...
    - Django pbkdf2: pbkdf2_sha256$...
    - sha256 hex de 64 chars (sin salt)
    - texto plano (fallback)
    """
    s = (stored or "").strip()
    if not s:
        return False

    # bcrypt
    if s.startswith("$2"):
        if not bcrypt:
            return False
        try:
            return bcrypt.verify(plain, s)
        except Exception:
            return False

    # argon2
    if s.startswith("$argon2"):
        if not argon2:
            return False
        try:
            return argon2.verify(plain, s)
        except Exception:
            return False

    # Django pbkdf2
    if s.startswith("pbkdf2_sha256$"):
        try:
            if django_pbkdf2_sha256:
                return django_pbkdf2_sha256.verify(plain, s)
            # fallback usando passlib pbkdf2_sha256 genérico (intenta igual)
            from passlib.hash import pbkdf2_sha256 as _pb
            return _pb.verify(plain, s)
        except Exception:
            return False

    # sha256 (64 hex, sin salt)
    if re.fullmatch(r"[0-9a-fA-F]{64}", s):
        return hashlib.sha256(plain.encode("utf-8")).hexdigest().lower() == s.lower()

    # Fallback: texto plano
    return plain == s


class LegacyBackend(ModelBackend):
    """
    Autentica con tu tabla dbo.Usuario (correo/Contraseña) y mapea rol a staff/superuser.
    Username del formulario admin = Correo.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        # Si tuvieras multi-DB con alias, usa: Usuario.objects.using("legacy").get(...)
        try:
            u = Usuario.objects.get(correo=username)
        except Usuario.DoesNotExist:
            return None

        # Estado debe ser 'Activo'
        if (u.estado or "").strip().lower() != "activo":
            return None

        # Verifica con el verificador flexible
        if not verify_legacy_password(password, u.contrasena):
            return None

        # Sincroniza/crea el User de Django
        User = get_user_model()
        with transaction.atomic():
            dj, _ = User.objects.get_or_create(
                username=u.correo,
                defaults={"email": u.correo, "is_active": True},
            )
            dj.email = u.correo
            dj.is_active = True

            es_admin = (u.id_rol == 3)  # 3 = Admin
            dj.is_staff = es_admin
            dj.is_superuser = es_admin

            dj.save()

        return dj
