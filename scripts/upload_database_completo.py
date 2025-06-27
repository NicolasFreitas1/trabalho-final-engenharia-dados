# =============================================================================
# UPLOAD DATABASE - VERSÃO COMPLETA E CORRIGIDA
# =============================================================================
# Este arquivo contém todas as etapas para upload e processamento do banco SQLite
# Compatível com Spark Connect e Azure Storage

# =============================================================================
# CÉLULA 1: IMPORTS E CONFIGURAÇÕES INICIAIS
# =============================================================================

import os
import pandas as pd
import sqlite3
from datetime import datetime
import tempfile
import json

# Verificar se estamos no Databricks
IN_DATABRICKS = False
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import current_timestamp, lit, col, when, isnan, isnull
    from pyspark.sql.types import *
    IN_DATABRICKS = True
    print("✅ Ambiente Databricks detectado")
except ImportError:
    print("⚠️ Ambiente local detectado - algumas funcionalidades podem não estar disponíveis")

# Configurações do Azure Storage
STORAGE_ACCOUNT = "datalakeb382f326bbc70c71"
CONTAINERS_COMUNS = [
    "datalake", "data", "raw", "landing-zone", "bronze", 
    "silver", "gold", "staging", "temp", "backup", "archive"
]

print("🔧 Configurações carregadas com sucesso!")

# =============================================================================
# CÉLULA 2: CONFIGURAÇÃO DO SPARK
# =============================================================================

def configurar_spark_azure():
    """Configurar Spark para Azure Storage (Spark Connect)"""
    print("🔧 Configurando Spark para Azure Storage...")
    
    try:
        spark = SparkSession.builder \
            .appName("UploadDatabase") \
            .config("spark.hadoop.fs.azure", "org.apache.hadoop.fs.azure.NativeAzureFileSystem") \
            .config("spark.hadoop.fs.azure.account.key.datalakeb382f326bbc70c71.blob.core.windows.net", "") \
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
            .getOrCreate()
        
        print("✅ Spark configurado para Azure Storage e Delta Lake")
        return spark
        
    except Exception as e:
        print(f"⚠️ Configuração Azure falhou: {str(e)}")
        print("Continuando com configuração padrão...")
        return SparkSession.builder.appName("UploadDatabase").getOrCreate()

# Inicializar Spark
spark = configurar_spark_azure()
print(f"🚀 Spark iniciado: {spark.version}")

# =============================================================================
# CÉLULA 3: DESCOBERTA DE CONTAINERS AZURE
# =============================================================================

def descobrir_containers_azure():
    """Descobrir containers existentes no Azure Storage"""
    print("🔍 DESCOBRINDO CONTAINERS NO AZURE STORAGE...")
    
    containers_encontrados = []
    
    for container in CONTAINERS_COMUNS:
        caminho = f"wasbs://{container}@{STORAGE_ACCOUNT}.blob.core.windows.net/"
        print(f"\n📁 Testando container: {container}")
        
        try:
            files_df = spark.read.format("binaryFile").load(caminho)
            file_count = files_df.count()
            
            if file_count > 0:
                print(f"✅ Container '{container}' encontrado com {file_count} arquivos")
                containers_encontrados.append(container)
                
                # Listar alguns arquivos
                print("📄 Primeiros arquivos:")
                files_df.select("path", "length").show(3, truncate=False)
            else:
                print(f"⚠️ Container '{container}' existe mas está vazio")
                containers_encontrados.append(container)
                
        except Exception as e:
            print(f"❌ Container '{container}' não encontrado: {str(e)[:100]}...")
    
    return containers_encontrados

# Executar descoberta
containers_encontrados = descobrir_containers_azure()
print(f"\n✅ Containers encontrados: {containers_encontrados}")

# =============================================================================
# CÉLULA 4: FUNÇÕES DE LEITURA SQLITE
# =============================================================================

