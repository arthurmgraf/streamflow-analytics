# TASK 05 - Plano de Implementacao (Product Backlog)

## Titulo
Product Backlog para Implementacao do Data Warehouse Moderno da MR. HEALTH

## Objetivo
Elaborar uma lista completa e cronologicamente organizada de todas as atividades necessarias para implementar o processo de ingestao e consolidacao de dados da MR. HEALTH em ambiente cloud. Cada atividade deve conter descricao clara, estimativa de esforco, dependencias e criterios de conclusao.

## Contexto
Este backlog e o consolidado executavel das tasks anteriores:
- **TASK_01**: Definiu o cenario atual e seus problemas
- **TASK_02**: Projetou o fluxo futuro que resolve esses problemas
- **TASK_03**: Especificou a arquitetura cloud e os servicos a utilizar
- **TASK_04**: Detalhou a estrategia de armazenamento em camadas do Datalake

O backlog deve traduzir todas essas definicoes em itens de trabalho acionaveis, organizados em fases logicas de implementacao, de modo que uma equipe de engenharia possa executar sequencialmente.

### Premissas
- Equipe tecnica enxuta (estimar 2-4 engenheiros de dados)
- Cloud provider ja selecionado (conforme TASK_03)
- Acesso ao ambiente de producao do PostgreSQL da sede disponivel
- Cooperacao das unidades para ajuste no mecanismo de envio de CSVs
- Metodologia agil (sprints de 2 semanas)

## Criterios de Aceitacao

1. **Lista completa de atividades** cobrindo todas as fases do projeto
2. **Organizacao cronologica** em fases/sprints logicos
3. **Para cada atividade**:
   - Identificador unico (ex.: IMPL-001)
   - Titulo claro e conciso
   - Descricao detalhada do que deve ser feito
   - Dependencias (quais atividades devem ser concluidas antes)
   - Estimativa de esforco (story points ou dias)
   - Criterio de aceitacao (definition of done)
   - Prioridade (must-have, should-have, nice-to-have)
4. **Marcos (milestones)** definidos para cada fase
5. **Riscos e mitigacoes** por fase
6. **Estimativa total** de timeline do projeto

## Subtasks

### 5.1 - Fase 0: Setup e Fundacao (Sprints 1-2)

#### Atividades Esperadas:
- **IMPL-001**: Criacao da conta/projeto cloud e configuracao inicial
  - Descricao: Criar conta no provider selecionado, configurar billing, definir naming conventions, tags
  - Prioridade: Must-have
  - Esforco estimado: 2-3 dias

- **IMPL-002**: Configuracao de Infrastructure as Code (IaC)
  - Descricao: Setup de Terraform/Pulumi/CloudFormation para gerenciar infraestrutura como codigo
  - Prioridade: Must-have
  - Esforco estimado: 3-5 dias

- **IMPL-003**: Configuracao de rede e seguranca base
  - Descricao: Criar VPC, subnets, security groups, IAM roles base, politicas de criptografia
  - Prioridade: Must-have
  - Esforco estimado: 3-5 dias

- **IMPL-004**: Setup do repositorio de codigo e CI/CD
  - Descricao: Criar repositorio Git, configurar pipelines de CI/CD para deploy de infraestrutura e codigo
  - Prioridade: Must-have
  - Esforco estimado: 2-3 dias

- **IMPL-005**: Setup do ambiente de desenvolvimento
  - Descricao: Configurar ambiente de dev separado do producao, com dados de teste
  - Prioridade: Must-have
  - Esforco estimado: 2-3 dias

**Milestone**: Infraestrutura base provisionada e pronta para desenvolvimento

### 5.2 - Fase 1: Datalake e Armazenamento (Sprints 3-4)

#### Atividades Esperadas:
- **IMPL-006**: Criacao do Datalake (Object Storage)
  - Descricao: Provisionar buckets/containers com estrutura de diretorios conforme TASK_04 (raw/, bronze/, silver/, gold/)
  - Prioridade: Must-have
  - Esforco estimado: 1-2 dias

- **IMPL-007**: Configuracao do Data Catalog
  - Descricao: Setup do catalogo de dados (Glue Catalog, Hive Metastore, Unity Catalog) com databases e schemas
  - Prioridade: Must-have
  - Esforco estimado: 2-3 dias

