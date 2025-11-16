import pandas as pd
import streamlit as st
import plotly.express as px

PALETA_CORES = [
    '#003366',  # Azul marinho profundo
    '#1f77b4',  # Azul clássico
    '#3399ff',  # Azul vibrante
    '#7fb3d5',  # Azul pastel claro
    '#005f99',  # Azul petróleo
    '#66c2ff',  # Azul céu
    '#2e86c1',  # Azul royal
    '#154360'   # Azul escuro acinzentado
]

# --- Carregar e preparar os dados ---
@st.cache_data
def carregar_dados():
    df = pd.read_csv('dados/enem_tratado.csv', sep=';', encoding='latin1', nrows=5000000)

    df = df.filter(items=[
        'TP_ESCOLA', 'NU_NOTA_MT', 'NU_NOTA_CN', 'NU_NOTA_CH','NU_NOTA_LC', 'NU_NOTA_REDACAO',
        'TP_FAIXA_ETARIA', 'TP_SEXO','NO_MUNICIPIO_ESC','SG_UF_ESC','TP_DEPENDENCIA_ADM_ESC'
    ]).dropna()

    df['TP_FAIXA_ETARIA'] = df['TP_FAIXA_ETARIA'].astype(str).replace({
        '1': 'Menor de 17 anos',
        '2': '17 anos',
        '3': '18 anos',
        '4': '19 anos',
        '5': '20 anos',
        '6': '21 anos',
        '7': '22 anos',
        '8': '23 anos',
        '9': '24 anos',
        '10': '25 anos',
        '11': 'Entre 26 e 30 anos',
        '12': 'Entre 31 e 35 anos',
        '13': 'Entre 36 e 40 anos',
        '14': 'Entre 41 e 45 anos',
        '15': 'Entre 46 e 50 anos',
        '16': 'Entre 51 e 55 anos',
        '17': 'Entre 56 e 60 anos',
        '18': 'Entre 61 e 65 anos',
        '19': 'Entre 66 e 70 anos',
        '20': 'Maior de 70 anos'})
    
    ordem_faixas = [
    'Menor de 17 anos', '17 anos', '18 anos', '19 anos', '20 anos', '21 anos', '22 anos', '23 anos', '24 anos',
    '25 anos', 'Entre 26 e 30 anos', 'Entre 31 e 35 anos', 'Entre 36 e 40 anos', 'Entre 41 e 45 anos',
    'Entre 46 e 50 anos', 'Entre 51 e 55 anos', 'Entre 56 e 60 anos', 'Entre 61 e 65 anos',
    'Entre 66 e 70 anos', 'Maior de 70 anos']

    df['TP_FAIXA_ETARIA'] = pd.Categorical(df['TP_FAIXA_ETARIA'], categories=ordem_faixas, ordered=True)
    
    df['TP_SEXO'] = df['TP_SEXO'].replace({'M': 'Masculino', 'F': 'Feminino'})
    
    df['TP_DEPENDENCIA_ADM_ESC'] = df['TP_DEPENDENCIA_ADM_ESC'].astype(str).replace({
        '1.0': 'Federal', '2.0': 'Estadual', '3.0': 'Municipal', '4.0': 'Privada'
    })
    df['TP_ESCOLA'] = df['TP_ESCOLA'].astype(str).replace({
        '1': 'Não Respondeu', '2': 'Pública', '3': 'Privada'})
    
    df['TP_ESCOLA'] = df['TP_ESCOLA'].str.strip()
    df = df[df['TP_ESCOLA'] != 'Não Respondeu']

    df['MEDIA_NOTAS'] = df[
        ['NU_NOTA_MT', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_REDACAO']
    ].mean(axis=1)

    return df

df = carregar_dados()

# --- Sidebar com filtros ---
st.sidebar.header("Filtros")

sexo = st.sidebar.selectbox("Sexo", options=['Todos', 'Masculino', 'Feminino'])
escola = st.sidebar.selectbox("Tipo de Escola", options=['Todos', 'Pública', 'Privada'])
# Filtro de Estado
ufs = ['Todos'] + sorted(df['SG_UF_ESC'].unique())
estado = st.sidebar.selectbox("Estado da Escola", options=ufs)

# Filtrar DataFrame temporariamente para obter municípios do estado selecionado
if estado != 'Todos':
    municipios_filtrados = sorted(df[df['SG_UF_ESC'] == estado]['NO_MUNICIPIO_ESC'].unique())
else:
    municipios_filtrados = sorted(df['NO_MUNICIPIO_ESC'].unique())

# Filtro de Município com base no estado selecionado
municipios = ['Todos'] + municipios_filtrados
municipio = st.sidebar.selectbox("Município da Escola", options=municipios)
 
# --- Aplicar filtros ---
df_filtrado = df.copy()

if sexo != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['TP_SEXO'] == sexo]

if escola != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['TP_ESCOLA'] == escola]

if estado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['SG_UF_ESC'] == estado]

if municipio != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['NO_MUNICIPIO_ESC'] == municipio]

# --- Gráfico de Sexo ---
sexo_counts = df_filtrado['TP_SEXO'].value_counts().reset_index()
sexo_counts.columns = ['Sexo', 'Quantidade']
fig_sexo = px.pie(sexo_counts, names='Sexo', values='Quantidade',
                  title='Distribuição por Sexo', hole=0.4,
                  color_discrete_sequence=PALETA_CORES)
fig_sexo.update_traces(textinfo='label+percent',
                       hovertemplate='%{label}<br>Quantidade: %{value}<br>Porcentagem: %{percent}')

