from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Newsletter, Cliente, InfosProfissao


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        exclude = ()

        widgets = {
            'nome_newsletter': forms.TextInput(attrs={'class': 'form-control', 'autofocus': ''}),
            'link_newsletter': forms.URLInput(attrs={'class': 'form-control'}),
            'titulo_materia_chamariz': forms.TextInput(attrs={'class': 'form-control'}),
            'desc_materia_chamativa': forms.Textarea(attrs={'class': 'form-control'}),
            'qtd_inscritos': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ClienteForm(UserCreationForm):
    nome = forms.CharField(max_length=255)
    carreira_de_interesse = forms.ModelChoiceField(queryset=InfosProfissao.objects.all())
    data_de_nascimento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'format': '%Y-%m-%d'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

        cliente, created = Cliente.objects.update_or_create(
            usuario=user,
            defaults={
                'nome': self.cleaned_data['nome'],
                'data_de_nascimento': self.cleaned_data['data_de_nascimento'],
                'carreira_de_interesse': self.cleaned_data['carreira_de_interesse']
            }
        )

        cliente.save()

        return user

