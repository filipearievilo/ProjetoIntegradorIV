import plotly.express as px

PALETA_CORES = [
    '#003366', '#1f77b4', '#3399ff', '#7fb3d5',
    '#005f99', '#66c2ff', '#2e86c1', '#154360'
]

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
    contagem = df[nome_coluna].value_counts().reset_index()
    contagem.columns = [nome_coluna, 'Quantidade']
    fig = px.pie(
        contagem,
        names=nome_coluna,
        values='Quantidade',
        title=titulo,
        hole=0.4,
        color_discrete_sequence=PALETA_CORES
    )
    return ajustar_grafico_rosca(fig)

def gerar_grafico_barra(df, x, y, color, titulo, legenda):
    fig = px.bar(
        df, x=x, y=y, color=color,
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
        df, x=x, y=y, box=True, points='all', color=x,
        color_discrete_sequence=PALETA_CORES,
        title=titulo,
        labels=legenda
    )
    fig.update_traces(meanline_visible=True, jitter=0.3, marker=dict(size=3, opacity=0.5))
    fig.update_layout(xaxis_title=x, yaxis_title=y, height=450)
    return fig