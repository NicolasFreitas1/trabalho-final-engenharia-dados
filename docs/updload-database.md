# SQLite para Lakehouse com Spark

Este conjunto de scripts permite ler dados de um banco SQLite localizado em um servidor e carregá-los na arquitetura Lakehouse usando Apache Spark.

## Pré-requisitos

### Para o Notebook (Databricks)

- Workspace do Databricks configurado
- Cluster Spark com acesso ao Azure Storage
- Permissões para montar storage no Databricks

## Configuração

### 1. Configurações do Azure Storage

Edite as seguintes variáveis nos scripts:

```python
storage_account_name = "datalake4b6c87c48101c278"  # Seu storage account
sas_token = "seu_token_sas_aqui"  # Token SAS do Azure Storage
```

### 2. Configurações do SQLite

Especifique o caminho do arquivo SQLite no servidor:

```python
# Para acesso direto ao arquivo
sqlite_path = "/caminho/para/servidor/db.sqlite"

# Para acesso via JDBC (se configurado)
sqlite_server_url = "jdbc:sqlite://servidor:porta/caminho/db.sqlite"
```

### 3. Tabelas a serem processadas

A lista padrão inclui as tabelas do dataset Olist:

```python
tables = [
    "customers", "geolocation", "leads_closed", "leads_qualified",
    "order_items", "order_payments", "order_reviews", "orders",
    "product_category_name_translation", "products", "sellers"
]
```

## Como Usar

### Opção 1: Notebook Databricks

1. Abra o notebook `upload-database-spark.ipynb` no Databricks
2. Execute as células em sequência
3. Ajuste as configurações conforme necessário
4. Monitore o progresso através das células de validação

### Opção 2: Script Python

1. Configure as variáveis no script
2. Execute o comando:

```bash
python upload_database_spark.py
```

Ou no Databricks:

```python
%run /path/to/upload_database_spark.py
```

## Fluxo de Processamento

1. **Configuração do Spark**: Criação da SparkSession
2. **Montagem do Storage**: Conexão com Azure Storage
3. **Leitura do SQLite**:
   - Método 1: JDBC (se disponível)
   - Método 2: pandas + sqlite3 (fallback)
4. **Adição de Metadados**: Timestamp e informações de origem
5. **Landing Zone**: Salvamento como CSV
6. **Camada Bronze**: Salvamento como Delta Lake
7. **Validação**: Verificação dos dados processados

## Estrutura de Saída

### Landing Zone

```
/mnt/{storage_account}/landing-zone/
├── customers_{timestamp}.csv
├── geolocation_{timestamp}.csv
├── leads_closed_{timestamp}.csv
├── ...
└── sellers_{timestamp}.csv
```

### Camada Bronze

```
/mnt/{storage_account}/bronze/
├── customers/
├── geolocation/
├── leads_closed/
├── ...
└── sellers/
```

## Metadados Adicionados

Cada tabela processada recebe as seguintes colunas de metadados:

- `data_hora_bronze`: Timestamp do processamento
- `nome_arquivo`: Nome do arquivo de origem
- `fonte_dados`: Identificação da fonte (sqlite_server)

## Tratamento de Erros

O script inclui tratamento robusto de erros:

- **Falha no JDBC**: Fallback automático para pandas
- **Erro de conexão**: Log detalhado do erro
- **Falha no storage**: Continuação com outras tabelas
- **Validação**: Verificação de integridade dos dados

## Monitoramento

### Logs de Execução

- Progresso de cada etapa
- Contagem de linhas por tabela
- Tempo de processamento
- Erros e avisos

### Validação de Dados

- Verificação de arquivos na landing zone
- Verificação de tabelas na Bronze
- Amostra de dados para validação

## Troubleshooting

### Problemas Comuns

1. **Erro de conexão SQLite**

   - Verifique o caminho do arquivo
   - Confirme permissões de acesso
   - Teste a conexão manualmente

2. **Erro de montagem do Storage**

   - Verifique o SAS token
   - Confirme o nome da storage account
   - Verifique permissões no Azure

3. **Erro de memória Spark**
   - Ajuste as configurações de partição
   - Reduza o tamanho do lote
   - Aumente a memória do cluster

### Comandos de Diagnóstico

```python
# Verificar montagens
display(dbutils.fs.mounts())

# Listar arquivos na landing zone
display(dbutils.fs.ls(f"/mnt/{storage_account}/landing-zone"))

# Verificar tabelas na Bronze
display(dbutils.fs.ls(f"/mnt/{storage_account}/bronze"))

# Testar leitura de uma tabela
df = spark.read.format('delta').load(f'/mnt/{storage_account}/bronze/products')
df.count()
```

## Personalização

### Adicionar Novas Tabelas

Edite a lista `tables` no script:

```python
tables = [
    "sua_tabela_1",
    "sua_tabela_2",
    # ... outras tabelas
]
```

### Modificar Metadados

Ajuste as colunas de metadados na função `read_sqlite_from_server`:

```python
df = df.withColumn("data_hora_bronze", current_timestamp()) \
       .withColumn("nome_arquivo", lit(f"{table}_{timestamp}.csv")) \
       .withColumn("fonte_dados", lit("sqlite_server")) \
       .withColumn("seu_metadado", lit("seu_valor"))
```

### Configurar Particionamento

Para otimizar o desempenho, configure o particionamento:

```python
df.write.format('delta') \
    .partitionBy("data_hora_bronze") \
    .mode("overwrite") \
    .save(bronze_path)
```

## Suporte

Para dúvidas ou problemas:

1. Verifique os logs de execução
2. Teste a conectividade manualmente
3. Valide as configurações do Azure Storage
4. Consulte a documentação do Spark e Databricks
