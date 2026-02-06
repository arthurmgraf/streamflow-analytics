# TASK 03 - Diagrama de Arquitetura Cloud

## Titulo
Proposta de Arquitetura Cloud para Ingestao e Consolidacao de Dados da MR. HEALTH

## Objetivo
Propor uma arquitetura completa em cloud para o sistema de ingestao e consolidacao de dados da MR. HEALTH. A arquitetura deve cobrir desde a coleta dos dados nas unidades ate a disponibilizacao dos dados consolidados para consumo, contemplando ambas as fontes: CSVs das unidades e tabelas PostgreSQL da sede.

## Contexto
A MR. HEALTH precisa de uma arquitetura cloud moderna que:

- **Suporte duas fontes de dados distintas**:
  - **CSVs das ~50 unidades**: PEDIDO.CSV e ITEM_PEDIDO.CSV, enviados diariamente a meia-noite (D-1)
  - **PostgreSQL da sede**: Tabelas de referencia PRODUTO, UNIDADE, ESTADO, PAIS
- **Cloud providers aceitos**: GCP, Azure ou AWS (deve-se recomendar um e justificar)
- **Requisitos nao-funcionais**:
  - Alta disponibilidade
  - Escalabilidade horizontal
  - Seguranca (dados de clientes/vendas)
  - Custo otimizado para o porte da empresa (~50 unidades)
  - Facilidade de operacao (equipe enxuta)

### Componentes Esperados na Arquitetura
1. Camada de ingestao (CSVs e PostgreSQL)
2. Camada de armazenamento (Datalake com camadas - detalhado na TASK_04)
3. Camada de processamento/transformacao
4. Camada de orquestracao
5. Camada de monitoramento e observabilidade
6. Camada de seguranca e governanca
7. Camada de consumo/servico de dados

## Criterios de Aceitacao

1. **Diagrama de arquitetura completo** em formato visual (Mermaid, draw.io ou similar) contendo:
   - Todos os componentes e servicos cloud utilizados
   - Fluxo de dados entre componentes (setas direcionais)
   - Separacao clara das camadas (ingestao, processamento, armazenamento, consumo)
2. **Justificativa do cloud provider** escolhido (GCP, Azure ou AWS)
3. **Catalogo de servicos** listando cada servico cloud proposto com:
   - Nome do servico
   - Funcao na arquitetura
   - Justificativa da escolha
   - Alternativas consideradas
4. **Especificacao de cada camada** com detalhes tecnicos
5. **Estimativa de custos** mensal (ordem de grandeza)
6. **Diagrama de rede/seguranca** mostrando VPCs, subnets, endpoints

## Subtasks

### 3.1 - Avaliacao e Selecao do Cloud Provider
- Comparar GCP, Azure e AWS para o cenario da MR. HEALTH
- Avaliar criterios: custo, ecossistema de dados, facilidade de uso, suporte no Brasil
- Recomendar provider com justificativa detalhada
- Mapear servicos equivalentes nos tres providers (tabela comparativa)

### 3.2 - Design da Camada de Ingestao
- **Para CSVs**:
  - Projetar mecanismo de upload (ex.: S3 + Event Notification, GCS + Cloud Functions)
  - Definir bucket/container structure (organizacao por unidade, data, tipo)
  - Definir politica de lifecycle dos arquivos raw
  - Projetar validacao na entrada (Lambda/Cloud Function de validacao)
- **Para PostgreSQL**:
  - Projetar mecanismo de extracao (ex.: AWS DMS, GCP Datastream, Azure Data Factory)
  - Definir conectividade segura (VPN, Direct Connect, Private Link)
  - Definir estrategia incremental vs full load por tabela

### 3.3 - Design da Camada de Processamento
- Selecionar engine de processamento (ex.: Spark/Databricks, AWS Glue, Dataflow, Synapse)
- Definir jobs de transformacao por etapa (raw -> bronze -> silver -> gold)
- Projetar mecanismo de data quality (ex.: Great Expectations, Deequ)
- Definir estrategia de particionamento e compactacao
- Especificar formato de armazenamento intermediario (Parquet, Delta, Iceberg)

