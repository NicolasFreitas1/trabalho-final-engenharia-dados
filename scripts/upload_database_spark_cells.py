#!/usr/bin/env python3
"""
SQLite para Lakehouse com Spark - Organizado em Células
Este arquivo está organizado em células comentadas para facilitar a criação manual do notebook .ipynb

CÉLULA 1: Importações e Configurações
CÉLULA 2: Configurações do Sistema  
CÉLULA 3: Criação da SparkSession
CÉLULA 4: Montagem do Azure Storage
CÉLULA 5: Leitura do SQLite
CÉLULA 6: Salvamento na Landing Zone
CÉLULA 7: Salvamento na Camada Bronze
CÉLULA 8: Validação dos Dados
CÉLULA 9: Resumo da Execução
CÉLULA 10: Limpeza (Opcional)
"""

# =============================================================================
# CÉLULA 1: Importações e Configurações
# =============================================================================

import os
import sys
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit
import sqlite3
import pandas as pd

print("Bibliotecas importadas com sucesso!")

# =============================================================================
# CÉLULA 2: Configurações do Sistema
# =============================================================================

# Configurações do Azure Storage
storage_account = "datalake4b6c87c48101c278"
sas_token = "sv=2024-11-04&ss=bfqt&srt=sco&sp=rwdlacupyx&se=2025-06-07T12:17:21Z&st=2025-06-07T04:17:21Z&spr=https&sig=BfwzYwM%2B5YR%2FBkSSyRv0Nn%2F3riHK9Wx4P%2FQoguM%2BA%2FM%3D"
container = "landing-zone"

# Caminho do SQLite no servidor (AJUSTE CONFORME NECESSÁRIO)
sqlite_path = "/caminho/para/servidor/db.sqlite"

# Lista de tabelas
tables = [
    "customers", "geolocation", "leads_closed", "leads_qualified",
    "order_items", "order_payments", "order_reviews", "orders",
    "product_category_name_translation", "products", "sellers"
]

timestamp = datetime.now().strftime("%Y%m%d%H%M")

print("=== CONFIGURAÇÕES ===")
print(f"Timestamp: {timestamp}")
print(f"SQLite path: {sqlite_path}")
print(f"Storage Account: {storage_account}")
print(f"Tabelas a processar: {len(tables)}")

# =============================================================================
# CÉLULA 3: Criação da SparkSession
# =============================================================================

def create_spark_session():
    """Cria e configura a SparkSession"""
    spark = SparkSession.builder \
        .appName("SQLite to Lakehouse") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()
    
    return spark

# Criar SparkSession
spark = create_spark_session()
print("SparkSession criada com sucesso!")
print(f"Spark Version: {spark.version}")

# =============================================================================
# CÉLULA 4: Montagem do Azure Storage
# =============================================================================

def mount_azure_storage(spark, storage_account, sas_token):
    """Monta o Azure Storage no Databricks"""
    try:
        # Usando dbutils para montar o storage
        dbutils = spark._jvm.com.databricks.service.DBUtils(spark._jsc.sc())
        
        containers = ['landing-zone', 'bronze', 'silver', 'gold']
        
        for container in containers:
            try:
                dbutils.fs.mount(
                    source=f"wasbs://{container}@{storage_account}.blob.core.windows.net",
                    mount_point=f"/mnt/{storage_account}/{container}",
                    extra_configs={'fs.azure.sas.' + container + '.' + storage_account + '.blob.core.windows.net': sas_token}
                )
                print(f"Container {container} montado com sucesso!")
            except Exception as e:
                print(f"Container {container} já montado ou erro: {e}")
                
    except Exception as e:
        print(f"Erro ao montar storage: {e}")

# Montar Azure Storage
print("=== MONTANDO AZURE STORAGE ===")
mount_azure_storage(spark, storage_account, sas_token)

# =============================================================================
# CÉLULA 5: Leitura do SQLite
# =============================================================================

def read_sqlite_from_server(spark, sqlite_path, tables):
    """Lê tabelas do SQLite usando Spark"""
    dataframes = {}
    
    for table in tables:
        try:
            # Método 1: Tentar usar JDBC
            df = spark.read.jdbc(
                url=f"jdbc:sqlite:{sqlite_path}",
                table=table,
                properties={"driver": "org.sqlite.JDBC"}
            )
            print(f"Tabela {table} lida via JDBC")
        except Exception as e:
            print(f"JDBC falhou para {table}, tentando pandas: {e}")
            try:
                # Método 2: Usar pandas + sqlite3
                conn = sqlite3.connect(sqlite_path)
                pandas_df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                conn.close()
                
                # Converter para Spark DataFrame
                df = spark.createDataFrame(pandas_df)
                print(f"Tabela {table} lida via pandas")
            except Exception as e2:
                print(f"Erro ao ler {table}: {e2}")
                continue
        
        # Adicionar metadados
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        df = df.withColumn("data_hora_bronze", current_timestamp()) \
               .withColumn("nome_arquivo", lit(f"{table}_{timestamp}.csv")) \
               .withColumn("fonte_dados", lit("sqlite_server"))
        
        dataframes[table] = df
        print(f"Tabela {table}: {df.count()} linhas, {len(df.columns)} colunas")
    
    return dataframes

