import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Dashboard Equipamentos AT",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar dados com tratamento de erro melhorado
@st.cache_data(ttl=3600)  # Cache de 1 hora para evitar memory leaks
def load_data():
    try:
        # Dados de exemplo - substitua pela sua planilha real
        data = {
            'Projeto': ['Intermunicipal', 'Municipal', 'Intermunicipal', 'Municipal'],
            'Fornecedor': ['Autopass', 'Viação São Paulo', 'Autopass', 'Metra'],
            'Modelo': ['K4', 'BX-345', 'K4', 'M200'],
            'C_Arquivo': ['SIM', 'NÃO', 'SIM', 'SIM'],
            'Informacao_arquivo': ['187', '', '189', '205'],
            'Numero_serie': ['SN001', 'SN002', 'SN003', 'SN001'],
            'Defeito': ['Não liga', 'Tela queimada', 'Problema audio', 'Não carrega'],
            'Data_envio': ['2024-01-15', '2024-02-10', '2024-03-05', '2024-01-20'],
            'Data_retorno': ['2024-01-30', '2024-02-25', '2024-03-20', '2024-02-05'],
            'Quantidade': [1, 1, 1, 2],
            'Empresa': ['AVUL', 'VSBL', 'AVUL', 'AVUL'],
            'Filial': ['Osasco', 'Jaguara', 'Osasco', 'Santana']
        }
        df = pd.DataFrame(data)
        
        # Converter datas com tratamento de erro
        df['Data_envio'] = pd.to_datetime(df['Data_envio'], errors='coerce')
        df['Data_retorno'] = pd.to_datetime(df['Data_retorno'], errors='coerce')
        
        # Remover linhas com datas inválidas
        df = df.dropna(subset=['Data_envio'])
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = load_data()

# Sidebar - Filtros
st.sidebar.header("🔧 Filtros")

# Verificar se há dados antes de prosseguir
if df.empty:
    st.error("❌ Não há dados para exibir. Verifique a fonte de dados.")
    st.stop()