- **IMPL-008**: Definicao e registro dos schemas Bronze
  - Descricao: Criar schemas/tabelas Bronze para todas as entidades (pedido, item_pedido, produto, unidade, estado, pais)
  - Prioridade: Must-have
  - Esforco estimado: 2-3 dias

- **IMPL-009**: Definicao e registro dos schemas Silver
  - Descricao: Criar schemas/tabelas Silver com transformacoes e integracoes definidas na TASK_04
  - Prioridade: Must-have
  - Esforco estimado: 2-3 dias

- **IMPL-010**: Definicao e registro dos schemas Gold
  - Descricao: Criar schemas do modelo dimensional (fato_vendas, dimensoes) conforme TASK_04
  - Prioridade: Must-have
  - Esforco estimado: 3-5 dias

- **IMPL-011**: Configuracao de politicas de lifecycle e retencao
  - Descricao: Implementar politicas de retencao por camada, lifecycle rules para transicao de storage class
  - Prioridade: Should-have
  - Esforco estimado: 1-2 dias

**Milestone**: Datalake provisionado com schemas registrados em todas as camadas

### 5.3 - Fase 2: Ingestao de Dados (Sprints 5-7)

#### Atividades Esperadas:
- **IMPL-012**: Implementacao da ingestao de CSVs - Mecanismo de upload
  - Descricao: Criar mecanismo para unidades enviarem CSVs ao Datalake (ex.: pre-signed URLs, agente de upload, SFTP gateway)
  - Prioridade: Must-have
  - Esforco estimado: 5-8 dias

- **IMPL-013**: Implementacao da ingestao de CSVs - Deteccao e validacao
  - Descricao: Criar trigger event-driven que detecta novos arquivos, valida formato/schema e move para raw/
  - Prioridade: Must-have
  - Esforco estimado: 3-5 dias

- **IMPL-014**: Implementacao da ingestao de CSVs - Tratamento de erros
  - Descricao: Criar mecanismo de quarentena para arquivos invalidos, notificacao de erros, dead-letter queue
  - Prioridade: Must-have
  - Esforco estimado: 3-5 dias

- **IMPL-015**: Implementacao da ingestao PostgreSQL - Conexao segura
  - Descricao: Configurar conectividade segura entre cloud e PostgreSQL da sede (VPN/tunnel/private link)
  - Prioridade: Must-have
  - Esforco estimado: 3-5 dias

- **IMPL-016**: Implementacao da ingestao PostgreSQL - Extracao
  - Descricao: Implementar jobs de extracao das tabelas PRODUTO, UNIDADE, ESTADO, PAIS (CDC ou batch)
  - Prioridade: Must-have
  - Esforco estimado: 5-8 dias

- **IMPL-017**: Testes de ingestao end-to-end
  - Descricao: Testar ingestao completa com dados reais de uma unidade piloto e dados PostgreSQL
  - Prioridade: Must-have
  - Esforco estimado: 3-5 dias

**Milestone**: Pipeline de ingestao funcional para ambas as fontes (CSV + PostgreSQL)

### 5.4 - Fase 3: Processamento e Transformacao (Sprints 8-10)

#### Atividades Esperadas:
- **IMPL-018**: Implementacao do pipeline Raw -> Bronze
  - Descricao: Jobs de parsing CSV para Parquet/Delta, aplicacao de schema, adicao de metadados de controle
  - Prioridade: Must-have
  - Esforco estimado: 5-8 dias

- **IMPL-019**: Implementacao do pipeline Bronze -> Silver (CSVs)
  - Descricao: Jobs de limpeza, validacao, deduplicacao e normalizacao dos dados de pedidos e itens
  - Prioridade: Must-have
  - Esforco estimado: 5-8 dias

- **IMPL-020**: Implementacao do pipeline Bronze -> Silver (PostgreSQL)
  - Descricao: Jobs de processamento das tabelas de referencia com SCD Type 2
  - Prioridade: Must-have
  - Esforco estimado: 3-5 dias

- **IMPL-021**: Implementacao da integracao Silver (JOIN CSV + PostgreSQL)
  - Descricao: Jobs que unificam dados de pedidos/itens com dados de referencia (produto, unidade, estado, pais)
  - Prioridade: Must-have
  - Esforco estimado: 5-8 dias

