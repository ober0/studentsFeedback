from django.db import models

class Students(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
