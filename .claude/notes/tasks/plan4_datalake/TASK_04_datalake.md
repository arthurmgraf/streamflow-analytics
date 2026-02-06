# TASK 04 - Estrategia de Armazenamento (Datalake)

## Titulo
Estrategia de Organizacao e Armazenamento de Dados no Datalake da MR. HEALTH

## Objetivo
Descrever a estrategia completa de organizacao dos dados no Datalake, definindo a estrutura de cada camada (Raw, Bronze, Silver, Gold), os schemas de dados em cada nivel, as transformacoes aplicadas entre camadas, e como as fontes CSV e PostgreSQL serao integradas ao longo do pipeline de armazenamento.

## Contexto
O Datalake sera o repositorio central de todos os dados da MR. HEALTH. A estrategia de armazenamento utiliza a arquitetura Medallion (medalhao) com 4 camadas progressivas de refinamento:

### Fontes de Dados a Integrar
1. **CSVs das Unidades** (diarios, D-1):
   - `PEDIDO.CSV` - Pedidos realizados (colunas esperadas: id_pedido, id_unidade, data_pedido, valor_total, etc.)
   - `ITEM_PEDIDO.CSV` - Itens de cada pedido (colunas esperadas: id_item, id_pedido, id_produto, quantidade, valor_unitario, etc.)
2. **PostgreSQL da Sede** (tabelas de referencia):
   - `PRODUTO` - Catalogo de produtos (id_produto, nome, categoria, preco_sugerido, etc.)
   - `UNIDADE` - Cadastro de unidades (id_unidade, nome, endereco, id_estado, etc.)
   - `ESTADO` - Estados (id_estado, sigla, nome, id_pais, etc.)
   - `PAIS` - Paises (id_pais, nome, sigla, etc.)

### Arquitetura Medallion (4 Camadas)
| Camada | Proposito | Qualidade | Consumidores |
|--------|-----------|-----------|--------------|
| **Raw** | Dado bruto, copia fiel da origem | Sem tratamento | Engenheiros de dados |
| **Bronze** | Dado estruturado, com metadados | Limpeza basica, tipagem | Engenheiros de dados |
| **Silver** | Dado limpo, validado, normalizado | Validado, deduplicado | Analistas de dados |
| **Gold** | Dado agregado, modelado para consumo | Business-ready | Gestores, BI, Aplicacoes |

## Criterios de Aceitacao

1. **Definicao detalhada de cada camada** contendo:
   - Proposito e publico-alvo
   - Schema/estrutura dos dados armazenados
   - Formato de armazenamento (CSV, Parquet, Delta, Iceberg)
   - Estrategia de particionamento
   - Politica de retencao
   - Transformacoes aplicadas na transicao para a proxima camada
2. **Mapeamento origem-destino** de cada fonte por camada
3. **Estrategia de integracao** mostrando em qual camada os dados CSV e PostgreSQL sao unificados
4. **Estrutura de diretorios/prefixos** no object storage
5. **Definicao de data quality** checks por camada
6. **Schema evolution strategy** para mudancas futuras
7. **Glossario de dados** (data dictionary) da camada Gold

## Subtasks

### 4.1 - Design da Camada Raw
- **Proposito**: Armazenar copia fiel dos dados de origem, sem nenhuma transformacao
- Definir estrutura de diretorios:
  ```
  raw/
    csv/
      pedido/
        year=YYYY/month=MM/day=DD/
          unidade_XX_pedido_YYYYMMDD.csv
      item_pedido/
        year=YYYY/month=MM/day=DD/
          unidade_XX_item_pedido_YYYYMMDD.csv
    postgresql/
      produto/
        year=YYYY/month=MM/day=DD/
          produto_full_YYYYMMDD.parquet
      unidade/
        ...
      estado/
        ...
      pais/
        ...
  ```
- Definir formato: CSV original para arquivos CSV, Parquet para dumps PostgreSQL
- Definir politica de retencao (ex.: 2 anos para compliance)
- Definir metadados de controle: timestamp de ingestao, nome do arquivo original, hash de integridade
- Nenhuma transformacao aplicada (dado bruto)

### 4.2 - Design da Camada Bronze
- **Proposito**: Dados estruturados com schema definido, limpeza basica e metadados
- Transformacoes Raw -> Bronze:
  - Parse dos CSVs para formato colunar (Parquet/Delta)
  - Aplicacao de schema (tipagem de colunas)
  - Adicao de colunas de controle: `_ingestion_timestamp`, `_source_file`, `_source_system`, `_batch_id`
  - Tratamento de encoding (UTF-8)
  - Deduplicacao exata (registros identicos)
- Definir schema Bronze para cada entidade:
  - `bronze_pedido` (schema completo com tipos)
  - `bronze_item_pedido` (schema completo com tipos)
  - `bronze_produto` (schema completo com tipos)
  - `bronze_unidade` (schema completo com tipos)
  - `bronze_estado` (schema completo com tipos)
  - `bronze_pais` (schema completo com tipos)
- Formato: Delta Lake ou Apache Iceberg (ACID transactions)
- Particionamento: por data de ingestao (`year/month/day`)

