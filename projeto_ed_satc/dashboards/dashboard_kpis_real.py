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
    page_title="Dashboard - KPIs e Métricas (Dados Reais)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Spark
@st.cache_resource
def init_spark():
    """Inicializa a sessão Spark"""
    try:
        spark = SparkSession.builder \
            .appName("DashboardKPIsReal") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        return spark
    except Exception as e:
        st.error(f"Erro ao inicializar Spark: {e}")
        return None

# Função para carregar dados integrados reais
@st.cache_data(ttl=3600)  # Cache por 1 hora
def carregar_dados_integrados_reais(spark, periodo_filtro=None):
    """Carrega dados integrados reais das tabelas Gold"""
    try:
        # Caminho base das tabelas Gold
        caminho_base = "/mnt/datalake4b6c87c48101c278/gold"
        
        # Carregar tabela fato
        fato_orders = spark.read.format("delta").load(f"{caminho_base}/fato_orders")
        
        # Carregar dimensões relacionadas
        dim_customers = spark.read.format("delta").load(f"{caminho_base}/dim_customers")
        dim_products = spark.read.format("delta").load(f"{caminho_base}/dim_products")
        dim_order_payments = spark.read.format("delta").load(f"{caminho_base}/dim_order_payments")
        dim_order_reviews = spark.read.format("delta").load(f"{caminho_base}/dim_order_reviews")
        
        # Fazer joins para dados integrados
        df_integrado = fato_orders \
            .join(dim_customers, "customer_id", "left") \
            .join(dim_products, "product_id", "left") \
            .join(dim_order_payments, "order_id", "left") \
            .join(dim_order_reviews, "order_id", "left")
        
        # Aplicar filtro de período se especificado
        if periodo_filtro:
            df_integrado = df_integrado.filter(col("order_purchase_date") >= periodo_filtro)
        
        # Limitar registros para performance
        df_limitado = df_integrado.limit(10000)
        
        # Converter para Pandas
        df_pandas = df_limitado.toPandas()
        
        return df_pandas
    except Exception as e:
        st.error(f"Erro ao carregar dados integrados: {e}")
        return gerar_dados_simulados_fallback()

def gerar_dados_simulados_fallback():
    """Gera dados simulados como fallback"""
    np.random.seed(42)
    
    # Gerar datas
    datas = pd.date_range(start='2016-01-01', end='2018-12-31', freq='D')
    n_dias = len(datas)
    
    # Dados de pedidos
    n_orders = 1000
    orders_data = {
        'order_id': [f'ORDER_{i:06d}' for i in range(1, n_orders + 1)],
        'customer_id': [f'CUST_{np.random.randint(1, 500):06d}' for _ in range(n_orders)],
        'order_purchase_date': np.random.choice(datas, n_orders),
        'order_status': np.random.choice(['delivered', 'shipped', 'processing', 'cancelled'], n_orders, p=[0.7, 0.15, 0.1, 0.05]),
        'total_order_value': np.random.uniform(50, 3000, n_orders),
        'total_freight_value': np.random.uniform(5, 100, n_orders),
        'total_items': np.random.randint(1, 8, n_orders),
        'payment_type': np.random.choice(['credit_card', 'boleto', 'voucher', 'debit_card'], n_orders, p=[0.6, 0.2, 0.1, 0.1]),
        'payment_installments': np.random.randint(1, 12, n_orders),
        'review_score': np.random.choice([1, 2, 3, 4, 5], n_orders, p=[0.05, 0.1, 0.15, 0.3, 0.4]),
        'product_category': np.random.choice(['electronics', 'computers_accessories', 'home_appliances', 'furniture_decor', 'sports_leisure'], n_orders),
        'customer_state': np.random.choice(['SP', 'RJ', 'MG', 'BA', 'DF', 'RS', 'PR', 'SC'], n_orders, p=[0.4, 0.2, 0.15, 0.1, 0.05, 0.03, 0.04, 0.03]),
        'seller_state': np.random.choice(['SP', 'RJ', 'MG', 'BA', 'DF'], n_orders, p=[0.5, 0.2, 0.15, 0.1, 0.05])
    }
    
    df_orders = pd.DataFrame(orders_data)
    
    # Dados de leads (simulados)
    n_leads = 200
    leads_data = {
        'lead_id': [f'LEAD_{i:06d}' for i in range(1, n_leads + 1)],
        'lead_date': np.random.choice(datas, n_leads),
        'lead_status': np.random.choice(['Qualificado', 'Fechado', 'Em Negociação'], n_leads, p=[0.4, 0.3, 0.3]),
        'lead_value': np.random.uniform(1000, 50000, n_leads),
        'lead_score': np.random.randint(50, 100, n_leads),
        'lead_source': np.random.choice(['Website', 'Social Media', 'Email', 'Referral'], n_leads)
    }
    
    df_leads = pd.DataFrame(leads_data)
    
    return df_orders, df_leads

