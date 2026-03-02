# core/admin.py
from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.core.exceptions import ValidationError

from inclass_legacy.models import Programa, Usuario, InstructorAsignado
from inclass_legacy.sync import upsert_usuario_from_django


# ---------------------------
# Helpers de Rol
# ---------------------------
ROLE_CHOICES = (
    ("aprendiz", "Aprendiz"),
    ("instructor", "Instructor"),
    ("admin", "Administrador"),
)


def ensure_role_groups():
    # Grupos en minúscula para que todo sea coherente
    for name in ("aprendiz", "instructor", "admin"):
        Group.objects.get_or_create(name=name)


def detect_role(user: User) -> str:
    if user.is_superuser:
        return "admin"
    if user.groups.filter(name="instructor").exists():
        return "instructor"
    if user.groups.filter(name="aprendiz").exists():
        return "aprendiz"
    return ""


def apply_role(user: User, role: str):
    ensure_role_groups()
    # Quitar roles previos
    for gname in ("aprendiz", "instructor", "admin"):
        g = Group.objects.filter(name=gname).first()
        if g:
            user.groups.remove(g)

    if role == "admin":
        user.is_staff = True
        user.is_superuser = True
        g = Group.objects.get(name="admin")
        user.groups.add(g)
    elif role == "instructor":
        user.is_staff = False
        user.is_superuser = False
        g = Group.objects.get(name="instructor")
        user.groups.add(g)
    else:  # aprendiz
        user.is_staff = False
        user.is_superuser = False
        g = Group.objects.get(name="aprendiz")
        user.groups.add(g)

    user.save()


