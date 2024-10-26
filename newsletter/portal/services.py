import pandas as pd
import re
from .models import InfosProfissao, VagaEmprego, Cliente, Newsletter, InscricaoNewsletter, NewsletterProfissao, Logs
from datetime import datetime, date, timedelta

def tratamentos_vagas(profissao_id):
    #df_infos_profissao = pd.DataFrame(list(InfosProfissao.objects.all().values()))
    # df_vaga_emprego = pd.DataFrame(list(VagaEmprego.objects.all().values()))
    df_vaga_emprego = pd.DataFrame(
    list(
        VagaEmprego.objects.select_related('profissao').values(
            'id', 'nome_vaga', 'salario', 'descricao_vaga', 'link_vaga', 
            'data_publicacao', 'profissao_id', 'profissao__nome_profissao', 'estado'
        )
    )
)

    df_vaga_emprego.rename(columns={'profissao__nome_profissao': 'nome_profissao'}, inplace=True)

    #df_cliente = pd.DataFrame(list(Cliente.objects.all().values()))
    #df_newsletter = pd.DataFrame(list(Newsletter.objects.all().values()))
    #df_inscricao_newsletter = pd.DataFrame(list(InscricaoNewsletter.objects.all().values()))
    #df_newsletter_profissao = pd.DataFrame(list(NewsletterProfissao.objects.all().values()))
    #df_logs = pd.DataFrame(list(Logs.objects.all().values()))
    print(df_vaga_emprego.columns)
    df_vaga_raw = df_vaga_emprego.copy()
    df_vaga = df_vaga_raw[df_vaga_raw['profissao_id'] == profissao_id]
    df_vaga.loc[:, 'senioridade'] = df_vaga['nome_vaga'].apply(verificar_senioridade)

    df_vaga['perfil'] = df_vaga.apply(verificar_perfil_mais_buscado, axis=1)

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