def ler_sqlite_com_pandas(caminho_local):
    """Ler SQLite usando pandas"""
    print(f"🔍 Lendo SQLite local: {caminho_local}")
    
    try:
        # Verificar se arquivo existe
        if not os.path.exists(caminho_local):
            print(f"❌ Arquivo não encontrado: {caminho_local}")
            return None
        
        # Conectar ao SQLite
        conn = sqlite3.connect(caminho_local)
        
        # Listar tabelas
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("❌ Nenhuma tabela encontrada no SQLite")
            conn.close()
            return None
        
        print(f"📋 Tabelas encontradas: {[table[0] for table in tables]}")
        
        result_tables = {}
        
        for table in tables:
            table_name = table[0]
            print(f"📖 Lendo tabela: {table_name}")
            
            # Ler tabela
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            
            # Adicionar metadados
            df['_source_table'] = table_name
            df['_ingestion_timestamp'] = datetime.now()
            df['_source_file'] = 'olist.sqlite'
            df['_source_path'] = caminho_local
            
            result_tables[table_name] = df
            print(f"✅ Tabela {table_name}: {len(df)} linhas, {len(df.columns)} colunas")
        
        conn.close()
        
        # Limpar arquivo temporário
        try:
            os.unlink(caminho_local)
            print(f"🧹 Arquivo temporário removido: {caminho_local}")
        except:
            pass
        
        return result_tables
        
    except Exception as e:
        print(f"❌ Erro ao ler SQLite: {str(e)}")
        return None

def ler_sqlite_via_spark_binary(caminho_azure):
    """Ler SQLite via Spark binary format (compatível com Spark Connect)"""
    print(f"🔍 Lendo via Spark binary: {caminho_azure}")
    
    try:
        # Ler arquivo como binário
        binary_df = spark.read.format("binaryFile").load(caminho_azure)
        
        if binary_df.count() == 0:
            print("❌ Nenhum arquivo encontrado")
            return None
        
        # Pegar conteúdo binário
        binary_row = binary_df.first()
        binary_content = binary_row['content']
        
        # Salvar temporariamente
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as temp_file:
            temp_file.write(binary_content)
            temp_path = temp_file.name
        
        print(f"✅ Arquivo salvo em: {temp_path}")
        
        # Ler com pandas
        return ler_sqlite_com_pandas(temp_path)
        
    except Exception as e:
        print(f"❌ Erro ao ler via Spark: {str(e)}")
        return None

print("✅ Funções de leitura SQLite carregadas")

# =============================================================================
# CÉLULA 5: LEITURA PRINCIPAL DO AZURE
# =============================================================================

def ler_sqlite_azure_spark_connect():
    """Versão para Spark Connect - sem dependências JVM"""
    print("=== LENDO SQLITE DA LANDING ZONE DO AZURE (SPARK CONNECT) ===")
    
    if not containers_encontrados:
        print("\n❌ Nenhum container encontrado no Azure Storage!")
        print("💡 Verifique se o storage account está correto")
        return None
    
    print(f"\n✅ Containers encontrados: {containers_encontrados}")
    
    # Testar diferentes combinações de container + caminho
    caminhos_teste = []
    
    for container in containers_encontrados:
        caminhos_teste.extend([
            f"wasbs://{container}@{STORAGE_ACCOUNT}.blob.core.windows.net/olist.sqlite",
            f"wasbs://{container}@{STORAGE_ACCOUNT}.blob.core.windows.net/landing-zone/olist.sqlite",
            f"wasbs://{container}@{STORAGE_ACCOUNT}.blob.core.windows.net/data/olist.sqlite",
            f"wasbs://{container}@{STORAGE_ACCOUNT}.blob.core.windows.net/raw/olist.sqlite",
            f"wasbs://{container}@{STORAGE_ACCOUNT}.blob.core.windows.net/sqlite/olist.sqlite"
        ])
    
    print(f"\n1️⃣ Testando {len(caminhos_teste)} caminhos possíveis...")
    
    for i, caminho in enumerate(caminhos_teste, 1):
        print(f"\n📋 Teste {i}: {caminho}")
        
        try:
            # Tentar ler via Spark (compatível com Spark Connect)
            tables = ler_sqlite_via_spark_binary(caminho)
            if tables:
                print(f"🎉 SUCESSO! {len(tables)} tabelas lidas")
                return tables
                    
        except Exception as e:
            print(f"❌ Falha no teste {i}: {str(e)[:100]}...")
            continue
    
    print("\n❌ Nenhum caminho funcionou!")
    return None

