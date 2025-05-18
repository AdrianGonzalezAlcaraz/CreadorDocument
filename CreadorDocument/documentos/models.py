from django.db import models
from django.conf import settings

class Documento(models.Model):
    TIPO_EXTENSION = [
        ('word', 'Documento Word'),
        ('txt', 'Texto Plano'),
        ('excel', 'Hoja de Cálculo Excel'),
        ('cal', 'Hoja de Cálculo CAL'),
        ('ppt', 'Presentación PowerPoint'),
        ('pdf', 'Documento PDF'),
        ('html', 'HTML'),
        ('php', 'PHP'),
        ('css', 'Hoja de Estilos CSS'),
        ('js', 'JavaScript'),
    ]

    titulo = models.CharField(max_length=200)
    archivo_path = models.FileField(upload_to='documentos/')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    extension = models.CharField(max_length=10, choices=TIPO_EXTENSION)

    def __str__(self):
        return f"{self.titulo} ({self.extension})"

    class Meta:
        indexes = [
            models.Index(fields=['titulo', 'usuario'])  # Esto es lo correcto
        ]
    '''def save(self, *args, **kwargs):
        # Al guardar, generamos el path si no existe
        if not self.path:
            nombre_archivo = f"{self.titulo}.{self.extension}"
            self.path = f"static/CreadorDocument/media/{nombre_archivo}"
        super().save(*args, **kwargs)'''
