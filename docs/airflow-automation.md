# Automação do Pipeline SQLite → Azure Data Lake com Airflow

Este projeto inclui um DAG do Airflow para automatizar o processo de exportação de tabelas de um banco SQLite para arquivos CSV e upload desses arquivos para o Azure Data Lake Gen2.

## Estrutura do DAG

O DAG `sqlite_to_datalake` executa duas tarefas principais, em sequência:

1. **Exportação do SQLite para CSV**

   - Utiliza a função `export_sqlite_to_csv` para exportar todas as tabelas do banco SQLite para arquivos CSV em um diretório local.
   - O modo de exportação (`skip`, `overwrite`, `force`) é configurável via variável do Airflow.

2. **Upload dos CSVs para o Data Lake**
   - Utiliza as funções `create_datalake_client` e `upload_files_to_datalake` para enviar os arquivos CSV para o Azure Data Lake Gen2.
   - O modo de upload (`skip`, `overwrite`, `force`) também é configurável via variável do Airflow.

## Configuração das Variáveis no Airflow

O DAG utiliza variáveis do Airflow para parametrização, facilitando a alteração de credenciais e modos de operação sem necessidade de alterar o código:

- `account_name`: Nome da Storage Account no Azure
- `sas_token`: SAS Token com permissões adequadas
- `filesystem_name`: Nome do container no Data Lake
- `landing_zone_path`: Caminho/pasta de destino no Data Lake
- `export_mode`: Modo de exportação do SQLite (`skip`, `overwrite`, `force`)
- `upload_mode`: Modo de upload para o Data Lake (`skip`, `overwrite`, `force`)

Essas variáveis podem ser definidas na interface do Airflow em Admin > Variables.

## Caminhos de Dados

- O banco SQLite deve estar disponível em `/opt/airflow/data/db.sqlite` (ajuste conforme necessário).
- Os arquivos CSV exportados são salvos em `/opt/airflow/data/exported_tables`.

## Agendamento

- O DAG está agendado para rodar diariamente (`schedule_interval='@daily'`).
- O parâmetro `catchup=False` garante que apenas execuções futuras sejam consideradas.

## Exemplo de Execução Manual

Você pode executar o DAG manualmente pela interface do Airflow, ou aguardar a execução automática conforme o agendamento.

## Extensões e Personalizações

- Para adicionar notificações, logging customizado ou integração com outros sistemas, basta adicionar novas tasks ou hooks no DAG.
- Para alterar o agendamento, modifique o parâmetro `schedule_interval`.
- Para rodar em outros ambientes, ajuste os caminhos dos arquivos conforme necessário.

---

Se tiver dúvidas sobre como configurar ou rodar o Airflow, consulte a [documentação oficial do Apache Airflow](https://airflow.apache.org/docs/).
