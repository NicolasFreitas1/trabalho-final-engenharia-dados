# -*- coding: utf-8 -*-
"""
Script de teste para verificar a conexão com dados reais do medalhão Gold
"""
import sys
import os

def testar_imports():
    """Testa se todos os imports necessários estão funcionando"""
    print("🔍 Testando imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Streamlit: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Pandas: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ Plotly importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Plotly: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar NumPy: {e}")
        return False
    
    try:
        from pyspark.sql import SparkSession
        print("✅ PySpark importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar PySpark: {e}")
        return False
    
    try:
        from pyspark.sql.functions import col, count, sum as spark_sum
        print("✅ PySpark functions importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar PySpark functions: {e}")
        return False
    
    return True

def testar_spark():
    """Testa se o Spark consegue ser inicializado"""
    print("\n🔄 Testando inicialização do Spark...")
    
    try:
        from pyspark.sql import SparkSession
        
        spark = SparkSession.builder \
            .appName("TesteConexao") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        
        print("✅ Spark inicializado com sucesso")
        print(f"📊 Versão do Spark: {spark.version}")
        
        # Testar se consegue ler dados
        print("\n🔄 Testando leitura de dados...")
        
        # Verificar se o caminho existe
        caminho_base = "/mnt/datalake4b6c87c48101c278/gold"
        
        if os.path.exists(caminho_base):
            print(f"✅ Caminho {caminho_base} existe")
            
            # Listar tabelas disponíveis
            tabelas = [d for d in os.listdir(caminho_base) 
                      if os.path.isdir(os.path.join(caminho_base, d))]
            print(f"📋 Tabelas encontradas: {tabelas}")
            
            # Testar carregamento de uma tabela
            if tabelas:
                tabela_teste = tabelas[0]
                print(f"\n🔄 Testando carregamento da tabela: {tabela_teste}")
                
                try:
                    df = spark.read.format("delta").load(f"{caminho_base}/{tabela_teste}")
                    count = df.count()
                    print(f"✅ Tabela {tabela_teste} carregada com sucesso")
                    print(f"📊 Total de registros: {count:,}")
                    
                    # Mostrar esquema
                    print(f"📋 Esquema da tabela {tabela_teste}:")
                    df.printSchema()
                    
                except Exception as e:
                    print(f"❌ Erro ao carregar tabela {tabela_teste}: {e}")
        else:
            print(f"❌ Caminho {caminho_base} não existe")
            print("💡 Isso é normal se você não tiver os dados reais configurados")
            print("💡 Os dashboards usarão dados simulados como fallback")
        
        spark.stop()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar Spark: {e}")
        return False

def testar_dashboards():
    """Testa se os dashboards podem ser importados"""
    print("\n📊 Testando importação dos dashboards...")
    
    try:
        # Testar dashboard de tabelas
        import dashboard_tabelas_real
        print("✅ dashboard_tabelas_real importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar dashboard_tabelas_real: {e}")
    
    try:
        # Testar dashboard de KPIs
        import dashboard_kpis_real
        print("✅ dashboard_kpis_real importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar dashboard_kpis_real: {e}")

def main():
    """Função principal"""
    print("🚀 Teste de Conexão - Dashboards do Medalhão Gold")
    print("=" * 60)
    
    # Testar imports
    if not testar_imports():
        print("\n❌ Falha nos imports. Verifique se todas as dependências estão instaladas.")
        return
    
    # Testar Spark
    testar_spark()
    
    # Testar dashboards
    testar_dashboards()
    
    print("\n✅ Teste concluído!")
    print("\n💡 Para executar os dashboards:")
    print("   streamlit run dashboard_tabelas_real.py --server.port 8503")
    print("   streamlit run dashboard_kpis_real.py --server.port 8504")

if __name__ == "__main__":
    main() 