# Título principal
st.title("📈 Dashboard - KPIs e Métricas do E-commerce (Dados Reais)")
st.markdown("---")

# Inicializar Spark
spark = init_spark()

if spark is None:
    st.error("❌ Não foi possível conectar ao Spark. Verifique se o ambiente está configurado corretamente.")
    st.stop()

# Sidebar para filtros
st.sidebar.header("🎯 Filtros")
periodo = st.sidebar.selectbox(
    "Período de Análise:",
    ["Últimos 30 dias", "Últimos 90 dias", "Últimos 6 meses", "Último ano", "Todo o período"]
)

# Aplicar filtros de período
if periodo == "Últimos 30 dias":
    data_limite = datetime.now() - timedelta(days=30)
elif periodo == "Últimos 90 dias":
    data_limite = datetime.now() - timedelta(days=90)
elif periodo == "Últimos 6 meses":
    data_limite = datetime.now() - timedelta(days=180)
elif periodo == "Último ano":
    data_limite = datetime.now() - timedelta(days=365)
else:
    data_limite = None

# Carregar dados reais
with st.spinner("Carregando dados reais do medalhão Gold..."):
    df_orders, df_leads = carregar_dados_integrados_reais(spark, data_limite)

# Filtrar dados por período se necessário
if data_limite:
    df_orders_filtrado = df_orders[df_orders['order_purchase_date'] >= data_limite]
    df_leads_filtrado = df_leads[df_leads['lead_date'] >= data_limite] if 'lead_date' in df_leads.columns else df_leads
else:
    df_orders_filtrado = df_orders
    df_leads_filtrado = df_leads

# Cálculo dos KPIs
total_orders = len(df_orders_filtrado)
total_revenue = df_orders_filtrado['total_order_value'].sum()
avg_order_value = df_orders_filtrado['total_order_value'].mean()
conversion_rate = len(df_orders_filtrado) / len(df_leads_filtrado) * 100 if len(df_leads_filtrado) > 0 else 0

# Métricas adicionais
total_customers = df_orders_filtrado['customer_id'].nunique()
avg_review_score = df_orders_filtrado['review_score'].mean() if 'review_score' in df_orders_filtrado.columns else 0

# Cálculo do delta de delivery_rate com proteção contra divisão por zero
if len(df_orders_filtrado) > 0:
    delivery_rate = len(df_orders_filtrado[df_orders_filtrado['order_status'] == 'delivered']) / len(df_orders_filtrado) * 100
else:
    delivery_rate = 0

prev_orders = df_orders[df_orders['order_purchase_date'] >= data_limite - timedelta(days=30)] if data_limite else df_orders
prev_total = len(prev_orders)
if prev_total > 0:
    prev_delivery_rate = len(prev_orders[prev_orders['order_status'] == 'delivered']) / prev_total * 100
else:
    prev_delivery_rate = 0

# Layout principal - KPIs
st.subheader("🎯 Principais KPIs")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📦 Total de Pedidos",
        value=f"{total_orders:,}",
        delta=f"{total_orders - len(df_orders[df_orders['order_purchase_date'] >= data_limite - timedelta(days=30)]) if data_limite else 0:+,}"
    )

with col2:
    st.metric(
        label="💰 Receita Total",
        value=f"R$ {total_revenue:,.2f}",
        delta=f"R$ {total_revenue - df_orders[df_orders['order_purchase_date'] >= data_limite - timedelta(days=30)]['total_order_value'].sum() if data_limite else 0:+,.2f}"
    )

with col3:
    st.metric(
        label="🛒 Ticket Médio",
        value=f"R$ {avg_order_value:.2f}",
        delta=f"R$ {avg_order_value - df_orders[df_orders['order_purchase_date'] >= data_limite - timedelta(days=30)]['total_order_value'].mean() if data_limite else 0:+.2f}"
    )

