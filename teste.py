import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.cluster import KMeans

# --- Paleta de cores azul refinada ---
PALETA_CORES = [
    '#003366', '#1f77b4', '#3399ff', '#7fb3d5',
    '#005f99', '#66c2ff', '#2e86c1', '#154360'
]

# --- Funções auxiliares ---
def ajustar_grafico_rosca(fig):
    fig.update_traces(
        textposition='outside',
        textfont_size=12,
        textinfo='label+percent',
        hovertemplate='%{label}<br>Quantidade: %{value}<br>Porcentagem: %{percent}'
    )
    fig.update_layout(margin=dict(t=60, b=60, l=60, r=60), height=400)
    return fig

def gerar_grafico_rosca(df, nome_coluna, valor_coluna, titulo):
    fig = px.pie(
        df,
        names=nome_coluna,
        values=valor_coluna,
        title=titulo,
        hole=0.4,
        color_discrete_sequence=PALETA_CORES
    )
    return ajustar_grafico_rosca(fig)

def gerar_grafico_barra(df, x, y, color, titulo, legenda):
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        barmode='group',
        title=titulo,
        color_discrete_sequence=PALETA_CORES,
        labels=legenda
    )
    fig.update_layout(xaxis_title=x, yaxis_title=y, height=450)
    return fig

def gerar_piramide_etaria(df):
    piramide = df.groupby(['TP_FAIXA_ETARIA', 'TP_SEXO']).size().reset_index(name='Quantidade')
    piramide['Quantidade'] = piramide.apply(
        lambda row: -row['Quantidade'] if row['TP_SEXO'] == 'Feminino' else row['Quantidade'], axis=1
    )
    fig = px.bar(
        piramide,
        x='Quantidade',
        y='TP_FAIXA_ETARIA',
        color='TP_SEXO',
        orientation='h',
        title='Pirâmide Etária por Sexo',
        color_discrete_map={'Masculino': '#3399ff', 'Feminino': '#7fb3d5'},
        labels={'TP_FAIXA_ETARIA': 'Faixa Etária', 'Quantidade': 'Quantidade'}
    )
    fig.update_layout(height=500, xaxis_title='Quantidade de Participantes', yaxis_title='Faixa Etária')
    return fig

def gerar_grafico_violino(df, x, y, titulo, legenda):
    fig = px.violin(
        df,
        x=x,
        y=y,
        box=True,
        points='all',
        color=x,
        color_discrete_sequence=PALETA_CORES,
        title=titulo,
        labels=legenda
    )
    fig.update_traces(meanline_visible=True, jitter=0.3, marker=dict(size=3, opacity=0.5))
    fig.update_layout(xaxis_title=x, yaxis_title=y, height=450)
    return fig

