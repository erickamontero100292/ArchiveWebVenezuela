#encoding:utf-8 
from django.forms import ModelForm
from django import forms
from principal.models import Buscador



class BuscadorForm(ModelForm):
    class Meta:
        model = Buscador
        fields = '__all__'


