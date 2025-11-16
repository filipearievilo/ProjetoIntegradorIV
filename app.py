import streamlit as st
import pandas as pd
from utils.graficos import (
    gerar_grafico_rosca, gerar_grafico_barra,
    gerar_piramide_etaria, gerar_grafico_violino
)
from utils.processamento import carregar_dados

df = carregar_dados()

# Filtros
st.sidebar.header("Filtros")
sexo = st.sidebar.selectbox("Sexo", ['Todos', 'Masculino', 'Feminino'])
escola = st.sidebar.selectbox("Tipo de Escola", ['Todos', 'Pública', 'Privada'])
ufs = ['Todos'] + sorted(df['SG_UF_ESC'].unique())
estado = st.sidebar.selectbox("Estado da Escola", ufs)
municipios_filtrados = sorted(df[df['SG_UF_ESC'] == estado]['NO_MUNICIPIO_ESC'].unique()) if estado != 'Todos' else sorted(df['NO_MUNICIPIO_ESC'].unique())
municipio = st.sidebar.selectbox("Município da Escola", ['Todos'] + municipios_filtrados)

# Aplicar filtros
df_filtrado = df.copy()
if sexo != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['TP_SEXO'] == sexo]
if escola != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['TP_ESCOLA'] == escola]
if estado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['SG_UF_ESC'] == estado]
if municipio != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['NO_MUNICIPIO_ESC'] == municipio]

# Título
st.markdown("""
<div style='text-align: center;'>
    <h1>A ESCOLA CONTA?</h1>
    <h4>ANÁLISE DE NOTAS DO ENEM 2023</h4>
    <h4>ANÁLISE DE DADOS E MACHINE LEARNING NA INVESTIGAÇÃO DO DESEMPENHO EDUCACIONAL</h4>
</div>
""", unsafe_allow_html=True)

# Gráficos
st.plotly_chart(gerar_piramide_etaria(df_filtrado), use_container_width=True)

# Roscas
from utils.processamento import filtrar_dependencia
fig_escola = gerar_grafico_rosca(df_filtrado, 'TP_ESCOLA', 'TP_ESCOLA', 'Tipo de Escola')
fig_dependencia = gerar_grafico_rosca(filtrar_dependencia(df_filtrado, escola), 'TP_DEPENDENCIA_ADM_ESC', 'TP_DEPENDENCIA_ADM_ESC', 'Dependência Administrativa')

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_escola, use_container_width=True)
with col2:
    st.plotly_chart(fig_dependencia, use_container_width=True)

# Médias por disciplina
from utils.processamento import preparar_media_disciplinas
media_long = preparar_media_disciplinas(df_filtrado)
fig_disciplinas = gerar_grafico_barra(
    media_long, 'Disciplina', 'Média', 'TP_ESCOLA',
    'Média por Disciplina e Tipo de Escola',
    {'TP_ESCOLA': 'Tipo de Escola'}
)
st.plotly_chart(fig_disciplinas, use_container_width=True)

# Violino
fig_violino = gerar_grafico_violino(
    df, 'TP_ESCOLA', 'MEDIA_NOTAS',
    'Distribuição da Média das Provas por Tipo de Escola (Gráfico Violino)',
    {'TP_ESCOLA': 'Tipo de Escola', 'MEDIA_NOTAS': 'Média das Notas'}
)
st.plotly_chart(fig_violino, use_container_width=True)