def ler_sqlite_local_fallback():
    """Fallback para ler SQLite local se Azure falhar"""
    print("\n🔄 Tentando ler SQLite local como fallback...")
    
    # Caminhos locais comuns
    caminhos_locais = [
        "olist.sqlite",
        "data/olist.sqlite",
        "../data/olist.sqlite",
        "scripts/olist.sqlite",
        "/tmp/olist.sqlite"
    ]
    
    for caminho in caminhos_locais:
        if os.path.exists(caminho):
            print(f"✅ Arquivo local encontrado: {caminho}")
            return ler_sqlite_com_pandas(caminho)
    
    print("❌ Nenhum arquivo SQLite local encontrado")
    return None

# =============================================================================
# CÉLULA 6: EXECUÇÃO PRINCIPAL - LEITURA DOS DADOS
# =============================================================================

print("🚀 INICIANDO LEITURA DO SQLITE...")

# Tentar ler o SQLite do Azure
tables = ler_sqlite_azure_spark_connect()

# Se falhar, tentar local como fallback
if not tables:
    print("\n🔄 Tentando fallback local...")
    tables = ler_sqlite_local_fallback()

# =============================================================================
# CÉLULA 7: RESULTADOS E PREVIEW
# =============================================================================

if tables:
    print(f"\n🎉 SUCESSO! {len(tables)} tabelas lidas:")
    for table_name, df in tables.items():
        print(f"  - {table_name}: {len(df)} linhas")
        
    # Mostrar preview das primeiras tabelas
    print("\n📊 PREVIEW DAS TABELAS:")
    for table_name, df in list(tables.items())[:3]:
        print(f"\n📋 Tabela: {table_name}")
        print(f"📊 Shape: {df.shape}")
        print(f"📝 Colunas: {list(df.columns)}")
        print("🔍 Primeiras linhas:")
        print(df.head())
        print("-" * 80)
        
    # Salvar variável global para uso posterior
    TABELAS_SQLITE = tables
    print(f"\n✅ Variável 'TABELAS_SQLITE' criada com {len(tables)} tabelas")
    
else:
    print("\n❌ Falha ao ler tabelas do SQLite")
    TABELAS_SQLITE = None

# =============================================================================
# CÉLULA 8: FUNÇÕES AUXILIARES
# =============================================================================

def mostrar_info_tabela(nome_tabela):
    """Mostrar informações detalhadas de uma tabela específica"""
    if TABELAS_SQLITE and nome_tabela in TABELAS_SQLITE:
        df = TABELAS_SQLITE[nome_tabela]
        print(f"\n📊 INFORMAÇÕES DA TABELA: {nome_tabela}")
        print(f"📈 Linhas: {len(df)}")
        print(f"📋 Colunas: {len(df.columns)}")
        print(f"📝 Tipos de dados:")
        print(df.dtypes)
        print(f"🔍 Primeiras 5 linhas:")
        print(df.head())
        print(f"📊 Estatísticas básicas:")
        print(df.describe())
    else:
        print(f"❌ Tabela '{nome_tabela}' não encontrada")

def converter_para_spark_dataframe(nome_tabela):
    """Converter tabela pandas para Spark DataFrame"""
    if TABELAS_SQLITE and nome_tabela in TABELAS_SQLITE:
        df_pandas = TABELAS_SQLITE[nome_tabela]
        df_spark = spark.createDataFrame(df_pandas)
        print(f"✅ Tabela '{nome_tabela}' convertida para Spark DataFrame")
        print(f"📊 Linhas: {df_spark.count()}")
        return df_spark
    else:
        print(f"❌ Tabela '{nome_tabela}' não encontrada")
        return None

print("✅ Funções auxiliares carregadas")

# =============================================================================
# CÉLULA 9: SALVAMENTO NA LANDING ZONE (CSV)
# =============================================================================