# --- Gráfico de Tipo de Escola ---
escola_counts = df_filtrado['TP_ESCOLA'].value_counts().reset_index()
escola_counts.columns = ['TipoEscola', 'Quantidade']
fig_escola = px.pie(escola_counts, names='TipoEscola', values='Quantidade',
                    title='Tipo de Escola', hole=0.4,
                    color_discrete_sequence=PALETA_CORES)
fig_escola.update_traces(textinfo='label+percent',
                         hovertemplate='%{label}<br>Quantidade: %{value}<br>Porcentagem: %{percent}')

# --- Gráfico de Dependência Administrativa ---
dependencia_filtrada = df_filtrado.copy()
if escola == 'Pública':
    dependencia_filtrada = dependencia_filtrada[dependencia_filtrada['TP_DEPENDENCIA_ADM_ESC'] != 'Privada']
elif escola == 'Privada':
    dependencia_filtrada = dependencia_filtrada[dependencia_filtrada['TP_DEPENDENCIA_ADM_ESC'] == 'Privada']

dependencia_counts = dependencia_filtrada['TP_DEPENDENCIA_ADM_ESC'].value_counts().reset_index()
dependencia_counts.columns = ['Dependencia', 'Quantidade']
fig_dependencia = px.pie(dependencia_counts, names='Dependencia', values='Quantidade',
                         title='Dependência Administrativa', hole=0.4,
                         color_discrete_sequence=PALETA_CORES)
fig_dependencia.update_traces(textinfo='label+percent',
                              hovertemplate='%{label}<br>Quantidade: %{value}<br>Porcentagem: %{percent}')

# Contagem por faixa etária
faixa_counts = df_filtrado['TP_FAIXA_ETARIA'].value_counts().reset_index()
faixa_counts.columns = ['FaixaEtaria', 'Quantidade']

# Gráfico de rosca
fig_faixa = px.pie(
    faixa_counts,
    names='FaixaEtaria',
    values='Quantidade',
    title='Distribuição por Faixa Etária',
    hole=0.4,
    color_discrete_sequence=PALETA_CORES
)

fig_faixa.update_traces(
    textinfo='label+percent',
    hovertemplate='%{label}<br>Quantidade: %{value}<br>Porcentagem: %{percent}'
)

# --- Exibir os gráficos ---
st.title("Análise ENEM 2023")

col1, col2, col3 = st.columns(3)
with col1:
    st.plotly_chart(fig_sexo, use_container_width=True)
with col2:
    st.plotly_chart(fig_escola, use_container_width=True)
with col3:
    st.plotly_chart(fig_dependencia, use_container_width=True)

# --- Gráfico de Médias por Disciplina e Tipo de Escola + Média Geral ---
disciplinas = ['NU_NOTA_MT', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_REDACAO']
disciplinas_legenda = {
    'NU_NOTA_MT': 'Matemática',
    'NU_NOTA_CN': 'Ciências da Natureza',
    'NU_NOTA_CH': 'Ciências Humanas',
    'NU_NOTA_LC': 'Linguagens e Códigos',
    'NU_NOTA_REDACAO': 'Redação',
    'MEDIA_NOTAS': 'Média Geral'
}

# Calcular médias por disciplina e tipo de escola
media_disciplinas = df_filtrado.groupby('TP_ESCOLA')[disciplinas].mean()

# Calcular média geral por tipo de escola
media_geral = df_filtrado.groupby('TP_ESCOLA')['MEDIA_NOTAS'].mean()

# Adicionar média geral ao DataFrame
media_disciplinas['MEDIA_NOTAS'] = media_geral

# Resetar índice para transformar em DataFrame
media_disciplinas = media_disciplinas.reset_index()

# Transformar para formato longo (long format)
media_long = media_disciplinas.melt(id_vars='TP_ESCOLA', value_vars=disciplinas + ['MEDIA_NOTAS'],
                                     var_name='Disciplina', value_name='Média')
media_long['Disciplina'] = media_long['Disciplina'].map(disciplinas_legenda)

# Criar gráfico de barras agrupadas
fig_disciplinas = px.bar(
    media_long,
    x='Disciplina',
    y='Média',
    color='TP_ESCOLA',
    barmode='group',
    title='Média por Disciplina e Tipo de Escola',
    color_discrete_sequence=PALETA_CORES,
    labels={'TP_ESCOLA': 'Tipo de Escola'}
)

fig_disciplinas.update_layout(xaxis_title='Disciplina', yaxis_title='Média das Notas')

# Exibir o gráfico
st.plotly_chart(fig_disciplinas, use_container_width=True)

# --- Gráfico de Linha Curva por Faixa Etária ---
faixa_counts = df_filtrado['TP_FAIXA_ETARIA'].value_counts().sort_index().reset_index()
faixa_counts.columns = ['FaixaEtaria', 'Quantidade']

fig_linha_faixa = px.line(
    faixa_counts,
    x='FaixaEtaria',
    y='Quantidade',
    title='Distribuição por Faixa Etária (Linha Curva)',
    markers=True,
    line_shape='spline'
)

fig_linha_faixa.update_traces(
    hovertemplate='%{x}<br>Quantidade: %{y}',
    line=dict(color='#3399ff', width=3)
)

fig_linha_faixa.update_layout(
    xaxis_title='Faixa Etária',
    yaxis_title='Quantidade de Participantes',
    xaxis_tickangle=-45
)

# Exibir o gráfico
st.plotly_chart(fig_linha_faixa, use_container_width=True)