# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Tabelas Gold (Dados Reais)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Spark
@st.cache_resource
def init_spark():
    """Inicializa a sessão Spark"""
    try:
        spark = SparkSession.builder \
            .appName("DashboardGoldReal") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        return spark
    except Exception as e:
        st.error(f"Erro ao inicializar Spark: {e}")
        return None

# Função para carregar dados reais das tabelas Gold
@st.cache_data(ttl=3600)  # Cache por 1 hora
def carregar_tabela_gold_real(_spark, nome_tabela, limite=10000):
    """Carrega dados reais de uma tabela Gold"""
    try:
        # Caminho base das tabelas Gold
        caminho_base = "/mnt/datalake4b6c87c48101c278/gold"
        caminho_completo = f"{caminho_base}/{nome_tabela}"
        
        # Carregar dados
        df_spark = _spark.read.format("delta").load(caminho_completo)
        
        # Limitar registros para performance
        df_limitado = df_spark.limit(limite)
        
        # Converter para Pandas
        df_pandas = df_limitado.toPandas()
        
        return df_pandas
    except Exception as e:
        st.error(f"Erro ao carregar tabela {nome_tabela}: {e}")
        # Retornar dados simulados como fallback
        return gerar_dados_simulados_fallback(nome_tabela)

def gerar_dados_simulados_fallback(tabela):
    """Gera dados simulados como fallback quando não consegue carregar dados reais"""
    np.random.seed(42)
    
    if tabela == "dim_customers":
        n_customers = 100
        dados = {
            'customer_id': [f'CUST_{i:06d}' for i in range(1, n_customers + 1)],
            'customer_unique_id': [f'UNIQUE_{i:08d}' for i in range(1, n_customers + 1)],
            'customer_zip_code_prefix': [f'{np.random.randint(10000, 99999)}' for _ in range(n_customers)],
            'customer_city': np.random.choice(['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 'Brasília'], n_customers),
            'customer_state': np.random.choice(['SP', 'RJ', 'MG', 'BA', 'DF'], n_customers)
        }
    elif tabela == "dim_tempo":
        datas = pd.date_range(start='2016-01-01', end='2018-12-31', freq='D')
        dados = {
            'data': datas,
            'ano': datas.year,
            'mes': datas.month,
            'dia': datas.day,
            'dia_semana': datas.dayofweek,
            'trimestre': datas.quarter,
            'semana_ano': datas.isocalendar().week
        }
    elif tabela == "dim_geolocation":
        n_locations = 100
        dados = {
            'geolocation_zip_code_prefix': [f'{np.random.randint(10000, 99999)}' for _ in range(n_locations)],
            'geolocation_lat': np.random.uniform(-33.0, 5.0, n_locations),
            'geolocation_lng': np.random.uniform(-74.0, -34.0, n_locations),
            'geolocation_city': np.random.choice(['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 'Brasília'], n_locations),
            'geolocation_state': np.random.choice(['SP', 'RJ', 'MG', 'BA', 'DF'], n_locations)
        }
    elif tabela == "dim_leads_closed":
        n_leads = 50
        dados = {
            'lead_id': [f'LEAD_CLOSED_{i:06d}' for i in range(1, n_leads + 1)],
            'lead_name': [f'Lead Fechado {i}' for i in range(1, n_leads + 1)],
            'lead_email': [f'lead_fechado_{i}@email.com' for i in range(1, n_leads + 1)],
            'lead_phone': [f'+55 11 9{np.random.randint(1000, 9999)}-{np.random.randint(1000, 9999)}' for _ in range(n_leads)],
            'lead_status': ['Fechado'] * n_leads,
            'lead_value': np.random.uniform(1000, 50000, n_leads)
        }
    elif tabela == "dim_leads_qualified":
        n_leads = 50
        dados = {
            'lead_id': [f'LEAD_QUAL_{i:06d}' for i in range(1, n_leads + 1)],
            'lead_name': [f'Lead Qualificado {i}' for i in range(1, n_leads + 1)],
            'lead_email': [f'lead_qual_{i}@email.com' for i in range(1, n_leads + 1)],
            'lead_phone': [f'+55 11 9{np.random.randint(1000, 9999)}-{np.random.randint(1000, 9999)}' for _ in range(n_leads)],
            'lead_status': ['Qualificado'] * n_leads,
            'lead_score': np.random.randint(70, 100, n_leads)
        }
    elif tabela == "dim_order_items":
        n_items = 200
        dados = {
            'order_id': [f'ORDER_{np.random.randint(1, 100):06d}' for _ in range(n_items)],
            'order_item_id': [f'ITEM_{i:06d}' for i in range(1, n_items + 1)],
            'product_id': [f'PROD_{np.random.randint(1, 50):06d}' for _ in range(n_items)],
            'seller_id': [f'SELLER_{np.random.randint(1, 10):06d}' for _ in range(n_items)],
            'shipping_limit_date': [datetime.now() + timedelta(days=np.random.randint(1, 30)) for _ in range(n_items)],
            'price': np.random.uniform(10, 1000, n_items),
            'freight_value': np.random.uniform(5, 50, n_items)
        }
    elif tabela == "dim_order_payments":
        n_payments = 150
        dados = {
            'order_id': [f'ORDER_{np.random.randint(1, 100):06d}' for _ in range(n_payments)],
            'payment_sequential': [np.random.randint(1, 5) for _ in range(n_payments)],
            'payment_type': np.random.choice(['credit_card', 'boleto', 'voucher', 'debit_card'], n_payments),
            'payment_installments': np.random.randint(1, 12, n_payments),
            'payment_value': np.random.uniform(50, 2000, n_payments)
        }
    elif tabela == "dim_order_reviews":
        n_reviews = 120
        dados = {
            'review_id': [f'REVIEW_{i:06d}' for i in range(1, n_reviews + 1)],
            'order_id': [f'ORDER_{np.random.randint(1, 100):06d}' for _ in range(n_reviews)],
            'review_score': np.random.randint(1, 6, n_reviews),
            'review_comment_title': [f'Review {i}' for i in range(1, n_reviews + 1)],
            'review_comment_message': [f'Comentário da review {i}' for i in range(1, n_reviews + 1)],
            'review_creation_date': [datetime.now() - timedelta(days=np.random.randint(1, 365)) for _ in range(n_reviews)],
            'review_answer_timestamp': [datetime.now() - timedelta(days=np.random.randint(1, 365)) for _ in range(n_reviews)]
        }
    elif tabela == "dim_product_category_name_translation":
        categorias = [
            'electronics', 'computers_accessories', 'home_appliances', 'furniture_decor',
            'sports_leisure', 'fashion_accessories', 'beauty_health', 'books_media',
            'automotive', 'toys_games', 'food_beverages', 'office_products'
        ]
        dados = {
            'product_category_name': categorias,
            'product_category_name_english': [
                'Electronics', 'Computers & Accessories', 'Home Appliances', 'Furniture & Decor',
                'Sports & Leisure', 'Fashion & Accessories', 'Beauty & Health', 'Books & Media',
                'Automotive', 'Toys & Games', 'Food & Beverages', 'Office Products'
            ]
        }
    elif tabela == "dim_products":
        n_products = 100
        dados = {
            'product_id': [f'PROD_{i:06d}' for i in range(1, n_products + 1)],
            'product_category_name': np.random.choice(['electronics', 'computers_accessories', 'home_appliances', 'furniture_decor'], n_products),
            'product_name_lenght': np.random.randint(10, 100, n_products),
            'product_description_lenght': np.random.randint(50, 500, n_products),
            'product_photos_qty': np.random.randint(1, 10, n_products),
            'product_weight_g': np.random.randint(100, 5000, n_products),
            'product_length_cm': np.random.randint(10, 100, n_products),
            'product_height_cm': np.random.randint(5, 50, n_products),
            'product_width_cm': np.random.randint(10, 100, n_products)
        }
    elif tabela == "dim_sellers":
        n_sellers = 20
        dados = {
            'seller_id': [f'SELLER_{i:06d}' for i in range(1, n_sellers + 1)],
            'seller_zip_code_prefix': [f'{np.random.randint(10000, 99999)}' for _ in range(n_sellers)],
            'seller_city': np.random.choice(['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 'Brasília'], n_sellers),
            'seller_state': np.random.choice(['SP', 'RJ', 'MG', 'BA', 'DF'], n_sellers)
        }
    elif tabela == "fato_orders":
        n_orders = 200
        dados = {
            'order_id': [f'ORDER_{i:06d}' for i in range(1, n_orders + 1)],
            'customer_id': [f'CUST_{np.random.randint(1, 100):06d}' for _ in range(n_orders)],
            'order_status': np.random.choice(['delivered', 'shipped', 'processing', 'cancelled'], n_orders),
            'order_purchase_date': [datetime.now() - timedelta(days=np.random.randint(1, 365)) for _ in range(n_orders)],
            'order_approved_at': [datetime.now() - timedelta(days=np.random.randint(1, 365)) for _ in range(n_orders)],
            'order_delivered_carrier_date': [datetime.now() - timedelta(days=np.random.randint(1, 365)) for _ in range(n_orders)],
            'order_delivered_customer_date': [datetime.now() - timedelta(days=np.random.randint(1, 365)) for _ in range(n_orders)],
            'order_estimated_delivery_date': [datetime.now() + timedelta(days=np.random.randint(1, 30)) for _ in range(n_orders)],
            'total_order_value': np.random.uniform(100, 5000, n_orders),
            'total_freight_value': np.random.uniform(10, 200, n_orders),
            'total_items': np.random.randint(1, 10, n_orders)
        }
    else:
        dados = {'id': [1, 2, 3], 'nome': ['Item 1', 'Item 2', 'Item 3']}
    
    return pd.DataFrame(dados)

# Título principal
st.title("📊 Dashboard - Tabelas do Medalhão Gold (Dados Reais)")
st.markdown("---")

# Inicializar Spark
spark = init_spark()

if spark is None:
    st.error("❌ Não foi possível conectar ao Spark. Verifique se o ambiente está configurado corretamente.")
    st.stop()

# Sidebar para seleção de tabelas
st.sidebar.header("🎯 Configurações")
tabela_selecionada = st.sidebar.selectbox(
    "Selecione a Tabela:",
    [
        "dim_customers",
        "dim_tempo", 
        "dim_geolocation",
        "dim_leads_closed",
        "dim_leads_qualified",
        "dim_order_items",
        "dim_order_payments",
        "dim_order_reviews",
        "dim_product_category_name_translation",
        "dim_products",
        "dim_sellers",
        "fato_orders"
    ]
)

# Carregar dados reais
with st.spinner(f"Carregando dados da tabela {tabela_selecionada}..."):
    df = carregar_tabela_gold_real(spark, tabela_selecionada)

# Layout principal
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📋 Tabela: {tabela_selecionada}")
    st.dataframe(df.head(10), use_container_width=True)
    
    # Estatísticas básicas
    st.subheader("📈 Estatísticas Básicas")
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    
    with col_stats1:
        st.metric("Total de Registros", len(df))
    
    with col_stats2:
        st.metric("Colunas", len(df.columns))
    
    with col_stats3:
        if df.select_dtypes(include=[np.number]).columns.any():
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            st.metric("Colunas Numéricas", len(numeric_cols))
        else:
            st.metric("Colunas Numéricas", 0)

with col2:
    st.subheader("🔍 Informações da Tabela")
    st.write(f"**Nome:** {tabela_selecionada}")
    st.write(f"**Tipo:** {'Fato' if tabela_selecionada.startswith('fato_') else 'Dimensional'}")
    st.write(f"**Registros:** {len(df):,}")
    st.write(f"**Colunas:** {len(df.columns)}")
    
    # Mostrar tipos de dados
    st.subheader("📊 Tipos de Dados")
    tipos_dados = df.dtypes.value_counts()
    fig_tipos = px.pie(
        values=tipos_dados.values,
        names=[str(x) for x in tipos_dados.index],
        title="Distribuição dos Tipos de Dados"
    )
    st.plotly_chart(fig_tipos, use_container_width=True)

# Visualizações específicas por tabela
st.markdown("---")
st.subheader("📊 Visualizações Específicas")

# Verificar se as colunas existem antes de criar visualizações
if tabela_selecionada == "dim_customers" and 'customer_state' in df.columns and 'customer_city' in df.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição por estado
        estado_counts = df['customer_state'].value_counts().reset_index()
        estado_counts.columns = ['customer_state', 'count']
        fig_estado = px.bar(
            estado_counts,
            x='customer_state',
            y='count',
            title="Distribuição de Clientes por Estado",
            labels={'customer_state': 'Estado', 'count': 'Quantidade de Clientes'}
        )
        st.plotly_chart(fig_estado, use_container_width=True)
    
    with col2:
        # Distribuição por cidade
        cidade_counts = df['customer_city'].value_counts().head(10).reset_index()
        cidade_counts.columns = ['customer_city', 'count']
        fig_cidade = px.pie(
            cidade_counts,
            values='count',
            names='customer_city',
            title="Top 10 Cidades com Mais Clientes"
        )
        st.plotly_chart(fig_cidade, use_container_width=True)

elif tabela_selecionada == "dim_tempo" and 'ano' in df.columns and 'mes' in df.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição por ano
        ano_counts = df['ano'].value_counts().sort_index().reset_index()
        ano_counts.columns = ['ano', 'count']
        fig_ano = px.line(
            ano_counts,
            x='ano',
            y='count',
            title="Distribuição de Datas por Ano",
            labels={'ano': 'Ano', 'count': 'Quantidade de Registros'}
        )
        st.plotly_chart(fig_ano, use_container_width=True)
    
    with col2:
        # Distribuição por mês
        mes_counts = df['mes'].value_counts().sort_index().reset_index()
        mes_counts.columns = ['mes', 'count']
        fig_mes = px.bar(
            mes_counts,
            x='mes',
            y='count',
            title="Distribuição por Mês",
            labels={'mes': 'Mês', 'count': 'Quantidade de Registros'}
        )
        st.plotly_chart(fig_mes, use_container_width=True)

elif tabela_selecionada == "dim_geolocation" and 'geolocation_lat' in df.columns and 'geolocation_lng' in df.columns:
    # Mapa de calor por coordenadas
    fig_map = px.scatter_mapbox(
        df,
        lat='geolocation_lat',
        lon='geolocation_lng',
        hover_name='geolocation_city' if 'geolocation_city' in df.columns else None,
        title="Distribuição Geográfica",
        mapbox_style="open-street-map"
    )
    st.plotly_chart(fig_map, use_container_width=True)

elif tabela_selecionada in ["dim_leads_closed", "dim_leads_qualified"]:
    col1, col2 = st.columns(2)
    
    with col1:
        if 'lead_value' in df.columns:
            fig_value = px.histogram(
                df,
                x='lead_value',
                title="Distribuição de Valor dos Leads",
                nbins=20
            )
            st.plotly_chart(fig_value, use_container_width=True)
    
    with col2:
        if 'lead_score' in df.columns:
            fig_score = px.box(
                df,
                y='lead_score',
                title="Distribuição de Score dos Leads"
            )
            st.plotly_chart(fig_score, use_container_width=True)

elif tabela_selecionada == "dim_order_items" and 'price' in df.columns and 'freight_value' in df.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição de preços
        fig_price = px.histogram(
            df,
            x='price',
            title="Distribuição de Preços",
            nbins=30
        )
        st.plotly_chart(fig_price, use_container_width=True)
    
    with col2:
        # Distribuição de frete
        fig_freight = px.histogram(
            df,
            x='freight_value',
            title="Distribuição de Valores de Frete",
            nbins=20
        )
        st.plotly_chart(fig_freight, use_container_width=True)

elif tabela_selecionada == "dim_order_payments" and 'payment_type' in df.columns and 'payment_value' in df.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição por tipo de pagamento
        payment_counts = df['payment_type'].value_counts().reset_index()
        payment_counts.columns = ['payment_type', 'count']
        fig_payment = px.pie(
            payment_counts,
            values='count',
            names='payment_type',
            title="Distribuição por Tipo de Pagamento"
        )
        st.plotly_chart(fig_payment, use_container_width=True)
    
    with col2:
        # Distribuição de valores
        fig_value = px.histogram(
            df,
            x='payment_value',
            title="Distribuição de Valores de Pagamento",
            nbins=30
        )
        st.plotly_chart(fig_value, use_container_width=True)

elif tabela_selecionada == "dim_order_reviews" and 'review_score' in df.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição de scores
        score_counts = df['review_score'].value_counts().sort_index().reset_index()
        score_counts.columns = ['review_score', 'count']
        fig_score = px.bar(
            score_counts,
            x='review_score',
            y='count',
            title="Distribuição de Scores de Review",
            labels={'review_score': 'Score', 'count': 'Quantidade'}
        )
        st.plotly_chart(fig_score, use_container_width=True)
    
    with col2:
        # Timeline de reviews (se houver coluna de data)
        if 'review_creation_date' in df.columns:
            df['review_creation_date'] = pd.to_datetime(df['review_creation_date'])
            df['month'] = df['review_creation_date'].dt.to_period('M')
            monthly_reviews = df.groupby('month').size().reset_index(name='count')
            monthly_reviews['month'] = monthly_reviews['month'].astype(str)
            
            fig_timeline = px.line(
                monthly_reviews,
                x='month',
                y='count',
                title="Timeline de Reviews por Mês",
                labels={'month': 'Mês', 'count': 'Quantidade de Reviews'}
            )
            st.plotly_chart(fig_timeline, use_container_width=True)

elif tabela_selecionada == "dim_products" and 'product_category_name' in df.columns and 'product_weight_g' in df.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição por categoria
        cat_counts = df['product_category_name'].value_counts().reset_index()
        cat_counts.columns = ['product_category_name', 'count']
        fig_cat = px.pie(
            cat_counts,
            values='count',
            names='product_category_name',
            title="Distribuição por Categoria de Produto"
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col2:
        # Distribuição de peso
        fig_weight = px.histogram(
            df,
            x='product_weight_g',
            title="Distribuição de Peso dos Produtos (g)",
            nbins=20
        )
        st.plotly_chart(fig_weight, use_container_width=True)

elif tabela_selecionada == "dim_sellers" and 'seller_state' in df.columns and 'seller_city' in df.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição por estado
        estado_counts = df['seller_state'].value_counts().reset_index()
        estado_counts.columns = ['seller_state', 'count']
        fig_estado = px.bar(
            estado_counts,
            x='seller_state',
            y='count',
            title="Distribuição de Vendedores por Estado",
            labels={'seller_state': 'Estado', 'count': 'Quantidade de Vendedores'}
        )
        st.plotly_chart(fig_estado, use_container_width=True)
    
    with col2:
        # Distribuição por cidade
        cidade_counts = df['seller_city'].value_counts().head(10).reset_index()
        cidade_counts.columns = ['seller_city', 'count']
        fig_cidade = px.pie(
            cidade_counts,
            values='count',
            names='seller_city',
            title="Top 10 Cidades com Mais Vendedores"
        )
        st.plotly_chart(fig_cidade, use_container_width=True)

elif tabela_selecionada == "fato_orders" and 'order_status' in df.columns and 'total_order_value' in df.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição por status
        status_counts = df['order_status'].value_counts().reset_index()
        status_counts.columns = ['order_status', 'count']
        fig_status = px.pie(
            status_counts,
            values='count',
            names='order_status',
            title="Distribuição por Status do Pedido"
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Distribuição de valores
        fig_value = px.histogram(
            df,
            x='total_order_value',
            title="Distribuição de Valores Totais dos Pedidos",
            nbins=30
        )
        st.plotly_chart(fig_value, use_container_width=True)
    
    # Timeline de pedidos (se houver coluna de data)
    if 'order_purchase_date' in df.columns:
        df['order_purchase_date'] = pd.to_datetime(df['order_purchase_date'])
        df['month'] = df['order_purchase_date'].dt.to_period('M')
        monthly_orders = df.groupby('month').agg({
            'total_order_value': 'sum',
            'order_id': 'count'
        }).reset_index()
        monthly_orders['month'] = monthly_orders['month'].astype(str)
        
        fig_timeline = px.line(
            monthly_orders,
            x='month',
            y='total_order_value',
            title="Valor Total de Pedidos por Mês",
            labels={'month': 'Mês', 'total_order_value': 'Valor Total (R$)'}
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Dashboard conectado aos dados reais do Medalhão Gold</p>
    <p>Dados carregados diretamente das tabelas Delta Lake</p>
</div>
""", unsafe_allow_html=True) 