with col4:
    st.metric(
        label="📈 Taxa de Conversão",
        value=f"{conversion_rate:.1f}%",
        delta=f"{conversion_rate - (len(df_orders[df_orders['order_purchase_date'] >= data_limite - timedelta(days=30)]) / len(df_leads[df_leads['lead_date'] >= data_limite - timedelta(days=30)]) * 100 if data_limite and len(df_leads[df_leads['lead_date'] >= data_limite - timedelta(days=30)]) > 0 else 0):+.1f}%"
    )

# Métricas secundárias
st.subheader("📊 Métricas Secundárias")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="👥 Clientes Únicos",
        value=f"{total_customers:,}",
        delta=f"{total_customers - df_orders[df_orders['order_purchase_date'] >= data_limite - timedelta(days=30)]['customer_id'].nunique() if data_limite else 0:+,}"
    )

with col2:
    st.metric(
        label="⭐ Score Médio de Reviews",
        value=f"{avg_review_score:.1f}/5.0",
        delta=f"{avg_review_score - df_orders[df_orders['order_purchase_date'] >= data_limite - timedelta(days=30)]['review_score'].mean() if data_limite and 'review_score' in df_orders.columns else 0:+.1f}"
    )

with col3:
    st.metric(
        label="🚚 Taxa de Entrega",
        value=f"{delivery_rate:.1f}%",
        delta=f"{delivery_rate - prev_delivery_rate:+.1f}%"
    )

# Visualizações
st.markdown("---")
st.subheader("📊 Análises Detalhadas")

# Gráfico 1: Evolução temporal da receita
col1, col2 = st.columns(2)

with col1:
    # Evolução temporal da receita
    if 'order_purchase_date' in df_orders_filtrado.columns:
        df_orders_filtrado['order_purchase_date'] = pd.to_datetime(df_orders_filtrado['order_purchase_date'])
        df_orders_filtrado['month'] = df_orders_filtrado['order_purchase_date'].dt.to_period('M')
        monthly_revenue = df_orders_filtrado.groupby('month').agg({
            'total_order_value': 'sum',
            'order_id': 'count'
        }).reset_index()
        monthly_revenue['month'] = monthly_revenue['month'].astype(str)
        
        fig_revenue = px.line(
            monthly_revenue,
            x='month',
            y='total_order_value',
            title="Evolução da Receita Mensal",
            labels={'month': 'Mês', 'total_order_value': 'Receita (R$)'}
        )
        fig_revenue.update_layout(showlegend=False)
        st.plotly_chart(fig_revenue, use_container_width=True)

with col2:
    # Distribuição por status de pedido
    if 'order_status' in df_orders_filtrado.columns:
        status_counts = df_orders_filtrado['order_status'].value_counts().reset_index()
        status_counts.columns = ['order_status', 'count']
        fig_status = px.pie(
            status_counts,
            values='count',
            names='order_status',
            title="Distribuição por Status dos Pedidos"
        )
        st.plotly_chart(fig_status, use_container_width=True)

# Gráfico 2: Análise de pagamentos e categorias
col1, col2 = st.columns(2)

with col1:
    # Distribuição por tipo de pagamento
    if 'payment_type' in df_orders_filtrado.columns:
        payment_counts = df_orders_filtrado['payment_type'].value_counts().reset_index()
        payment_counts.columns = ['payment_type', 'count']
        fig_payment = px.bar(
            payment_counts,
            x='payment_type',
            y='count',
            title="Distribuição por Tipo de Pagamento",
            labels={'payment_type': 'Tipo de Pagamento', 'count': 'Quantidade'}
        )
        st.plotly_chart(fig_payment, use_container_width=True)

with col2:
    # Distribuição por categoria de produto
    if 'product_category' in df_orders_filtrado.columns:
        category_counts = df_orders_filtrado['product_category'].value_counts().reset_index()
        category_counts.columns = ['product_category', 'count']
        fig_category = px.pie(
            category_counts,
            values='count',
            names='product_category',
            title="Distribuição por Categoria de Produto"
        )
        st.plotly_chart(fig_category, use_container_width=True)

# Gráfico 3: Análise geográfica e de reviews
col1, col2 = st.columns(2)

with col1:
    # Distribuição por estado do cliente
    if 'customer_state' in df_orders_filtrado.columns:
        state_counts = df_orders_filtrado['customer_state'].value_counts().reset_index()
        state_counts.columns = ['customer_state', 'count']
        fig_state = px.bar(
            state_counts.head(10),
            x='customer_state',
            y='count',
            title="Top 10 Estados por Volume de Pedidos",
            labels={'customer_state': 'Estado', 'count': 'Quantidade de Pedidos'}
        )
        st.plotly_chart(fig_state, use_container_width=True)

