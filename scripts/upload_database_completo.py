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

# Configurações do Azure Storage (baseado no notebook que funcionou)
STORAGE_ACCOUNT = "datalake4b6c87c48101c278"
CONTAINERS_COMUNS = [
    "datalake", "data", "raw", "landing-zone", "bronze", 
    "silver", "gold", "staging", "temp", "backup", "archive"
]

# CONFIGURAÇÃO DO SAS TOKEN - IMPORTANTE!
# Cole seu SAS token aqui (deve começar com ?sv=...)
AZURE_SAS_TOKEN = "sv=2024-11-04&ss=bfqt&srt=sco&sp=rwdlacupyx&se=2025-06-07T12:17:21Z&st=2025-06-07T04:17:21Z&spr=https&sig=BfwzYwM%2B5YR%2FBkSSyRv0Nn%2F3riHK9Wx4P%2FQoguM%2BA%2FM%3D"

# Inicializar variável spark
spark = None

print("🔧 Configurações carregadas com sucesso!")
print(f"📊 Storage Account: {STORAGE_ACCOUNT}")
print(f"🔑 SAS Token configurado: {'Sim' if AZURE_SAS_TOKEN else 'Não'}")

# =============================================================================
# CÉLULA 2: CONFIGURAÇÃO DO SPARK IGUAL AO DATABRICKS
# =============================================================================

def configurar_spark_igual_databricks():
    """Configurar Spark igual ao notebook do Databricks"""
    print("🔧 Configurando Spark igual ao Databricks...")
    
    global spark, AZURE_SAS_TOKEN, STORAGE_ACCOUNT
    
    # Verificar se temos as configurações necessárias
    if not AZURE_SAS_TOKEN:
        print("❌ ERRO: SAS token não configurado!")
        print("💡 Configure AZURE_SAS_TOKEN antes de continuar")
        return None
    
    if not STORAGE_ACCOUNT:
        print("❌ ERRO: Storage Account não configurado!")
        return None
    
    try:
        # VERIFICAR SE A SESSÃO SPARK EXISTE
        if spark is None:
            print("🔄 Sessão Spark não encontrada, criando uma...")
            try:
                # Tentar criar uma sessão Spark simples
                spark = SparkSession.builder \
                    .appName("UploadDatabase") \
                    .master("local[*]") \
                    .getOrCreate()
                print("✅ Sessão Spark criada com sucesso")
            except Exception as e:
                print(f"❌ Erro ao criar sessão Spark: {str(e)}")
                return None
        else:
            print("✅ Sessão Spark existente encontrada")
        
        # CONFIGURAR SAS TOKEN IGUAL AO NOTEBOOK
        print("🔧 Configurando SAS token igual ao notebook...")
        
        # Configuração exata do notebook
        storageAccountName = STORAGE_ACCOUNT
        sasToken = AZURE_SAS_TOKEN
        
        # Configurar SAS token diretamente
        print("📁 Configurando containers via SAS token...")
        containers = ['landing-zone', 'bronze', 'silver', 'gold']
        
        for container in containers:
            try:
                # Configuração SAS por container
                spark.conf.set(
                    f"fs.azure.sas.{container}.{storageAccountName}.blob.core.windows.net",
                    sasToken
                )
                
                # Configuração de autenticação
                spark.conf.set(
                    f"fs.azure.account.auth.type.{storageAccountName}.blob.core.windows.net",
                    "SAS"
                )
                
                print(f"✅ SAS configurado para {container}")
                
            except Exception as e:
                print(f"⚠️ Erro ao configurar {container}: {str(e)[:100]}...")
                continue
        
        print("✅ Configuração Spark concluída igual ao Databricks")
        return spark
        
    except Exception as e:
        print(f"❌ Erro na configuração: {str(e)}")
        return None

# Inicializar Spark igual ao Databricks
spark = configurar_spark_igual_databricks()
if spark:
    print(f"🚀 Spark configurado igual ao Databricks: {spark.version}")
