# inclass_legacy/admin.py
from django.contrib import admin
from .models import (
    Programa, Usuario, CodigoGenerado,
    Asistencia, Justificaciones, HistorialAsistencia
)

@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = ("nombre_programa", "ficha", "jornada", "usuarios_count")
    search_fields = ("nombre_programa", "ficha", "jornada")
    list_filter = ("jornada",)
    ordering = ("nombre_programa", "ficha")

    def usuarios_count(self, obj):
        return obj.usuarios.count()
    usuarios_count.short_description = "Usuarios"

@admin.register(Usuario)
class UsuarioLegacyAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "correo", "estado", "id_rol", "programa")
    search_fields = ("nombre", "apellido", "correo")
    list_filter = ("estado", "id_rol", "programa")
    ordering = ("apellido", "nombre")

@admin.register(CodigoGenerado)
class CodigoGeneradoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "tipo_codigo", "fecha", "hora", "usuario", "programa")
    search_fields = ("codigo",)
    list_filter = ("tipo_codigo", "programa", "fecha")
    date_hierarchy = "fecha"
    ordering = ("-fecha", "-hora")

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "programa", "tipo_registro", "estado", "fecha_registro", "hora_registro", "codigo")
    list_filter = ("tipo_registro", "estado", "programa", "fecha_registro")
    search_fields = ("usuario__nombre", "usuario__apellido", "usuario__correo")
    date_hierarchy = "fecha_registro"
    ordering = ("-fecha_registro", "-hora_registro")

@admin.register(Justificaciones)
class JustificacionesAdmin(admin.ModelAdmin):
    list_display = ("id_justificacion", "usuario", "estado", "motivo", "fecha_inasistencia", "fecha_envio")
    list_filter = ("estado", "motivo", "fecha_inasistencia")
    search_fields = ("usuario__nombre", "usuario__apellido", "observacion")
    date_hierarchy = "fecha_inasistencia"
    ordering = ("-fecha_inasistencia", "-fecha_envio")

@admin.register(HistorialAsistencia)
class HistorialAsistenciaAdmin(admin.ModelAdmin):
    list_display = ("id_historial", "asistencia", "usuario", "campo_modificado", "valor_anterior", "valor_nuevo", "fecha_cambio")
    list_filter = ("campo_modificado", "fecha_cambio")
    search_fields = ("usuario__nombre", "usuario__apellido", "campo_modificado", "valor_nuevo")
    date_hierarchy = "fecha_cambio"
    ordering = ("-fecha_cambio",)
