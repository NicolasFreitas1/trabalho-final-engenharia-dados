# -*- coding: utf-8 -*-
# 📊 Dashboards do Medalhão Gold

Este diretório contém dashboards interativos para visualização e análise dos dados do medalhão Gold do Lakehouse.

## 🎯 Dashboards Disponíveis

### 1. Dashboard de Tabelas (Dados Simulados)
- **Arquivo:** `dashboard_tabelas.py`
- **Descrição:** Exploração detalhada de todas as tabelas do medalhão Gold
- **Funcionalidades:**
  - Visualização de dados por tabela
  - Estatísticas básicas
  - Gráficos específicos por tipo de tabela
  - Análise de distribuições

### 2. Dashboard de KPIs e Métricas (Dados Simulados)
- **Arquivo:** `dashboard_kpis.py`
- **Descrição:** Dashboard executivo com KPIs e métricas de negócio
- **Funcionalidades:**
  - 4 KPIs principais
  - 2 métricas secundárias
  - Análises temporais
  - Gráficos de performance

### 3. Dashboard de Tabelas (Dados Reais) ⭐ NOVO
- **Arquivo:** `dashboard_tabelas_real.py`
- **Descrição:** Versão conectada aos dados reais do medalhão Gold
- **Funcionalidades:**
  - Conexão direta com Spark e Delta Lake
  - Dados reais das tabelas Gold
  - Fallback para dados simulados em caso de erro
  - Performance otimizada

### 4. Dashboard de KPIs e Métricas (Dados Reais) ⭐ NOVO
- **Arquivo:** `dashboard_kpis_real.py`
- **Descrição:** Dashboard executivo com dados reais integrados
- **Funcionalidades:**
  - KPIs calculados com dados reais
  - Joins entre tabelas fato e dimensões
  - Filtros temporais
  - Análises integradas

## 🚀 Como Executar

### Pré-requisitos
```bash
pip install -r requirements.txt
```

### Opção 1: Dashboards com Dados Simulados
```bash
# Executar dashboard de tabelas
streamlit run dashboard_tabelas.py

# Executar dashboard de KPIs
streamlit run dashboard_kpis.py

# Ou usar o script automatizado
python run_dashboards.py
```

### Opção 2: Dashboards com Dados Reais ⭐ RECOMENDADO
```bash
# Executar dashboard de tabelas com dados reais
streamlit run dashboard_tabelas_real.py

# Executar dashboard de KPIs com dados reais
streamlit run dashboard_kpis_real.py

# Ou usar o script automatizado
python run_dashboards_real.py
```

## 📋 Tabelas do Medalhão Gold

### Tabelas de Dimensão
- `dim_customers` - Informações dos clientes
- `dim_tempo` - Dimensão temporal
- `dim_geolocation` - Dados geográficos
- `dim_leads_closed` - Leads fechados
- `dim_leads_qualified` - Leads qualificados
- `dim_order_items` - Itens dos pedidos
- `dim_order_payments` - Pagamentos dos pedidos
- `dim_order_reviews` - Reviews dos pedidos
- `dim_product_category_name_translation` - Tradução de categorias
- `dim_products` - Informações dos produtos
- `dim_sellers` - Informações dos vendedores

### Tabelas de Fato
- `fato_orders` - Pedidos (tabela fato principal)

## 🔧 Configuração para Dados Reais

### Requisitos do Ambiente
- Apache Spark configurado
- Delta Lake habilitado
- Acesso às tabelas Gold no caminho: `/mnt/datalake4b6c87c48101c278/gold/`

### Estrutura de Conexão
Os dashboards com dados reais utilizam:
```python
# Caminho base das tabelas Gold
caminho_base = "/mnt/datalake4b6c87c48101c278/gold"

# Carregamento com Spark
df = spark.read.format("delta").load(f"{caminho_base}/{nome_tabela}")
```

### Fallback Automático
Se houver erro na conexão com dados reais, os dashboards automaticamente:
1. Exibem mensagem de erro
2. Carregam dados simulados como fallback
3. Permitem continuar a análise

## 📊 KPIs e Métricas Disponíveis

### KPIs Principais
1. **Total de Pedidos** - Volume de vendas
2. **Receita Total** - Valor total das vendas
3. **Ticket Médio** - Valor médio por pedido
4. **Taxa de Conversão** - Conversão de leads em vendas

### Métricas Secundárias
1. **Clientes Únicos** - Base de clientes ativa
2. **Score Médio de Reviews** - Satisfação do cliente
3. **Taxa de Entrega** - Eficiência operacional

## 🎨 Funcionalidades dos Dashboards

### Filtros Disponíveis
- **Período:** Últimos 30 dias, 90 dias, 6 meses, 1 ano, todo período
- **Tabela:** Seleção específica de tabelas
- **Categoria:** Filtros por categoria de produto
- **Status:** Filtros por status de pedido

### Visualizações
- Gráficos de linha (evolução temporal)
- Gráficos de pizza (distribuições)
- Gráficos de barras (comparações)
- Histogramas (distribuições de valores)
- Mapas (dados geográficos)
- Tabelas interativas

## 🔍 Análises Específicas por Tabela

### dim_customers
- Distribuição por estado e cidade
- Análise geográfica dos clientes

### dim_tempo
- Evolução temporal
- Sazonalidade por mês/ano

### dim_geolocation
- Mapa de distribuição geográfica
- Concentração por região

### dim_leads_*
- Análise de conversão
- Performance por fonte
- Distribuição por status

### dim_order_*
- Análise de pagamentos
- Distribuição de reviews
- Performance de itens

### dim_products
- Distribuição por categoria
- Análise de peso e dimensões

### dim_sellers
- Distribuição geográfica
- Performance por vendedor

### fato_orders
- KPIs principais
- Análise de status
- Performance temporal

## 🛠️ Solução de Problemas

### Erro de Conexão Spark
```bash
# Verificar se o Spark está configurado
pyspark --version

# Verificar variáveis de ambiente
echo $SPARK_HOME
echo $JAVA_HOME
```

### Erro de Encoding
```bash
# Executar script de correção de encoding
python fix_encoding.py
```

### Erro de Null Bytes
```bash
# Executar script de remoção de null bytes
python fix_null_bytes.py
```

### Performance Lenta
- Reduzir limite de registros nos dashboards
- Usar cache adequado
- Verificar configurações do Spark

## 📝 Logs e Monitoramento

Os dashboards incluem:
- Indicadores de carregamento
- Mensagens de erro detalhadas
- Cache automático de dados
- Logs de performance

## 🔄 Atualizações

### Versão 2.0 - Dados Reais
- ✅ Conexão direta com medalhão Gold
- ✅ Fallback automático para dados simulados
- ✅ Performance otimizada
- ✅ Filtros temporais avançados

### Próximas Versões
- [ ] Cache persistente
- [ ] Exportação de relatórios
- [ ] Alertas automáticos
- [ ] Integração com APIs externas

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs de erro
2. Testar conexão Spark
3. Validar caminhos das tabelas
4. Consultar documentação do projeto

---

**Desenvolvido para o projeto de Engenharia de Dados - Lakehouse Architecture** 