else:
    print("❌ Falha ao configurar Spark")
    spark = None

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
    
    # FOCAR APENAS NO CONTAINER LANDING-ZONE
    if 'landing-zone' not in containers_encontrados:
        print("❌ Container 'landing-zone' não encontrado!")
        print(f"💡 Containers disponíveis: {containers_encontrados}")
        return None
    
    print("🎯 Focando no container 'landing-zone'...")
    
    # PRIMEIRO: Listar arquivos na landing zone
    arquivos_encontrados = listar_arquivos_landing_zone()
    
    if not arquivos_encontrados:
        print("❌ Nenhum arquivo encontrado na landing zone!")
        return None
    
    # PROCURAR POR ARQUIVOS SQLITE
    sqlite_files = [f for f in arquivos_encontrados if '.sqlite' in f.lower()]
    
    if not sqlite_files:
        print("❌ Nenhum arquivo .sqlite encontrado na landing zone!")
        print("💡 Verifique se o arquivo foi enviado corretamente")
        return None
    
    print(f"\n🎯 Arquivos SQLite encontrados: {sqlite_files}")
    
    # TENTAR LER CADA ARQUIVO SQLITE ENCONTRADO
    for sqlite_file in sqlite_files:
        print(f"\n📖 Tentando ler: {sqlite_file}")
        
        try:
            # Tentar ler via Spark (compatível com Spark Connect)
            tables = ler_sqlite_via_spark_binary(sqlite_file)
            if tables:
                print(f"🎉 SUCESSO! {len(tables)} tabelas lidas do arquivo: {sqlite_file}")
                return tables
                    
        except Exception as e:
            print(f"❌ Falha ao ler {sqlite_file}: {str(e)[:100]}...")
            continue
    
    print("\n❌ Nenhum arquivo SQLite pôde ser lido!")
    print("💡 Verifique se os arquivos SQLite estão corrompidos ou inacessíveis")
    return None

# =============================================================================
# CÉLULA 6: EXECUÇÃO PRINCIPAL - LEITURA DOS DADOS
# =============================================================================

print("🚀 INICIANDO LEITURA DO SQLITE DO AZURE...")

# Tentar ler o SQLite do Azure (SEM FALLBACK LOCAL)
tables = ler_sqlite_azure_spark_connect()

# =============================================================================
# CÉLULA 7: RESULTADOS E PREVIEW
# =============================================================================

if tables:
    print(f"\n🎉 SUCESSO! {len(tables)} tabelas lidas do Azure:")
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
    print("\n❌ FALHA AO LER TABELAS DO AZURE!")
    print("💡 Verifique:")
    print("  1. Se o arquivo olist.sqlite existe na landing zone")
    print("  2. Se o SAS token está configurado corretamente")
    print("  3. Se o storage account está acessível")
    print("  4. Se o container 'landing-zone' existe")
    
    # NÃO criar dados de exemplo - forçar leitura do Azure
    TABELAS_SQLITE = None
    print("\n🚫 Nenhum dado de exemplo criado - leia o arquivo correto do Azure")

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
        print(f" Linhas: {df_spark.count()}")
        return df_spark
    else:
        print(f"❌ Tabela '{nome_tabela}' não encontrada")
        return None

print("✅ Funções auxiliares carregadas")

# =============================================================================
# CÉLULA 9: SALVAMENTO NA LANDING ZONE (CSV) - CORRIGIDO
# =============================================================================

