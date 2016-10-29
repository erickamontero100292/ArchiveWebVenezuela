#encoding:utf-8
from django.db import models
from django.contrib.auth.models import User

class Buscador(models.Model):
	palabraClave = models.TextField(help_text='Palabras a buscar')
	def __unicode__(self):
		return self.palabraClave 

