from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class InfosProfissao(models.Model):
    nome_profissao = models.CharField(max_length=255)

    def __str__(self):
        return self.nome_profissao

class VagaEmprego(models.Model):
    nome_vaga = models.CharField(max_length=255)
    salario = models.CharField(max_length=255)
    descricao_vaga = models.TextField()
    link_vaga = models.URLField()
    data_publicacao = models.CharField(max_length=255)
    profissao = models.ForeignKey(InfosProfissao, on_delete=models.SET_NULL, null=True)
    estado = models.CharField(max_length=255, null=True)

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cliente", null=True)
    nome = models.CharField(max_length=255)
    carreira_de_interesse = models.ForeignKey(InfosProfissao, on_delete=models.SET_NULL, null=True, verbose_name="carreira de interesse")
    data_de_nascimento = models.DateField(null=True)
    data_inscricao = models.DateTimeField(default=timezone.now)
    email = models.EmailField()

class NewsMercado(models.Model):
    nome_newsletter = models.CharField(max_length=255)
    link_newsletter = models.URLField()
    titulo_materia_chamariz = models.CharField(max_length=255)
    desc_materia_chamativa = models.TextField()
    qtd_inscritos = models.IntegerField()
    profissao = models.ForeignKey(InfosProfissao, on_delete=models.SET_NULL, null=True)

class NewsMercadoIncricao(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    news_mercado = models.ForeignKey(NewsMercado, on_delete=models.CASCADE)
    data_inscricao = models.DateTimeField(default=timezone.now)

class ComparacaoSalarios(models.Model):
    junior_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pleno_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    senior_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    junior_clt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pleno_clt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    senior_clt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    junior_pj = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pleno_pj = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    senior_pj = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profissao = models.ForeignKey(InfosProfissao, on_delete=models.SET_NULL, null=True)

class NewsEmpreendedor(models.Model):
    nome_newsletter = models.CharField(max_length=255)
    link_newsletter = models.URLField()
    titulo_materia_chamariz = models.CharField(max_length=255)
    desc_materia_chamativa = models.TextField()
    qtd_inscritos = models.IntegerField()
    profissao = models.ForeignKey(InfosProfissao, on_delete=models.SET_NULL, null=True)

class NewsEmpreendedorInscricao(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    news_empreendedor = models.ForeignKey(NewsEmpreendedor, on_delete=models.CASCADE)
    data_inscricao = models.DateTimeField(default=timezone.now)

class Newsletter(models.Model):
    nome_newsletter = models.CharField(max_length=255)
    link_newsletter = models.URLField()
    titulo_materia_chamariz = models.CharField(max_length=255)
    desc_materia_chamativa = models.TextField()
    qtd_inscritos = models.IntegerField()
    profissao = models.ForeignKey(InfosProfissao, on_delete=models.SET_NULL, null=True)

class InscricaoNewsletter(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE)
    data_inscricao = models.DateTimeField(default=timezone.now)

class NewsletterProfissao(models.Model):
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE)
    profissao = models.ForeignKey(InfosProfissao, on_delete=models.CASCADE)

class Logs(models.Model):
    qtd_acessos = models.IntegerField()
    data_ultimo_acesso = models.DateField()
    esta_logado = models.BooleanField()

    def add_acesso(self, quantidade):
        self.qtd_acessos += quantidade
        self.data_ultimo_acesso = timezone.now()
        self.save()