def salvar_csv_landing_zone_corrigido():
    """Salvar tabelas como CSV na landing zone - VERSÃO CORRIGIDA"""
    if not TABELAS_SQLITE:
        print("❌ Nenhuma tabela disponível para salvar")
        return
    
    print("💾 SALVANDO TABELAS COMO CSV NA LANDING ZONE (VERSÃO CORRIGIDA)...")
    
    # Contadores para relatório
    salvos_azure = 0
    falhas = 0
    
    for table_name, df in TABELAS_SQLITE.items():
        print(f"\n📋 Processando tabela: {table_name}")
        
        try:
            # Converter para Spark DataFrame
            df_spark = spark.createDataFrame(df)
            
            # DIFERENTES FORMATOS DE CAMINHO PARA TESTAR
            caminhos_teste = [
                # Formato 1: wasbs com SAS configurado
                f"wasbs://landing-zone@{STORAGE_ACCOUNT}.blob.core.windows.net/csv/{table_name}",
                
                # Formato 2: abfss (Azure Data Lake Gen2)
                f"abfss://landing-zone@{STORAGE_ACCOUNT}.dfs.core.windows.net/csv/{table_name}",
                
                # Formato 3: Caminho direto com SAS na URL
                f"wasbs://landing-zone@{STORAGE_ACCOUNT}.blob.core.windows.net/csv/{table_name}?{AZURE_SAS_TOKEN.lstrip('?')}"
            ]
            
            sucesso = False
            
            for i, caminho in enumerate(caminhos_teste, 1):
                print(f"  🧪 Tentativa {i}: {caminho.split('?')[0]}...")  # Não mostrar SAS token no log
                
                try:
                    # Tentar salvar
                    df_spark.coalesce(1).write.mode("overwrite").option("header", "true").csv(caminho)
                    
                    print(f"  ✅ Sucesso na tentativa {i}")
                    sucesso = True
                    break
                    
                except Exception as e:
                    print(f"  ❌ Tentativa {i} falhou: {str(e)[:100]}...")
                    continue
            
            if sucesso:
                print(f"✅ Tabela '{table_name}' salva com sucesso!")
                salvos_azure += 1
            else:
                print(f"❌ Todas as tentativas falharam para '{table_name}'")
                falhas += 1
                    
        except Exception as e:
            print(f"❌ Erro geral ao processar '{table_name}': {str(e)[:200]}...")
            falhas += 1
    
    # Relatório final
    print(f"\n📊 RELATÓRIO DE SALVAMENTO CSV (CORRIGIDO):")
    print(f"  ✅ Salvos no Azure: {salvos_azure}")
    print(f"  ❌ Falhas: {falhas}")
    print(f"  📈 Total processado: {len(TABELAS_SQLITE)}")

# Executar salvamento CSV
if TABELAS_SQLITE:
    salvar_csv_landing_zone_corrigido()

# =============================================================================
# CÉLULA 10: SALVAMENTO NA CAMADA BRONZE (DELTA LAKE) - CORRIGIDO
# =============================================================================

