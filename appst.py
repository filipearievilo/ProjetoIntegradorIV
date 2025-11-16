import pandas as pd
import streamlit as st
import plotly.express as px

# --- Carregar e preparar os dados ---
@st.cache_data
def carregar_dados():
    df = pd.read_csv('dados/enem_tratado.csv', sep=';', encoding='latin1', nrows=5000)

    df = df.filter(items=[
        'TP_ESCOLA', 'NU_NOTA_MT', 'NU_NOTA_CN', 'NU_NOTA_CH','NU_NOTA_LC', 'NU_NOTA_REDACAO',
        'TP_FAIXA_ETARIA', 'TP_SEXO','NO_MUNICIPIO_ESC','SG_UF_ESC','TP_DEPENDENCIA_ADM_ESC'
    ]).dropna()

    df['TP_SEXO'] = df['TP_SEXO'].replace({'M': 'Masculino', 'F': 'Feminino'})
    df['TP_DEPENDENCIA_ADM_ESC'] = df['TP_DEPENDENCIA_ADM_ESC'].astype(str).replace({
        '1.0': 'Federal', '2.0': 'Estadual', '3.0': 'Municipal', '4.0': 'Privada'
    })
    df['TP_ESCOLA'] = df['TP_ESCOLA'].astype(str).replace({
        '1': 'Não Respondeu', '2': 'Pública', '3': 'Privada'
    })
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

# --- Aplicar filtros ---
df_filtrado = df.copy()

if sexo != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['TP_SEXO'] == sexo]

if escola != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['TP_ESCOLA'] == escola]

# --- Gráfico de Sexo ---
sexo_counts = df_filtrado['TP_SEXO'].value_counts().reset_index()
sexo_counts.columns = ['Sexo', 'Quantidade']
fig_sexo = px.pie(sexo_counts, names='Sexo', values='Quantidade',
                  title='Distribuição por Sexo', hole=0.4,
                  color_discrete_sequence=px.colors.qualitative.Set2)
fig_sexo.update_traces(textinfo='label+percent',
                       hovertemplate='%{label}<br>Quantidade: %{value}<br>Porcentagem: %{percent}')

# --- Gráfico de Tipo de Escola ---
escola_counts = df_filtrado['TP_ESCOLA'].value_counts().reset_index()
escola_counts.columns = ['TipoEscola', 'Quantidade']
fig_escola = px.pie(escola_counts, names='TipoEscola', values='Quantidade',
                    title='Tipo de Escola', hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3)
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
                         color_discrete_sequence=px.colors.qualitative.Pastel)
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
    color_discrete_sequence=px.colors.qualitative.Prism
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