from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .forms import NewsletterForm, ClienteForm
from .models import InfosProfissao, VagaEmprego, Cliente, Newsletter, InscricaoNewsletter, NewsletterProfissao, Logs, NewsMercado, NewsEmpreendedor, ComparacaoSalarios
from .graphs import radar, barras, evolucao_salario, barras_comparacao
import pandas as pd
from .services import tratamentos_vagas
import plotly.io as pio
import random

@login_required
def index(request):
    cliente_logado = Cliente.objects.filter(usuario=request.user).first()

    if not cliente_logado:
        return redirect('cadastro')

    profissoes = InfosProfissao.objects.filter(cliente=cliente_logado)
    profissao_id = cliente_logado.carreira_de_interesse.id if cliente_logado.carreira_de_interesse else None
    print('profissao_id: ', profissao_id)
    df_vagas = tratamentos_vagas(profissao_id)
    cliente = Cliente.objects.all()
    inscricao_newsletter = InscricaoNewsletter.objects.filter(cliente=cliente_logado)
    news = Newsletter.objects.filter(inscricaonewsletter__in=inscricao_newsletter).distinct()
    logs = Logs.objects.all()
    comparacao_salarios = ComparacaoSalarios.objects.all()

    print(cliente_logado.carreira_de_interesse)
    if cliente_logado.carreira_de_interesse:
        newsletter_profissao = Newsletter.objects.filter(profissao=cliente_logado.carreira_de_interesse).distinct()
    else:
        newsletter_profissao = Newsletter.objects.none()

    if cliente_logado.carreira_de_interesse:
        newsletter_mercado = NewsMercado.objects.filter(profissao=cliente_logado.carreira_de_interesse).distinct()
    else:
        newsletter_mercado = NewsMercado.objects.none()

    if cliente_logado.carreira_de_interesse:
        newsletter_empreendedor = NewsEmpreendedor.objects.filter(profissao=cliente_logado.carreira_de_interesse).distinct()
    else:
        newsletter_empreendedor = NewsEmpreendedor.objects.none()



#Compondo graficos

    df_vaga = df_vagas.copy()
    df_vaga_hab_especif = df_vaga[df_vaga['habilidade'] != 'Não Especificado']
    habilidade_freq = df_vaga_hab_especif['habilidade'].value_counts().reset_index()
    habilidade_freq.columns = ['habilidade', 'count']

    df_vaga = df_vagas.copy()
    formacao_freq = df_vaga['min_anos_formacao'].value_counts().reset_index()
    formacao_freq.columns = ['min_anos_formacao', 'count']

    df_linha = df_vagas.copy()
    df_linha = df_linha[(df_linha['senioridade'] != 'Não Especificado')]
    df_linha.set_index('data_publicacao', inplace=True)
    df_linha['salario'] = pd.to_numeric(df_linha['salario'], errors='coerce')
    df_linha_resample = df_linha.groupby('senioridade').resample('W')

    df_comparacao_salarios = pd.DataFrame(list(comparacao_salarios.values()))
    df_foco = df_comparacao_salarios[['junior_clt', 'pleno_clt', 'senior_clt', 'junior_pj', 'pleno_pj', 'senior_pj']]
    df_melt = df_foco.melt(var_name='Categoria', value_name='Salário')
    df_melt['Contrato'] = df_melt['Categoria'].apply(lambda x: 'CLT' if 'clt' in x else 'PJ')
    df_melt['Categoria'] = df_melt['Categoria'].apply(lambda x: x.replace('_clt', '').replace('_pj', ''))

    df_resampled = df_linha_resample['salario'].mean().interpolate()
    df_resampled = df_resampled.reset_index()

    grafico_radar = radar(habilidade_freq, 'count', 'habilidade')
    grafico_barras = barras(formacao_freq, 'min_anos_formacao', 'count')
    grafico_linhas = evolucao_salario(df_resampled)
    grafico_compara = barras_comparacao(df_melt)

    radar_json = pio.to_json(grafico_radar)
    barras_json = pio.to_json(grafico_barras)
    linhas_json = pio.to_json(grafico_linhas)
    compara_json = pio.to_json(grafico_compara)

    df_vaga = df_vagas.copy()
    df_vaga_perfil_especif = df_vaga[(df_vaga['perfil'] != 'Não Especificado') & (df_vaga['perfil'] != 'estágiario')]
    top_perfil = df_vaga_perfil_especif['perfil'].value_counts().head(4)

    df_vaga = df_vagas.copy()
    df_salario_prenc = df_vaga.dropna(subset=['salario'])
    df_vaga_perfil_especif = df_salario_prenc[(df_salario_prenc['senioridade'] != 'Não Especificado') & (df_salario_prenc['senioridade'] != 'estágiario')]
    media_salario_grupo = df_vaga_perfil_especif.groupby('senioridade')['salario'].mean().reset_index()

    salario_medio = df_salario_prenc['salario'].mean()
    qtd_vagas = df_vaga.size

    if newsletter_profissao.count() >= 2:
        newsletters_selecionadas = random.sample(list(newsletter_profissao), 2)
    else:
        newsletters_selecionadas = newsletter_profissao

    if newsletter_empreendedor.count() >= 1:
        newsletters_empreende_selecionadas = random.sample(list(newsletter_empreendedor), 1)
    else:
        newsletters_empreende_selecionadas = newsletter_empreendedor

    if newsletter_mercado.count() >= 1:
        newsletters_mercado_selecionadas = random.sample(list(newsletter_mercado), 1)
    else:
        newsletters_mercado_selecionadas = newsletter_mercado

    context = {
        'profissoes': profissoes,
        'vagas': df_vagas,
        'cliente': cliente,
        'newsletters': news,
        'inscricao_newsletter': inscricao_newsletter,
        'newsletter_profissao': newsletter_profissao,
        'logs': logs,
        'radar_vagas': radar_json,
        'barras_vagas': barras_json,
        'linhas_salario': linhas_json,
        'barras_compara': compara_json,
        'top_perfil': top_perfil,
        'media_salario_grupo':media_salario_grupo,
        'salario_medio': salario_medio,
        'qtd_vagas': qtd_vagas,
        'newsletter_1': newsletters_selecionadas[0] if len(newsletters_selecionadas) > 0 else None,
        'newsletter_2': newsletters_selecionadas[1] if len(newsletters_selecionadas) > 1 else None,
        'news_mercado': newsletters_mercado_selecionadas[0] if len(newsletters_mercado_selecionadas) > 0 else None,
        'news_empreendedor': newsletters_empreende_selecionadas[0] if len(newsletters_empreende_selecionadas) > 0 else None,
    }

    return render(request, 'portal/index.html', context)

