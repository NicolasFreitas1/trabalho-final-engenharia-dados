# Pipeline de Dados para E-commerce

[![Lint & Tests](https://img.shields.io/github/actions/workflow/status/jlsilva01/projeto-ed-satc/ci.yml?branch=main)](https://github.com/jlsilva01/projeto-ed-satc/actions)  
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen.svg)](https://github.com/jlsilva01/projeto-ed-satc)  
[![Docker Pulls](https://img.shields.io/docker/pulls/jlsilva01/projeto-ed-satc)](https://hub.docker.com/r/jlsilva01/projeto-ed-satc)  
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue)](https://jlsilva01.github.io/projeto-ed-satc/)

Repositório para desenvolvimento do projeto final da disciplina de Engenharia de Dados do curso de Engenharia de Software da UNISATC.

## 📋 Sobre o Projeto

Este projeto implementa um pipeline de dados completo para e-commerce utilizando a arquitetura Lakehouse com Azure Data Lake Storage Gen2 e Apache Spark. O pipeline processa dados através das camadas Bronze (ingestão), Silver (limpeza) e Gold (agregação).

### 🆕 Funcionalidades Principais

- **📊 Pipeline Lakehouse Completo**: Bronze → Silver → Gold
- **🗄️ Exportação SQLite para Data Lake**: Script Python para exportar bancos SQLite
- **🤖 Automação com Airflow**: DAG para automatizar o processo de exportação e upload
- **☁️ Integração Azure**: Data Lake Storage Gen2 com SAS Token
- **📚 Documentação Completa**: MkDocs com guias detalhados

## 🏗️ Desenho de Arquitetura

![image](https://github.com/NicolasFreitas1/trabalho-final-engenharia-dados/blob/main/assets/arquitetura.png)

## 🛠️ Pré-requisitos e Ferramentas Utilizadas

🐍 **Python 3.11.9**: Linguagem principal para processamento  
🐳 **Docker Desktop** (manter aberto durante o uso): Containerização dos serviços  
📁 **Git**: Controle de versão  
💻 **VS Code ou IDE de preferência**: Editor de código  
☁️ **Azure CLI**: Autenticação e gerenciamento de recursos Azure  
🏗️ **Terraform**: Infraestrutura como código  
📊 **Apache Spark**: Processamento distribuído de dados  
🎯 **Azure Databricks**: Ambiente de execução dos notebooks  
📦 **Poetry**: Gerenciamento de dependências Python  
🤖 **Apache Airflow**: Orquestração de pipelines

## 🚀 Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/NicolasFreitas1/trabalho-final-engenharia-dados.git
cd trabalho-final-engenharia-dados
```

### 2. Criar ambiente virtual Python

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependências

```bash
# Instalar Poetry (se não estiver instalado)
pip install poetry

# Instalar dependências do projeto
poetry install

# Ou instalar dependências manualmente
pip install pyspark delta-spark azure-storage-file-datalake pandas faker jupyter notebook mkdocs mkdocs-material
```

## 🏗️ Configuração da Infraestrutura Azure

### 1. Autenticação no Azure

```bash
# Login no Azure
az login

# Verificar a conta ativa
az account show
```

### 2. Provisionamento com Terraform

```bash
cd iac

# Inicializar
terraform init

# Verificar o plano
terraform plan

# Aplicar a infraestrutura
terraform apply
```

### 3. Configuração do Azure Data Lake Storage

Após o deploy, você terá:

- ✅ Storage Account criada
- ✅ Containers: `landing-zone`, `bronze`, `silver`, `gold`
- ✅ Políticas de retenção configuradas

## 📊 Execução dos Pipelines

### 🗄️ Exportação SQLite para Data Lake

#### 1. Script Python Manual

```bash
# Configurar parâmetros no script
cd scripts
python export_and_upload_sqlite_to_datalake.py
```

**Modos disponíveis:**

- `skip`: Pula arquivos existentes
- `overwrite`: Sobrescreve arquivos existentes
- `force`: Deleta arquivos antigos antes de exportar/subir

#### 2. Automação com Airflow

```bash
# Configurar variáveis no Airflow
# Executar o DAG sqlite_to_datalake
```

### 🎲 Geração de Dados de Teste

```bash
cd scripts
python faker_gerador_ecommerce.py
```

Gera arquivos CSV com dados realistas de e-commerce.

### 📊 Pipeline Lakehouse (Databricks)

#### 1. Camada Bronze (Ingestão)

Execute o notebook `projeto_ed_satc/Atividade Pratica - Lakehouse - Bronze.ipynb`:

```python
# Configure as variáveis de conexão
storageAccountName = "seu-storage-account"
sasToken = "seu-sas-token"
```

#### 2. Camada Silver (Limpeza)

Execute o notebook `projeto_ed_satc/Atividade Pratica - Lakehouse - Silver.ipynb`

#### 3. Camada Gold (Agregação)

Execute o notebook `projeto_ed_satc/Atividade Pratica - Lakehouse - Gold.ipynb`

## 📚 Documentação

### Acessar a documentação local

```bash
# Servidor de desenvolvimento
poetry run mkdocs serve

# Build para produção
poetry run mkdocs build

# Deploy para GitHub Pages
poetry run mkdocs gh-deploy
```

Acesse: `http://127.0.0.1:8000`

### Documentação disponível

- **📖 Upload de Banco de Dados**: Guia completo para exportação SQLite
- **🤖 Automação com Airflow**: Configuração e uso do DAG
- **🏗️ Configuração do Ambiente**: Setup inicial do projeto

## 🛠️ Resolução de Problemas

### Problemas Comuns:

1. **Erro de autenticação Azure**:

   ```bash
   az login --use-device-code
   ```

2. **Erro de permissões Terraform**:

   ```bash
   az role assignment create --assignee <app-id> --role Contributor --scope /subscriptions/<subscription-id>
   ```

3. **Erro de conexão com Storage**:

   - Verifique se o SAS Token está correto
   - Confirme se o container existe
   - Verifique as permissões de acesso

4. **Erro no Poetry**:

   ```bash
   pip install poetry
   poetry --version
   ```

5. **Erro no MkDocs**:
   ```bash
   poetry add mkdocs mkdocs-material
   poetry run mkdocs serve
   ```

## 📝 Observações Importantes

- 🐳 Mantenha o **Docker Desktop** aberto durante todo o processo
- ☁️ Certifique-se de ter créditos suficientes na conta Azure
- 📁 Os dados gerados são fictícios para fins educacionais
- 🔐 Mantenha as credenciais seguras e não as compartilhe
- 📊 O Databricks é recomendado para execução dos notebooks
- 🤖 Configure as variáveis do Airflow antes de executar o DAG

## 🤝 Colaboração

1. Abra uma **issue** para discutir sua feature ou bug
2. Crie um **branch**:
   ```bash
   git checkout -b feature/nome-da-sua-feature
   ```
3. Faça suas alterações e **commit** seguindo o [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
4. Envie um **pull request** para `main`
5. Aguarde revisão e merge

## 📈 Versão

Este projeto está na versão 0.1.0 e utiliza controle de versão semântico.

## 👥 Autores

- **Deyvid Charles Souza de Negreiros** - _Dashboard_ - [DeivydCharles](https://github.com/DeivydCharles)
- **Diogo Dias de Abreu Alves** - _Mkdocs_ - [DiogoDiasAlves](https://github.com/DiogoDiasAlves)
- **Lucas Perito Lopes** - _Documentação_ - [(llucaslopes)](https://github.com/llucaslopes)
- **Marcos Vinicius Goudinho da Silva** - _Implementação dos medalhões_ - [marcosgoudinho](https://github.com/marcosgoudinho)
- **Nicolas Andrade de Freitas** - _Ingestão de dados_ - [NicolasFreitas1](https://github.com/NicolasFreitas1)
- **Vitor Valcanaia Rosendo Martins** - _KPIs_ - [Valcanaia282](https://github.com/Valcanaia282)
## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.  
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 📖 Referências

Repositórios de referência:

- 📖 [Projeto ED SATC](https://github.com/jlsilva01/projeto-ed-satc)

Documentações:

- 📖 [Documentação Jupyter](https://docs.jupyter.org/en/latest/)
- 📖 [Documentação Azure Data Lake Storage](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction)
- 📖 [Documentação Delta Lake](https://docs.delta.io/)
- 📖 [Documentação Apache Spark](https://spark.apache.org/docs/latest/)
- 📖 [Documentação Terraform Azure](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- 📖 [Documentação Apache Airflow](https://airflow.apache.org/docs/)
