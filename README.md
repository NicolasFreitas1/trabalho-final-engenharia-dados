# Pipeline de Dados para E-commerce

[![Lint & Tests](https://img.shields.io/github/actions/workflow/status/jlsilva01/projeto-ed-satc/ci.yml?branch=main)](https://github.com/jlsilva01/projeto-ed-satc/actions)  
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen.svg)](https://github.com/jlsilva01/projeto-ed-satc)  
[![Docker Pulls](https://img.shields.io/docker/pulls/jlsilva01/projeto-ed-satc)](https://hub.docker.com/r/jlsilva01/projeto-ed-satc)  
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue)](https://jlsilva01.github.io/projeto-ed-satc/)  

Repositório para desenvolvimento do projeto final da disciplina de Engenharia de Dados do curso de Engenharia de Software da UNISATC.

## 📋 Sobre o Projeto

Este projeto implementa um pipeline de dados completo para e-commerce utilizando a arquitetura Lakehouse com Azure Data Lake Storage Gen2 e Apache Spark. O pipeline processa dados através das camadas Bronze (ingestão), Silver (limpeza) e Gold (agregação).

## 🏗️ Desenho de Arquitetura

Coloque uma imagem do seu projeto, como no exemplo abaixo:

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

## 🚀 Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/NicolasFreitas1/trabalho-final-engenharia-dados.git
cd trabalho-final-engenharia-dados
```

### 2. Crie um ambiente virtual Python:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 🏗️ Configuração da Infraestrutura Azure

#### 1. Autenticação no Azure

```bash
# Login no Azure
az login

# Verificar a conta ativa
az account show
```

#### 2. Provisionamento com Terraform

Navegue até a pasta de infraestrutura:
```bash
cd iac
```

Configure as variáveis (opcional):
```bash
# Edite o arquivo variables.tf se necessário
# resource_group_name e location
```

Execute o Terraform:
```bash
# Inicializar
terraform init

# Verificar o plano
terraform plan

# Aplicar a infraestrutura
terraform apply
```

#### 3. Configuração do Azure Data Lake Storage

Após o deploy, você terá:
- ✅ Storage Account criada
- ✅ Containers: `landing-zone`, `bronze`, `silver`, `gold`
- ✅ Políticas de retenção configuradas

### 📦 Instalação de Dependências Python

Instale as dependências necessárias:

```bash
# Instalar Poetry (se não estiver instalado)
pip install poetry

# Instalar dependências do projeto
poetry install

# Ou instalar dependências manualmente
pip install pyspark
pip install delta-spark
pip install azure-storage-blob
pip install pandas
pip install faker
pip install jupyter
pip install notebook
```

### 🎲 Geração de Dados

Execute o script para gerar dados de teste:

```bash
cd scripts
python faker_gerador_ecommerce.py
```

Isso irá gerar arquivos CSV com dados realistas de e-commerce:
- `clientes.csv`
- `produtos.csv`
- `pedidos.csv`
- `pagamentos.csv`
- E outros...

### ☁️ Configuração do Azure Data Lake Storage

#### 1. Upload dos Dados para Landing Zone

```bash
# Usando Azure CLI
az storage blob upload-batch \
  --account-name <storage-account-name> \
  --container-name landing-zone \
  --source ./scripts \
  --pattern "*.csv"
```

#### 2. Configuração de Acesso

Configure as credenciais de acesso no Azure:
- Gere um SAS Token ou configure Service Principal
- Configure as variáveis de ambiente ou use Azure Key Vault

### 📊 Execução dos Pipelines

#### 1. Camada Bronze (Ingestão)

Abra o notebook `projeto_ed_satc/Atividade Pratica - Lakehouse - Bronze.ipynb`:

```python
# Configure as variáveis de conexão
storageAccountName = "seu-storage-account"
sasToken = "seu-sas-token"

# Execute as células para:
# - Montar os containers
# - Ler dados CSV
# - Adicionar metadados
# - Salvar em Delta Lake
```

#### 2. Camada Silver (Limpeza)

Execute o notebook `projeto_ed_satc/Atividade Pratica - Lakehouse - Silver.ipynb`:

```python
# Processos realizados:
# - Leitura dos dados Bronze
# - Padronização de colunas
# - Limpeza de dados
# - Salvamento na camada Silver
```

#### 3. Camada Gold (Agregação)

Execute o notebook `projeto_ed_satc/Atividade Pratica - Lakehouse - Gold.ipynb`:

```python
# Processos realizados:
# - Agregações de negócio
# - Cálculo de métricas
# - Preparação para dashboards
```

## 📝 Observações Importantes

- 🐳 Mantenha o **Docker Desktop** aberto durante todo o processo
- ☁️ Certifique-se de ter créditos suficientes na conta Azure
- 📁 Os dados gerados são fictícios para fins educacionais
- 🔐 Mantenha as credenciais seguras e não as compartilhe
- 📊 O Databricks é recomendado para execução dos notebooks

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

4. **Erro no Spark**:
   - Verifique se o Java está instalado
   - Configure as variáveis de ambiente JAVA_HOME
   - Use Databricks para melhor compatibilidade

## 📚 Documentação (MkDocs)

Toda a documentação está em `docs/`:

```bash
poetry run mkdocs build
poetry run mkdocs serve
```

Acesse o site em `http://127.0.0.1:8000`.

Para publicar o site estático:

```bash
poetry run mkdocs gh-deploy
```

## 🤝 Colaboração

1. Abra uma **issue** para discutir sua feature ou bug.  
2. Crie um **branch**:  

   ```bash
   git checkout -b feature/nome-da-sua-feature
   ```
3. Faça suas alterações e **commit** seguindo o [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).  
4. Envie um **pull request** para `main`.  
5. Aguarde revisão e merge.

## 📈 Versão

Este projeto está na versão 0.1.0 e utiliza controle de versão semântico.

## 👥 Autores

Mencione todos aqueles que ajudaram a levantar o projeto desde o seu início

* **Deyvid Charles Souza de Negreiros** - *Documentação* - [https://github.com/DeivydCharles](https://github.com/DeivydCharles)
* **Diogo Dias de Abreu Alves** - *Documentação* - [https://github.com/DiogoDiasAlves](https://github.com/DiogoDiasAlves)
* **Lucas Perito Lopes** - *Trabalho Inicial* - [(https://github.com/llucaslopes)](https://github.com/llucaslopes)
* **Marcos Vinicius Goudinho da Silva** - *Documentação* - [https://github.com/marcosgoudinho](https://github.com/marcosgoudinho)
* **Nicolas Andrade de Freitas** - *Documentação* - [https://github.com/NicolasFreitas1](https://github.com/NicolasFreitas1)

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
