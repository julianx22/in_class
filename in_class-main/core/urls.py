from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

app_name = "core"

urlpatterns = [
    path("", views.login_view, name="root"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Registro público
    path("registro/", views.register_view, name="register"),

    path("home/", views.home_redirect, name="home"),

    path("dash/aprendiz/",   views.dash_aprendiz,   name="dash_aprendiz"),
    path("dash/instructor/", views.dash_instructor, name="dash_instructor"),

    path("perfil/editar/", views.profile_edit, name="profile_edit"),

    # ===== QR
    path("qr/generar/",     views.qr_generar,     name="qr_generar"),
    path("qr/api/generar/", views.qr_generar_api, name="qr_generar_api"),

    # nuevo: fichas por programa (para la pantalla de QR)
    path(
        "qr/api/fichas-por-programa/",
        views.api_fichas_por_programa,
        name="api_fichas_por_programa",
    ),

    # antiguo (lo dejo por compatibilidad)
    path(
        "qr/api/programa-por-ficha/",
        views.api_programa_por_ficha,
        name="api_programa_por_ficha",
    ),

    path("qr/<str:code>/", views.qr_scan_router, name="qr_scan_router"),
    path(
        "asistencia/registrar/auto/<str:code>/",
        views.registrar_asistencia_auto,
        name="registrar_asistencia_auto",
    ),
    path(
        "api/asistencia/live/<str:code>/",
        views.asistencia_list_api,
        name="asistencia_list_api",
    ),

    path("qr/api/activo/", views.api_qr_activo, name="api_qr_activo"),

    path(
        "asistencia/registrar/",
        views.registrar_asistencia,
        name="registrar_asistencia",
    ),
    path(
        "asistencia/api/registrar/",
        views.registrar_asistencia_api,
        name="registrar_asistencia_api",
    ),

    # ===== Historial (aprendiz)
    path(
        "asistencia/historial/",
        views.historial_asistencia_view,
        name="historial_asistencia",
    ),
    path(
        "api/asistencia/historial/",
        views.historial_asistencia_api,
        name="historial_asistencia_api",
    ),

    # ===== Notificaciones (aprendiz)
    path("notificaciones/", views.notificaciones_view, name="notificaciones"),
    path(
        "api/notif/list/",
        views.notificaciones_list_api,
        name="api_notif_list",
    ),
    path(
        "api/notif/mark-read/",
        views.notificacion_mark_read_api,
        name="api_notif_mark_read",
    ),
    path(
        "api/notif/mark-all/",
        views.notificacion_mark_all_api,
        name="api_notif_mark_all",
    ),
    path(
        "api/notif/unread-count/",
        views.notif_unread_count_api,
        name="api_notif_unread_count",
    ),

    path("acerca/",   views.acerca_view,   name="acerca"),
    path("ayuda/",    views.ayuda_view,    name="ayuda"),
    path("contacto/", views.contacto_view, name="contacto"),
    path("creditos/", views.creditos_view, name="creditos"),

    # ================== RECUPERACIÓN DE CONTRASEÑA ==================
    path(
        "password-reset/",
        views.CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=reverse_lazy("core:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

    # =========================================================
    # ================== JUSTIFICACIONES (NUEVO) ==============
    # =========================================================

    # Aprendiz
    path(
        "justificaciones/",
        views.justificaciones_aprendiz,
        name="justificaciones_aprendiz",
    ),
    path(
        "api/justif/create/",
        views.justificacion_create_api,
        name="justif_create_api",
    ),
    path(
        "api/justif/list/",
        views.justificacion_list_api,
        name="justif_list_api",
    ),
    path(
        "api/justif/instructores/",
        views.justif_instructores_aprendiz_api,
        name="justif_instructores_aprendiz_api",
    ),

    # Instructor
    path(
        "instructor/justificaciones/",
        views.justificaciones_instructor,
        name="justificaciones_instructor",
    ),
    path(
        "instructor/api/justif/list/",
        views.instructor_justif_list_api,
        name="instructor_justif_list_api",
    ),
    path(
        "instructor/api/justif/set-state/",
        views.instructor_justif_set_state_api,
        name="instructor_justif_set_state_api",
    ),

    # Reportes (instructor)
    path(
        "instructor/reportes/",
        views.instructor_reportes,
        name="instructor_reportes",
    ),

    # Historial de asistencia (instructor)
    path(
        "instructor/historial/",
        views.instructor_historial_view,
        name="instructor_historial",
    ),
    path(
        "instructor/api/asistencia/historial/",
        views.instructor_historial_api,
        name="instructor_historial_api",
    ),
    path(
        "instructor/asistencia/historial/excel/",
        views.instructor_historial_excel,
        name="instructor_historial_excel",
    ),

    # Alertas de deserción temprana (instructor)
    path(
        "instructor/alertas-desercion/",
        views.instructor_alertas_desercion_view,
        name="instructor_alertas_desercion",
    ),
    path(
        "instructor/api/alertas-desercion/",
        views.instructor_alertas_desercion_api,
        name="instructor_alertas_desercion_api",
    ),
]