### 4.3 - Design da Camada Silver
- **Proposito**: Dados limpos, validados, normalizados e prontos para analise
- Transformacoes Bronze -> Silver:
  - Validacao de regras de negocio (ex.: valor_total > 0, id_unidade valido)
  - Deduplicacao logica (ex.: mesmo pedido de unidades diferentes)
  - Normalizacao de campos (ex.: datas no formato ISO, strings trimmed)
  - Enriquecimento com dados de referencia (JOIN com tabelas PostgreSQL)
  - Tratamento de dados ausentes (nulls) com regras definidas
  - Aplicacao de SCD (Slowly Changing Dimensions) para tabelas de referencia
- Definir schema Silver:
  - `silver_pedido` - Pedido limpo e enriquecido com dados da unidade
  - `silver_item_pedido` - Item limpo e enriquecido com dados do produto
  - `silver_produto` - Produto validado com historico (SCD Type 2)
  - `silver_unidade` - Unidade validada com estado e pais
- **Ponto de integracao**: CSVs e PostgreSQL sao unificados nesta camada
- Formato: Delta Lake / Iceberg
- Particionamento: por data do pedido (`year/month`) e/ou por unidade

### 4.4 - Design da Camada Gold
- **Proposito**: Dados agregados e modelados para consumo de negocio
- Transformacoes Silver -> Gold:
  - Agregacoes de negocio (vendas por unidade, por produto, por periodo)
  - Metricas calculadas (ticket medio, produtos mais vendidos, tendencias)
  - Modelagem dimensional (Star Schema ou similar)
  - Criacao de tabelas/views prontas para BI
- Definir modelos Gold:
  - `gold_fato_vendas` - Fato principal: vendas consolidadas
    - Granularidade: item de pedido
    - Metricas: quantidade, valor_unitario, valor_total, desconto
    - Dimensoes: produto, unidade, estado, data
  - `gold_dim_produto` - Dimensao produto
  - `gold_dim_unidade` - Dimensao unidade (com estado e pais desnormalizados)
  - `gold_dim_data` - Dimensao calendario
  - `gold_agg_vendas_diarias` - Agregacao de vendas por dia/unidade
  - `gold_agg_vendas_produto` - Agregacao de vendas por produto/periodo
  - `gold_agg_performance_unidade` - Metricas de performance por unidade
- Formato: Delta Lake / Iceberg
- Particionamento: otimizado para queries mais comuns
- Definir refresh strategy (incremental vs full rebuild)

### 4.5 - Definicao de Data Quality por Camada
- **Raw**: Apenas verificacao de integridade do arquivo (hash, tamanho)
- **Bronze**: Schema validation, tipo de dados, completude de campos obrigatorios
- **Silver**: Regras de negocio, integridade referencial, ranges validos, unicidade
- **Gold**: Reconciliacao de totais, consistency checks, SLA de freshness
- Definir framework de data quality (Great Expectations, Deequ, custom)
- Definir acoes para falhas de qualidade (quarentena, alerta, bloqueio)

### 4.6 - Estrategia de Schema Evolution
- Definir como novas colunas nos CSVs serao tratadas
- Definir como mudancas nas tabelas PostgreSQL serao propagadas
- Projetar versionamento de schemas
- Definir politica de backward compatibility

### 4.7 - Glossario de Dados e Documentacao
- Criar data dictionary completo da camada Gold
- Documentar linhagem de dados (data lineage) da origem ate Gold
- Definir ownership e stewardship de cada dominio de dados
- Documentar regras de negocio aplicadas em cada transformacao

## Dependencias

| Dependencia | Tipo | Descricao |
|-------------|------|-----------|
| TASK_01 (Processo Atual) | **Obrigatoria** | Entender as fontes de dados e seus schemas |
| TASK_02 (Processo Futuro) | **Obrigatoria** | O fluxo TO-BE define como os dados chegam ao Datalake |
| TASK_03 (Arquitetura) | **Obrigatoria/Bidirecional** | Os servicos cloud selecionados determinam tecnologias de armazenamento |
| TASK_05 (Backlog) | Informativa | A estrategia de armazenamento gera itens de implementacao |

## Agentes Sugeridos (Claude Code)

| Agente | Papel | Justificativa |
|--------|-------|---------------|
| **Agente Engenheiro de Dados** | Design das camadas e transformacoes | Definir schemas, transformacoes, formatos e particionamento por camada |
| **Agente Arquiteto de Dados** | Modelagem dimensional Gold | Projetar Star Schema, definir fatos e dimensoes, otimizar para queries |
| **Agente de Data Quality** | Framework de qualidade | Definir validacoes por camada, regras de negocio, acoes para falhas |
| **Agente Analista de Negocios** | Definicao de metricas Gold | Definir quais agregacoes e metricas sao relevantes para o negocio |
| **Agente de Documentacao** | Glossario e data lineage | Criar documentacao de dados, dicionario, linhagem |

## Notas Adicionais
- A escolha entre Delta Lake, Apache Iceberg ou Apache Hudi deve ser justificada com base no cloud provider da TASK_03
- O ponto de integracao entre CSVs e PostgreSQL na camada Silver e critico - documentar com diagramas
- Considerar uso de table format moderno (Delta/Iceberg) desde a camada Bronze para suportar ACID e time travel
- A granularidade da camada Gold deve ser validada com requisitos de negocio (quais relatorios/dashboards serao criados)
- Incluir exemplos concretos de dados em cada camada para facilitar compreensao
- Documentar custos estimados de armazenamento por camada (baseado no volume de ~50 unidades)
- Considerar compactacao (Parquet + Snappy/Zstd) para otimizar custos de storage
- A politica de retencao deve considerar requisitos legais/fiscais (dados de vendas)
