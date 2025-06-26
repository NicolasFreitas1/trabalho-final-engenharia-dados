# 🚀 Configuração do Ambiente - E-commerce Data Pipeline

## 📋 Pré-requisitos

Antes de iniciar, certifique-se de ter instalado em sua máquina:

- 🐍 **Python 3.11.9**
- 🐳 **Docker Desktop** (manter aberto durante o uso)
- 📁 **Git**
- 💻 **VS Code** ou IDE de preferência
- ☁️ **Azure CLI** (para autenticação)
- 🏗️ **Terraform** (para provisionamento da infraestrutura)
- 📊 **Apache Spark** (via Databricks ou local)

## ⚙️ Configuração do Ambiente

### 📂 Preparação do Workspace

1. Clone o repositório:
```bash
git clone https://github.com/NicolasFreitas1/trabalho-final-engenharia-dados.git
cd trabalho-final-engenharia-dados
```

2. Crie um ambiente virtual Python:
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
# Dependências principais
pip install pyspark
pip install delta-spark
pip install azure-storage-blob
pip install pandas
pip install faker

# Dependências para desenvolvimento
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

## 📚 Recursos Adicionais

- 📖 [Documentação Azure Data Lake Storage](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction)
- 📖 [Documentação Delta Lake](https://docs.delta.io/)
- 📖 [Documentação Apache Spark](https://spark.apache.org/docs/latest/)
- 📖 [Documentação Terraform Azure](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)

---

🎯 **Pronto para começar!** Siga os passos acima e você terá um pipeline completo de dados funcionando!
