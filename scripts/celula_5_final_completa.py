# =============================================================================
# CÉLULA 1: IMPORTS E CONFIGURAÇÕES
# =============================================================================

import os
import pandas as pd
import sqlite3
from datetime import datetime
import tempfile

# Verificar se estamos no Databricks
IN_DATABRICKS = False
try:
    from pyspark.sql import SparkSession
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
            .appName("AzureSQLiteReader") \
            .config("spark.hadoop.fs.azure", "org.apache.hadoop.fs.azure.NativeAzureFileSystem") \
            .config("spark.hadoop.fs.azure.account.key.datalakeb382f326bbc70c71.blob.core.windows.net", "") \
            .getOrCreate()
        
        print("✅ Spark configurado para Azure Storage")
        return spark
        
    except Exception as e:
        print(f"⚠️ Configuração Azure falhou: {str(e)}")
        print("Continuando com configuração padrão...")
        return SparkSession.builder.appName("SQLiteReader").getOrCreate()

# Inicializar Spark
spark = configurar_spark_azure()
print(f"🚀 Spark iniciado: {spark.version}")

# =============================================================================
# CÉLULA 3: DESCOBERTA DE CONTAINERS
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
# CÉLULA 4: FUNÇÃO DE LEITURA SQLITE
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

print("✅ Função de leitura SQLite carregada")

# =============================================================================
# CÉLULA 5: LEITURA VIA SPARK BINARY
# =============================================================================

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

print("✅ Função de leitura Spark Binary carregada")

# =============================================================================
# CÉLULA 6: LEITURA PRINCIPAL DO AZURE
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
    print("\n💡 POSSÍVEIS SOLUÇÕES:")
    print("1. Verifique se o arquivo 'olist.sqlite' existe no Azure Storage")
    print("2. Verifique se o nome do arquivo está correto")
    print("3. Execute: spark.read.format('binaryFile').load('wasbs://[container]@datalakeb382f326bbc70c71.blob.core.windows.net/')")
    
    return None

# =============================================================================
# CÉLULA 7: FALLBACK LOCAL
# =============================================================================

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

print("✅ Função de fallback local carregada")

# =============================================================================
# CÉLULA 8: EXECUÇÃO PRINCIPAL
# =============================================================================

print("🚀 INICIANDO LEITURA DO SQLITE...")

# Tentar ler o SQLite do Azure
tables = ler_sqlite_azure_spark_connect()

# Se falhar, tentar local como fallback
if not tables:
    print("\n🔄 Tentando fallback local...")
    tables = ler_sqlite_local_fallback()

# =============================================================================
# CÉLULA 9: RESULTADOS E PREVIEW
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
# CÉLULA 10: FUNÇÕES AUXILIARES (OPCIONAL)
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
print("💡 Use 'mostrar_info_tabela(nome)' para ver detalhes de uma tabela")
print("💡 Use 'converter_para_spark_dataframe(nome)' para converter para Spark")

# =============================================================================
# CÉLULA 11: SALVAMENTO NO AZURE (OPCIONAL)
# =============================================================================

def salvar_tabelas_azure_bronze():
    """Salvar tabelas na camada Bronze do Azure"""
    if not TABELAS_SQLITE:
        print("❌ Nenhuma tabela disponível para salvar")
        return
    
    print("💾 SALVANDO TABELAS NA CAMADA BRONZE...")
    
    for table_name, df in TABELAS_SQLITE.items():
        try:
            # Converter para Spark DataFrame
            df_spark = spark.createDataFrame(df)
            
            # Caminho de destino
            bronze_path = f"wasbs://bronze@{STORAGE_ACCOUNT}.blob.core.windows.net/{table_name}"
            
            # Salvar como Delta Lake
            df_spark.write.mode("overwrite").format("delta").save(bronze_path)
            
            print(f"✅ Tabela '{table_name}' salva em: {bronze_path}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar '{table_name}': {str(e)}")
    
    print("🎉 Processo de salvamento concluído!")

# Função disponível para uso posterior
print("💾 Função 'salvar_tabelas_azure_bronze()' disponível para salvar dados")

# =============================================================================
# CÉLULA 12: EXEMPLOS DE USO (OPCIONAL)
# =============================================================================

print("\n" + "="*80)
print("🎯 EXEMPLOS DE USO:")
print("="*80)

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
        print(f"  {i}. {table_name}: {len(df)} linhas, {len(df.columns)} colunas")
else:
    print("❌ Nenhuma tabela disponível")

print("\n" + "="*80)
print("✅ CÓDIGO COMPLETO EXECUTADO COM SUCESSO!")
print("="*80) 