- **IMPL-022**: Implementacao do pipeline Silver -> Gold
  - Descricao: Jobs de agregacao, modelagem dimensional, criacao de fato_vendas e dimensoes
  - Prioridade: Must-have
  - Esforco estimado: 5-8 dias

- **IMPL-023**: Implementacao de Data Quality checks
  - Descricao: Validacoes automaticas por camada (Great Expectations/Deequ), com alertas e quarentena
  - Prioridade: Must-have
  - Esforco estimado: 5-8 dias

- **IMPL-024**: Testes de processamento end-to-end
  - Descricao: Testar pipeline completo Raw->Bronze->Silver->Gold com dados reais de varias unidades
  - Prioridade: Must-have
  - Esforco estimado: 3-5 dias

**Milestone**: Pipeline de processamento completo, dados chegando na camada Gold

### 5.5 - Fase 4: Orquestracao e Automacao (Sprints 11-12)

#### Atividades Esperadas:
- **IMPL-025**: Setup do orquestrador
  - Descricao: Provisionar e configurar orquestrador (Airflow/MWAA/Cloud Composer/Step Functions)
  - Prioridade: Must-have
  - Esforco estimado: 3-5 dias

- **IMPL-026**: Implementacao das DAGs/workflows
  - Descricao: Criar DAGs orquestrando todo o pipeline: ingestao -> raw -> bronze -> silver -> gold
  - Prioridade: Must-have
  - Esforco estimado: 5-8 dias

- **IMPL-027**: Configuracao de scheduling
  - Descricao: Configurar agendamento diario alinhado com janela de envio (pos meia-noite), com tolerancia e retries
  - Prioridade: Must-have
  - Esforco estimado: 2-3 dias

- **IMPL-028**: Implementacao de mecanismo de backfill
  - Descricao: Criar capacidade de reprocessar dados historicos para datas especificas
  - Prioridade: Should-have
  - Esforco estimado: 3-5 dias

**Milestone**: Pipeline totalmente orquestrado e automatizado

### 5.6 - Fase 5: Monitoramento e Observabilidade (Sprints 13-14)

#### Atividades Esperadas:
- **IMPL-029**: Configuracao de logging centralizado
  - Descricao: Configurar coleta de logs de todos os componentes em servico centralizado
  - Prioridade: Must-have
  - Esforco estimado: 2-3 dias

- **IMPL-030**: Criacao de dashboards operacionais
  - Descricao: Dashboard com metricas do pipeline: status de ingestao por unidade, volume processado, latencia, erros
  - Prioridade: Must-have
  - Esforco estimado: 3-5 dias

- **IMPL-031**: Configuracao de alertas
  - Descricao: Alertas para falhas criticas: unidade sem envio, pipeline com erro, data quality violation
  - Prioridade: Must-have
  - Esforco estimado: 2-3 dias

- **IMPL-032**: Implementacao de data lineage
  - Descricao: Rastreabilidade da origem ate o destino de cada dado (lineage metadata)
  - Prioridade: Nice-to-have
  - Esforco estimado: 3-5 dias

**Milestone**: Operacao monitorada com alertas e visibilidade completa

### 5.7 - Fase 6: Testes, Migracao e Go-Live (Sprints 15-17)

#### Atividades Esperadas:
- **IMPL-033**: Testes de carga com todas as unidades
  - Descricao: Simular envio de 50 unidades simultaneamente, validar performance e corretude
  - Prioridade: Must-have
  - Esforco estimado: 3-5 dias

- **IMPL-034**: Testes de resiliencia e falha
  - Descricao: Testar cenarios de falha: unidade offline, arquivo corrompido, banco indisponivel, pipeline retry
  - Prioridade: Must-have
  - Esforco estimado: 3-5 dias

- **IMPL-035**: Migracao de dados historicos
  - Descricao: Carregar dados historicos (planilhas consolidadas da equipe do Ricardo) no Datalake
  - Prioridade: Should-have
  - Esforco estimado: 5-8 dias