# ---------------------------
# Formularios (Rol + Programa + Ficha + Instructores)
# ---------------------------
class PrettyUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Rol", initial="aprendiz")
    program = forms.ModelChoiceField(
        queryset=Programa.objects.all(),
        required=False,
        empty_label="(Sin programa)",
        label="Programa",
    )
    ficha = forms.CharField(max_length=50, required=False, label="Ficha")
    instructores = forms.ModelMultipleChoiceField(
        queryset=Usuario.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": "8"}),
        label="Instructores (INCLASS)",
        help_text="Solo aplica si el rol es Aprendiz.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo usuarios legacy con rol instructor
        self.fields["instructores"].queryset = Usuario.objects.filter(id_rol=2)

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            raise forms.ValidationError(
                "El email es obligatorio para sincronizar con SQL Server."
            )
        return email


class PrettyUserChangeForm(UserChangeForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Rol", required=False)
    program = forms.ModelChoiceField(
        queryset=Programa.objects.all(),
        required=False,
        empty_label="(Sin programa)",
        label="Programa",
    )
    ficha = forms.CharField(max_length=50, required=False, label="Ficha")
    instructores = forms.ModelMultipleChoiceField(
        queryset=Usuario.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": "8"}),
        label="Instructores (INCLASS)",
        help_text="Instructores asignados al aprendiz en la tabla Instructor_Asignado.",
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            raise forms.ValidationError(
                "El email es obligatorio para sincronizar con SQL Server."
            )
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # queryset de instructores: solo legacy con rol=2 (Instructor)
        self.fields["instructores"].queryset = Usuario.objects.filter(id_rol=2)

        # Precargar rol, programa, ficha e instructores desde legacy
        if self.instance and self.instance.pk:
            self.fields["role"].initial = detect_role(self.instance)
            correo = (self.instance.email or "").strip() or self.instance.username
            try:
                u = (
                    Usuario.objects.select_related("programa")
                    .get(correo__iexact=correo)
                )
                # Programa / ficha
                self.fields["program"].initial = u.programa_id
                if u.programa:
                    self.fields["ficha"].initial = u.programa.ficha

                # Instructores asignados (tabla Instructor_Asignado)
                inst_ids = (
                    InstructorAsignado.objects.filter(aprendiz=u)
                    .values_list("instructor_id", flat=True)
                )
                self.fields["instructores"].initial = Usuario.objects.filter(
                    pk__in=list(inst_ids)
                )
            except Usuario.DoesNotExist:
                pass


# ---------------------------
# Reemplazar el UserAdmin por defecto
# ---------------------------
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = PrettyUserCreationForm
    form = PrettyUserChangeForm

    # Columna "Rol" en el listado
    def role_display(self, obj):
        m = {
            "admin": "Administrador",
            "instructor": "Instructor",
            "aprendiz": "Aprendiz",
        }
        return m.get(detect_role(obj), "—")

    role_display.short_description = "Rol"

    list_display = BaseUserAdmin.list_display + ("role_display",)
    list_filter = BaseUserAdmin.list_filter + ("is_staff", "is_superuser")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Información personal", {"fields": ("first_name", "last_name", "email")}),
        (
            "Rol y programa",
            {
                "fields": (
                    "role",
                    "program",
                    "ficha",
                    "instructores",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "role",
                    "program",
                    "ficha",
                    "instructores",
                    "is_active",
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        """
        Guarda el usuario, aplica rol, sincroniza con dbo.Usuario
        y actualiza las relaciones en Instructor_Asignado.
        """
        super().save_model(request, obj, form, change)

        # ---- Rol + flags ----
        role = form.cleaned_data.get("role") or "aprendiz"
        apply_role(obj, role)

        # ---- Sincronizar con dbo.Usuario ----
        programa = form.cleaned_data.get("program")
        ficha = (form.cleaned_data.get("ficha") or "").strip()
        jornada = ""  # ya no se maneja desde aquí

        try:
            upsert_usuario_from_django(
                obj,
                role,
                programa,
                jornada=jornada,
                ficha=ficha,
            )
            messages.success(request, "Usuario sincronizado en SQL Server ✅")
        except Exception as e:
            messages.error(request, f"⚠️ No se pudo sincronizar en SQL Server: {e}")

        # ---- Instructores asignados (solo sentido si es aprendiz) ----
        instructores = form.cleaned_data.get("instructores") or []
        correo = (obj.email or "").strip() or obj.username

        try:
            aprendiz_legacy = Usuario.objects.filter(correo__iexact=correo).first()
            if not aprendiz_legacy:
                # Si no existe en dbo.Usuario, no podemos guardar relaciones
                if instructores and role == "aprendiz":
                    messages.warning(
                        request,
                        "No se encontraron datos en dbo.Usuario para asignar instructores.",
                    )
                return

            with transaction.atomic():
                # Siempre limpiamos relaciones previas
                InstructorAsignado.objects.filter(aprendiz=aprendiz_legacy).delete()

                # Si ya no es aprendiz o no hay instructores seleccionados, solo limpiamos
                if role != "aprendiz" or not instructores:
                    return

                # Crear nuevas filas. TipoCompetencia no acepta NULL,
                # así que usamos un valor por defecto.
                for inst in instructores:
                    InstructorAsignado.objects.create(
                        aprendiz=aprendiz_legacy,
                        instructor=inst,
                        tipo_competencia="GENERAL",
                        trimestre="",
                    )
        except Exception as e:
            messages.error(
                request,
                f"⚠️ No se pudieron actualizar los instructores asignados: {e}",
            )


# =========================
# Admin de Programa (único por NOMBRE)
# =========================

class ProgramaAdminForm(forms.ModelForm):
    class Meta:
        model = Programa
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        model = self._meta.model

        # Detectar dinámicamente el campo de nombre del programa
        nombre_field = None
        for f in model._meta.fields:
            db_col = getattr(f, "db_column", None)
            if db_col == "NombrePrograma" or f.name == "NombrePrograma":
                nombre_field = f.name
                break

        nombre = (cleaned.get(nombre_field) or "").strip() if nombre_field else ""

        if nombre:
            filtros = {}
            if nombre_field:
                filtros[f"{nombre_field}__iexact"] = nombre

            if filtros:
                qs = model.objects.filter(**filtros)
                if self.instance.pk:
                    qs = qs.exclude(pk=self.instance.pk)
                if qs.exists():
                    # Error SOLO por el nombre del programa, sin importar ficha/jornada
                    raise ValidationError({
                        nombre_field: "Ya existe un programa con este nombre. "
                                      "No se puede repetir aunque cambies ficha o jornada."
                    })

        return cleaned


class ProgramaAdmin(admin.ModelAdmin):
    form = ProgramaAdminForm


# Re-registrar Programa con nuestro admin (por si ya estaba registrado)
try:
    admin.site.unregister(Programa)
except admin.sites.NotRegistered:
    pass

admin.site.register(Programa, ProgramaAdmin)
