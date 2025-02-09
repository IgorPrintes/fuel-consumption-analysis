import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(layout='wide')

# Função para carregar dados
def load_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    return None

# Função para formatar números
def formata_numero(valor, prefixo=''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

# Função para converter DataFrame em CSV
def converte_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Página 1: Dados Brutos
def pagina_dados_brutos(df):
    st.title(' 🚗 DADOS BRUTOS - CONSUMO DE COMBUSTÍVEL E EMISSÕES ⛽')

    with st.expander('Colunas'):
        colunas = st.multiselect(
            'Selecione as colunas', 
            list(df.columns), 
            list(df.columns),
            placeholder="Escolha as colunas"
        )

    st.sidebar.title('Filtros')
    with st.sidebar.expander('Fabricante'):
        fabricantes = st.multiselect(
            'Selecione os fabricantes', 
            df['MAKE'].unique(), 
            df['MAKE'].unique(),
            placeholder="Escolha o Fabricante"
        )
    with st.sidebar.expander('Classe do veículo'):
        classes = st.multiselect(
            'Selecione as classes', 
            df['VEHICLECLASS'].unique(), 
            df['VEHICLECLASS'].unique(),
            placeholder="Escolha a Classe"
        )
    with st.sidebar.expander('Tipo de combustível'):
        combustiveis = st.multiselect(
            'Selecione os combustíveis', 
            df['FUELTYPE'].unique(), 
            df['FUELTYPE'].unique(),
            placeholder="Escolha o Combustível"
        )
    with st.sidebar.expander('Tamanho do motor'):
        engine_size = st.slider(
            'Selecione o tamanho do motor (L)', 
            float(df['ENGINESIZE'].min()), 
            float(df['ENGINESIZE'].max()), 
            (float(df['ENGINESIZE'].min()), float(df['ENGINESIZE'].max()))
        )
    with st.sidebar.expander('Emissões de CO2'):
        co2 = st.slider(
            'Selecione as emissões de CO2 (g/km)', 
            int(df['CO2EMISSIONS'].min()), 
            int(df['CO2EMISSIONS'].max()), 
            (int(df['CO2EMISSIONS'].min()), int(df['CO2EMISSIONS'].max()))
        )

    query = '''
    MAKE in @fabricantes and \
    VEHICLECLASS in @classes and \
    FUELTYPE in @combustiveis and \
    ENGINESIZE >= @engine_size[0] and ENGINESIZE <= @engine_size[1] and \
    CO2EMISSIONS >= @co2[0] and CO2EMISSIONS <= @co2[1]
    '''

    dados_filtrados = df.query(query)
    dados_filtrados = dados_filtrados[colunas]

    st.dataframe(dados_filtrados)
    st.markdown(f'A tabela possui **{dados_filtrados.shape[0]}** linhas e **{dados_filtrados.shape[1]}** colunas')

    st.markdown('**Download dos dados filtrados:**')
    col1, col2 = st.columns(2)
    with col1:
        nome_arquivo = st.text_input('Nome do arquivo:', 'dados_filtrados.csv')
    with col2:
        st.download_button(
            'Baixar CSV',
            data=converte_csv(dados_filtrados),
            file_name=nome_arquivo,
            mime='text/csv'
        )

# Página 2: Dashboard
def pagina_dashboard(df):
    st.title('🚗 DASHBOARD - EMISSÕES E CONSUMO ⛽')

    st.sidebar.title('Filtros')
    fabricante = st.sidebar.multiselect(
        'Fabricante', 
        df['MAKE'].unique(),
        placeholder="Escolha o Fabricante"
    )
    tipo_combustivel = st.sidebar.multiselect(
        'Tipo de combustível', 
        df['FUELTYPE'].unique(),
        placeholder="Escolha o Combustível"
    )
    classe_veiculo = st.sidebar.multiselect(
        'Classe do veículo', 
        df['VEHICLECLASS'].unique(),
        placeholder="Escolha a Classe"
    )

    filtered_df = df.copy()
    if fabricante:
        filtered_df = filtered_df[filtered_df['MAKE'].isin(fabricante)]
    if tipo_combustivel:
        filtered_df = filtered_df[filtered_df['FUELTYPE'].isin(tipo_combustivel)]
    if classe_veiculo:
        filtered_df = filtered_df[filtered_df['VEHICLECLASS'].isin(classe_veiculo)]

    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Média de CO₂ (g/km)', f"{filtered_df['CO2EMISSIONS'].mean():.1f}")
    with col2:
        st.metric('Consumo médio combinado', f"{filtered_df['FUELCONSUMPTION_COMB'].mean():.1f} L/100km")
    with col3:
        st.metric('Tamanho médio do motor', f"{filtered_df['ENGINESIZE'].mean():.1f} L")

    # Abas
    tab1, tab2, tab3 = st.tabs([
        "Relação Motor-CO₂", 
        "Emissões por Classe", 
        "Consumo Combinado"
    ])

    with tab1:
        st.subheader("Relação entre Tamanho do Motor e Emissões de CO₂")
        fig1 = px.scatter(
            filtered_df,
            x='ENGINESIZE',
            y='CO2EMISSIONS',
            color='FUELTYPE',
            labels={
                'ENGINESIZE': 'Tamanho do Motor (L)',
                'CO2EMISSIONS': 'Emissões de CO₂ (g/km)',
                'FUELTYPE': 'Tipo de Combustível'
            }
        )
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        st.subheader("Distribuição de Emissões por Classe de Veículo")
        fig2 = px.box(
            filtered_df,
            x='VEHICLECLASS',
            y='CO2EMISSIONS',
            labels={
                'VEHICLECLASS': 'Classe do Veículo',
                'CO2EMISSIONS': 'Emissões de CO₂ (g/km)'
            }
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.subheader("Distribuição do Consumo de Combustível Combinado")
        fig3 = px.histogram(
            filtered_df,
            x='FUELCONSUMPTION_COMB',
            nbins=30,
            labels={
                'FUELCONSUMPTION_COMB': 'Consumo Combinado (L/100km)'
            }
        )
        fig3.update_layout(
            bargap=0.1,
            bargroupgap=0.05,
            yaxis_title='Quantidade de Veículos',
            xaxis_title='Consumo Combinado (L/100km)'
        )
        st.plotly_chart(fig3, use_container_width=True)

# Interface principal
def main():
    st.sidebar.title("Carregar Dados")
    uploaded_file = st.sidebar.file_uploader(
        "Selecione o arquivo FuelConsumptionCo2.csv",
        type=["csv"],
        accept_multiple_files=False
    )

    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        if df is not None:
            pagina = st.sidebar.selectbox(
                'Selecione a página', 
                ['Dados Brutos', 'Dashboard'],
                placeholder="Escolha a Página"
            )
            
            if pagina == 'Dados Brutos':
                pagina_dados_brutos(df)
            else:
                pagina_dashboard(df)
    else:
        st.warning("Por favor, carregue o arquivo CSV usando o botão na barra lateral")

if __name__ == "__main__":
    main()