# Ler dados do SQLite
print("=== LENDO DADOS DO SQLITE ===")
dataframes = read_sqlite_from_server(spark, sqlite_path, tables)

if not dataframes:
    print("Nenhuma tabela foi lida com sucesso!")
else:
    print(f"\nTotal de tabelas lidas: {len(dataframes)}")

# =============================================================================
# CÉLULA 6: Salvamento na Landing Zone
# =============================================================================

def save_to_landing_zone(spark, dataframes, storage_account, container, timestamp):
    """Salva os dataframes como CSV na landing zone"""
    for table_name, df in dataframes.items():
        output_path = f"/mnt/{storage_account}/{container}/{table_name}_{timestamp}.csv"
        
        try:
            df.write.mode("overwrite") \
                .option("header", "true") \
                .csv(output_path)
            print(f"Tabela {table_name} salva na landing zone: {output_path}")
        except Exception as e:
            print(f"Erro ao salvar {table_name} na landing zone: {e}")

# Salvar na landing zone
print("=== SALVANDO NA LANDING ZONE ===")
save_to_landing_zone(spark, dataframes, storage_account, container, timestamp)

# =============================================================================
# CÉLULA 7: Salvamento na Camada Bronze
# =============================================================================

def save_to_bronze(spark, dataframes, storage_account):
    """Salva os dataframes na camada Bronze usando Delta Lake"""
    for table_name, df in dataframes.items():
        bronze_path = f"/mnt/{storage_account}/bronze/{table_name}"
        
        try:
            df.write.format('delta').mode("overwrite").save(bronze_path)
            print(f"Tabela {table_name} salva na Bronze: {bronze_path}")
        except Exception as e:
            print(f"Erro ao salvar {table_name} na Bronze: {e}")

# Salvar na Bronze
print("=== SALVANDO NA CAMADA BRONZE ===")
save_to_bronze(spark, dataframes, storage_account)

# =============================================================================
# CÉLULA 8: Validação dos Dados
# =============================================================================

# Verificar arquivos na landing zone
print("=== VALIDAÇÃO - LANDING ZONE ===")
try:
    dbutils = spark._jvm.com.databricks.service.DBUtils(spark._jsc.sc())
    landing_files = dbutils.fs.ls(f"/mnt/{storage_account}/{container}")
    print(f"Arquivos na landing zone: {len(landing_files)}")
    for file in landing_files:
        print(f"  - {file.name}")
except Exception as e:
    print(f"Erro ao listar landing zone: {e}")

# Verificar tabelas na Bronze
print("\n=== VALIDAÇÃO - CAMADA BRONZE ===")
try:
    bronze_files = dbutils.fs.ls(f"/mnt/{storage_account}/bronze")
    print(f"Tabelas na Bronze: {len(bronze_files)}")
    for file in bronze_files:
        print(f"  - {file.name}")
except Exception as e:
    print(f"Erro ao listar Bronze: {e}")

# Exemplo de leitura de dados da Bronze
print("\n=== EXEMPLO DE DADOS DA BRONZE ===")
if 'products' in dataframes:
    try:
        bronze_df = spark.read.format('delta').load(f'/mnt/{storage_account}/bronze/products')
        print(f"Tabela products na Bronze: {bronze_df.count()} linhas")
        print("\nPrimeiras 5 linhas:")
        bronze_df.limit(5).show()
    except Exception as e:
        print(f"Erro ao ler products da Bronze: {e}")
else:
    print("Tabela products não foi processada")

# =============================================================================
# CÉLULA 9: Resumo da Execução
# =============================================================================

# Resumo final
print("=== RESUMO DA EXECUÇÃO ===")
print(f"Timestamp de processamento: {timestamp}")
print(f"Storage Account: {storage_account}")
print(f"Tabelas processadas: {list(dataframes.keys())}")
print(f"Total de tabelas: {len(dataframes)}")

print("\nDetalhes por tabela:")
for table_name, df in dataframes.items():
    print(f"- {table_name}: {df.count()} linhas")

print("\n✅ Processamento concluído com sucesso!")

# =============================================================================
# CÉLULA 10: Limpeza (Opcional)
# =============================================================================

# Parar SparkSession (opcional - só execute se quiser parar o Spark)
# spark.stop()
# print("SparkSession parada.")

print("Nota: SparkSession mantida ativa para uso posterior.")
print("Execute 'spark.stop()' se quiser parar o Spark.") 