def salvar_tabelas_azure_bronze():
    """Salvar tabelas na camada Bronze do Azure (Delta Lake) - usando caminhos montados"""
    if not TABELAS_SQLITE:
        print("❌ Nenhuma tabela disponível para salvar")
        return
    
    print("💾 SALVANDO TABELAS NA CAMADA BRONZE (DELTA LAKE)...")
    
    # Contadores para relatório
    salvos_azure = 0
    falhas = 0
    
    # Verificar se SAS está configurado
    if not AZURE_SAS_TOKEN:
        print("❌ SAS token não configurado!")
        print("💡 Configure AZURE_SAS_TOKEN para salvar no Azure Storage")
        print("📝 Exemplo: AZURE_SAS_TOKEN = '?sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupitx&se=...'")
        return
    
    print("✅ SAS token configurado - salvando no Azure")
    
    for table_name, df in TABELAS_SQLITE.items():
        print(f"\n📋 Processando tabela: {table_name}")
        
        try:
            # Converter para Spark DataFrame
            df_spark = spark.createDataFrame(df)
            
            # Adicionar metadados de bronze
            df_bronze = df_spark.withColumn("data_hora_bronze", current_timestamp()) \
                               .withColumn("nome_arquivo", lit(f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet")) \
                               .withColumn("fonte_dados", lit("azure_sqlite"))
            
            # Caminho de destino Azure (usando formato do notebook que funcionou)
            bronze_path = f"wasbs://bronze@{STORAGE_ACCOUNT}.blob.core.windows.net/{table_name}"
            
            # Salvar como Delta Lake no Azure
            df_bronze.write.mode("overwrite").format("delta").save(bronze_path)
            
            print(f"✅ Tabela '{table_name}' salva em Delta Lake no Azure: {bronze_path}")
            salvos_azure += 1
                    
        except Exception as e:
            print(f"❌ Erro ao salvar '{table_name}' no Azure: {str(e)[:200]}...")
            falhas += 1
    
    # Relatório final
    print(f"\n📊 RELATÓRIO DE SALVAMENTO DELTA LAKE:")
    print(f"  ✅ Salvos no Azure: {salvos_azure}")
    print(f"  ❌ Falhas: {falhas}")
    print(f"  📈 Total processado: {len(TABELAS_SQLITE)}")
    
    if falhas > 0:
        print(f"\n⚠️ {falhas} tabelas falharam - verifique se o SAS token tem permissões de escrita")
        print("💡 Permissões necessárias: Read, Write, Delete, List")

# Executar salvamento Delta Lake
if TABELAS_SQLITE:
    salvar_tabelas_azure_bronze()

# =============================================================================
# CÉLULA 11: QUALIDADE DOS DADOS E VALIDAÇÕES (CORRIGIDA)
# =============================================================================

def validar_qualidade_dados():
    """Validar qualidade dos dados carregados (versão corrigida)"""
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
        
        # Verificar valores nulos (apenas colunas não-metadados)
        colunas_com_nulos = []
        for coluna in df_spark.columns:
            if coluna.startswith('_'):  # Pular colunas de metadados
                continue
            try:
                count_nulos = df_spark.filter(col(coluna).isNull() | isnan(col(coluna))).count()
                if count_nulos > 0:
                    colunas_com_nulos.append((coluna, count_nulos))
            except Exception as e:
                print(f"⚠️ Erro ao verificar nulos na coluna '{coluna}': {str(e)[:50]}...")
                continue
        
        # Verificar duplicatas
        try:
            count_duplicatas = df_spark.count() - df_spark.dropDuplicates().count()
        except Exception as e:
            print(f"⚠️ Erro ao verificar duplicatas: {str(e)[:50]}...")
            count_duplicatas = 0
        
        # Verificar tipos de dados (sem usar describe())
        tipos_dados = {}
        for coluna in df_spark.columns:
            if coluna.startswith('_'):  # Pular colunas de metadados
                continue
            try:
                # Pegar tipo da coluna
                tipo = df_spark.schema[coluna].dataType
                tipos_dados[coluna] = str(tipo)
            except Exception as e:
                tipos_dados[coluna] = "UNKNOWN"
        
        # Resultados da validação
        resultado = {
            'total_linhas': total_linhas,
            'total_colunas': total_colunas,
            'colunas_com_nulos': colunas_com_nulos,
            'count_duplicatas': count_duplicatas,
            'tipos_dados': tipos_dados,
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
        
        # Mostrar alguns tipos de dados
        print("  📊 Tipos de dados (primeiras 5 colunas):")
        for i, (coluna, tipo) in enumerate(list(tipos_dados.items())[:5]):
            print(f"    - {coluna}: {tipo}")
    
    return resultados_validacao

# Executar validação
if TABELAS_SQLITE:
    resultados_validacao = validar_qualidade_dados()
    if resultados_validacao:
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

def listar_arquivos_landing_zone():
    """Listar arquivos na landing zone para encontrar o SQLite"""
    print("🔍 LISTANDO ARQUIVOS NA LANDING ZONE...")
    
    try:
        # Listar arquivos na raiz do container landing-zone
        caminho_raiz = f"wasbs://landing-zone@{STORAGE_ACCOUNT}.blob.core.windows.net/"
        
        files_df = spark.read.format("binaryFile").load(caminho_raiz)
        file_count = files_df.count()
        
        if file_count == 0:
            print("❌ Nenhum arquivo encontrado na raiz da landing zone")
            return []
        
        print(f"✅ Encontrados {file_count} arquivos na landing zone:")
        
        # Mostrar todos os arquivos
        files_df.select("path", "length").show(file_count, truncate=False)
        
        # Procurar por arquivos SQLite
        sqlite_files = files_df.filter(col("path").contains(".sqlite")).collect()
        
        if sqlite_files:
            print(f"\n🎯 Arquivos SQLite encontrados:")
            for file in sqlite_files:
                print(f"  - {file['path']} ({file['length']} bytes)")
        else:
            print("\n⚠️ Nenhum arquivo .sqlite encontrado na landing zone")
        
        return [file['path'] for file in files_df.collect()]
        
    except Exception as e:
        print(f"❌ Erro ao listar arquivos: {str(e)}")
        return [] 