def verificar_perfil_mais_buscado(row):

    nome_vaga = row['nome_vaga']
    profissao = row['nome_profissao']
    
    if 'advogado' in profissao.lower():
        if re.search(r'trabalhista|do trabalho', nome_vaga, re.IGNORECASE):
            return 'Adv. Trabalhista'
        elif re.search(r'analista', nome_vaga, re.IGNORECASE):
            return 'Analista Jurídico'
        elif re.search(r'cível|civil|civel', nome_vaga, re.IGNORECASE):
            return 'Adv. Cível'
        elif re.search(r'tributário|tributária', nome_vaga, re.IGNORECASE):
            return 'Adv. Tributário'
        elif re.search(r'empresárial|empresarial', nome_vaga, re.IGNORECASE):
            return 'Adv. Empresárial'
        elif re.search(r'contratos', nome_vaga, re.IGNORECASE):
            return 'Adv. Contratos'
        elif re.search(r'estágiario|estagiario|estágio|estagio', nome_vaga, re.IGNORECASE):
            return 'Adv. Estágiario'
        elif re.search(r'aduaneiro', nome_vaga, re.IGNORECASE):
            return 'Adv. Aduaneiro'
        elif re.search(r'societario|societário', nome_vaga, re.IGNORECASE):
            return 'Adv. Societario'
        elif re.search(r'securitário|securitario', nome_vaga, re.IGNORECASE):
            return 'Adv. Securitário'
        elif re.search(r'mercado de capitais', nome_vaga, re.IGNORECASE):
            return 'Adv. Mercado de Capitais'
        elif re.search(r'assistente', nome_vaga, re.IGNORECASE):
            return 'Assistente Jurídico'
        else:
            return 'Advogado genérico'

    if 'marketing digital' in profissao.lower():
        if re.search(r'gerente em marketing digital', nome_vaga, re.IGNORECASE):
            return 'Gerente em Marketing Digital'
        elif re.search(r'analista', nome_vaga, re.IGNORECASE):
            return 'Analista de Marketing Digital'
        elif re.search(r'midias sociais|social media|mídias socias', nome_vaga, re.IGNORECASE):
            return 'Especialista em Midias Sociais'
        elif re.search(r'Especialista em SEO|Search Engine Optimization|SEO', nome_vaga, re.IGNORECASE):
            return 'Especialista em SEO'
        elif re.search(r'Especialista em SEM|Search Engine Marketing|SEM', nome_vaga, re.IGNORECASE):
            return 'Especialista em SEM'
        elif re.search(r'dados', nome_vaga, re.IGNORECASE):
            return 'Analista de dados de Marketing'
        elif re.search(r'estágiario|estagiario|estágio|estagio', nome_vaga, re.IGNORECASE):
            return 'Estágiario em Marketing Digital'
        elif re.search(r'assistente', nome_vaga, re.IGNORECASE):
            return 'Assistente em Marketing Digital'
        elif re.search(r'conteúdo|conteudo', nome_vaga, re.IGNORECASE):
            return 'Gerente de Conteúdo'
        elif re.search(r'e-mail', nome_vaga, re.IGNORECASE):
            return 'Especialista em E-mail de Marketing'
        elif re.search(r'coordenador', nome_vaga, re.IGNORECASE):
            return 'Coordernador de Marketing'
        else:
            return 'Marketing Digital genérico'
            
    if 'desenvolvedor' in profissao.lower():
        if re.search(r'Full Stack|fullstack|full-stack', nome_vaga, re.IGNORECASE):
            return 'Desenvolvedor Full Stack'
        elif re.search(r'Fornt-end|front end|frontend', nome_vaga, re.IGNORECASE):
            return 'Desenvolvedor Front End'
        elif re.search(r'back end|back-end|backend', nome_vaga, re.IGNORECASE):
            return 'Desenvolvedor Back End'
        elif re.search(r'iOS', nome_vaga, re.IGNORECASE):
            return 'Desenvolvedor iOS'
        elif re.search(r'Android|desktop', nome_vaga, re.IGNORECASE):
            return 'Desenvolvedor Android/Desktop'
        elif re.search(r'web', nome_vaga, re.IGNORECASE):
            return 'Desenvolvedor WEB'
        elif re.search(r'analista de sistemas|sistemas|sistema', nome_vaga, re.IGNORECASE):
            return 'Analista de Sistema'
        elif re.search(r'analista desenvolvedor|TI', nome_vaga, re.IGNORECASE):
            return 'Analista Desenvolvedor'
        elif re.search(r'analista de banco de dados|banco de dados|SQL', nome_vaga, re.IGNORECASE):
            return 'Analista de Banco de Dados'
        elif re.search(r'analista programador|programador', nome_vaga, re.IGNORECASE):
            return 'Programador'
        elif re.search(r'product analyst|PA', nome_vaga, re.IGNORECASE):
            return 'Product Analyst'
        elif re.search(r'product manager|PM', nome_vaga, re.IGNORECASE):
            return 'Product Manager'
        elif re.search(r'web design|design', nome_vaga, re.IGNORECASE):
            return 'Web Design'
        elif re.search(r'software', nome_vaga, re.IGNORECASE):
            return 'Desenvolvedor de Software'
        else:
            return 'Desenvolvedor Genérico'

    if 'analista de dados' in profissao.lower():
        if re.search(r'power bi|bi|', nome_vaga, re.IGNORECASE):
            return 'Analista de Power BI'
        elif re.search(r'implementação|implementar', nome_vaga, re.IGNORECASE):
            return 'Analisata de Implementação'
        elif re.search(r'adminitrativo|administração', nome_vaga, re.IGNORECASE):
            return 'Assistente Administrativo'
        elif re.search(r'PCP|PCM', nome_vaga, re.IGNORECASE):
            return 'Analista de PCP/PCM'
        elif re.search(r'dados|data', nome_vaga, re.IGNORECASE):
            return 'Analista de Dados'
        elif re.search(r'backoffice', nome_vaga, re.IGNORECASE):
            return 'Analista e BackOffice'
        elif re.search(r'analista de sistemas|sistemas|sistema', nome_vaga, re.IGNORECASE):
            return 'Analista de Sistema'
        elif re.search(r'analista de suporte|suporte|suport', nome_vaga, re.IGNORECASE):
            return 'Analista de Suporte'
        elif re.search(r'planejamento', nome_vaga, re.IGNORECASE):
            return 'Analista de Planejamento'
        elif re.search(r'analista de projeto|project analyst|projeto|projetos', nome_vaga, re.IGNORECASE):
            return 'Analista de Projetos'
        elif re.search(r'analista de negócios|negócio|negocio|negócios|negocios', nome_vaga, re.IGNORECASE):
            return 'Analista de Projetos'
        else:
            return 'Analista de Dados genérico'


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
    'direito digital': 'direito digital',
    'digital': 'direito digital',
    'trabalho em equipe': 'trabalho em equipe',
    'equipe': 'trabalho em equipe',
    'compliance': 'compliance',
    'gestão de risco': 'gestão de risco',
    'analise de risco': 'gestão de risco',
    'experiência em escritório': 'exp. em escritório',
    'experiencia em escritorio': 'exp. em escritório',
    'office': 'office',
    'ofice': 'office',
    'excel': 'office',
    'outlook': 'office',
    'inglês fluente': 'inglês fluente',
    'fluencia': 'inglês fluente',
    'avançado': 'inglês fluente',
    'intermediário': 'inglês intermediário',
    'intermediario': 'inglês intermediário',
    'inglês intermediario': 'inglês intermediário',
    'lgpd': 'lgpd',
    'lei geral de proteção de dados': 'lgpd',
    'comunicação': 'comunicação efetiva',
    'comunicativa': 'comunicação efetiva',
    'escrita': 'comunicação efetiva',
    'comunicação oral': 'comunicação efetiva',
    'redação': 'comunicação efetiva',
    'cumprir prazos': 'comprometida com as entregas',
    'pontualidade': 'comprometida com as entregas',
    'organização': 'comprometida com as entregas',
    'html': 'conhecimentos em HTML',
    'linguagem de marcação': 'conhecimentos em HTML',
    'css': 'conhecimentos em CSS',
    'folhas de estilo': 'conhecimentos em CSS',
    'javascript': 'conhecimentos em JavaScript',
    'js': 'conhecimentos em JavaScript',
    'java': 'conhecimentos em Java',
    'instagram': 'social media',
    'tiktok': 'social media',
    'facebook': 'social media',
    'twitter': 'social media',
    'linkedin': 'social media',
    'social media marketing': 'social media',
    'marketing em redes sociais': 'social media',
    'capcut': 'conhecimentos de edição',
    'inshot': 'conhecimentos de edição',
    'mojo': 'conhecimentos de edição',
    'edição de vídeo': 'conhecimentos de edição',
    'produção de conteúdo': 'conhecimentos de edição',
    'proatividade': 'proatividade',
    'proativo': 'proatividade',
    'proativa': 'proatividade',
    'iniciativa': 'proatividade',
    'resolução de problemas': 'resolução de problemas',
    'resolver problemas': 'resolução de problemas',
    'solução de problemas': 'resolução de problemas',
    'estratégia': 'pensamento estratégico',
    'estratégico': 'pensamento estratégico',
    'planejamento estratégico': 'pensamento estratégico',
    'estratégio': 'pensamento estratégico',
    'python': 'python',
    'sql': 'sql',
    'mysql': 'sql',
    'linguagem de consulta': 'sql',
    'c#': 'c#',
    'c++': 'c++',
    'banco de dados': 'banco de dados',
    'dml': 'banco de dados',
    'ddl': 'banco de dados',
    'oracle': 'banco de dados',
    'db2': 'banco de dados',
    'experiência jurídica': 'experiência jurídica',
    'advogado': 'experiência jurídica',
    'bacharel em direito': 'experiência jurídica',
    'elaboração de contratos': 'elaboração de contratos',
    'contratos jurídicos': 'elaboração de contratos',
    'contrato': 'elaboração de contratos',
    'pesquisa jurídica': 'pesquisa jurídica',
    'jurisprudência': 'pesquisa jurídica',
    'legislação': 'pesquisa jurídica',
    'petições': 'petições',
    'peças processuais': 'petições',
    'ajuizamento de ações': 'petições',
    'tribunais': 'atuação em tribunais',
    'audiências': 'atuação em tribunais',
    'advocacia contenciosa': 'atuação em tribunais',
    'contencioso': 'atuação em tribunais',
    'seo': 'seo',
    'otimização de sites': 'seo',
    'otimização para mecanismos de busca': 'seo',
    'otimização': 'seo',
    'google analytics': 'google analytics',
    'análise de dados do google': 'google analytics',
    'google': 'google analytics',
    'marketing de conteúdo': 'marketing de conteúdo',
    'blogging': 'marketing de conteúdo',
    'conteúdo': 'marketing de conteúdo',
    'publicidade online': 'publicidade online',
    'google ads': 'publicidade online',
    'facebook ads': 'publicidade online',
    'desenvolvimento web': 'desenvolvimento web',
    'web development': 'desenvolvimento web',
    'web': 'desenvolvimento web',
    'desenvolvimento mobile': 'desenvolvimento mobile',
    'mobile development': 'desenvolvimento mobile',
    'mobile': 'desenvolvimento mobile',
    'frontend': 'frontend',
    'interface do usuário': 'frontend',
    'front-end': 'frontend',
    'front end': 'frontend',
    'backend': 'backend',
    'servidor': 'backend',
    'lógica de negócios': 'backend',
    'back-end': 'backend',
    'back end': 'backend',
    'git': 'git',
    'versionamento de código': 'git',
    'controle de versão': 'git',
    'github': 'git',
    'análise de dados': 'análise de dados',
    'data analysis': 'análise de dados',
    'analytics': 'análise de dados',
    'mineração de dados': 'mineração de dados',
    'data mining': 'mineração de dados',
    'business intelligence': 'business intelligence',
    'bi': 'business intelligence',
    'sql avançado': 'sql avançado',
    'consultas complexas': 'sql avançado',
    'python para análise de dados': 'python para análise de dados',
    'análise de dados com python': 'python para análise de dados'
}


    for habilidade, retorno in habilidades.items():
        if habilidade in descricao_vaga:
            if habilidade in ['revisar contrato', 'analisar contrato', 'elaborar contrato'] and ' contrato' in descricao_vaga:
                return retorno
            return retorno
    return 'Não Especificado'

    


