import pandas as pd
import re
from .models import InfosProfissao, VagaEmprego, Cliente, Newsletter, InscricaoNewsletter, NewsletterProfissao, Logs
from datetime import datetime, date, timedelta

def tratamentos_vagas(profissao_id):
    #df_infos_profissao = pd.DataFrame(list(InfosProfissao.objects.all().values()))
    df_vaga_emprego = pd.DataFrame(list(VagaEmprego.objects.all().values()))
    #df_cliente = pd.DataFrame(list(Cliente.objects.all().values()))
    #df_newsletter = pd.DataFrame(list(Newsletter.objects.all().values()))
    #df_inscricao_newsletter = pd.DataFrame(list(InscricaoNewsletter.objects.all().values()))
    #df_newsletter_profissao = pd.DataFrame(list(NewsletterProfissao.objects.all().values()))
    #df_logs = pd.DataFrame(list(Logs.objects.all().values()))

    df_vaga_raw = df_vaga_emprego.copy()
    df_vaga = df_vaga_raw[df_vaga_raw['profissao_id'] == profissao_id]
    df_vaga.loc[:, 'senioridade'] = df_vaga['nome_vaga'].apply(verificar_senioridade)

    df_vaga['perfil'] = df_vaga['nome_vaga'].apply(verificar_perfil_mais_buscado)

    df_vaga.loc[:, 'min_anos_formacao'] = extrai_formacao(df_vaga['descricao_vaga'])
    df_vaga.loc[:, 'min_anos_formacao'] = pd.to_numeric(df_vaga['min_anos_formacao'], errors='coerce')

    df_vaga.loc[:, 'min_anos_experiencia'] = extrai_xp(df_vaga['descricao_vaga'])
    df_vaga.loc[:, 'min_anos_experiencia'] = pd.to_numeric(df_vaga['min_anos_experiencia'], errors='coerce')


    df_vaga.loc[:, 'habilidade'] = df_vaga['descricao_vaga'].apply(verificar_habilidades_mais_buscadas)

    df_vaga.loc[:, 'salario'] = df_vaga['salario'].str.extract(r'R\$ ([\d.]+) por mês')[0].astype(str).str.replace('.', '').astype(float)

    arruma_data_publicacao(df_vaga)

    return df_vaga


def verificar_senioridade(nome_vaga):
    if 'estágiario' in nome_vaga.lower() or 'estagiario' in nome_vaga.lower() or 'estágio' in nome_vaga.lower() or 'estagio' in nome_vaga.lower():
        return 'Estágio'
    elif 'junior' in nome_vaga.lower():
        return 'Junior'
    elif 'pleno' in nome_vaga.lower():
        return 'Pleno'
    elif 'senior' in nome_vaga.lower():
        return 'Senior'
    else:
        return 'Não Especificado'

def verificar_perfil_mais_buscado(nome_vaga):
    nome_vaga = nome_vaga.lower()
    if 'trabalhista' in nome_vaga:
        return 'adv. trabalhista'
    elif 'analista' in nome_vaga:
        return 'analista jurídico'
    elif 'cível' in nome_vaga:
        return 'adv. cível'
    elif 'tributário' in nome_vaga:
        return 'adv. tributário'
    elif 'empresárial' in nome_vaga:
        return 'adv. empresárial'
    elif 'contratos' in nome_vaga:
        return 'adv. contratos'
    elif 'estágiario' in nome_vaga or 'estagiario' in nome_vaga or 'estágio' in nome_vaga or 'estagio' in nome_vaga:
        return 'estágiario'
    elif 'aduaneiro' in nome_vaga:
        return 'adv. aduaneiro'
    elif 'societario' in nome_vaga or 'societário' in nome_vaga:
        return 'adv. societario'
    elif 'securitário' in nome_vaga or 'securitario' in nome_vaga:
        return 'adv. securitário'
    elif 'mercado de capitais' in nome_vaga:
        return 'adv. mercado de capitais'
    else:
        return 'Não Especificado'


def extrai_formacao(coluna):
    regex = r"(?:Mais de )?(\d+) anos de forma"
    infos = []
    for texto in coluna:
        matches = list(re.finditer(regex, texto))
        if matches:
            infos.append(matches[0].group(1))
        else:
            infos.append(None)
    return infos

def extrai_xp(coluna):
    regex = r"(?:Mais de )?(\d+) anos de exp"
    infos = []
    for texto in coluna:
        matches = list(re.finditer(regex, texto))
        if matches:
            anos_exp = int(matches[0].group(1))
            if anos_exp < 10:
                infos.append(anos_exp)
            else:
                infos.append(None)
        else:
            infos.append(None)
    return infos


def verificar_habilidades_mais_buscadas(descricao_vaga):
    descricao_vaga = descricao_vaga.lower()
    habilidades = {
        'office': 'office',
        'inglês intermediario': 'inglês intermediario',
        'inglês avançado': 'inglês avançado',
        'inglês fluente': 'inglês fluente',
        'lgpd': 'lgpd',
        'pós graduação': 'pós graduação',
        'pós-graduação': 'pós-graduação',
        'experiência em escritório': 'exp. em escritório',
        'Experiencia em escritorio': 'exp. em escritório',
    }
    for habilidade, retorno in habilidades.items():
        if habilidade in descricao_vaga:
            if habilidade in ['revisar contrato', 'analisar contrato', 'elaborar contrato'] and ' contrato' in descricao_vaga:
                return retorno
            return retorno
    return 'Não Especificado'

def dias_desde_publicacao(data_publicacao):
    if re.search(r'hoje|Recém', data_publicacao, re.IGNORECASE):
        return 0
    match = re.search(r'(\d+)\s+dia', data_publicacao)
    if match:
        return int(match.group(1))
    if "mais de 30 dias" in data_publicacao:
        return 30
    return None

def arruma_data_publicacao(df_vaga):
    hoje = date.today()
    df_vaga.loc[:, 'dias_data_publicacao'] = df_vaga['data_publicacao'].apply(dias_desde_publicacao)
    df_vaga['publicacao_data'] = df_vaga['dias_data_publicacao'].apply(
        lambda x: hoje - timedelta(days=x) if x is not None else None)
    df_vaga.loc[:, 'data_publicacao'] = df_vaga['publicacao_data'].apply(lambda x: x.strftime('%d-%m-%Y'))
    df_vaga.drop(['dias_data_publicacao', 'publicacao_data'], axis=1, inplace=True)
    df_vaga.loc[:, 'data_publicacao'] = pd.to_datetime(df_vaga['data_publicacao'], dayfirst=True)
