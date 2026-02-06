# TASK 02 - Mapeamento do Processo Futuro de Dados

## Titulo
Design do Novo Fluxo de Dados da MR. HEALTH em Ambiente Cloud

## Objetivo
Projetar o fluxo de dados futuro (TO-BE) que resolva todos os problemas identificados no mapeamento atual (TASK_01). O novo fluxo deve considerar migracao total para nuvem, automatizacao completa do processo de ingestao e consolidacao, e capacidade de escalar alem das 50 unidades atuais.

## Contexto
Com base nos gargalos e problemas mapeados na TASK_01, o novo processo deve:

- **Eliminar etapas manuais**: A consolidacao feita manualmente pela equipe do Ricardo Martins deve ser totalmente automatizada
- **Garantir confiabilidade**: Mecanismos de validacao, retry e monitoramento devem ser incorporados
- **Escalar horizontalmente**: O processo deve suportar crescimento da rede (50 -> 100+ unidades) sem degradacao
- **Integrar todas as fontes**: CSVs das unidades e tabelas PostgreSQL da sede devem convergir em um pipeline unificado
- **Migrar para cloud**: Toda a infraestrutura de dados deve residir em ambiente cloud (GCP, Azure ou AWS)
- **Garantir qualidade dos dados**: Validacoes automaticas, deduplicacao e tratamento de erros

### Requisitos do Novo Processo
- Ingestao automatizada dos CSVs (PEDIDO.CSV e ITEM_PEDIDO.CSV) das ~50 unidades
- Ingestao automatizada das tabelas PostgreSQL (PRODUTO, UNIDADE, ESTADO, PAIS) da sede
- Processamento e transformacao dos dados em pipeline orquestrado
- Armazenamento em camadas (Datalake - detalhado na TASK_04)
- Monitoramento e alertas em tempo real
- Capacidade de reprocessamento historico

## Criterios de Aceitacao

1. **Diagrama de fluxo TO-BE** documentado com todas as etapas do novo processo
2. **Tabela comparativa AS-IS vs TO-BE** mostrando como cada problema do processo atual sera resolvido
3. **Definicao dos mecanismos de ingestao**:
   - Como os CSVs serao coletados das unidades (push vs pull, protocolo, frequencia)
   - Como os dados PostgreSQL serao extraidos (CDC, dump periodico, replicacao)
4. **Estrategia de orquestracao** do pipeline de dados
5. **Plano de monitoramento e alertas** definindo:
   - Metricas a serem monitoradas
   - Condicoes de alerta
   - SLAs de processamento
6. **Estrategia de tratamento de erros e reprocessamento**
7. **Analise de escalabilidade** demonstrando capacidade de crescimento

## Subtasks

### 2.1 - Design do Mecanismo de Ingestao de CSVs
- Definir como as unidades enviarao os CSVs (ex.: upload para bucket S3/GCS/Blob Storage)
- Projetar mecanismo de deteccao de novos arquivos (event-driven)
- Definir validacao na entrada (schema validation, completude, formato)
- Projetar tratamento de arquivos invalidos ou ausentes
- Definir politica de retry e dead-letter para falhas
- Considerar janela de envio (meia-noite) e tolerancia de atraso

### 2.2 - Design do Mecanismo de Ingestao PostgreSQL
- Avaliar opcoes de extracao: CDC (Change Data Capture), dump periodico, replicacao logica
- Definir frequencia de sincronizacao (diaria, near-real-time)
- Projetar mecanismo de extracao incremental vs full
- Definir tratamento de schema evolution nas tabelas de origem
- Considerar impacto na performance do banco de producao

### 2.3 - Design do Pipeline de Processamento
- Definir etapas de transformacao dos dados CSV (parsing, limpeza, enriquecimento)
- Definir etapas de transformacao dos dados PostgreSQL
- Projetar integracao/join entre dados CSV e tabelas de referencia
- Definir ferramenta de orquestracao (ex.: Airflow, Step Functions, Cloud Composer)
- Projetar DAG/workflow com dependencias entre etapas
- Definir estrategia de idempotencia (reprocessamento seguro)

### 2.4 - Design do Monitoramento e Observabilidade
- Definir metricas-chave do pipeline (latencia, volume, taxa de erro, completude)
- Projetar dashboards operacionais
- Definir alertas criticos (ex.: unidade nao enviou dados, pipeline falhou)
- Projetar mecanismo de notificacao (email, Slack, PagerDuty)
- Definir SLAs de disponibilidade dos dados consolidados

### 2.5 - Elaboracao da Tabela Comparativa AS-IS vs TO-BE
- Para cada problema da TASK_01, descrever a solucao no novo fluxo
- Quantificar ganhos esperados (tempo, confiabilidade, custo operacional)
- Documentar riscos residuais do novo processo
- Identificar premissas e restricoes

### 2.6 - Consolidacao do Documento TO-BE
- Compilar diagrama de fluxo TO-BE completo (Mermaid)
- Redigir narrativa do novo processo end-to-end
- Documentar decisoes de design e justificativas
- Incluir analise de escalabilidade (projecao para 100, 200 unidades)

## Dependencias

| Dependencia | Tipo | Descricao |
|-------------|------|-----------|
| TASK_01 (Processo Atual) | **Obrigatoria** | O mapeamento AS-IS e base fundamental para o design TO-BE |
| TASK_03 (Arquitetura) | Bidirecional | O processo futuro e a arquitetura devem ser co-desenvolvidos |
| TASK_04 (Datalake) | Informativa | A estrategia de armazenamento influencia as etapas finais do pipeline |

## Agentes Sugeridos (Claude Code)

| Agente | Papel | Justificativa |
|--------|-------|---------------|
| **Agente Arquiteto de Dados** | Design do pipeline e fluxo TO-BE | Projetar a solucao tecnica de ingestao, processamento e armazenamento |
| **Agente de Engenharia de Dados** | Detalhamento tecnico dos mecanismos | Especificar tecnicamente os mecanismos de ingestao, CDC, orquestracao |
| **Agente Analista de Negocios** | Validacao da tabela AS-IS vs TO-BE | Garantir que todos os problemas de negocio foram enderecados |
| **Agente de Documentacao** | Estruturacao e diagramas | Criar diagramas Mermaid e documentacao clara do novo fluxo |

## Notas Adicionais
- O diagrama TO-BE deve ser visualmente comparavel ao AS-IS da TASK_01 para facilitar comunicacao com stakeholders
- Priorizar solucoes cloud-native e serverless quando possivel (reducao de overhead operacional)
- Considerar custos operacionais ao escolher entre abordagens (ex.: CDC real-time vs batch diario)
- A escolha do cloud provider (GCP/Azure/AWS) sera detalhada na TASK_03, mas o design do processo deve ser provider-agnostic quando possivel
- Documentar trade-offs de cada decisao (ex.: simplicidade vs flexibilidade, custo vs performance)