# --- Carregar e preparar os dados ---
@st.cache_data
def carregar_dados():
    df = pd.read_csv('dados/enem_tratado.csv', sep=';', encoding='latin1', nrows=5000000)

    df = df.filter(items=[
        'TP_ESCOLA', 'NU_NOTA_MT', 'NU_NOTA_CN', 'NU_NOTA_CH','NU_NOTA_LC', 'NU_NOTA_REDACAO',
        'TP_FAIXA_ETARIA', 'TP_SEXO','NO_MUNICIPIO_ESC','SG_UF_ESC','TP_DEPENDENCIA_ADM_ESC'
    ]).dropna()

    df['TP_FAIXA_ETARIA'] = df['TP_FAIXA_ETARIA'].astype(str).replace({
        '1': 'Menor de 17 anos', '2': '17 anos', '3': '18 anos', '4': '19 anos', '5': '20 anos',
        '6': '21 anos', '7': '22 anos', '8': '23 anos', '9': '24 anos', '10': '25 anos',
        '11': 'Entre 26 e 30 anos', '12': 'Entre 31 e 35 anos', '13': 'Entre 36 e 40 anos',
        '14': 'Entre 41 e 45 anos', '15': 'Entre 46 e 50 anos', '16': 'Entre 51 e 55 anos',
        '17': 'Entre 56 e 60 anos', '18': 'Entre 61 e 65 anos', '19': 'Entre 66 e 70 anos',
        '20': 'Maior de 70 anos'
    })

    ordem_faixas = [
        'Menor de 17 anos', '17 anos', '18 anos', '19 anos', '20 anos', '21 anos', '22 anos', '23 anos', '24 anos',
        '25 anos', 'Entre 26 e 30 anos', 'Entre 31 e 35 anos', 'Entre 36 e 40 anos', 'Entre 41 e 45 anos',
        'Entre 46 e 50 anos', 'Entre 51 e 55 anos', 'Entre 56 e 60 anos', 'Entre 61 e 65 anos',
        'Entre 66 e 70 anos', 'Maior de 70 anos'
    ]
    df['TP_FAIXA_ETARIA'] = pd.Categorical(df['TP_FAIXA_ETARIA'], categories=ordem_faixas, ordered=True)

    df['TP_SEXO'] = df['TP_SEXO'].replace({'M': 'Masculino', 'F': 'Feminino'})
    df['TP_DEPENDENCIA_ADM_ESC'] = df['TP_DEPENDENCIA_ADM_ESC'].astype(str).replace({
        '1.0': 'Federal', '2.0': 'Estadual', '3.0': 'Municipal', '4.0': 'Privada'
    })
    df['TP_ESCOLA'] = df['TP_ESCOLA'].astype(str).replace({
        '1': 'Não Respondeu', '2': 'Pública', '3': 'Privada'
    }).str.strip()
    df = df[df['TP_ESCOLA'] != 'Não Respondeu']

    df['MEDIA_NOTAS'] = df[
        ['NU_NOTA_MT', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_REDACAO']
    ].mean(axis=1)

    kmeans = KMeans(n_clusters=3, random_state=42)
    df['CLUSTER'] = kmeans.fit_predict(df[['MEDIA_NOTAS']])

    return df

# --- Interface principal ---
df = carregar_dados()

# --- Sidebar com filtros ---
st.sidebar.header("Filtros")
sexo = st.sidebar.selectbox("Sexo", ['Todos', 'Masculino', 'Feminino'])
escola = st.sidebar.selectbox("Tipo de Escola", ['Todos', 'Pública', 'Privada'])
ufs = ['Todos'] + sorted(df['SG_UF_ESC'].unique())
estado = st.sidebar.selectbox("Estado da Escola", ufs)

municipios_filtrados = sorted(df[df['SG_UF_ESC'] == estado]['NO_MUNICIPIO_ESC'].unique()) if estado != 'Todos' else sorted(df['NO_MUNICIPIO_ESC'].unique())
municipio = st.sidebar.selectbox("Município da Escola", ['Todos'] + municipios_filtrados)

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

# --- Título ---
st.markdown("""
<div style='text-align: center;'>
    <h1>A ESCOLA CONTA?</h1>
    <h4>ANÁLISE DE NOTAS DO ENEM 2023</h4>
    <h4>ANÁLISE DE DADOS E MACHINE LEARNING NA INVESTIGAÇÃO DO DESEMPENHO EDUCACIONAL</h4>
</div>
""", unsafe_allow_html=True)

# --- Pirâmide Etária ---
fig_piramide = gerar_piramide_etaria(df_filtrado)
st.plotly_chart(fig_piramide, use_container_width=True)

# --- Gráficos de Escola ---
escola_counts = df_filtrado['TP_ESCOLA'].value_counts().reset_index()
escola_counts.columns = ['TipoEscola', 'Quantidade']
fig_escola = gerar_grafico_rosca(escola_counts, 'TipoEscola', 'Quantidade', 'Tipo de Escola')

dependencia_filtrada = df_filtrado.copy()
if escola == 'Pública':
    dependencia_filtrada = dependencia_filtrada[dependencia_filtrada['TP_DEPENDENCIA_ADM_ESC'] != 'Privada']
elif escola == 'Privada':
    dependencia_filtrada = dependencia_filtrada[dependencia_filtrada['TP_DEPENDENCIA_ADM_ESC'] == 'Privada']

dependencia_counts = dependencia_filtrada['TP_DEPENDENCIA_ADM_ESC'].value_counts().reset_index()
dependencia_counts.columns = ['Dependencia', 'Quantidade']
fig_dependencia = gerar_grafico_rosca(dependencia_counts, 'Dependencia', 'Quantidade', 'Dependência Administrativa')

# --- Exibir gráficos de escola em duas colunas ---
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_escola, use_container_width=True)
with col2:
    st.plotly_chart(fig_dependencia, use_container_width=True)

# --- Gráfico de Médias por Disciplina ---
disciplinas = ['NU_NOTA_MT', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_REDACAO']
disciplinas_legenda = {
    'NU_NOTA_MT': 'Matemática',
    'NU_NOTA_CN': 'Ciências da Natureza',
    'NU_NOTA_CH': 'Ciências Humanas',
    'NU_NOTA_LC': 'Linguagens e Códigos',
    'NU_NOTA_REDACAO': 'Redação',
    'MEDIA_NOTAS': 'Média Geral'
}

media_disciplinas = df_filtrado.groupby('TP_ESCOLA')[disciplinas].mean()
media_geral = df_filtrado.groupby('TP_ESCOLA')['MEDIA_NOTAS'].mean()
media_disciplinas['MEDIA_NOTAS'] = media_geral
media_disciplinas = media_disciplinas.reset_index()

media_long = media_disciplinas.melt(id_vars='TP_ESCOLA', value_vars=disciplinas + ['MEDIA_NOTAS'],
                                     var_name='Disciplina', value_name='Média')
media_long['Disciplina'] = media_long['Disciplina'].map(disciplinas_legenda)

fig_disciplinas = gerar_grafico_barra(
    media_long,
    x='Disciplina',
    y='Média',
    color='TP_ESCOLA',
    titulo='Média por Disciplina e Tipo de Escola',
    legenda={'TP_ESCOLA': 'Tipo de Escola'}
)

st.plotly_chart(fig_disciplinas, use_container_width=True)

# --- Gráfico Violino: Distribuição da Média das Provas por Tipo de Escola ---
fig_violino = gerar_grafico_violino(
    df,
    x='TP_ESCOLA',
    y='MEDIA_NOTAS',
    titulo='Distribuição da Média das Provas por Tipo de Escola (Gráfico Violino)',
    legenda={'TP_ESCOLA': 'Tipo de Escola', 'MEDIA_NOTAS': 'Média das Notas'}
)

st.plotly_chart(fig_violino, use_container_width=True)