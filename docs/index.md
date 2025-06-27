# 🛒 E-commerce Data Pipeline - Projeto Final Engenharia de Dados

## 📊 Visão Geral

Este projeto implementa uma solução completa de engenharia de dados para uma plataforma de **e-commerce**, abrangendo desde a geração e ingestão de dados até a criação de um pipeline completo com arquitetura **Data Lake** em camadas.

A arquitetura foi desenvolvida utilizando tecnologias modernas de big data, incluindo **Apache Spark**, **Azure Data Lake Storage**, **Delta Lake** e ferramentas de infraestrutura como código. A temática escolhida — plataforma de e-commerce — permite trabalhar com dados realistas e ricos em volume e variedade, simulando um ambiente de produção real.

## 🏗️ Arquitetura da Solução

O projeto segue uma arquitetura de **Data Lake** com processamento em camadas:

### 📥 Camada de Ingestão (Landing Zone)
- Geração automatizada de dados com **Faker**
- Upload de dados de banco **SQLite** existente
- Dados de múltiplas entidades (clientes, produtos, pedidos, pagamentos)
- Armazenamento em formato CSV para processamento inicial

### 🥉 Bronze Layer
- Dados brutos no formato original
- Armazenamento em formato **Delta Lake**
- Adição de metadados (timestamp, nome do arquivo, fonte)
- Histórico completo de todas as informações

### 🥈 Silver Layer
- Dados limpos e estruturados
- Padronização de colunas (nomenclatura em maiúsculas)
- Aplicação de regras de negócio básicas
- Preparação para transformações

### 🥇 Gold Layer
- Dados agregados e otimizados para consumo
- Métricas de negócio calculadas
- Pronto para análises e relatórios
- Dashboards e visualizações

### ☁️ Infraestrutura Cloud
- **Azure Data Lake Storage Gen2** provisionado via Terraform
- Containers organizados por camada
- Políticas de retenção configuradas
- Escalabilidade automática

## 🎯 Objetivos do Projeto

- **📊 Análise de Vendas**: Entender padrões de compra e comportamento do cliente
- **🔍 Monitoramento**: Acompanhar métricas de performance em tempo real
- **💡 Insights**: Gerar recomendações baseadas em dados históricos
- **⚡ Escalabilidade**: Arquitetura preparada para crescimento
- **🛠️ Automação**: Pipeline completo com infraestrutura como código
- **🔄 Migração de Dados**: Suporte para upload de bancos existentes

## 🛠️ Tecnologias Utilizadas

- **🐍 Python 3.11+**: Linguagem principal para processamento
- **🌪️ Apache Spark**: Processamento distribuído de dados
- **☁️ Azure Data Lake Storage Gen2**: Armazenamento na nuvem
- **📊 Delta Lake**: Formato de dados para data lakes
- **🏗️ Terraform**: Infraestrutura como código
- **🐳 Docker**: Containerização dos serviços
- **📚 MkDocs**: Documentação técnica
- **🎲 Faker**: Geração de dados realistas
- **🗄️ SQLite**: Banco de dados para upload de dados existentes

## 📋 Pré-requisitos

Antes de iniciar, certifique-se de ter instalado em sua máquina:

- 🐍 **Python 3.11.9**
- 🐳 **Docker Desktop** (manter aberto durante o uso)
- 📁 **Git**
- 💻 **VS Code** ou IDE de preferência
- ☁️ **Azure CLI** (para deploy da infraestrutura)
- 🏗️ **Terraform** (para provisionamento)

## 🚀 Como Começar

1. **📖 Leia a documentação** de configuração do ambiente
2. **🏗️ Configure** a infraestrutura Azure com Terraform
3. **📦 Execute** o gerador de dados ou **🗄️ faça upload** de banco existente
4. **🔄 Execute** os pipelines de dados (Bronze → Silver → Gold)
5. **📊 Explore** os resultados e análises

## 🎓 Contexto Acadêmico

Este projeto foi desenvolvido como parte do curso de **Engenharia de Dados** da UNISATC, aplicando conceitos modernos de:

- **Data Engineering**: Pipelines robustos e escaláveis
- **Data Architecture**: Padrões de mercado (Data Lake, Delta Lake)
- **Cloud Computing**: Infraestrutura na nuvem (Azure)
- **DevOps**: Infraestrutura como código (Terraform)
- **Analytics**: Insights orientados por dados

## 📁 Estrutura do Projeto

```
trabalho-final-engenharia-dados/
├── 📚 docs/                    # Documentação
│   ├── index.md               # Página principal
│   ├── sobre.md               # Configuração do ambiente
│   └── updload-database.md    # Upload de banco de dados
├── 🏗️ iac/                     # Infraestrutura como código
├── 📊 projeto_ed_satc/         # Notebooks principais
├── 🔧 scripts/                 # Scripts auxiliares
│   ├── faker_gerador_ecommerce.py      # Gerador de dados
│   ├── upload_database_spark_cells.py  # Upload SQLite
│   └── upload-database.ipynb           # Notebook de upload
├── 🖼️ assets/                  # Diagramas
└── 📄 Configurações
```

## 🔄 Funcionalidades Principais

### 📊 Geração de Dados
- Script automatizado com **Faker** para dados realistas
- Múltiplas entidades de e-commerce
- Exportação em formato CSV

### 🗄️ Upload de Banco de Dados
- Suporte para **SQLite** existente
- Processamento via **Apache Spark**
- Migração automática para Data Lake
- Metadados de rastreabilidade

### ☁️ Pipeline de Dados
- Processamento em camadas (Bronze → Silver → Gold)
- Armazenamento em **Delta Lake**
- Integração com **Azure Data Lake Storage**

## 👥 Autores

- **Deyvid Charles Souza de Negreiros**
- **Diogo Dias de Abreu Alves**
- **Lucas Perito Lucas**
- **Marcos Vinicius Goudinho da Silva**
- **Nicolas Andrade de Freitas**
- **Vitor Valcanaia Rosendo Martins**

---

🚀 **Pronto para começar?** Acesse a seção de [Configuração do Ambiente](sobre.md) e siga o passo a passo!