# Filtro por período com validação
try:
    min_date = df['Data_envio'].min().date()
    max_date = df['Data_envio'].max().date()
    
    date_range = st.sidebar.date_input(
        "Período",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
except Exception as e:
    st.sidebar.error("Erro ao carregar filtro de datas")
    date_range = [df['Data_envio'].min().date(), df['Data_envio'].max().date()]

# Filtros múltiplos com validação
try:
    empresa_filter = st.sidebar.multiselect(
        "Empresa",
        options=df['Empresa'].unique(),
        default=df['Empresa'].unique()
    )

    projeto_filter = st.sidebar.multiselect(
        "Projeto", 
        options=df['Projeto'].unique(),
        default=df['Projeto'].unique()
    )
    
    # Aplicar filtros com validação
    if empresa_filter and projeto_filter:
        df_filtered = df[
            (df['Empresa'].isin(empresa_filter)) & 
            (df['Projeto'].isin(projeto_filter))
        ]
    else:
        df_filtered = df.copy()
        
except Exception as e:
    st.error(f"Erro ao aplicar filtros: {e}")
    df_filtered = df.copy()

# BUSCADOR POR NÚMERO DE SÉRIE
st.sidebar.header("🔍 Buscar Equipamento")
numero_serie_busca = st.sidebar.text_input("Digite o número de série:")

# LAYOUT PRINCIPAL
st.title("📊 Dashboard de Equipamentos - Assistência Técnica")

try:
    if numero_serie_busca:
        # BUSCA ESPECÍFICA com tratamento de erro
        equipamento_data = df[df['Numero_serie'] == numero_serie_busca]
        
        if not equipamento_data.empty:
            st.header(f"🔍 Equipamento: {numero_serie_busca}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("📋 Dados do Equipamento")
                st.write(f"**Modelo:** {equipamento_data['Modelo'].iloc[0]}")
                st.write(f"**Fornecedor:** {equipamento_data['Fornecedor'].iloc[0]}")
                st.write(f"**Empresa/Filial:** {equipamento_data['Empresa'].iloc[0]} - {equipamento_data['Filial'].iloc[0]}")
                st.write(f"**Projeto:** {equipamento_data['Projeto'].iloc[0]}")
            
            with col2:
                st.subheader("🔄 Histórico")
                total_envios = len(equipamento_data)
                st.metric("Total de Envios", total_envios)
                st.write(f"**Primeiro envio:** {equipamento_data['Data_envio'].min().strftime('%d/%m/%Y')}")
                st.write(f"**Último envio:** {equipamento_data['Data_envio'].max().strftime('%d/%m/%Y')}")
                
                # Status atual com tratamento de NaN
                ultimo_envio = equipamento_data.loc[equipamento_data['Data_envio'].idxmax()]
                if pd.isna(ultimo_envio['Data_retorno']):
                    st.error("⏳ Status: Em assistência")
                else:
                    st.success("✅ Status: Retornado")
            
            with col3:
                st.subheader("📊 Métricas")
                # Tempo médio em assistência com tratamento
                tempos_delta = (equipamento_data['Data_retorno'] - equipamento_data['Data_envio']).dt.days
                tempos_media = tempos_delta.mean()
                if not pd.isna(tempos_media):
                    st.metric("Tempo médio AT", f"{tempos_media:.0f} dias")
                else:
                    st.metric("Tempo médio AT", "N/A")
                
                # Fornecedor mais usado
                if not equipamento_data['Fornecedor'].empty:
                    fornecedor_mais_comum = equipamento_data['Fornecedor'].mode()
                    if not fornecedor_mais_comum.empty:
                        st.write(f"**Fornecedor mais usado:** {fornecedor_mais_comum.iloc[0]}")
            
            # TABELA DE HISTÓRICO COMPLETO
            st.subheader("📋 Histórico Completo de Assistências")
            historico_cols = ['Data_envio', 'Data_retorno', 'Defeito', 'Fornecedor', 'C_Arquivo']
            st.dataframe(equipamento_data[historico_cols].sort_values('Data_envio', ascending=False))
            
        else:
            st.warning("❌ Número de série não encontrado")

    else:
        # DASHBOARD GERAL
        
        # KPIs PRINCIPAIS com verificação de dados
        st.header("📈 Métricas Gerais")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_envios = len(df_filtered)
            st.metric("Total de Envios", total_envios)
        
        with col2:
            equipamentos_unicos = df_filtered['Numero_serie'].nunique()
            st.metric("Equipamentos Únicos", equipamentos_unicos)
        
        with col3:
            # Calcular tempo médio com tratamento
            tempos_delta = (df_filtered['Data_retorno'] - df_filtered['Data_envio']).dt.days
            tempo_medio = tempos_delta.mean()
            if not pd.isna(tempo_medio):
                st.metric("Tempo Médio AT", f"{tempo_medio:.0f} dias")
            else:
                st.metric("Tempo Médio AT", "N/A")
        
        with col4:
            reincidentes = df_filtered['Numero_serie'].value_counts()
            equipamentos_reincidentes = (reincidentes > 1).sum()
            st.metric("Equipamentos Reincidentes", equipamentos_reincidentes)
        
        # GRÁFICOS apenas se houver dados
        if not df_filtered.empty:
            st.header("📊 Análises Visuais")
            
            # 1. GRÁFICO MENSAL - TODOS FORNECEDORES
            st.subheader("📅 Volume Mensal - Todos Fornecedores")
            
            try:
                df_mensal = df_filtered.groupby(df_filtered['Data_envio'].dt.to_period('M')).size().reset_index()
                df_mensal['Data_envio'] = df_mensal['Data_envio'].dt.to_timestamp()
                
                fig_mensal = px.line(
                    df_mensal, 
                    x='Data_envio', 
                    y=0,
                    title="Total de Envios por Mês",
                    labels={'0': 'Quantidade', 'Data_envio': 'Mês'}
                )
                st.plotly_chart(fig_mensal, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao criar gráfico mensal: {e}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 2. RANKING FORNECEDORES
                st.subheader("🏆 Ranking por Fornecedor")
                try:
                    fornecedores_count = df_filtered['Fornecedor'].value_counts()
                    fig_fornecedores = px.bar(
                        fornecedores_count,
                        title="Total de Envios por Fornecedor",
                        labels={'value': 'Quantidade', 'index': 'Fornecedor'}
                    )
                    st.plotly_chart(fig_fornecedores, use_container_width=True)
                except Exception as e:
                    st.error(f"Erro ao criar gráfico de fornecedores: {e}")
            
            with col2:
                # 3. DISTRIBUIÇÃO POR PROJETO/EMPRESA
                st.subheader("🏢 Distribuição por Empresa")
                try:
                    empresa_count = df_filtered['Empresa'].value_counts()
                    fig_empresa = px.pie(
                        empresa_count,
                        values=empresa_count.values,
                        names=empresa_count.index,
                        title="Distribuição por Empresa"
                    )
                    st.plotly_chart(fig_empresa, use_container_width=True)
                except Exception as e:
                    st.error(f"Erro ao criar gráfico de empresas: {e}")
            
            # 4. GRÁFICOS INDIVIDUAIS POR FORNECEDOR (TOP 5)
            st.subheader("📈 Evolução Mensal por Fornecedor (Top 5)")
            
            try:
                top_fornecedores = df_filtered["Fornecedor"].value_counts().head(5).index
                
                for fornecedor in top_fornecedores:
                    df_fornecedor = df_filtered[df_filtered["Fornecedor"] == fornecedor]
                    if not df_fornecedor.empty:
                        df_fornecedor_mensal = df_fornecedor.groupby(
                            df_fornecedor['Data_envio'].dt.to_period('M')
                        ).size().reset_index()
                        df_fornecedor_mensal['Data_envio'] = df_fornecedor_mensal['Data_envio'].dt.to_timestamp()

                        fig = px.line(
                            df_fornecedor_mensal,
                            x="Data_envio",
                            y=0,
                            title=f"{fornecedor} - Evolução Mensal"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao criar gráficos por fornecedor: {e}")
        
        # TABELA DETALHADA
        st.header("📋 Dados Detalhados")
        st.dataframe(df_filtered)

except Exception as e:
    st.error(f"❌ Ocorreu um erro na aplicação: {e}")
    st.info("📞 Entre em contato com o suporte técnico")

# Rodapé
st.sidebar.markdown("---")
st.sidebar.info("📞 Suporte: equipe@empresa.com")

# Limpeza de recursos (importante para estabilidade)
import gc
gc.collect()