from django.db import models

# Nota importante:
# Estas clases reflejan tablas que YA existen en SQL Server.
# managed = False le dice a Django "no me crees ni me toques la tabla,
# solo úsala". Así podemos hacer .objects sin migraciones raras.

class Programa(models.Model):
    id_programa = models.AutoField(db_column='ID_Programa', primary_key=True)
    nombreprograma = models.CharField(db_column='NombrePrograma', max_length=100)
    jornada = models.CharField(db_column='Jornada', max_length=50)
    ficha = models.CharField(db_column='Ficha', max_length=50)

    class Meta:
        db_table = 'Programa'
        managed = False

    def __str__(self):
        return f"{self.ficha} - {self.nombreprograma}"


class CodigoGenerado(models.Model):
    id_codigo = models.AutoField(db_column='ID_Codigo', primary_key=True)
    tipocodigo = models.CharField(db_column='TipoCodigo', max_length=50)
    fecha = models.DateField(db_column='Fecha')
    codigo = models.CharField(db_column='Codigo', max_length=200)
    hora = models.TimeField(db_column='Hora')
    id_usuario = models.IntegerField(db_column='ID_Usuario')
    id_programa = models.IntegerField(db_column='ID_Programa')

    class Meta:
        db_table = 'Codigo_Generado'
        managed = False

    def __str__(self):
        return f"{self.tipocodigo} {self.codigo} ({self.fecha} {self.hora})"


class Justificacion(models.Model):
    id_justificacion = models.AutoField(db_column='ID_Justificacion', primary_key=True)
    fechaenvio = models.DateField(db_column='FechaEnvio')
    archivoadjunto = models.CharField(db_column='ArchivoAdjunto', max_length=200, blank=True, null=True)
    fechainasistencia = models.DateField(db_column='FechaInasistencia')
    observacion = models.CharField(db_column='Observacion', max_length=200, blank=True, null=True)
    estado = models.CharField(db_column='Estado', max_length=20)
    motivo = models.CharField(db_column='Motivo', max_length=100)
    id_usuario = models.IntegerField(db_column='ID_Usuario')
    id_asistencia = models.IntegerField(db_column='ID_Asistencia')

    class Meta:
        db_table = 'Justificaciones'
        managed = False

    def __str__(self):
        return f"{self.id_justificacion} - {self.estado}"