with col2:
    # Distribuição de scores de review
    if 'review_score' in df_orders_filtrado.columns:
        score_counts = df_orders_filtrado['review_score'].value_counts().sort_index().reset_index()
        score_counts.columns = ['review_score', 'count']
        fig_score = px.bar(
            score_counts,
            x='review_score',
            y='count',
            title="Distribuição de Scores de Review",
            labels={'review_score': 'Score', 'count': 'Quantidade'}
        )
        st.plotly_chart(fig_score, use_container_width=True)

# Gráfico 4: Análise de leads
if len(df_leads_filtrado) > 0:
    st.subheader("🎯 Análise de Leads")
    col1, col2 = st.columns(2)
    
    with col1:
        # Status dos leads
        if 'lead_status' in df_leads_filtrado.columns:
            lead_status_counts = df_leads_filtrado['lead_status'].value_counts().reset_index()
            lead_status_counts.columns = ['lead_status', 'count']
            fig_lead_status = px.pie(
                lead_status_counts,
                values='count',
                names='lead_status',
                title="Distribuição por Status dos Leads"
            )
            st.plotly_chart(fig_lead_status, use_container_width=True)
    
    with col2:
        # Fonte dos leads
        if 'lead_source' in df_leads_filtrado.columns:
            lead_source_counts = df_leads_filtrado['lead_source'].value_counts().reset_index()
            lead_source_counts.columns = ['lead_source', 'count']
            fig_lead_source = px.bar(
                lead_source_counts,
                x='lead_source',
                y='count',
                title="Distribuição por Fonte dos Leads",
                labels={'lead_source': 'Fonte', 'count': 'Quantidade'}
            )
            st.plotly_chart(fig_lead_source, use_container_width=True)

# Gráfico 5: Análise de performance
st.subheader("📈 Análise de Performance")
col1, col2 = st.columns(2)

with col1:
    # Ticket médio por categoria
    if 'product_category' in df_orders_filtrado.columns:
        avg_ticket_category = df_orders_filtrado.groupby('product_category')['total_order_value'].mean().sort_values(ascending=False).reset_index()
        avg_ticket_category.columns = ['product_category', 'avg_ticket']
        fig_ticket_category = px.bar(
            avg_ticket_category,
            x='product_category',
            y='avg_ticket',
            title="Ticket Médio por Categoria",
            labels={'product_category': 'Categoria', 'avg_ticket': 'Ticket Médio (R$)'}
        )
        st.plotly_chart(fig_ticket_category, use_container_width=True)

with col2:
    # Parcelamento vs Valor
    if 'payment_installments' in df_orders_filtrado.columns:
        df_orders_filtrado['installment_range'] = pd.cut(
            df_orders_filtrado['payment_installments'],
            bins=[0, 3, 6, 9, 12],
            labels=['1-3x', '4-6x', '7-9x', '10-12x']
        )
        avg_value_installment = df_orders_filtrado.groupby('installment_range')['total_order_value'].mean()
        fig_installment = px.bar(
            x=avg_value_installment.index,
            y=avg_value_installment.values,
            title="Valor Médio por Faixa de Parcelamento",
            labels={'x': 'Parcelamento', 'y': 'Valor Médio (R$)'}
        )
        st.plotly_chart(fig_installment, use_container_width=True)

# Tabela de resumo
st.subheader("📋 Resumo Executivo")
col1, col2 = st.columns(2)

with col1:
    st.write("**Métricas de Vendas:**")
    st.write(f"- Total de pedidos: {total_orders:,}")
    st.write(f"- Receita total: R$ {total_revenue:,.2f}")
    st.write(f"- Ticket médio: R$ {avg_order_value:.2f}")
    st.write(f"- Taxa de conversão: {conversion_rate:.1f}%")

with col2:
    st.write("**Métricas de Qualidade:**")
    st.write(f"- Score médio de reviews: {avg_review_score:.1f}/5.0")
    st.write(f"- Taxa de entrega: {delivery_rate:.1f}%")
    st.write(f"- Clientes únicos: {total_customers:,}")
    st.write(f"- Período analisado: {periodo}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Dashboard de KPIs e Métricas - Dados Reais do Medalhão Gold</p>
    <p>Dados carregados diretamente das tabelas Delta Lake</p>
</div>
""", unsafe_allow_html=True) 