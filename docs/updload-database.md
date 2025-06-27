# SQLite para Lakehouse com Python e Azure Data Lake Gen2

Este conjunto de scripts permite exportar dados de um banco SQLite local para arquivos CSV e carregá-los na arquitetura Lakehouse (landing zone) no Azure Data Lake Gen2, com controle total sobre sobrescrita e limpeza dos arquivos.

## Pré-requisitos

- Python 3.8+
- Bibliotecas: `pandas`, `azure-storage-file-datalake`, `sqlite3`
- SAS Token do Azure Storage com permissões adequadas
- Acesso ao arquivo SQLite local

> **O arquivo SQLite utilizado neste projeto está disponível publicamente em:** > [https://www.kaggle.com/datasets/terencicp/e-commerce-dataset-by-olist-as-an-sqlite-database?resource=download](https://www.kaggle.com/datasets/terencicp/e-commerce-dataset-by-olist-as-an-sqlite-database?resource=download)
>
> Baixe o arquivo e coloque-o no diretório indicado em `db_path`.

## Instalação de Dependências

```bash
pip install pandas azure-storage-file-datalake
```

## Configuração

### 1. Parâmetros do Azure Storage

Edite as seguintes variáveis no script:

```python
account_name = "SEU_ACCOUNT_NAME"  # Nome da storage account
sas_token = "SEU_SAS_TOKEN"        # Token SAS do Azure Storage
filesystem_name = "landing-zone"   # Nome do container
landing_zone_path = "csvs"         # Pasta de destino no Data Lake (ou "" para raiz)
```

### 2. Parâmetros do SQLite

```python
db_path = '../data/db.sqlite'          # Caminho para o banco SQLite
export_dir = '../data/exported_tables' # Diretório para salvar os CSVs
```

## Modos de Operação

Tanto a exportação quanto o upload aceitam três modos:

- `'skip'`: pula arquivos que já existem (não sobrescreve nada)
- `'overwrite'`: sobrescreve arquivos existentes
- `'force'`: deleta arquivos antigos antes de exportar/subir

Exemplo de configuração:

```python
export_mode = 'skip'      # Para exportação do SQLite
upload_mode = 'overwrite' # Para upload ao Data Lake
```

## Como Usar

### 1. Edite o script `scripts/export_and_upload_sqlite_to_datalake.py` com seus parâmetros.

### 2. Execute o script:

```bash
python scripts/export_and_upload_sqlite_to_datalake.py
```

### 3. Exemplo de uso das funções no seu próprio notebook ou script:

```python
from export_and_upload_sqlite_to_datalake import export_sqlite_to_csv, create_datalake_client, upload_files_to_datalake

# Parâmetros
account_name = "SEU_ACCOUNT_NAME"
sas_token = "SEU_SAS_TOKEN"
filesystem_name = "landing-zone"
landing_zone_path = "csvs"
db_path = 'data/db.sqlite'
export_dir = 'data/exported_tables'

# Modos
export_mode = 'force'      # 'skip', 'overwrite' ou 'force'
upload_mode = 'force'      # 'skip', 'overwrite' ou 'force'

# Exportação
export_sqlite_to_csv(db_path, export_dir, mode=export_mode)

# Cliente Data Lake
datalake_client = create_datalake_client(account_name, sas_token, filesystem_name)

# Upload
upload_files_to_datalake(export_dir, landing_zone_path, datalake_client, mode=upload_mode)
```

## O que cada modo faz?

- **skip**: nunca sobrescreve arquivos já existentes, ideal para execuções incrementais.
- **overwrite**: sempre sobrescreve arquivos existentes, sem deletar explicitamente antes.
- **force**: deleta arquivos antigos antes de exportar/subir, garantindo limpeza total.

## Fluxo de Processamento

1. **Exportação do SQLite**: Exporta todas as tabelas para CSV, conforme o modo escolhido.
2. **Upload para o Data Lake**: Faz upload dos CSVs para a landing zone, conforme o modo escolhido.
3. **Logs informativos**: O script imprime o modo selecionado e o que está sendo feito em cada etapa.

## Estrutura de Saída

### Landing Zone

```
landing-zone/csvs/
├── customers.csv
├── geolocation.csv
├── leads_closed.csv
├── ...
└── sellers.csv
```

## Troubleshooting

- **Permissões SAS**: Certifique-se de que o SAS Token tem permissões de leitura, escrita, criação e deleção para o container e objetos.
- **Erros de conexão**: Verifique o caminho do banco SQLite e as credenciais do Azure.
- **Sobrescrita/limpeza**: Use o modo adequado para seu caso de uso.

## Personalização

- Para exportar apenas algumas tabelas, edite a função de exportação para filtrar as tabelas desejadas.
- Para mudar o formato de saída (ex: Parquet), adapte a função de exportação.

---

**Dúvidas ou problemas? Consulte o script e os prints de log para entender o que foi feito em cada etapa.**