- **IMPL-036**: Onboarding de unidades piloto (5-10 unidades)
  - Descricao: Migrar primeiras unidades para o novo mecanismo de envio, validar em paralelo com processo antigo
  - Prioridade: Must-have
  - Esforco estimado: 5-8 dias

- **IMPL-037**: Onboarding progressivo das demais unidades
  - Descricao: Migrar as ~40 unidades restantes em lotes, com validacao a cada lote
  - Prioridade: Must-have
  - Esforco estimado: 8-13 dias

- **IMPL-038**: Descomissionamento do processo manual
  - Descricao: Encerrar o processo manual de consolidacao em planilhas, documentar procedimento de rollback
  - Prioridade: Must-have
  - Esforco estimado: 2-3 dias

- **IMPL-039**: Documentacao operacional e treinamento
  - Descricao: Criar runbooks, documentacao de operacao, treinar equipe do Ricardo Martins no novo processo
  - Prioridade: Must-have
  - Esforco estimado: 5-8 dias

**Milestone**: Sistema em producao com todas as 50 unidades migradas

### 5.8 - Consolidacao do Backlog Final
- Compilar todas as atividades em formato de backlog estruturado
- Calcular timeline total estimada (em sprints e semanas)
- Criar Gantt chart simplificado ou roadmap visual
- Identificar caminho critico do projeto
- Documentar riscos por fase com planos de mitigacao
- Definir criterios de go/no-go para cada milestone

## Resumo de Timeline Estimada

| Fase | Sprints | Semanas | Descricao |
|------|---------|---------|-----------|
| Fase 0 | 1-2 | 4 | Setup e Fundacao |
| Fase 1 | 3-4 | 4 | Datalake e Armazenamento |
| Fase 2 | 5-7 | 6 | Ingestao de Dados |
| Fase 3 | 8-10 | 6 | Processamento e Transformacao |
| Fase 4 | 11-12 | 4 | Orquestracao e Automacao |
| Fase 5 | 13-14 | 4 | Monitoramento e Observabilidade |
| Fase 6 | 15-17 | 6 | Testes, Migracao e Go-Live |
| **Total** | **17 sprints** | **~34 semanas (~8 meses)** | **Projeto completo** |

## Dependencias

| Dependencia | Tipo | Descricao |
|-------------|------|-----------|
| TASK_01 (Processo Atual) | **Obrigatoria** | Define o escopo dos problemas a resolver |
| TASK_02 (Processo Futuro) | **Obrigatoria** | Define o que sera implementado |
| TASK_03 (Arquitetura) | **Obrigatoria** | Define quais servicos e tecnologias serao usados |
| TASK_04 (Datalake) | **Obrigatoria** | Define a estrutura de armazenamento a implementar |

## Agentes Sugeridos (Claude Code)

| Agente | Papel | Justificativa |
|--------|-------|---------------|
| **Agente de Gestao de Projeto** | Organizacao e priorizacao do backlog | Sequenciar atividades, estimar esforco, identificar dependencias e caminho critico |
| **Agente Engenheiro de Dados** | Detalhamento tecnico das atividades | Validar viabilidade tecnica, detalhar description of done, estimar complexidade |
| **Agente DevOps/Infra** | Atividades de infraestrutura | Detalhar atividades de IaC, CI/CD, rede, seguranca |
| **Agente Arquiteto Cloud** | Revisao de coerencia | Garantir que o backlog cobre toda a arquitetura da TASK_03 |
| **Agente de Documentacao** | Formatacao e visualizacao | Criar roadmap visual, Gantt chart, documentacao do backlog |

## Notas Adicionais
- O backlog assume sprints de 2 semanas com equipe de 2-4 engenheiros de dados
- As estimativas de esforco sao em dias de trabalho de um engenheiro (ajustar conforme tamanho da equipe)
- A Fase 6 (Go-Live) pode ser acelerada ou desacelerada conforme apetite de risco da empresa
- Recomenda-se abordagem de "walk before you run": comecar com piloto pequeno antes de escalar
- Cada milestone deve ter um checkpoint formal com stakeholders (Ricardo Martins e gestao)
- O backlog deve ser tratado como documento vivo, refinado a cada sprint
- Considerar buffer de 20-30% nas estimativas para imprevistos tecnicos
- Priorizar sempre must-have antes de should-have e nice-to-have em cada fase
