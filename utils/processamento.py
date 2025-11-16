import pandas as pd
from sklearn.cluster import KMeans
import streamlit as st

@st.cache_data
def carregar_dados():
    df = pd.read_csv('dados/enem_tratado.csv', sep=';', encoding='latin1', nrows=5000000)

    # Seleção e limpeza das colunas
    df = df.filter(items=[
        'TP_ESCOLA', 'NU_NOTA_MT', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_REDACAO',
        'TP_FAIXA_ETARIA', 'TP_SEXO', 'NO_MUNICIPIO_ESC', 'SG_UF_ESC', 'TP_DEPENDENCIA_ADM_ESC'
    ]).dropna()

    # Faixa etária categorizada
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

    # Ajustes de texto
    df['TP_SEXO'] = df['TP_SEXO'].replace({'M': 'Masculino', 'F': 'Feminino'})
    df['TP_DEPENDENCIA_ADM_ESC'] = df['TP_DEPENDENCIA_ADM_ESC'].astype(str).replace({
        '1.0': 'Federal', '2.0': 'Estadual', '3.0': 'Municipal', '4.0': 'Privada'
    })
    df['TP_ESCOLA'] = df['TP_ESCOLA'].astype(str).replace({
        '1': 'Não Respondeu', '2': 'Pública', '3': 'Privada'
    }).str.strip()
    df = df[df['TP_ESCOLA'] != 'Não Respondeu']

    # Média das notas
    df['MEDIA_NOTAS'] = df[
        ['NU_NOTA_MT', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_REDACAO']
    ].mean(axis=1)

    # Clusterização com K-Means
    kmeans = KMeans(n_clusters=3, random_state=42)
    df['CLUSTER'] = kmeans.fit_predict(df[['MEDIA_NOTAS']])

    return df

# Função auxiliar para filtrar dependência administrativa
def filtrar_dependencia(df, tipo_escola):
    if tipo_escola == 'Pública':
        return df[df['TP_DEPENDENCIA_ADM_ESC'] != 'Privada']
    elif tipo_escola == 'Privada':
        return df[df['TP_DEPENDENCIA_ADM_ESC'] == 'Privada']
    return df

# Função auxiliar para preparar médias por disciplina
def preparar_media_disciplinas(df):
    disciplinas = ['NU_NOTA_MT', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_REDACAO']
    disciplinas_legenda = {
        'NU_NOTA_MT': 'Matemática',
        'NU_NOTA_CN': 'Ciências da Natureza',
        'NU_NOTA_CH': 'Ciências Humanas',
        'NU_NOTA_LC': 'Linguagens e Códigos',
        'NU_NOTA_REDACAO': 'Redação',
        'MEDIA_NOTAS': 'Média Geral'
    }

    media_disciplinas = df.groupby('TP_ESCOLA')[disciplinas].mean()
    media_geral = df.groupby('TP_ESCOLA')['MEDIA_NOTAS'].mean()
    media_disciplinas['MEDIA_NOTAS'] = media_geral
    media_disciplinas = media_disciplinas.reset_index()

    media_long = media_disciplinas.melt(id_vars='TP_ESCOLA', value_vars=disciplinas + ['MEDIA_NOTAS'],
                                         var_name='Disciplina', value_name='Média')
    media_long['Disciplina'] = media_long['Disciplina'].map(disciplinas_legenda)
    return media_long