def newsletter(request):
    newsletter_dados = Newsletter.objects.all()

    context = {
        'newsletter_dados': newsletter_dados
    }

    return render(request, 'portal/newsletter.html', context)

def newsletter_add(request):
    context = {}

    form_news = NewsletterForm(request.POST or None)

    if form_news.is_valid():
        form_news.save()
        return redirect('newsletter')

    context['form'] = form_news
    return render(request, "portal/newsletter_add.html", context)

def abertura(request):
    profissoes = InfosProfissao.objects.all()
    df_vagas = tratamentos_vagas(1)
    cliente = Cliente.objects.all()
    news = Newsletter.objects.all()
    newsMercado = NewsMercado.objects.all()
    newsEmpreendedor = NewsEmpreendedor.objects.all()
    inscricao_newsletter = InscricaoNewsletter.objects.all()
    newsletter_profissao = NewsletterProfissao.objects.all()
    logs = Logs.objects.all()

    df_vaga = df_vagas.copy()
    df_salario_prenc = df_vaga.dropna(subset=['salario'])
    df_vaga_perfil_especif = df_salario_prenc[(df_salario_prenc['senioridade'] != 'Não Especificado') & (df_salario_prenc['senioridade'] != 'estágiario')]
    media_salario_grupo = df_vaga_perfil_especif.groupby('senioridade')['salario'].mean().reset_index()

    df_vaga = df_vagas.copy()
    df_vaga_perfil_especif = df_vaga[(df_vaga['perfil'] != 'Não Especificado') & (df_vaga['perfil'] != 'estágiario')]
    top_perfil = df_vaga_perfil_especif['perfil'].value_counts().head(4)

    if news.count() >= 4:
        newsletters_selecionadas = random.sample(list(news), 4)
    else:
        newsletters_selecionadas = news

    if newsMercado.count() >= 1:
        newsletters_mercado_selecionadas = random.sample(list(newsMercado), 1)
    else:
        newsletters_mercado_selecionadas = newsMercado

    if newsEmpreendedor.count() >= 1:
        newsletters_empreendedor_selecionadas = random.sample(list(newsEmpreendedor), 1)
    else:
        newsletters_empreendedor_selecionadas = newsEmpreendedor

    context = {
        'profissoes': profissoes,
        'vagas': df_vagas,
        'cliente': cliente,
        'newsletters': news,
        'inscricao_newsletter': inscricao_newsletter,
        'newsletter_profissao': newsletter_profissao,
        'logs': logs,
        'media_salario_grupo': media_salario_grupo,
        'top_perfil': top_perfil,
        'newsletter_1': newsletters_selecionadas[0] if len(newsletters_selecionadas) > 0 else None,
        'newsletter_2': newsletters_selecionadas[1] if len(newsletters_selecionadas) > 1 else None,
        'newsletter_3': newsletters_selecionadas[2] if len(newsletters_selecionadas) > 2 else None,
        'newsletter_4': newsletters_selecionadas[3] if len(newsletters_selecionadas) > 3 else None,
        'news_empreendedor': newsletters_empreendedor_selecionadas[0] if len(newsletters_empreendedor_selecionadas)>0 else None,
        'news_mercado': newsletters_mercado_selecionadas[0] if len(newsletters_empreendedor_selecionadas)>0 else None,
    }

    return render(request, "portal/abertura.html", context)

def cadastro(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('../abertura')
    else:
        form = ClienteForm()

    return render(request, "portal/cadastro.html", {'form': form})

def login_pagina(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('../index')
        else:
            return render(request, 'portal/login.html', {'error': 'Login inválido.'})
    else:
        return render(request, 'portal/login.html')

@login_required
def inscrever_newsletter(request, newsletter_id):
    if request.method == 'POST':
        newsletter = Newsletter.objects.get(id=newsletter_id)
        cliente = Cliente.objects.get(usuario=request.user)
        InscricaoNewsletter.objects.create(cliente=cliente, newsletter=newsletter)

        return redirect('home')
    else:
        return redirect('home')


@login_required
def configuracoes(request):

    return render(request, 'portal/configuracoes.html')



@login_required
@require_POST
def unsubscribe_newsletter(request, newsletter_id):
    try:
        subscription = InscricaoNewsletter.objects.get(newsletter_id=newsletter_id, cliente__usuario=request.user)
        subscription.delete()
        return JsonResponse({'success': True})
    except InscricaoNewsletter.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Subscription not found'})