def verificar_requisitos_mais_buscados(descricao_vaga, profissao):
    if not descricao_vaga:
        return 'Não Especificado'
    
    descricao_vaga = descricao_vaga.lower()
    
    requisitos_por_profissao = {
        'advogado': {
            'oab ativa': 'OAB Ativa',
            'oab': 'OAB Ativa',
            'pos-graduação': 'Pós-Graduação',
            'pós graduação': 'Pós-Graduação',
            'graduação cursando': 'Graduação Cursando',
            'graduação completa': 'Graduação Completa',
            'graduação concluída': 'Graduação Completa',
            'formado em direito': 'Formado em Direito',
            'ensino superior concluído': 'Graduação Completa',
            'cursando graduação': 'Graduação Cursando',
            'ensino superior completo': 'Graduação Completa',
            'experiência em área jurídica': 'Experiência na Área Jurídica',
            'experiência com jurídico': 'Experiência na Área Jurídica',
        },
        'marketing digital': {
            'formado em marketing': 'Formado em Marketing',
            'formação em marketing': 'Formado em Marketing',
            'formado em comunicação': 'Formado em Comunicação',
            'formado em jornalismo': 'Formado em Jornalismo',
            'formado em publicidade': 'Formado em Publicidade',
            'experiência em social media': 'Experiência em Social Media',
            'gerenciamento de redes sociais': 'Gerenciamento de Redes Sociais',
            'análise de redes sociais': 'Análise de Redes Sociais',
        },
        'desenvolvedor': {
            'experiência com desenvolvimento web': 'Experiência em Desenvolvimento Web',
            'experiência com desenvolvimento mobile': 'Experiência em Desenvolvimento Mobile',
            'experiência em frontend': 'Experiência em Frontend',
            'experiência em backend': 'Experiência em Backend',
            'conhecimentos em html, css e javascript': 'Conhecimentos em HTML, CSS e JavaScript',
            'experiência com controle de versão (git)': 'Experiência com Controle de Versão (Git)',
            'experiência em sql e bancos de dados relacionais': 'Experiência em SQL e Bancos de Dados Relacionais',
        },
        'analista de dados': {
            'python': 'Experiência com Python para Análise de Dados', 'numpy':'Experiência com Python para Análise de Dados', 'pandas': 'Experiência com Ferramentas de Análise de Dados (pandas, numpy)',
            'experiência com linguagens de programação como python, r ou scala': 'Experiência com Linguagens de Programação como Python, R ou Scala',
            'experiência em ciência de dados e machine learning': 'Experiência em Ciência de Dados e Machine Learning',
        }
    }
    
    if profissao in requisitos_por_profissao:
        requisitos = requisitos_por_profissao[profissao]
        for requisito, retorno in requisitos.items():
            if re.search(r'\b' + re.escape(requisito) + r'\b', descricao_vaga):
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



def extrair_valor_medio(salario):
    if isinstance(salario, str):
        partes = salario.split(' - ')
        if len(partes) == 2:
            valor_min = float(partes[0].replace('R$ ', '').replace('.', '').replace(',', '.'))
            return valor_min
        else:
            try:
                salario_numerico = float(salario.replace('R$ ', '').replace('.', '').replace(',', '.'))
                return salario_numerico
            except ValueError:
                return np.nan
    return np.nan
