from django.db import models

# --- PROGRAMA ---
class Programa(models.Model):
    id_programa = models.AutoField(primary_key=True, db_column="ID_Programa")
    nombre_programa = models.CharField(max_length=100, db_column="NombrePrograma")
    jornada = models.CharField(max_length=50, db_column="Jornada")
    ficha = models.CharField(max_length=50, db_column="Ficha")

    class Meta:
        managed = False
        db_table = 'dbo.Programa'
        # ✅ NombrePrograma + Ficha no se pueden repetir a nivel Django/admin
        unique_together = (('nombre_programa', 'ficha'),)

    def __str__(self):
        return f"{self.nombre_programa} ({self.ficha})"


# --- USUARIO ---
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True, db_column="ID_Usuario")
    nombre = models.CharField(max_length=100, db_column="Nombre")
    apellido = models.CharField(max_length=100, db_column="Apellido")
    correo = models.EmailField(max_length=100, unique=True, db_column="Correo")
    contrasena = models.CharField(max_length=100, db_column="Contraseña")
    estado = models.CharField(max_length=20, db_column="Estado")  # 'Activo' / 'Inactivo'
    id_rol = models.IntegerField(db_column="ID_Rol")              # 1=Aprendiz, 2=Instructor, 3=Admin
    programa = models.ForeignKey(
        "Programa",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="ID_Programa",
        related_name="usuarios",
    )

    class Meta:
        managed = False
        db_table = 'dbo.Usuario'

    def __str__(self):
        return f"{self.nombre} {self.apellido} <{self.correo}>"


# --- CODIGO_GENERADO ---
class CodigoGenerado(models.Model):
    id_codigo = models.AutoField(primary_key=True, db_column="ID_Codigo")
    tipo_codigo = models.CharField(max_length=50, db_column="TipoCodigo")   # p.ej. 'QR'
    fecha = models.DateField(db_column="Fecha")
    codigo = models.CharField(max_length=200, db_column="Codigo")
    hora = models.TimeField(db_column="Hora")
    usuario = models.ForeignKey(
        "Usuario",
        on_delete=models.CASCADE,
        db_column="ID_Usuario",
        related_name="codigos_generados",
    )
    programa = models.ForeignKey(
        "Programa",
        on_delete=models.CASCADE,
        db_column="ID_Programa",
        related_name="codigos_generados",
    )

    class Meta:
        managed = False
        db_table = 'dbo.Codigo_Generado'

    def __str__(self):
        return f"{self.tipo_codigo} {self.codigo} ({self.fecha} {self.hora})"


# --- ASISTENCIA ---
class Asistencia(models.Model):
    id_asistencia = models.AutoField(primary_key=True, db_column="ID_Asistencia")
    tipo_registro = models.CharField(max_length=20, db_column="TipoRegistro")  # Entrada / Salida
    fecha_registro = models.DateField(db_column="FechaRegistro")
    hora_registro = models.TimeField(db_column="HoraRegistro")
    estado = models.CharField(max_length=20, db_column="Estado")               # Presente / Tarde / Ausente
    usuario = models.ForeignKey(
        "Usuario",
        on_delete=models.CASCADE,
        db_column="ID_Usuario",
        related_name="asistencias",
    )
    programa = models.ForeignKey(
        "Programa",
        on_delete=models.CASCADE,
        db_column="ID_Programa",
        related_name="asistencias",
    )
    codigo = models.ForeignKey(
        "CodigoGenerado",
        on_delete=models.CASCADE,
        db_column="ID_Codigo",
        related_name="asistencias",
    )

    class Meta:
        managed = False
        db_table = 'dbo.Asistencia'

    def __str__(self):
        return f"{self.usuario} - {self.tipo_registro} - {self.fecha_registro}"


# --- JUSTIFICACIONES ---
class Justificaciones(models.Model):
    id_justificacion = models.AutoField(primary_key=True, db_column="ID_Justificacion")
    fecha_envio = models.DateField(db_column="FechaEnvio")
    archivo_adjunto = models.CharField(max_length=200, null=True, blank=True, db_column="ArchivoAdjunto")
    fecha_inasistencia = models.DateField(db_column="FechaInasistencia")
    observacion = models.CharField(max_length=200, null=True, blank=True, db_column="Observacion")
    estado = models.CharField(max_length=20, db_column="Estado")               # Pendiente / Aprobado / Rechazado
    motivo = models.CharField(max_length=100, db_column="Motivo")
    usuario = models.ForeignKey(
        "Usuario",
        on_delete=models.CASCADE,
        db_column="ID_Usuario",
        related_name="justificaciones",
    )
    asistencia = models.ForeignKey(
        "Asistencia",
        on_delete=models.CASCADE,
        db_column="ID_Asistencia",
        related_name="justificaciones",
    )

    class Meta:
        managed = False
        db_table = 'dbo.Justificaciones'

    def __str__(self):
        return f"Justificación {self.id_justificacion} - {self.estado}"


# --- HISTORIAL_ASISTENCIA ---
class HistorialAsistencia(models.Model):
    id_historial = models.AutoField(primary_key=True, db_column="ID_Historial")
    asistencia = models.ForeignKey(
        "Asistencia",
        on_delete=models.CASCADE,
        db_column="ID_Asistencia",
        related_name="historial",
    )
    usuario = models.ForeignKey(
        "Usuario",
        on_delete=models.CASCADE,
        db_column="ID_Usuario",
        related_name="historial_cambios",
    )
    campo_modificado = models.CharField(max_length=100, db_column="CampoModificado")
    valor_anterior = models.CharField(max_length=100, null=True, blank=True, db_column="ValorAnterior")
    valor_nuevo = models.CharField(max_length=100, db_column="ValorNuevo")
    fecha_cambio = models.DateField(db_column="FechaCambio")

    class Meta:
        managed = False
        db_table = 'dbo.Historial_Asistencia'

    def __str__(self):
        return f"Historial {self.id_historial} - {self.campo_modificado}"


# --- INSTRUCTOR_ASIGNADO ---
class InstructorAsignado(models.Model):
    # OJO: la columna real en SQL es ID_Asignacion
    id_relacion = models.AutoField(
        primary_key=True,
        db_column="ID_Asignacion",
    )
    aprendiz = models.ForeignKey(
        "Usuario",
        on_delete=models.CASCADE,
        db_column="ID_Aprendiz",
        related_name="asignaciones_como_aprendiz",
    )
    instructor = models.ForeignKey(
        "Usuario",
        on_delete=models.CASCADE,
        db_column="ID_Instructor",
        related_name="asignaciones_como_instructor",
    )
    tipo_competencia = models.CharField(
        max_length=20,           # en SQL es varchar(20)
        db_column="TipoCompetencia",
        null=True,
        blank=True,
    )
    trimestre = models.CharField(
        max_length=20,           # en SQL es varchar(20)
        db_column="Trimestre",
        null=True,
        blank=True,
    )

    class Meta:
        managed = False
        db_table = "dbo.Instructor_Asignado"

    def __str__(self):
        return f"{self.aprendiz} → {self.instructor} ({self.tipo_competencia or '—'} / {self.trimestre or '—'})"