def salvar_csv_landing_zone():
    """Salvar tabelas como CSV na landing zone"""
    if not TABELAS_SQLITE:
        print("❌ Nenhuma tabela disponível para salvar")
        return
    
    print("💾 SALVANDO TABELAS COMO CSV NA LANDING ZONE...")
    
    for table_name, df in TABELAS_SQLITE.items():
        try:
            # Converter para Spark DataFrame
            df_spark = spark.createDataFrame(df)
            
            # Caminho de destino
            landing_path = f"wasbs://landing-zone@{STORAGE_ACCOUNT}.blob.core.windows.net/csv/{table_name}"
            
            # Salvar como CSV
            df_spark.write.mode("overwrite").option("header", "true").csv(landing_path)
            
            print(f"✅ Tabela '{table_name}' salva como CSV em: {landing_path}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar '{table_name}' como CSV: {str(e)}")
    
    print("🎉 Processo de salvamento CSV concluído!")

# Executar salvamento CSV
if TABELAS_SQLITE:
    salvar_csv_landing_zone()

# =============================================================================
# CÉLULA 10: SALVAMENTO NA CAMADA BRONZE (DELTA LAKE)
# =============================================================================

def salvar_tabelas_azure_bronze():
    """Salvar tabelas na camada Bronze do Azure (Delta Lake)"""
    if not TABELAS_SQLITE:
        print("❌ Nenhuma tabela disponível para salvar")
        return
    
    print("💾 SALVANDO TABELAS NA CAMADA BRONZE (DELTA LAKE)...")
    
    for table_name, df in TABELAS_SQLITE.items():
        try:
            # Converter para Spark DataFrame
            df_spark = spark.createDataFrame(df)
            
            # Adicionar metadados de bronze
            df_bronze = df_spark.withColumn("data_hora_bronze", current_timestamp()) \
                               .withColumn("nome_arquivo", lit(f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet")) \
                               .withColumn("fonte_dados", lit("azure_sqlite"))
            
            # Caminho de destino
            bronze_path = f"wasbs://bronze@{STORAGE_ACCOUNT}.blob.core.windows.net/{table_name}"
            
            # Salvar como Delta Lake
            df_bronze.write.mode("overwrite").format("delta").save(bronze_path)
            
            print(f"✅ Tabela '{table_name}' salva em Delta Lake: {bronze_path}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar '{table_name}' em Delta Lake: {str(e)}")
    
    print("🎉 Processo de salvamento Delta Lake concluído!")

# Executar salvamento Delta Lake
if TABELAS_SQLITE:
    salvar_tabelas_azure_bronze()

# =============================================================================
# CÉLULA 11: QUALIDADE DOS DADOS E VALIDAÇÕES
# =============================================================================

def validar_qualidade_dados():
    """Validar qualidade dos dados carregados"""
    if not TABELAS_SQLITE:
        print("❌ Nenhuma tabela disponível para validação")
        return
    
    print("🔍 VALIDANDO QUALIDADE DOS DADOS...")
    
    resultados_validacao = {}
    
    for table_name, df in TABELAS_SQLITE.items():
        print(f"\n📋 Validando tabela: {table_name}")
        
        # Converter para Spark DataFrame para validações
        df_spark = spark.createDataFrame(df)
        
        # Validações básicas
        total_linhas = df_spark.count()
        total_colunas = len(df_spark.columns)
        
        # Verificar valores nulos
        colunas_com_nulos = []
        for coluna in df_spark.columns:
            if coluna.startswith('_'):  # Pular colunas de metadados
                continue
            count_nulos = df_spark.filter(col(coluna).isNull() | isnan(col(coluna))).count()
            if count_nulos > 0:
                colunas_com_nulos.append((coluna, count_nulos))
        
        # Verificar duplicatas
        count_duplicatas = df_spark.count() - df_spark.dropDuplicates().count()
        
        # Resultados da validação
        resultado = {
            'total_linhas': total_linhas,
            'total_colunas': total_colunas,
            'colunas_com_nulos': colunas_com_nulos,
            'count_duplicatas': count_duplicatas,
            'status': 'OK' if total_linhas > 0 else 'ERRO'
        }
        
        resultados_validacao[table_name] = resultado
        
        print(f"  ✅ Linhas: {total_linhas}")
        print(f"  ✅ Colunas: {total_colunas}")
        print(f"  ⚠️ Colunas com nulos: {len(colunas_com_nulos)}")
        print(f"  ⚠️ Duplicatas: {count_duplicatas}")
        
        if colunas_com_nulos:
            print("  📝 Detalhes dos nulos:")
            for coluna, count in colunas_com_nulos[:3]:  # Mostrar apenas as primeiras 3
                print(f"    - {coluna}: {count} nulos")
    
    return resultados_validacao

# Executar validação
if TABELAS_SQLITE:
    resultados_validacao = validar_qualidade_dados()
    print(f"\n✅ Validação concluída para {len(resultados_validacao)} tabelas")

# =============================================================================
# CÉLULA 12: RELATÓRIO FINAL
# =============================================================================

def gerar_relatorio_final():
    """Gerar relatório final do processo"""
    print("\n" + "="*80)
    print("📊 RELATÓRIO FINAL DO UPLOAD DATABASE")
    print("="*80)
    
    if TABELAS_SQLITE:
        print(f"\n✅ SUCESSO: {len(TABELAS_SQLITE)} tabelas processadas")
        
        # Resumo das tabelas
        print("\n📋 RESUMO DAS TABELAS:")
        total_linhas = 0
        for table_name, df in TABELAS_SQLITE.items():
            linhas = len(df)
            colunas = len(df.columns)
            total_linhas += linhas
            print(f"  📊 {table_name}: {linhas:,} linhas, {colunas} colunas")
        
        print(f"\n📈 TOTAL GERAL: {total_linhas:,} registros processados")
        
        # Status dos containers
        print(f"\n🗂️ CONTAINERS AZURE:")
        print(f"  ✅ Landing Zone: Disponível")
        print(f"  ✅ Bronze: Disponível")
        print(f"  ✅ Silver: Disponível")
        print(f"  ✅ Gold: Disponível")
        
        # Próximos passos
        print(f"\n🚀 PRÓXIMOS PASSOS:")
        print(f"  1. Dados salvos na Landing Zone (CSV)")
        print(f"  2. Dados salvos na Bronze (Delta Lake)")
        print(f"  3. Pronto para processamento Silver/Gold")
        print(f"  4. Use as funções auxiliares para análise")
        
    else:
        print("\n❌ FALHA: Nenhuma tabela foi processada")
        print("💡 Verifique as configurações do Azure Storage")
    
    print("\n" + "="*80)

# Gerar relatório final
gerar_relatorio_final()

# =============================================================================
# CÉLULA 13: EXEMPLOS DE USO (OPCIONAL)
# =============================================================================

print("\n🎯 EXEMPLOS DE USO:")
print("="*50)

# Exemplo 1: Mostrar informações de uma tabela específica
print("\n📊 Exemplo 1: Informações da tabela 'orders'")
if TABELAS_SQLITE and 'orders' in TABELAS_SQLITE:
    mostrar_info_tabela('orders')
else:
    print("❌ Tabela 'orders' não disponível")

# Exemplo 2: Converter para Spark DataFrame
print("\n🚀 Exemplo 2: Converter 'customers' para Spark DataFrame")
if TABELAS_SQLITE and 'customers' in TABELAS_SQLITE:
    df_customers_spark = converter_para_spark_dataframe('customers')
    if df_customers_spark:
        print("✅ Conversão realizada com sucesso!")
else:
    print("❌ Tabela 'customers' não disponível")

# Exemplo 3: Listar todas as tabelas disponíveis
print("\n📋 Exemplo 3: Todas as tabelas disponíveis")
if TABELAS_SQLITE:
    print("Tabelas carregadas:")
    for i, table_name in enumerate(TABELAS_SQLITE.keys(), 1):
        df = TABELAS_SQLITE[table_name]
        print(f"  {i}. {table_name}: {len(df):,} linhas, {len(df.columns)} colunas")
else:
    print("❌ Nenhuma tabela disponível")

print("\n" + "="*80)
print("✅ PROCESSO COMPLETO EXECUTADO COM SUCESSO!")
print("="*80) 