### 3.4 - Design da Camada de Armazenamento
- Definir servico de object storage para Datalake (S3, GCS, ADLS)
- Projetar estrutura de diretorios/prefixos (alinhado com TASK_04)
- Definir servico de data catalog (Glue Catalog, Hive Metastore, Unity Catalog)
- Selecionar formato de tabela (Delta Lake, Apache Iceberg, Apache Hudi)
- Definir politicas de retencao e lifecycle

### 3.5 - Design da Camada de Orquestracao
- Selecionar orquestrador (Airflow/MWAA/Cloud Composer, Step Functions, Data Factory)
- Projetar DAGs/pipelines principais
- Definir scheduling e dependencias entre jobs
- Projetar mecanismo de retry e tratamento de falhas
- Definir estrategia de backfill/reprocessamento

### 3.6 - Design da Camada de Monitoramento
- Selecionar ferramentas de monitoramento (CloudWatch, Stackdriver, Azure Monitor)
- Definir metricas e dashboards operacionais
- Projetar alertas e notificacoes
- Definir logging centralizado
- Projetar auditoria de dados (data lineage)

### 3.7 - Design da Camada de Seguranca
- Projetar IAM (roles, policies, service accounts)
- Definir criptografia em repouso e em transito
- Projetar network security (VPC, subnets, security groups, endpoints)
- Definir estrategia de acesso aos dados (RBAC no Datalake)
- Considerar LGPD para dados de clientes/pedidos

### 3.8 - Design da Camada de Consumo
- Definir como os dados consolidados serao acessados (SQL engine, API, BI)
- Selecionar servico de query (Athena, BigQuery, Synapse SQL)
- Projetar integracao com ferramentas de BI (se aplicavel)
- Definir modelo de acesso para diferentes perfis de usuario

### 3.9 - Consolidacao do Diagrama de Arquitetura
- Criar diagrama completo integrando todas as camadas
- Elaborar catalogo de servicos com justificativas
- Estimar custos mensais por componente
- Documentar decisoes arquiteturais (ADRs)
- Revisar coerencia entre todas as camadas

## Dependencias

| Dependencia | Tipo | Descricao |
|-------------|------|-----------|
| TASK_01 (Processo Atual) | **Obrigatoria** | Entender o cenario atual e os problemas a resolver |
| TASK_02 (Processo Futuro) | **Obrigatoria** | O fluxo TO-BE define os requisitos da arquitetura |
| TASK_04 (Datalake) | Bidirecional | A estrategia de armazenamento deve ser coerente com a arquitetura |

## Agentes Sugeridos (Claude Code)

| Agente | Papel | Justificativa |
|--------|-------|---------------|
| **Agente Arquiteto Cloud** | Design principal da arquitetura | Selecionar servicos, projetar integracao entre componentes, garantir boas praticas |
| **Agente de Engenharia de Dados** | Detalhamento tecnico de pipelines | Especificar jobs de processamento, formatos de dados, estrategias de particao |
| **Agente de Seguranca/DevOps** | Design de seguranca e infraestrutura | Projetar IAM, rede, criptografia, compliance LGPD |
| **Agente de FinOps** | Estimativa de custos | Calcular custos estimados por servico, otimizar arquitetura para custo |
| **Agente de Documentacao** | Diagramas e documentacao | Criar diagramas Mermaid/visuais, documentar ADRs |

## Notas Adicionais
- A arquitetura deve ser realista para o porte da MR. HEALTH (~50 unidades, equipe tecnica enxuta)
- Evitar over-engineering: preferir servicos gerenciados/serverless que reduzam overhead operacional
- Considerar a curva de aprendizado da equipe ao selecionar tecnologias
- O diagrama deve ser compreensivel tanto para perfis tecnicos quanto para gestores
- Documentar claramente os trade-offs de cada decisao (custo vs performance vs complexidade)
- Considerar possibilidade de evolucao futura (ex.: streaming, ML) sem exigir refatoracao completa
- Para cada servico proposto, listar alternativas avaliadas e motivo da nao-selecao
