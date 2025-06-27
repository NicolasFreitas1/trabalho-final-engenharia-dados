# -*- coding: utf-8 -*-
"""
Exemplo de conexão com dados reais do medalhão Gold
Este script demonstra como conectar e carregar dados das tabelas Gold
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import pandas as pd

def inicializar_spark():
    """Inicializa a sessão Spark com configurações otimizadas"""
    spark = SparkSession.builder \
        .appName("ConexaoGoldReal") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.sql.adaptive.skewJoin.enabled", "true") \
        .config("spark.sql.adaptive.localShuffleReader.enabled", "true") \
        .getOrCreate()
    
    return spark

def listar_tabelas_gold(spark):
    """Lista todas as tabelas disponíveis no medalhão Gold"""
    caminho_base = "/mnt/datalake4b6c87c48101c278/gold"
    
    try:
        # Tentar listar as tabelas
        tabelas = spark.read.format("delta").load(caminho_base)
        print(f"✅ Conexão estabelecida com sucesso!")
        print(f"📁 Caminho base: {caminho_base}")
        
        # Listar tabelas disponíveis
        import os
        if os.path.exists(caminho_base):
            tabelas_disponiveis = [d for d in os.listdir(caminho_base) 
                                 if os.path.isdir(os.path.join(caminho_base, d))]
            print(f"📋 Tabelas disponíveis: {tabelas_disponiveis}")
            return tabelas_disponiveis
        else:
            print(f"❌ Caminho {caminho_base} não encontrado!")
            return []
            
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return []

def carregar_tabela_gold(spark, nome_tabela, limite=1000):
    """Carrega uma tabela específica do medalhão Gold"""
    caminho_base = "/mnt/datalake4b6c87c48101c278/gold"
    caminho_completo = f"{caminho_base}/{nome_tabela}"
    
    try:
        print(f"🔄 Carregando tabela: {nome_tabela}")
        
        # Carregar dados
        df_spark = spark.read.format("delta").load(caminho_completo)
        
        # Mostrar esquema
        print(f"📊 Esquema da tabela {nome_tabela}:")
        df_spark.printSchema()
        
        # Contar registros
        total_registros = df_spark.count()
        print(f"📈 Total de registros: {total_registros:,}")
        
        # Limitar para demonstração
        df_limitado = df_spark.limit(limite)
        
        # Converter para Pandas
        df_pandas = df_limitado.toPandas()
        
        print(f"✅ Tabela {nome_tabela} carregada com sucesso!")
        print(f"📋 Amostra de {len(df_pandas)} registros:")
        print(df_pandas.head())
        
        return df_pandas
        
    except Exception as e:
        print(f"❌ Erro ao carregar tabela {nome_tabela}: {e}")
        return None

def carregar_dados_integrados(spark, tabelas_principais=None):
    """Carrega dados integrados de múltiplas tabelas"""
    if tabelas_principais is None:
        tabelas_principais = ["fato_orders", "dim_customers", "dim_products"]
    
    try:
        print("🔄 Carregando dados integrados...")
        
        # Carregar tabela fato
        fato_orders = spark.read.format("delta").load("/mnt/datalake4b6c87c48101c278/gold/fato_orders")
        
        # Carregar dimensões
        dim_customers = spark.read.format("delta").load("/mnt/datalake4b6c87c48101c278/gold/dim_customers")
        dim_products = spark.read.format("delta").load("/mnt/datalake4b6c87c48101c278/gold/dim_products")
        
        # Fazer joins
        df_integrado = fato_orders \
            .join(dim_customers, "customer_id", "left") \
            .join(dim_products, "product_id", "left")
        
        # Limitar registros
        df_limitado = df_integrado.limit(5000)
        
        # Converter para Pandas
        df_pandas = df_limitado.toPandas()
        
        print(f"✅ Dados integrados carregados com sucesso!")
        print(f"📊 Total de registros integrados: {len(df_pandas):,}")
        print(f"📋 Colunas disponíveis: {list(df_pandas.columns)}")
        
        return df_pandas
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados integrados: {e}")
        return None

def executar_queries_exemplo(spark):
    """Executa queries de exemplo nas tabelas Gold"""
    print("\n🔍 Executando queries de exemplo...")
    
    try:
        # Query 1: Total de pedidos por status
        print("\n📊 Query 1: Total de pedidos por status")
        query1 = spark.sql("""
            SELECT order_status, COUNT(*) as total_pedidos
            FROM delta.`/mnt/datalake4b6c87c48101c278/gold/fato_orders`
            GROUP BY order_status
            ORDER BY total_pedidos DESC
        """)
        query1.show()
        
        # Query 2: Top 5 estados com mais clientes
        print("\n📊 Query 2: Top 5 estados com mais clientes")
        query2 = spark.sql("""
            SELECT customer_state, COUNT(*) as total_clientes
            FROM delta.`/mnt/datalake4b6c87c48101c278/gold/dim_customers`
            GROUP BY customer_state
            ORDER BY total_clientes DESC
            LIMIT 5
        """)
        query2.show()
        
        # Query 3: Receita total por mês
        print("\n📊 Query 3: Receita total por mês")
        query3 = spark.sql("""
            SELECT 
                YEAR(order_purchase_date) as ano,
                MONTH(order_purchase_date) as mes,
                SUM(total_order_value) as receita_total
            FROM delta.`/mnt/datalake4b6c87c48101c278/gold/fato_orders`
            GROUP BY YEAR(order_purchase_date), MONTH(order_purchase_date)
            ORDER BY ano, mes
        """)
        query3.show()
        
    except Exception as e:
        print(f"❌ Erro ao executar queries: {e}")

def main():
    """Função principal"""
    print("🚀 Exemplo de Conexão com Dados Reais do Medalhão Gold")
    print("=" * 60)
    
    # Inicializar Spark
    print("🔄 Inicializando Spark...")
    spark = inicializar_spark()
    
    # Listar tabelas disponíveis
    print("\n📋 Verificando tabelas disponíveis...")
    tabelas = listar_tabelas_gold(spark)
    
    if not tabelas:
        print("❌ Nenhuma tabela encontrada. Verifique a configuração do ambiente.")
        return
    
    # Carregar tabela de exemplo
    if "fato_orders" in tabelas:
        print("\n📊 Carregando tabela fato_orders como exemplo...")
        df_orders = carregar_tabela_gold(spark, "fato_orders", limite=100)
        
        if df_orders is not None:
            print(f"✅ Tabela fato_orders carregada com {len(df_orders)} registros")
    
    # Carregar dados integrados
    print("\n🔄 Carregando dados integrados...")
    df_integrado = carregar_dados_integrados(spark)
    
    if df_integrado is not None:
        print(f"✅ Dados integrados carregados com {len(df_integrado)} registros")
        
        # Mostrar algumas estatísticas
        print("\n📈 Estatísticas dos dados integrados:")
        print(f"- Total de registros: {len(df_integrado):,}")
        print(f"- Total de colunas: {len(df_integrado.columns)}")
        
        if 'total_order_value' in df_integrado.columns:
            receita_total = df_integrado['total_order_value'].sum()
            print(f"- Receita total: R$ {receita_total:,.2f}")
        
        if 'customer_id' in df_integrado.columns:
            clientes_unicos = df_integrado['customer_id'].nunique()
            print(f"- Clientes únicos: {clientes_unicos:,}")
    
    # Executar queries de exemplo
    executar_queries_exemplo(spark)
    
    # Fechar Spark
    spark.stop()
    print("\n✅ Conexão finalizada com sucesso!")

if __name__ == "__main__":
    main() 