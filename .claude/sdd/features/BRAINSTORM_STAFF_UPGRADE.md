# BRAINSTORM: Staff Engineer Upgrade — StreamFlow Analytics 10/10

> Plano completo e definitivo para elevar o StreamFlow Analytics de 4.5/10 para 10/10 em qualidade de Staff Data Engineer. Cobrindo todos os 10 problemas criticos identificados na auditoria.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | STAFF_UPGRADE |
| **Date** | 2026-02-07 |
| **Author** | the-planner (Claude Opus 4.6) |
| **Status** | Ready for Define |
| **Score Atual** | 4.5/10 |
| **Score Alvo** | 10/10 |
| **Estimativa Total** | ~65 arquivos novos + ~30 modificados = ~95 arquivos |
| **Complexidade** | ALTA — Reescrita de componentes core + infraestrutura nova |

---

## Initial Idea

**Raw Input:** Elevar o StreamFlow Analytics para nivel genuino de Staff Data Engineer. O projeto atual tem fundacao solida (models, generators, utils, SQL, Terraform) mas os componentes criticos — Flink jobs, ML, testes, DAGs, CI/CD, observabilidade — estao abaixo do padrao profissional. O objetivo e criar um portfolio que impressione em entrevistas de Staff/Principal.

**Context Gathered:**
- Projeto ja tem 99 arquivos, 85 testes passando, ruff + mypy + pytest limpos
- Infraestrutura K8s bem definida (5 namespaces, Strimzi, Flink Operator, CloudNativePG, Airflow)
- Modelos Pydantic v2 robustos com validacao e serializacao
- Geradores sinteticos funcionais (TransactionGenerator, FraudInjector, CustomerGenerator)
- SQL Medallion bem estruturado (4 migrations, 2 transforms, 1 quality check)
- Server K3s real disponivel (15.235.61.251, 4 CPU, 9.7GB RAM, 598GB disco)
- PROBLEMA CRITICO: `fraud_detector.py` usa dicts Python para estado, NAO e um job Flink real
- PROBLEMA CRITICO: Zero componentes de ML em um projeto de deteccao de fraude
- CI/CD basico (ci.yaml tem lint+test, deploy.yaml e manual com Terraform)

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Flink State | Dicts Python simples em `FraudEngine` (linhas 57-61) | Estado perdido em restart — reescrever com `KeyedProcessFunction` + `ValueState` |
| ML Pipeline | Inexistente | Adicionar Isolation Forest com Feature Store pattern |
| DLQ | Eventos malformados descartados silenciosamente | Implementar Dead Letter Queue com topico Kafka dedicado |
| DAGs Airflow | 4 DAGs com 1-3 tasks lineares cada | Refatorar com TaskGroups, callbacks, SLA, alertas |
| Testes E2E | `test_full_pipeline.py` testa FraudEngine em memoria | Criar testes de integracao reais + contract tests |
| Schema Evolution | `schema_version: 1` hardcoded | Implementar versionamento forward-compatible |
| K8s Hardening | Sem PDB, NetworkPolicy, probes configurados | Adicionar configs de producao |
| CI/CD | Sem ArgoCD, sem quality gates automaticos | Implementar GitOps completo |
| Observabilidade | Sem metricas customizadas, sem tracing | Adicionar metricas de negocio + OpenTelemetry |
| Chaos Engineering | Inexistente | Adicionar testes de resiliencia com LitmusChaos ou scripts |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual o objetivo principal? | 10/10 maximo — impressionar entrevistadores de Staff | Todas as 10 lacunas devem ser corrigidas, sem atalhos |
| 2 | Qual abordagem de ML? | Isolation Forest + Feature Store (features pre-computadas no PostgreSQL Gold) | ML offline com scoring inline — sem complexidade de serving |
| 3 | Deploy real ou simulado? | Deploy real no K3s (15.235.61.251) com screenshots | Precisa funcionar de verdade, nao apenas "parece que funciona" |
| 4 | Nivel de testes? | Unit + Integration + Contract Tests (Testcontainers no server SSH) | Testes de integracao reais com Kafka e PostgreSQL via Testcontainers |
| 5 | CI/CD? | GitHub Actions + ArgoCD para GitOps | Pipeline completo: lint -> test -> build -> deploy automatico |
| 6 | Documentacao? | Premium README + Mermaid diagrams + screenshots | Documentacao que vende o projeto |
| 7 | Extra? | Chaos Engineering (kill pods, simular falhas) | Demonstrar mentalidade de producao — resiliencia |
| 8 | Budget? | $0 — tudo open-source | Sem servicos pagos, tudo roda no K3s on-premise |
| 9 | Servidor aguenta? | 4 CPU, 9.7GB RAM, ~5.7GB free, 527GB disco livre | Budget de 4GB RAM para StreamFlow — ML leve, sem GPU |
| 10 | Prioridade se faltar tempo? | Architecture > Code Quality > Tests > ML > CI/CD > Chaos | Flink real e ML sao indispensaveis, chaos e nice-to-have |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Transaction model | `src/models/transaction.py` | 1 | Pydantic v2, 10 campos, validacao completa |
| FraudAlert model | `src/models/fraud_alert.py` | 1 | 5 FraudRuleIds, Decimal scores |
| Customer model | `src/models/customer.py` | 1 | Profile com risk_profile |
| Store model | `src/models/store.py` | 1 | 10 cidades brasileiras |
| State helpers | `src/flink_jobs/common/state.py` | 1 | RunningStats (Welford), GeoLocation, haversine_km |
| Fraud patterns | `src/generators/fraud_patterns.py` | 4 | High value, velocity, geographic, time anomaly |
| SQL transforms | `sql/transforms/` | 3 | bronze_to_silver, silver_to_gold, update_customer_stats |
| SQL quality | `sql/quality/quality_checks.sql` | 1 | 4 checks (null, dup, freshness, amount) |
| K8s manifests | `k8s/` | 6 | 3 Flink, 1 Kafka topics, 1 alerting, 1 service monitors |
| Grafana dashboards | `k8s/monitoring/` | 4 | Pipeline, Kafka, Flink, Fraud (JSON) |
| Unit tests | `tests/unit/` | 5 | models, config, serialization, generators, fraud_detector |
| E2E tests | `tests/e2e/` | 1 | test_full_pipeline.py (FALSO — so testa in-memory) |

**Como os samples serao usados:**
- Modelos Pydantic existentes serao reutilizados sem alteracao (Transaction, Customer, Store)
- FraudAlert ganha novo membro `ML_ANOMALY = "FR-006"`
- RunningStats ganha `to_bytes()`/`from_bytes()` para serializacao Flink
- SQL transforms sao divididos em arquivos individuais para paralelismo no Airflow
- Testes existentes continuam passando via alias `FraudEngine = FraudRuleEvaluator`

---

## Auditoria Detalhada: Os 10 Problemas Criticos

### P1: Flink `fraud_detector.py` NAO e um Job Flink Real

**Severidade:** CRITICA (bloqueia credibilidade)

**Evidencia no codigo:**
```python
# src/flink_jobs/fraud_detector.py linhas 57-61
self._amount_stats: dict[str, RunningStats] = {}
self._velocity_windows: dict[str, list[float]] = {}
self._last_locations: dict[str, GeoLocation] = {}
self._hour_stats: dict[str, RunningStats] = {}
self._blacklist: set[str] = set()
```

**Por que e critico:** Estado em dicts Python e volatil. Se o TaskManager reiniciar (OOM, crash, upgrade), TODOS os historicos de clientes sao perdidos. Em Flink real, usamos `ValueState<T>` que e persistido em checkpoints e sobrevive a falhas. A classe inteira `FraudEngine` nao usa NENHUMA API do Flink — e Python puro com import do Flink apenas no `transaction_processor.py`.

**Evidencia no K8s:**
```yaml
# k8s/flink/fraud-detector.yaml
state.backend: hashmap      # Deveria ser rocksdb para producao
upgradeMode: stateless       # Deveria ser savepoint para preservar estado
```

**Impacto no score:** -2.0 pontos (diferenca entre "parece Flink" e "e Flink de verdade")

---

### P2: Zero Componentes de ML

**Severidade:** CRITICA (gap de skill esperado para Staff)

**Evidencia:** Nenhum arquivo de ML existe no projeto. A deteccao de fraude usa apenas 5 regras com pesos fixos. Staff Data Engineers em fraud detection devem demonstrar:
- Feature engineering (extrair sinais preditivos dos dados)
- Model training (treinar modelo offline com dados historicos)
- Model scoring (integrar score ML no pipeline de streaming)
- Model versioning (controlar qual modelo esta em producao)

**Impacto no score:** -1.5 pontos

---

### P3: Sem Dead Letter Queue (DLQ)

**Severidade:** ALTA

**Evidencia:**
```python
# src/flink_jobs/transaction_processor.py linha 47
logger.warning("Skipping malformed event: %s", raw[:200])
return None
```

Eventos malformados sao descartados silenciosamente. Em producao, isso e inaceitavel porque:
- Nao ha como investigar POR QUE eventos falharam
- Nao ha como reprocessar eventos corrigidos
- Metricas de erro ficam imprecisas

**Impacto no score:** -0.5 pontos

---

### P4: DAGs Airflow Triviais

**Severidade:** ALTA

**Evidencia detalhada por DAG:**

| DAG | Tasks | Complexidade | Falta |
|-----|-------|-------------|-------|
| `bronze_to_silver.py` | 2 (linear) | Minima | TaskGroups, callbacks, SLA, validacao pre/pos |
| `silver_to_gold.py` | 2 + sensor | Baixa | TaskGroups por dimensao/fato, notificacao |
| `data_quality.py` | 1 (!) | Minima | Tasks individuais, alertas, branching |
| `maintenance.py` | 3 (linear) | Baixa | Paralelismo, callbacks, metricas |

**O que falta globalmente:** TaskGroups, `on_failure_callback`, `on_success_callback`, `sla` no default_args, `sla_miss_callback`, tarefas dinamicas com `@task`, Jinja templates `{{ ds }}`, XCom para passar contagens entre tasks, alertas no Slack/email.

**Impacto no score:** -0.5 pontos

---

### P5: Testes E2E Falsos

**Severidade:** ALTA

**Evidencia:** `tests/e2e/test_full_pipeline.py` esta marcado como `@pytest.mark.e2e` mas:
- Nao conecta em Kafka
- Nao conecta em PostgreSQL
- Nao sobe Flink
- So instancia `FraudEngine()` em memoria e chama `process_transaction()`
- E basicamente um teste de integracao in-memory disfarçado de E2E

**O que falta:**
- Testes de integracao com Testcontainers (Kafka + PostgreSQL reais)
- Contract tests para compatibilidade de schema
- Testes da `KeyedProcessFunction` com estado mockado
- Testes de DAG structure (DagBag validation)

**Impacto no score:** -0.5 pontos

---

### P6: Sem Schema Evolution

**Severidade:** MEDIA

**Evidencia:**
```python
# src/flink_jobs/transaction_processor.py linha 44
"schema_version": 1,
```

Hardcoded, sem estrategia de versionamento. Se o schema mudar:
- Consumers antigos nao sabem lidar com campos novos
- Nao ha backward/forward compatibility
- Nao ha registro de qual versao e "atual"

**Impacto no score:** -0.3 pontos

---

### P7: K8s Configs Minimas

**Severidade:** MEDIA

**Evidencia em `k8s/flink/fraud-detector.yaml`:**
- Sem `readinessProbe` / `livenessProbe` customizados
- Sem `PodDisruptionBudget`
- Sem `NetworkPolicy` entre namespaces
- Sem `topologySpreadConstraints`
- Sem `podAntiAffinity`
- Resource requests/limits existem mas nao foram tunados

**Impacto no score:** -0.3 pontos

---

### P8: CI/CD Incompleto

**Severidade:** MEDIA

**Evidencia:**
- `ci.yaml` existe mas so faz lint+test (sem build de imagem, sem quality gates)
- `deploy.yaml` e `workflow_dispatch` manual (nao e GitOps)
- Sem ArgoCD para deploy automatico
- Sem Codecov integration
- Sem security scanning (trivy, bandit)
- Sem matrix de dependencias

**Impacto no score:** -0.3 pontos

---

### P9: Gaps de Observabilidade

**Severidade:** MEDIA

**Evidencia:**
- 9 alert rules existem (bom!) mas faltam metricas de negocio customizadas:
  - `streamflow_fraud_detection_latency_seconds` (p50, p95, p99)
  - `streamflow_transactions_processed_total` por customer_risk_level
  - `streamflow_ml_score_distribution` (histograma do score ML)
  - `streamflow_dlq_events_total` (contagem de eventos na DLQ)
- Sem distributed tracing (OpenTelemetry)
- Sem log aggregation (Loki ou similar)
- Dashboards existem mas sao baseados em metricas genericas do Flink/Kafka

**Impacto no score:** -0.2 pontos

---

### P10: Sem Chaos Engineering

**Severidade:** BAIXA (mas impressiona muito em entrevistas)

**Evidencia:** Nenhum teste de resiliencia. Staff Engineers devem demonstrar:
- O que acontece quando um pod Kafka morre?
- O que acontece quando PostgreSQL reinicia?
- O que acontece quando Flink faz checkpoint durante pico de carga?
- Os alertas disparam corretamente?
- O pipeline se recupera automaticamente?

**Impacto no score:** -0.2 pontos

---

## Approaches Explored

### Approach A: Upgrade Incremental em 10 Fases (Sequencial Controlado)

**Description:** Atacar cada problema em uma fase separada, com dependencias claras entre fases. Cada fase produz codigo funcional e testado. Build do mais critico para o menos critico.

**Pros:**
- Progresso mensuravel a cada fase
- Se parar no meio, o que ja foi feito funciona
- Facilita code review (PRs menores e focados)
- Testes passam a cada fase
- Git history limpo com conventional commits

**Cons:**
- Pode levar mais tempo total
- Algumas fases tem dependencias cruzadas

**Why Recommended:** Para um portfolio de Staff Engineer, o processo importa tanto quanto o resultado. Commits organizados, PRs coerentes e progresso incremental demonstram maturidade de engenharia.

---

### Approach B: Big Bang Rewrite

**Description:** Reescrever tudo de uma vez, criar branch `feat/staff-upgrade`, mergear quando tudo estiver pronto.

**Pros:**
- Possivelmente mais rapido se tudo der certo
- Evita conflitos entre fases

**Cons:**
- Alto risco de regressoes
- Dificil de debugar se algo quebrar
- Git history ruim (1 commit gigante)
- Impossivel pausar no meio — ou termina ou perde tudo
- NAO demonstra mentalidade de Staff (que e incremental por natureza)

---

### Approach C: Feature Flags Graduais

**Description:** Implementar tudo atras de feature flags, ativar gradualmente.

**Pros:**
- Rollback facil
- Pode testar A/B

**Cons:**
- Over-engineering para um portfolio project
- Complexidade de feature flags desnecessaria
- YAGNI — nao ha usuarios reais para A/B testing

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A — Upgrade Incremental em 10 Fases |
| **User Confirmation** | 2026-02-07 (sessao de brainstorm) |
| **Reasoning** | Demonstra mentalidade de Staff Engineer: incrementalismo, testes continuo, zero regressao. Cada fase e um PR que pode ser revisado e apreciado independentemente. |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Manter `FraudRuleEvaluator` como Python puro, envolver em `KeyedProcessFunction` | Separa logica de negocio da API do Flink — testabilidade + SRP | Reescrever tudo dentro do KeyedProcessFunction (menos testavel) |
| 2 | Isolation Forest (nao XGBoost/LightGBM) | Nao-supervisionado, nao precisa de labels, perfeito para anomaly detection, leve | XGBoost (precisa labels), Neural Network (overkill, precisa GPU) |
| 3 | Feature Store no PostgreSQL Gold (nao Redis/Feast) | Zero infra nova, features pre-computadas no batch, $0 custo | Redis (mais RAM), Feast (over-engineering), DynamoDB ($) |
| 4 | Testcontainers para integration tests (nao mocks) | Testa infraestrutura real, encontra bugs reais | Mocks puros (nao testam integracao real), Kind cluster (muito pesado) |
| 5 | ArgoCD para GitOps (nao FluxCD) | Mais popular, UI melhor, mais reconhecido em entrevistas | FluxCD (menos UI), Jenkins (old school), Spinnaker (overkill) |
| 6 | Scripts de chaos (nao LitmusChaos/ChaosMesh) | Server tem 4GB budget, operadores de chaos consomem muita RAM | LitmusChaos (~500MB RAM), ChaosMesh (~300MB RAM) |
| 7 | Mermaid diagrams (nao Excalidraw/draw.io) | Renderiza nativamente no GitHub, vive no codigo, versionavel | Excalidraw (precisa exportar PNG), draw.io (nao e texto) |
| 8 | Contract tests com schema registry local | Valida compatibilidade sem Confluent Schema Registry (que custa RAM) | Confluent Schema Registry (~256MB RAM) |
| 9 | OpenTelemetry manual (nao auto-instrumentation) | Controle fino sobre spans, sem overhead de agent | Auto-instrumentation (overhead, magica demais) |
| 10 | 10 fases (nao 5 como o ROADMAP anterior) | Cobrir TODOS os gaps, nao apenas os 5 mais obvios | ROADMAP antigo com 5 fases (incompleto) |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Confluent Schema Registry | Consome ~256MB RAM, schema validation pode ser feita no codigo | Yes |
| Apache Avro (substituir JSON) | Overhead de tooling, JSON e suficiente para portfolio | Yes |
| Real-time ML model retraining | Over-engineering — modelo pode ser retreinado manualmente | Yes |
| Kubernetes HPA (Horizontal Pod Autoscaler) | Single-node K3s, nao ha nodes para escalar | No |
| Service Mesh (Istio/Linkerd) | Consome 500MB+ RAM, desnecessario para single-node | No |
| ELK Stack (Elasticsearch + Logstash + Kibana) | Consome 2GB+ RAM, Loki e mais leve mas ainda e extra | Yes |
| Apache Pinot/Druid para OLAP | Over-engineering, PostgreSQL Gold e suficiente | Yes |
| Feature Flags (LaunchDarkly/Flagsmith) | YAGNI — sem usuarios reais para A/B testing | Yes |
| Canary Deployments | Precisa de 2+ replicas, single-node impossibilita | No |
| Slack Webhooks para alertas | Precisa de Slack workspace, log de alertas e suficiente | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Audit dos 10 problemas | Sim | Concordou com todos os 10 | Nao |
| Escolha de ML (Isolation Forest) | Sim | Confirmou: Feature Store no PostgreSQL Gold | Nao |
| Deploy real vs simulado | Sim | Confirmou: deploy real com screenshots | Nao |
| Testes (Testcontainers) | Sim | Confirmou: server SSH suporta Docker/Testcontainers | Nao |
| CI/CD (GitHub Actions + ArgoCD) | Sim | Confirmou | Nao |
| Chaos (scripts vs operators) | Sim | Confirmou: scripts leves (sem LitmusChaos) | Nao |
| 10 fases vs 5 fases | Sim | Confirmou: 10 fases para cobertura total | Nao |

---

## PLANO DE IMPLEMENTACAO: 10 FASES

```
ORDEM DE EXECUCAO E DEPENDENCIAS

Fase 1: KeyedProcessFunction Real ←── CRITICO (base para tudo)
  │
  ├──► Fase 2: ML Pipeline (depende da Fase 1)
  │       │
  │       └──► Fase 5: Testes de Integracao (depende da Fase 1+2+3)
  │
  ├──► Fase 3: Dead Letter Queue + Schema Evolution (independente apos Fase 1)
  │
  ├──► Fase 4: DAGs Airflow Producao (independente)
  │
  ├──► Fase 6: K8s Hardening (independente)
  │
  ├──► Fase 7: Observabilidade Avancada (depende da Fase 1+2+3)
  │
  ├──► Fase 8: CI/CD GitOps (depende da Fase 5)
  │       │
  │       └──► Fase 9: Deploy Real + Screenshots (depende da Fase 8)
  │
  └──► Fase 10: Chaos Engineering + Docs Premium (depende da Fase 9)
```

---

### FASE 1: KeyedProcessFunction Real no PyFlink

**Objetivo:** Transformar o `FraudEngine` em um verdadeiro job Flink com estado fault-tolerant.

**Complexidade:** ALTA | **Estimativa:** ~8 arquivos | **Prioridade:** P0 (CRITICA)

**Dependencias:** Nenhuma (e a base para tudo)

**Estrategia detalhada:**

A ideia central e SEPARAR a logica de negocios (regras de fraude) da infraestrutura do Flink. O `FraudEngine` atual vira `FraudRuleEvaluator` (Python puro, sem imports do Flink), e uma nova classe `FraudDetectorFunction(KeyedProcessFunction)` gerencia o estado Flink e chama o evaluator.

```
ANTES:
  FraudEngine (Python puro + dicts volateis)
  └── evaluate() — le/escreve em self._amount_stats (dict)

DEPOIS:
  FraudRuleEvaluator (Python puro, sem Flink)
  └── evaluate(amount_stats, velocity_window, ...) — recebe estado como parametro

  FraudDetectorFunction(KeyedProcessFunction)
  ├── open() — inicializa ValueState[bytes], ListState[bytes]
  ├── process_element() — desserializa estado, chama evaluator, persiste estado
  └── OutputTag("fraud-alerts") — side output para alertas
```

**Arquivos a CRIAR:**

| # | Arquivo | Descricao |
|---|---------|-----------|
| 1 | `src/flink_jobs/fraud_detector_function.py` | `FraudDetectorFunction(KeyedProcessFunction)` com `ValueState`, `ListState`, `OutputTag`. Metodo `open()` inicializa descritores de estado. Metodo `process_element()` desserializa estado -> chama `FraudRuleEvaluator.evaluate()` -> serializa estado atualizado -> emite resultado. Side output para alertas de fraude. |
| 2 | `src/flink_jobs/fraud_pipeline.py` | Funcao `build_fraud_detection_pipeline(env, config)` que monta: `KafkaSource` -> `key_by(customer_id)` -> `FraudDetectorFunction` -> `KafkaSink(fraud.alerts)` + `JdbcSink(bronze.raw_fraud_alerts)`. Entry point `main()`. |
| 3 | `src/flink_jobs/common/state_serializer.py` | Funcoes `serialize_state(obj) -> bytes` e `deserialize_state(data: bytes) -> obj` usando `msgpack` ou `pickle` com protocolo fixo. Suporta `RunningStats`, `GeoLocation`, `list[float]`. Inclui `STATE_SCHEMA_VERSION` para evolucao futura do formato de estado. |

**Arquivos a MODIFICAR:**

| # | Arquivo | Mudanca |
|---|---------|---------|
| 1 | `src/flink_jobs/fraud_detector.py` | Renomear `FraudEngine` para `FraudRuleEvaluator`. Refatorar `evaluate()` para receber objetos de estado como parametros (`amount_stats: RunningStats`, `velocity_window: list[float]`, etc.) em vez de ler de `self._*`. Refatorar cada `_eval_*` para ser metodo puro (sem side effects em self). Manter alias `FraudEngine = FraudRuleEvaluator` no final do arquivo para backward compatibility (todos os 85 testes existentes continuam passando). |
| 2 | `src/flink_jobs/common/state.py` | Adicionar `to_bytes()` e `from_bytes()` ao `RunningStats` e `GeoLocation`. Adicionar `VelocityWindow` dataclass com `timestamps: list[float]` + `to_bytes()`/`from_bytes()`. |
| 3 | `k8s/flink/fraud-detector.yaml` | Mudar `state.backend: rocksdb`. Mudar `upgradeMode: savepoint`. Adicionar `execution.checkpointing.mode: EXACTLY_ONCE`. Adicionar `execution.checkpointing.timeout: "120000"`. Atualizar `jarURI` e `args` para apontar para `fraud_pipeline.py`. |
| 4 | `pyproject.toml` | Adicionar `msgpack>=1.0.0` nas dependencies (ou usar pickle built-in — decisao na Fase 1). |
| 5 | `config/fraud_rules.yaml` | Adicionar secao `flink:` com `checkpoint_interval_ms`, `state_backend`, `exactly_once`. |

**Testes novos (criados na Fase 1):**

| # | Arquivo | O que testa |
|---|---------|-------------|
| 1 | `tests/unit/test_fraud_rule_evaluator.py` | Testa `FraudRuleEvaluator` com estado passado como parametro. Valida que a refatoracao nao quebrou a logica. Testa edge cases: primeiro transaction (sem historico), stats com std_dev zero, velocity window vazia. |
| 2 | `tests/unit/test_state_serializer.py` | Testa roundtrip `serialize_state` -> `deserialize_state` para cada tipo de estado. Testa backward compatibility do `STATE_SCHEMA_VERSION`. |

**Criterio de sucesso:**
- [ ] Todos os 85 testes existentes continuam passando (via alias `FraudEngine`)
- [ ] Novos testes do `FraudRuleEvaluator` passam com estado parametrizado
- [ ] `FraudDetectorFunction` compila e instancia (mesmo sem Flink runtime)
- [ ] `fraud-detector.yaml` tem `state.backend: rocksdb` e `upgradeMode: savepoint`
- [ ] ruff + mypy --strict: 0 erros
- [ ] Serializacao de estado funciona (roundtrip RunningStats -> bytes -> RunningStats)

---

### FASE 2: ML Pipeline — Isolation Forest + Feature Store

**Objetivo:** Adicionar componente de Machine Learning com treino offline e scoring inline.

**Complexidade:** ALTA | **Estimativa:** ~10 arquivos | **Prioridade:** P0 (CRITICA)

**Dependencias:** Fase 1 (precisa do `FraudRuleEvaluator` refatorado)

**Estrategia detalhada:**

O pattern e "Feature Store + Offline Training + Online Scoring":

```
OFFLINE (batch):
  PostgreSQL Gold → Feature Engineering → Train IsolationForest → Save model.joblib

ONLINE (streaming):
  Transaction → Extract Features → Score (model.predict) → Combinar com regras
                                                              │
                                              score_final = alpha * ml + (1-alpha) * rules
```

**Feature Store Pattern:**
Features sao pre-computadas no PostgreSQL Gold como uma tabela `gold.customer_features`:
- `amount_mean`, `amount_std`: Media e desvio padrao de valores do cliente
- `tx_count_30d`: Total de transacoes nos ultimos 30 dias
- `avg_tx_per_day`: Media diaria de transacoes
- `distinct_stores`: Numero de lojas distintas
- `fraud_history_count`: Quantas vezes o cliente ja teve alerta
- `hour_entropy`: Entropia da distribuicao de horas de transacao

Essas features sao calculadas por uma DAG Airflow e materializadas em Gold. O modelo treina sobre elas. No streaming, as mesmas features sao calculadas inline a partir do estado Flink (aproximacao em tempo real).

**Arquivos a CRIAR:**

| # | Arquivo | Descricao |
|---|---------|-----------|
| 1 | `src/flink_jobs/ml/__init__.py` | Package init |
| 2 | `src/flink_jobs/ml/feature_engineering.py` | Classe `FeatureExtractor` com metodo `extract(amount_stats: RunningStats, velocity_window: list[float], hour_stats: RunningStats, geo_location: GeoLocation, is_blacklisted: bool) -> FeatureVector`. `FeatureVector` e um `@dataclass` com 8 features numericas. Python puro, sem dependencia do Flink. Cada feature tem docstring explicando o calculo. |
| 3 | `src/flink_jobs/ml/model_scorer.py` | Classe `AnomalyScorer`: `__init__(model_path: str)` carrega modelo joblib. Metodo `score(features: FeatureVector) -> float` retorna score normalizado [0, 1]. Normaliza `decision_function` do Isolation Forest com min-max scaling. Thread-safe (modelo e read-only apos load). |
| 4 | `src/flink_jobs/ml/model_registry.py` | Classe `ModelRegistry` que gerencia versoes de modelos. Metodos: `get_latest_model(model_dir: str) -> Path`, `register_model(path: Path, metrics: dict)`. Salva `model_metadata.json` com versao, metricas, timestamp de treino. |
| 5 | `scripts/train_model.py` | Script de treino offline: (1) Gera 50k transacoes com `TransactionGenerator` + `FraudInjector`, (2) Extrai features com `FeatureExtractor`, (3) Treina `IsolationForest(n_estimators=100, contamination=0.02, random_state=42)`, (4) Avalia metricas (AUC, precision@10%, recall@10%), (5) Salva em `models/fraud_model_v{N}.joblib` + metadata JSON. CLI com argparse. |
| 6 | `models/.gitkeep` | Diretorio para modelos treinados (modelos .joblib ficam no .gitignore, mas metadata.json e versionado) |
| 7 | `models/model_metadata.json` | Template de metadata: `{"version": 1, "algorithm": "IsolationForest", "n_estimators": 100, "contamination": 0.02, "trained_on": "...", "metrics": {...}}` |
| 8 | `sql/migrations/005_create_feature_store.sql` | `CREATE TABLE gold.customer_features (customer_id TEXT PK, amount_mean NUMERIC, amount_std NUMERIC, tx_count_30d INT, avg_tx_per_day NUMERIC, distinct_stores INT, fraud_history_count INT, hour_entropy NUMERIC, computed_at TIMESTAMPTZ DEFAULT NOW())` |
| 9 | `sql/transforms/compute_features.sql` | SQL que computa as 7 features a partir de `silver.clean_transactions` + `gold.fact_fraud_alerts`, com UPSERT em `gold.customer_features`. Usado pela DAG Airflow. |

**Arquivos a MODIFICAR:**

| # | Arquivo | Mudanca |
|---|---------|---------|
| 1 | `src/flink_jobs/fraud_detector.py` | Adicionar parametro `ml_scorer: AnomalyScorer | None = None` ao `FraudRuleEvaluator.__init__()`. No `evaluate()`: se `ml_scorer` estiver presente, extrair features, calcular `ml_score`, combinar: `final_score = alpha * ml_score + (1 - alpha) * rules_score`. Adicionar `FR-006: ML_ANOMALY` aos resultados. |
| 2 | `src/flink_jobs/fraud_detector_function.py` | No `open()`: carregar modelo ML via `AnomalyScorer(model_path)`. Passar scorer para o `FraudRuleEvaluator`. |
| 3 | `src/models/fraud_alert.py` | Adicionar `ML_ANOMALY = "FR-006"` ao `FraudRuleId` enum. |
| 4 | `config/fraud_rules.yaml` | Adicionar secao `ml:` com `alpha: 0.3`, `model_path: /opt/flink/models/fraud_model.joblib`, `enabled: true`. Adicionar `FR-006:` com `name: ML Anomaly`, `weight: 0.20`. Rebalancear pesos das outras regras para somar 1.0. |
| 5 | `pyproject.toml` | Adicionar optional dependency: `ml = ["scikit-learn>=1.4.0", "joblib>=1.3.0", "numpy>=1.26.0"]` |
| 6 | `.gitignore` | Adicionar `models/*.joblib` (modelos binarios nao devem ir para o git) |

**Testes novos:**

| # | Arquivo | O que testa |
|---|---------|-------------|
| 1 | `tests/unit/test_feature_engineering.py` | Testa `FeatureExtractor.extract()` com dados conhecidos. Testa edge cases: primeiro transaction (sem historico), RunningStats com count=0, velocity_window vazia. Verifica shape do FeatureVector (8 features). Verifica que todas as features estao no range esperado. |
| 2 | `tests/unit/test_model_scorer.py` | Treina IsolationForest pequeno (100 samples) no setup do teste. Testa `AnomalyScorer.score()` retorna float no range [0, 1]. Testa com features normais (score baixo) e features anomalas (score alto). |
| 3 | `tests/unit/test_model_registry.py` | Testa `get_latest_model()` com multiplas versoes. Testa `register_model()` cria metadata correto. |
| 4 | `tests/integration/test_ml_pipeline.py` | Teste end-to-end: gera transacoes -> extrai features -> treina modelo -> faz scoring -> verifica que scores anomalos sao maiores que normais. |

**Criterio de sucesso:**
- [ ] `FeatureExtractor` produz vetor de 8 features (Python puro)
- [ ] `AnomalyScorer` carrega modelo e retorna scores no range [0, 1]
- [ ] `scripts/train_model.py` treina modelo com sucesso e salva metadata
- [ ] `FraudRuleEvaluator` combina score ML + regras corretamente
- [ ] `FR-006: ML_ANOMALY` aparece nos resultados quando ML detecta anomalia
- [ ] Todos os testes anteriores continuam passando
- [ ] ruff + mypy --strict: 0 erros
- [ ] Cobertura >= 80%

---

### FASE 3: Dead Letter Queue + Schema Evolution

**Objetivo:** Implementar tratamento robusto de erros e versionamento de schema.

**Complexidade:** MEDIA | **Estimativa:** ~7 arquivos | **Prioridade:** P1

**Dependencias:** Fase 1 (precisa do pipeline refatorado)

**Arquivos a CRIAR:**

| # | Arquivo | Descricao |
|---|---------|-----------|
| 1 | `src/flink_jobs/common/dlq.py` | Classe `DeadLetterRecord` (Pydantic): `original_event: str`, `error_type: str`, `error_message: str`, `source_topic: str`, `failed_at: datetime`, `retry_count: int = 0`, `processing_stage: str`. Funcao `build_dlq_record(raw: str, error: Exception, topic: str, stage: str) -> DeadLetterRecord`. Trunca `original_event` em 10KB para evitar mensagens gigantes na DLQ. |
| 2 | `src/flink_jobs/common/schema_registry.py` | Classe `SchemaVersion` com `CURRENT = 2`, `SUPPORTED = {1, 2}`. Funcao `parse_with_version(raw: str) -> tuple[int, dict]` que extrai `schema_version` do JSON e faz parse adequado. Para versao desconhecida: log warning e tenta parse com fields conhecidos (forward-compatible). Para versao antiga: aplica migration (e.g., v1 nao tem `payment_method` -> adiciona default). |
| 3 | `sql/migrations/006_create_dlq_table.sql` | `CREATE TABLE bronze.dead_letter_events (id BIGSERIAL PK, original_event TEXT, error_type TEXT, error_message TEXT, source_topic TEXT, failed_at TIMESTAMPTZ, retry_count INT DEFAULT 0, processing_stage TEXT, reprocessed BOOLEAN DEFAULT FALSE, created_at TIMESTAMPTZ DEFAULT NOW())`. Index em `failed_at` e `reprocessed`. |
| 4 | `src/dags/dlq_monitor.py` | DAG Airflow `dlq_monitor` (schedule `*/5 * * * *`): (1) Conta eventos DLQ nao reprocessados, (2) Se count > threshold -> log WARNING com detalhes, (3) Task de limpeza de DLQ > 30 dias. |

**Arquivos a MODIFICAR:**

| # | Arquivo | Mudanca |
|---|---------|---------|
| 1 | `src/flink_jobs/transaction_processor.py` | Na funcao `_parse_and_validate()`: em vez de retornar `None`, emitir side output `OutputTag("dead-letter-queue")` com `DeadLetterRecord`. No `build_pipeline()`: adicionar sink da DLQ para topico Kafka `streamflow.dlq` e/ou tabela `bronze.dead_letter_events`. Atualizar `schema_version` para usar `SchemaVersion.CURRENT`. |
| 2 | `src/flink_jobs/common/serialization.py` | Adicionar `SCHEMA_VERSION` import e usar nos metodos de serialize. Adicionar `schema_version` nos JSONs produzidos. Fazer `deserialize_transaction()` usar `parse_with_version()` para backward compatibility. |
| 3 | `k8s/kafka/kafka-topics.yaml` | Adicionar topico `streamflow.dlq` (1 particao, retencao 30 dias, cleanup.policy: delete). |

**Testes novos:**

| # | Arquivo | O que testa |
|---|---------|-------------|
| 1 | `tests/unit/test_dlq.py` | Testa `build_dlq_record()`: estrutura correta, truncamento de eventos grandes, campos obrigatorios. Testa serializacao/desserializacao do `DeadLetterRecord`. |
| 2 | `tests/unit/test_schema_registry.py` | Testa `parse_with_version()` com schema v1, v2, versao desconhecida. Testa forward compatibility (campo novo ignorado). Testa backward compatibility (campo faltando -> default). |

**Criterio de sucesso:**
- [ ] Eventos malformados vao para DLQ em vez de serem descartados
- [ ] Schema v1 e v2 sao parseados corretamente
- [ ] Versao desconhecida gera warning mas nao crash
- [ ] `DeadLetterRecord` tem todos os metadados para investigacao
- [ ] DAG `dlq_monitor` carrega sem erros no DagBag
- [ ] Topico `streamflow.dlq` existe no Kafka
- [ ] ruff + mypy --strict: 0 erros

---

### FASE 4: DAGs Airflow de Nivel Producao

**Objetivo:** Refatorar as 4 DAGs existentes para nivel profissional + criar DAG de ML.

**Complexidade:** MEDIA | **Estimativa:** ~16 arquivos | **Prioridade:** P1

**Dependencias:** Nenhuma (independente das Fases 1-3)

**Arquivos a CRIAR:**

| # | Arquivo | Descricao |
|---|---------|-----------|
| 1 | `src/dags/common/__init__.py` | Package init |
| 2 | `src/dags/common/callbacks.py` | `on_failure_callback(context)`: loga erro com task_id, dag_id, execution_date, exception. `on_success_callback(context)`: loga sucesso com duracao. `on_sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis)`: loga SLA miss com detalhes. `on_retry_callback(context)`: loga retry com attempt number. |
| 3 | `src/dags/common/alerts.py` | `check_quality_results(min_pass_rate: float, **context)`: PythonOperator callable que le resultados da tabela `silver.quality_check_results`, verifica taxa de aprovacao, lanca `AirflowException` se abaixo do threshold. |
| 4 | `src/dags/ml_feature_pipeline.py` | DAG `ml_feature_pipeline` (schedule `@daily` as 02:00): TaskGroup "compute_features" com task `compute_customer_features` que executa `sql/transforms/compute_features.sql`. TaskGroup "train_model" com `PythonOperator` que chama `scripts/train_model.py` se dados suficientes. `on_failure_callback` em todas as tasks. |
| 5-11 | `sql/transforms/gold/upsert_dim_customer.sql` | 7 arquivos SQL individuais extraidos de `silver_to_gold.sql` — cada um com uma unica operacao (ver lista abaixo) |
| 12-15 | `sql/quality/check_*.sql` | 4 arquivos SQL individuais extraidos de `quality_checks.sql` — cada um com um unico check |

**SQL files a criar (extraidos dos monolitos):**

```
sql/transforms/gold/upsert_dim_customer.sql
sql/transforms/gold/upsert_dim_store.sql
sql/transforms/gold/upsert_dim_product.sql
sql/transforms/gold/load_fact_transactions.sql
sql/transforms/gold/load_fact_fraud_alerts.sql
sql/transforms/gold/refresh_hourly_sales.sql
sql/transforms/gold/refresh_daily_fraud.sql

sql/quality/check_null_rate.sql
sql/quality/check_duplicates.sql
sql/quality/check_freshness.sql
sql/quality/check_amounts.sql
```

**Arquivos a MODIFICAR:**

| # | Arquivo | Mudanca |
|---|---------|---------|
| 1 | `src/dags/bronze_to_silver.py` | Adicionar `on_failure_callback`, `on_success_callback`, `sla: timedelta(minutes=30)` ao `default_args`. Criar TaskGroup `"validate"` com task pre-check (count bronze rows). Criar TaskGroup `"transform"` com task existente. Criar TaskGroup `"post_validate"` com `PythonOperator` que verifica se rows foram inseridas. Adicionar `doc_md` ao DAG com descricao em Markdown. Adicionar `tags` mais descritivos. |
| 2 | `src/dags/silver_to_gold.py` | Separar `build_gold` em TaskGroup `"dimensions"` (3 tasks: dim_customer, dim_store, dim_product executando em paralelo) + TaskGroup `"facts"` (2 tasks: fact_transactions, fact_fraud_alerts executando em paralelo) + TaskGroup `"aggregations"` (2 tasks: hourly_sales, daily_fraud em paralelo). Cada task usa seu proprio arquivo SQL. Adicionar `sla`, callbacks, `doc_md`. |
| 3 | `src/dags/data_quality.py` | Separar `run_quality_checks` em 4 tasks individuais (uma por check SQL) + `PythonOperator` `"evaluate_results"` que chama `check_quality_results()`. Usar `@task` decorator para tarefas Python. Adicionar XCom para passar contagem de falhas entre tasks. |
| 4 | `src/dags/maintenance.py` | Criar TaskGroup `"prune"` com tasks `prune_bronze` e `prune_quality_logs` executando em paralelo (nao sequencial). Adicionar `PythonOperator` `"log_maintenance_stats"` que loga tamanho antes/depois via XCom. Adicionar callbacks. |

**Testes novos:**

| # | Arquivo | O que testa |
|---|---------|-------------|
| 1 | `tests/unit/test_dag_structure.py` | DagBag validation: importa todos os DAGs sem erros. Verifica contagem de tasks por DAG. Verifica dependencias (upstream/downstream) estao corretas. Verifica que todos os DAGs tem `on_failure_callback`. Verifica que nenhum DAG tem `catchup=True`. |
| 2 | `tests/unit/test_dag_callbacks.py` | Testa `on_failure_callback` loga corretamente. Testa `on_sla_miss_callback` loga corretamente. Testa `check_quality_results` com dados mock. |

**Criterio de sucesso:**
- [ ] Todos os 5+ DAGs carregam sem erros no DagBag
- [ ] `bronze_to_silver`: 3+ TaskGroups com validate/transform/post_validate
- [ ] `silver_to_gold`: 3+ TaskGroups (dimensions/facts/aggregations) com paralelismo
- [ ] `data_quality`: 4+ tasks individuais + evaluator
- [ ] `maintenance`: tasks de prune em paralelo
- [ ] `ml_feature_pipeline`: DAG de ML funcional
- [ ] Todas as DAGs tem callbacks e SLA
- [ ] ruff + mypy (src/dags excluido do mypy strict, mas lint ok)

---

### FASE 5: Testes de Integracao Reais + Contract Tests

**Objetivo:** Criar suite de testes robusta com infraestrutura real via Testcontainers.

**Complexidade:** ALTA | **Estimativa:** ~12 arquivos | **Prioridade:** P1

**Dependencias:** Fases 1, 2, 3 (precisa de tudo implementado para testar)

**Arquivos a CRIAR:**

| # | Arquivo | Descricao |
|---|---------|-----------|
| 1 | `tests/integration/__init__.py` | Package init |
| 2 | `tests/integration/conftest.py` | Fixtures de Testcontainers: `@pytest.fixture(scope="session") def kafka_container()` — sobe container Kafka (confluentinc/cp-kafka). `@pytest.fixture(scope="session") def postgres_container()` — sobe container PostgreSQL 16 com migrations aplicadas. `@pytest.fixture def kafka_producer(kafka_container)` — cria producer conectado. `@pytest.fixture def pg_cursor(postgres_container)` — cria cursor conectado com rollback automatico. |
| 3 | `tests/integration/test_kafka_roundtrip.py` | Testa: produz Transaction no topico `transactions.raw`, consome, valida schema. Testa: produz FraudAlert no topico `fraud.alerts`, consome, valida schema. Testa: serialization roundtrip completo via Kafka real. |
| 4 | `tests/integration/test_postgres_medallion.py` | Testa: insere raw_transaction no Bronze, executa SQL bronze_to_silver, verifica Silver. Testa: insere clean_transaction no Silver, executa SQL silver_to_gold, verifica Gold dimensions + facts. Testa: insere dados invalidos, verifica quality_checks detectam. |
| 5 | `tests/integration/test_dlq_flow.py` | Testa: envia evento malformado -> verifica que aparece na DLQ (topico Kafka ou tabela PostgreSQL). Testa: envia evento com schema_version desconhecido -> verifica comportamento forward-compatible. |
| 6 | `tests/integration/test_ml_pipeline.py` | Testa end-to-end: gera dados -> extrai features -> treina modelo -> scoring. Verifica que scores anomalos > scores normais (basico sanity check). |
| 7 | `tests/integration/test_feature_store.py` | Testa: insere transacoes no Silver, executa `compute_features.sql`, verifica `gold.customer_features` tem valores corretos. |
| 8 | `tests/contract/__init__.py` | Package init |
| 9 | `tests/contract/test_schema_compatibility.py` | Contract tests: verifica que `Transaction.to_json_dict()` produz JSON compativel com o que `deserialize_transaction()` espera. Verifica que `FraudAlert.to_json_dict()` e compativel com `deserialize_fraud_alert()`. Verifica forward compatibility: adiciona campo desconhecido ao JSON, parse nao falha. Verifica backward compatibility: remove campo opcional, parse funciona com default. |
| 10 | `tests/contract/test_sql_schema_contract.py` | Verifica que colunas de `bronze.raw_transactions` INSERT match com Pydantic model fields. Verifica que colunas de `silver.clean_transactions` match com SQL transform output. Verifica que `gold.customer_features` match com `FeatureVector` fields. |

**Arquivos a MODIFICAR:**

| # | Arquivo | Mudanca |
|---|---------|---------|
| 1 | `pyproject.toml` | Adicionar `testcontainers = ["testcontainers[kafka,postgres]>=4.0.0"]` nos optional-dependencies. Adicionar markers: `integration`, `contract`. Configurar pytest para `--ignore=tests/integration` por default (rodar apenas com `pytest -m integration`). |
| 2 | `tests/conftest.py` | Adicionar fixtures globais de ML (mock model, sample features). Adicionar fixture `sample_transactions(n=10)` que gera transacoes deterministicas. |
| 3 | `tests/e2e/test_full_pipeline.py` | Renomear para `tests/integration/test_fraud_engine_flow.py`. Mudar marker de `e2e` para `integration`. Atualizar imports se necessario. |
| 4 | `Makefile` | Adicionar targets: `test-integration`, `test-contract`, `test-all`. |

**Testes RENOMEADOS/MOVIDOS:**

| De | Para | Motivo |
|----|------|--------|
| `tests/e2e/test_full_pipeline.py` | `tests/integration/test_fraud_engine_flow.py` | Nao era E2E real — e teste de integracao in-memory |
| `tests/e2e/__init__.py` | (deletar diretorio `tests/e2e/`) | Diretorio vazio apos mover |

**Criterio de sucesso:**
- [ ] `pytest -m integration` roda com containers reais (Kafka + PostgreSQL)
- [ ] `pytest -m contract` valida compatibilidade de schemas
- [ ] Testes unitarios continuam rodando sem containers (`pytest tests/unit/`)
- [ ] Cobertura total >= 80%
- [ ] Makefile tem `test-integration`, `test-contract`, `test-all`
- [ ] Zero testes marcados como `e2e` (renomeados para `integration`)

---

### FASE 6: K8s Hardening — Configs de Producao

**Objetivo:** Elevar os manifests K8s para padrao de producao.

**Complexidade:** MEDIA | **Estimativa:** ~8 arquivos | **Prioridade:** P2

**Dependencias:** Nenhuma (independente)

**Arquivos a CRIAR:**

| # | Arquivo | Descricao |
|---|---------|-----------|
| 1 | `k8s/network-policies/deny-all.yaml` | `NetworkPolicy` default deny em cada namespace `streamflow-*`. So permite trafego explicitamente permitido. |
| 2 | `k8s/network-policies/allow-streamflow.yaml` | `NetworkPolicy` que permite: Flink -> Kafka (porta 9092), Flink -> PostgreSQL (porta 5432), Airflow -> PostgreSQL (porta 5432), Prometheus -> todos (porta metrics). |
| 3 | `k8s/pod-disruption-budgets.yaml` | `PodDisruptionBudget` para: Kafka (minAvailable: 1), Flink JobManager (minAvailable: 1), PostgreSQL (minAvailable: 1). |
| 4 | `k8s/resource-quotas.yaml` | `ResourceQuota` por namespace limitando total de CPU e RAM. Previne um namespace de consumir todos os recursos do node. |

**Arquivos a MODIFICAR:**

| # | Arquivo | Mudanca |
|---|---------|---------|
| 1 | `k8s/flink/fraud-detector.yaml` | Adicionar `livenessProbe` e `readinessProbe` no TaskManager. Adicionar `podTemplate` com `terminationGracePeriodSeconds: 120` (tempo para checkpoint antes de morrer). |
| 2 | `k8s/flink/transaction-processor.yaml` | Mesmo: probes + graceful shutdown. |
| 3 | `k8s/flink/realtime-aggregator.yaml` | Mesmo: probes + graceful shutdown. |
| 4 | `k8s/monitoring/alerting-rules.yaml` | Adicionar regras: `DLQEventsHigh` (DLQ > 100 eventos em 1h), `MLModelStale` (modelo nao atualizado > 7 dias), `NetworkPolicyViolation` (tentativa de acesso negado). |

**Criterio de sucesso:**
- [ ] `kubectl apply -f k8s/network-policies/` funciona
- [ ] PDBs existem para componentes criticos
- [ ] Flink pods tem probes configurados
- [ ] AlertManager tem regras de DLQ e ML
- [ ] `kubectl get networkpolicy -A` mostra policies em todos os namespaces streamflow

---

### FASE 7: Observabilidade Avancada

**Objetivo:** Adicionar metricas de negocio customizadas, tracing e metricas ML.

**Complexidade:** MEDIA | **Estimativa:** ~6 arquivos | **Prioridade:** P2

**Dependencias:** Fases 1, 2, 3 (precisa de DLQ, ML, KeyedProcessFunction)

**Arquivos a CRIAR:**

| # | Arquivo | Descricao |
|---|---------|-----------|
| 1 | `src/utils/metrics.py` | Classe `StreamFlowMetrics` usando Prometheus client library. Metricas: `Counter("streamflow_transactions_processed_total", labels=["status", "risk_level"])`, `Histogram("streamflow_fraud_detection_latency_seconds", buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0])`, `Gauge("streamflow_ml_score", labels=["customer_risk"])`, `Counter("streamflow_dlq_events_total", labels=["error_type", "source_topic"])`, `Histogram("streamflow_ml_score_distribution", buckets=[0.0, 0.1, 0.2, ..., 1.0])`, `Counter("streamflow_fraud_alerts_total", labels=["rule_id"])`. Singleton pattern para acesso global. |
| 2 | `src/utils/tracing.py` | Setup basico de OpenTelemetry com `ConsoleSpanExporter` (para logs) e `OTLPSpanExporter` (para Jaeger/Tempo se disponivel). Funcoes: `create_tracer(service_name: str)`, `@traced` decorator para funcoes criticas. Spans para: `process_transaction`, `evaluate_fraud_rules`, `score_ml_model`, `write_to_bronze`. |
| 3 | `k8s/monitoring/business-metrics-dashboard.json` | Dashboard Grafana focado em metricas de negocio: taxa de fraude por hora, distribuicao de ML score, DLQ count, latencia p95/p99 de processamento, transacoes por risk_level. |
| 4 | `k8s/monitoring/ml-dashboard.json` | Dashboard Grafana de ML: distribuicao de scores, drift detection (media movel de score vs baseline), top features contribuindo para anomalias, model staleness. |

**Arquivos a MODIFICAR:**

| # | Arquivo | Mudanca |
|---|---------|---------|
| 1 | `src/flink_jobs/fraud_detector_function.py` | No `process_element()`: incrementar `streamflow_transactions_processed_total`, registrar latencia no `Histogram`, registrar score ML no `Histogram`, emitir `streamflow_fraud_alerts_total` por rule_id quando alerta e gerado. |
| 2 | `src/flink_jobs/transaction_processor.py` | Na DLQ: incrementar `streamflow_dlq_events_total`. No processamento: registrar latencia. |
| 3 | `pyproject.toml` | Adicionar `prometheus-client>=0.20.0`, `opentelemetry-api>=1.20.0`, `opentelemetry-sdk>=1.20.0` nos dependencies. |
| 4 | `k8s/monitoring/service-monitors.yaml` | Adicionar ServiceMonitor para metricas customizadas dos Flink jobs (porta onde prometheus client expoe `/metrics`). |

**Criterio de sucesso:**
- [ ] Metricas customizadas expostas em `/metrics` endpoint
- [ ] Dashboard de negocio importavel no Grafana
- [ ] Dashboard de ML importavel no Grafana
- [ ] Spans de tracing aparecem nos logs (ConsoleSpanExporter)
- [ ] `streamflow_fraud_detection_latency_seconds` registra p50/p95/p99

---

### FASE 8: CI/CD GitOps Completo

**Objetivo:** Pipeline de CI robusto + deploy automatico via ArgoCD.

**Complexidade:** MEDIA | **Estimativa:** ~10 arquivos | **Prioridade:** P2

**Dependencias:** Fase 5 (testes de integracao prontos)

**Arquivos a CRIAR:**

| # | Arquivo | Descricao |
|---|---------|-----------|
| 1 | `.github/workflows/ci-complete.yaml` | Pipeline completo: (1) Lint (ruff check + format check), (2) Type check (mypy --strict), (3) Unit tests (pytest tests/unit/), (4) Integration tests (pytest -m integration — com Testcontainers), (5) Contract tests (pytest -m contract), (6) Coverage check (fail se < 80%), (7) Security scan (bandit + safety), (8) Build check (pip install -e ".[dev,ml]"). Matrix: Python 3.11 + 3.12. Cache pip. Upload coverage para artifact. |
| 2 | `.github/workflows/security.yaml` | Security scanning: (1) `bandit -r src/` (Python security linter), (2) `safety check` (dependency vulnerabilities), (3) `trivy fs .` (filesystem scan). Roda em PRs e push para main. |
| 3 | `.github/workflows/deploy-argocd.yaml` | Deploy via ArgoCD: (1) Conecta via SSH ao server, (2) Sync ArgoCD application, (3) Aguarda health check, (4) Roda `scripts/verify_pipeline.py`. Trigger: push para main (apos CI passar). |
| 4 | `k8s/argocd/application.yaml` | ArgoCD `Application` CRD: source do Git repo, target namespace, sync policy `automated` com `selfHeal: true` e `prune: true`. |
| 5 | `k8s/argocd/project.yaml` | ArgoCD `AppProject` que limita acesso apenas aos namespaces `streamflow-*`. |
| 6 | `infra/modules/argocd/main.tf` | Terraform module que instala ArgoCD via Helm no K3s. Configuracoes minimas para economizar RAM. |
| 7 | `infra/modules/argocd/variables.tf` | Variaveis do modulo ArgoCD. |
| 8 | `infra/environments/dev/argocd/terragrunt.hcl` | Terragrunt config para ArgoCD no ambiente dev. |

**Arquivos a MODIFICAR:**

| # | Arquivo | Mudanca |
|---|---------|---------|
| 1 | `.github/workflows/ci.yaml` | Renomear para `ci-legacy.yaml` ou deletar (substituido por `ci-complete.yaml`). |
| 2 | `.github/workflows/deploy.yaml` | Manter como fallback manual, mas `deploy-argocd.yaml` e o padrao. |
| 3 | `infra/environments/dev/terragrunt.hcl` | Adicionar ArgoCD como dependency (instalar apos monitoring). |

**Criterio de sucesso:**
- [ ] Push para `main` dispara CI completo automaticamente
- [ ] CI falha se: ruff, mypy, testes, cobertura < 80%, security scan
- [ ] ArgoCD detecta mudancas no Git e faz sync automatico
- [ ] Deploy e verificado com `verify_pipeline.py`
- [ ] Nenhum deploy manual necessario (100% GitOps)

---

### FASE 9: Deploy Real + Screenshots

**Objetivo:** Fazer o deploy real no servidor K3s e capturar evidencias.

**Complexidade:** MEDIA | **Estimativa:** ~5 arquivos | **Prioridade:** P2

**Dependencias:** Fase 8 (CI/CD configurado)

**Arquivos a CRIAR:**

| # | Arquivo | Descricao |
|---|---------|-----------|
| 1 | `docs/screenshots/01-k8s-pods-running.png` | Screenshot de `kubectl get pods -A \| grep streamflow` mostrando todos os pods Running. |
| 2 | `docs/screenshots/02-grafana-pipeline-dashboard.png` | Screenshot do dashboard Pipeline Overview com metricas reais. |
| 3 | `docs/screenshots/03-grafana-fraud-dashboard.png` | Screenshot do dashboard Fraud Monitoring com alertas reais. |
| 4 | `docs/screenshots/04-airflow-dags.png` | Screenshot do Airflow UI mostrando DAGs com TaskGroups. |
| 5 | `docs/screenshots/05-flink-dashboard.png` | Screenshot do Flink Dashboard mostrando jobs RUNNING com checkpoints. |
| 6 | `docs/screenshots/06-argocd-sync.png` | Screenshot do ArgoCD mostrando app synced e healthy. |
| 7 | `docs/screenshots/07-ci-pipeline-green.png` | Screenshot do GitHub Actions com CI completo passando. |
| 8 | `scripts/deploy_full.sh` | Script que faz deploy completo: (1) terragrunt apply, (2) kubectl apply manifests, (3) run migrations, (4) seed data, (5) generate events (5 min), (6) verify pipeline, (7) captura screenshots (opcional). |
| 9 | `scripts/capture_screenshots.sh` | Script que usa `kubectl port-forward` + `curl` para capturar screenshots dos dashboards (ou instrucoes manuais). |

**Arquivos a MODIFICAR:**

| # | Arquivo | Mudanca |
|---|---------|---------|
| 1 | `README.md` | Adicionar secao "Live Deployment" com screenshots. Adicionar badges reais (CI status, coverage, ArgoCD status). Adicionar Mermaid diagrams para data flow e architecture. Reescrever overview para ser mais conciso e impactante. |
| 2 | `ARCHITECTURE.md` | Adicionar Mermaid diagrams (flowchart, sequence diagram, C4 context). Adicionar secao ML Pipeline. Adicionar secao DLQ. Atualizar ADRs com decisoes novas. |

**Criterio de sucesso:**
- [ ] Todos os pods em estado Running no K3s
- [ ] Dashboards Grafana mostrando metricas reais
- [ ] Airflow DAGs executando com sucesso
- [ ] Flink jobs com checkpoints completando
- [ ] ArgoCD mostrando app Synced + Healthy
- [ ] Screenshots no `docs/screenshots/`
- [ ] README com screenshots embedados

---

### FASE 10: Chaos Engineering + Documentacao Premium

**Objetivo:** Testes de resiliencia + documentacao que impressiona.

**Complexidade:** MEDIA | **Estimativa:** ~12 arquivos | **Prioridade:** P3

**Dependencias:** Fase 9 (precisa de deploy funcional)

**Arquivos a CRIAR:**

| # | Arquivo | Descricao |
|---|---------|-----------|
| 1 | `tests/chaos/__init__.py` | Package init |
| 2 | `tests/chaos/test_kafka_failure.py` | Script que: (1) Verifica pipeline healthy, (2) `kubectl delete pod kafka-0 -n streamflow-kafka`, (3) Aguarda pod reiniciar, (4) Verifica consumer lag se recupera, (5) Verifica zero perda de dados. Loga timeline: down_at, up_at, recovered_at, lag_recovered_at. |
| 3 | `tests/chaos/test_postgres_failure.py` | Script que: (1) Verifica pipeline healthy, (2) `kubectl delete pod streamflow-pg-1 -n streamflow-data`, (3) Aguarda CloudNativePG recriar pod, (4) Verifica conexoes Flink + Airflow se reconectam, (5) Verifica dados nao corrompidos (count before == count after). |
| 4 | `tests/chaos/test_flink_checkpoint_recovery.py` | Script que: (1) Injeta 1000 transacoes, (2) Aguarda checkpoint completar, (3) `kubectl delete pod flink-taskmanager-* -n streamflow-processing`, (4) Aguarda restart, (5) Verifica que estado foi restaurado do checkpoint (score de um customer especifico preservado). |
| 5 | `tests/chaos/test_network_partition.py` | Script que: (1) Aplica NetworkPolicy que bloqueia Flink -> Kafka temporariamente, (2) Verifica que alerta `FlinkJobFailed` dispara, (3) Remove NetworkPolicy, (4) Verifica que pipeline se recupera. |
| 6 | `tests/chaos/conftest.py` | Fixtures de chaos: `kubectl_context`, `wait_for_pod_ready(name, namespace, timeout)`, `get_pod_restart_count(name, namespace)`, `verify_data_integrity(cursor)`. |
| 7 | `docs/CHAOS_REPORT.md` | Relatorio de chaos engineering: cenarios testados, resultados, tempo de recuperacao, gaps encontrados, remediacoes. Formato profissional com tabelas e graficos. |
| 8 | `docs/FRAUD_DETECTION.md` (rewrite) | Reescrita completa: adicionar secao ML (Isolation Forest), Feature Store pattern, scoring formula, feature importance, model versioning. Adicionar Mermaid sequence diagram do fluxo de deteccao. |
| 9 | `docs/ML_PIPELINE.md` | Novo documento focado em ML: feature engineering detalhado (cada feature com formula e justificativa), modelo (hyperparameters, metricas, tradeoffs), scoring (como ML combina com regras), retraining (quando e como retreinar). |
| 10 | `docs/RUNBOOK.md` (rewrite) | Reescrita: adicionar runbook de DLQ (como investigar, como reprocessar), runbook de ML (como retreinar modelo, como rollback), runbook de chaos (procedimentos de recovery), runbook de ArgoCD (como forcar sync, como rollback deploy). |

**Arquivos a MODIFICAR:**

| # | Arquivo | Mudanca |
|---|---------|---------|
| 1 | `README.md` | Versao final premium: Mermaid diagrams inline, secao "Chaos Engineering Results" com tabela de cenarios, secao "ML Pipeline" com feature importance, secao "Architecture Decisions" com links para ADRs, badges reais do CI/CD. |
| 2 | `Makefile` | Adicionar target `chaos` que roda `pytest tests/chaos/ -v --timeout=300`. |

**Criterio de sucesso:**
- [ ] 4 cenarios de chaos executados com sucesso
- [ ] `CHAOS_REPORT.md` documentando resultados
- [ ] Pipeline se recupera de TODOS os cenarios (Kafka down, PG down, Flink crash, network partition)
- [ ] Tempo de recuperacao documentado
- [ ] README com Mermaid diagrams renderizando no GitHub
- [ ] `ML_PIPELINE.md` com feature importance e metricas do modelo
- [ ] `RUNBOOK.md` com procedimentos de recovery

---

## RISK ASSESSMENT

### Risk Matrix

```
              | Low Impact  | Med Impact  | High Impact |
--------------+-------------+-------------+-------------+
High Prob     | Monitor     | Plan        | CRITICAL    |
--------------+-------------+-------------+-------------+
Med Prob      | Accept      | Monitor     | Plan        |
--------------+-------------+-------------+-------------+
Low Prob      | Accept      | Accept      | Monitor     |
--------------+-------------+-------------+-------------+
```

### Risk Register

| # | Risk | Impact | Prob | Category | Mitigation |
|---|------|--------|------|----------|------------|
| R1 | PyFlink KeyedProcessFunction API incompativel com versao instalada | HIGH | MED | PLAN | Verificar API do PyFlink 1.20 via docs antes de implementar. Ter fallback com ProcessFunction generica. |
| R2 | Server K3s sem RAM suficiente para ArgoCD + ML + tudo | HIGH | MED | PLAN | ArgoCD minimo (~256MB). Modelo ML leve (< 50MB). Monitorar `kubectl top nodes` durante deploy. Budget total: 4GB. |
| R3 | Testcontainers nao funciona no server SSH | MED | LOW | MONITOR | Testcontainers precisa de Docker. K3s usa containerd. Solucao: instalar Docker CE no server ou usar podman. Fallback: testes de integracao com mocks. |
| R4 | IsolationForest nao detecta fraudes sinteticas | MED | MED | PLAN | Dados sinteticos tem padroes claros (FR-001 a FR-005). Se IsoForest nao detectar, ajustar `contamination` e features. Fallback: usar score ML como sinal adicional, nao como gate. |
| R5 | CI/CD actions falham por falta de secrets configurados | LOW | HIGH | PLAN | Documentar todos os secrets necessarios: SSH_PRIVATE_KEY, K3S_HOST, SSH_USER. Criar setup guide. |
| R6 | Schema evolution quebra consumers existentes | MED | LOW | MONITOR | Estrategia conservadora: adicionar campos opcionales, nunca remover. Version bump so quando necessario. |
| R7 | Chaos engineering derruba o server de verdade | HIGH | LOW | MONITOR | Scripts de chaos com timeout (max 60s de downtime). Verificar health apos cada teste. Ter script de recovery rapido. |
| R8 | Grafana dashboards nao renderizam metricas customizadas | LOW | MED | ACCEPT | Verificar que ServiceMonitor esta scraping a porta correta. Fallback: dashboards com metricas built-in do Flink/Kafka. |
| R9 | Conflito entre ArgoCD e Terraform para gerenciar mesmos recursos | MED | MED | PLAN | ArgoCD gerencia APENAS manifests em `k8s/`. Terraform gerencia APENAS operators e infra. Zero overlap. Documentar ownership claramente. |
| R10 | Tempo insuficiente para completar 10 fases | MED | MED | PLAN | Fases 1-5 sao indispensaveis (de 4.5 para ~8.0). Fases 6-8 elevam para ~9.0. Fases 9-10 completam 10/10. Se faltar tempo, parar apos Fase 8. |

### Contingency Plans

| Trigger | Response |
|---------|----------|
| PyFlink API nao suporta KeyedProcessFunction em Python | Usar `ProcessFunction` com `getRuntimeContext().getState()`. Menos elegante mas funcional. |
| Server sem RAM | Desativar monitoring (libera ~384MB) ou reduzir Flink TaskManager memory. |
| Testcontainers impossivel no server | Usar mocks sofisticados com `fakeredis`-style para Kafka e SQLite para PostgreSQL. |
| ML model nao detecta fraudes | Ajustar features, contamination rate, ou usar modelo ensemble (IsoForest + LOF). |
| ArgoCD consome muita RAM | Usar Flux v2 (mais leve) ou deploy via GitHub Actions direto (sem GitOps operator). |

---

## INVENTARIO COMPLETO DE ARQUIVOS

### Arquivos NOVOS a Criar (por fase)

| Fase | Arquivo | Tipo |
|------|---------|------|
| **1** | `src/flink_jobs/fraud_detector_function.py` | Python |
| **1** | `src/flink_jobs/fraud_pipeline.py` | Python |
| **1** | `src/flink_jobs/common/state_serializer.py` | Python |
| **1** | `tests/unit/test_fraud_rule_evaluator.py` | Test |
| **1** | `tests/unit/test_state_serializer.py` | Test |
| **2** | `src/flink_jobs/ml/__init__.py` | Python |
| **2** | `src/flink_jobs/ml/feature_engineering.py` | Python |
| **2** | `src/flink_jobs/ml/model_scorer.py` | Python |
| **2** | `src/flink_jobs/ml/model_registry.py` | Python |
| **2** | `scripts/train_model.py` | Script |
| **2** | `models/.gitkeep` | Config |
| **2** | `models/model_metadata.json` | Config |
| **2** | `sql/migrations/005_create_feature_store.sql` | SQL |
| **2** | `sql/transforms/compute_features.sql` | SQL |
| **2** | `tests/unit/test_feature_engineering.py` | Test |
| **2** | `tests/unit/test_model_scorer.py` | Test |
| **2** | `tests/unit/test_model_registry.py` | Test |
| **2** | `tests/integration/test_ml_pipeline.py` | Test |
| **3** | `src/flink_jobs/common/dlq.py` | Python |
| **3** | `src/flink_jobs/common/schema_registry.py` | Python |
| **3** | `sql/migrations/006_create_dlq_table.sql` | SQL |
| **3** | `src/dags/dlq_monitor.py` | Python |
| **3** | `tests/unit/test_dlq.py` | Test |
| **3** | `tests/unit/test_schema_registry.py` | Test |
| **4** | `src/dags/common/__init__.py` | Python |
| **4** | `src/dags/common/callbacks.py` | Python |
| **4** | `src/dags/common/alerts.py` | Python |
| **4** | `src/dags/ml_feature_pipeline.py` | Python |
| **4** | `sql/transforms/gold/upsert_dim_customer.sql` | SQL |
| **4** | `sql/transforms/gold/upsert_dim_store.sql` | SQL |
| **4** | `sql/transforms/gold/upsert_dim_product.sql` | SQL |
| **4** | `sql/transforms/gold/load_fact_transactions.sql` | SQL |
| **4** | `sql/transforms/gold/load_fact_fraud_alerts.sql` | SQL |
| **4** | `sql/transforms/gold/refresh_hourly_sales.sql` | SQL |
| **4** | `sql/transforms/gold/refresh_daily_fraud.sql` | SQL |
| **4** | `sql/quality/check_null_rate.sql` | SQL |
| **4** | `sql/quality/check_duplicates.sql` | SQL |
| **4** | `sql/quality/check_freshness.sql` | SQL |
| **4** | `sql/quality/check_amounts.sql` | SQL |
| **4** | `tests/unit/test_dag_structure.py` | Test |
| **4** | `tests/unit/test_dag_callbacks.py` | Test |
| **5** | `tests/integration/__init__.py` | Test |
| **5** | `tests/integration/conftest.py` | Test |
| **5** | `tests/integration/test_kafka_roundtrip.py` | Test |
| **5** | `tests/integration/test_postgres_medallion.py` | Test |
| **5** | `tests/integration/test_dlq_flow.py` | Test |
| **5** | `tests/integration/test_feature_store.py` | Test |
| **5** | `tests/contract/__init__.py` | Test |
| **5** | `tests/contract/test_schema_compatibility.py` | Test |
| **5** | `tests/contract/test_sql_schema_contract.py` | Test |
| **6** | `k8s/network-policies/deny-all.yaml` | K8s |
| **6** | `k8s/network-policies/allow-streamflow.yaml` | K8s |
| **6** | `k8s/pod-disruption-budgets.yaml` | K8s |
| **6** | `k8s/resource-quotas.yaml` | K8s |
| **7** | `src/utils/metrics.py` | Python |
| **7** | `src/utils/tracing.py` | Python |
| **7** | `k8s/monitoring/business-metrics-dashboard.json` | Grafana |
| **7** | `k8s/monitoring/ml-dashboard.json` | Grafana |
| **8** | `.github/workflows/ci-complete.yaml` | CI/CD |
| **8** | `.github/workflows/security.yaml` | CI/CD |
| **8** | `.github/workflows/deploy-argocd.yaml` | CI/CD |
| **8** | `k8s/argocd/application.yaml` | K8s |
| **8** | `k8s/argocd/project.yaml` | K8s |
| **8** | `infra/modules/argocd/main.tf` | Terraform |
| **8** | `infra/modules/argocd/variables.tf` | Terraform |
| **8** | `infra/environments/dev/argocd/terragrunt.hcl` | Terragrunt |
| **9** | `docs/screenshots/*.png` (7 screenshots) | Assets |
| **9** | `scripts/deploy_full.sh` | Script |
| **9** | `scripts/capture_screenshots.sh` | Script |
| **10** | `tests/chaos/__init__.py` | Test |
| **10** | `tests/chaos/test_kafka_failure.py` | Test |
| **10** | `tests/chaos/test_postgres_failure.py` | Test |
| **10** | `tests/chaos/test_flink_checkpoint_recovery.py` | Test |
| **10** | `tests/chaos/test_network_partition.py` | Test |
| **10** | `tests/chaos/conftest.py` | Test |
| **10** | `docs/CHAOS_REPORT.md` | Docs |
| **10** | `docs/ML_PIPELINE.md` | Docs |

**Total de arquivos NOVOS: ~78**

### Arquivos EXISTENTES a Modificar (por fase)

| Fase | Arquivo | Mudanca Resumida |
|------|---------|-----------------|
| **1** | `src/flink_jobs/fraud_detector.py` | Rename FraudEngine -> FraudRuleEvaluator, parametrizar estado |
| **1** | `src/flink_jobs/common/state.py` | Adicionar to_bytes/from_bytes, VelocityWindow |
| **1** | `k8s/flink/fraud-detector.yaml` | rocksdb, savepoint, EXACTLY_ONCE |
| **1** | `pyproject.toml` | msgpack dependency |
| **1** | `config/fraud_rules.yaml` | Secao flink |
| **2** | `src/flink_jobs/fraud_detector.py` | Integrar ML scorer |
| **2** | `src/flink_jobs/fraud_detector_function.py` | Carregar modelo no open() |
| **2** | `src/models/fraud_alert.py` | FR-006 ML_ANOMALY |
| **2** | `config/fraud_rules.yaml` | Secao ml, FR-006, rebalancear pesos |
| **2** | `pyproject.toml` | scikit-learn, joblib, numpy |
| **2** | `.gitignore` | models/*.joblib |
| **3** | `src/flink_jobs/transaction_processor.py` | DLQ side output |
| **3** | `src/flink_jobs/common/serialization.py` | Schema version |
| **3** | `k8s/kafka/kafka-topics.yaml` | Topico streamflow.dlq |
| **4** | `src/dags/bronze_to_silver.py` | TaskGroups, callbacks, SLA |
| **4** | `src/dags/silver_to_gold.py` | TaskGroups, paralelismo |
| **4** | `src/dags/data_quality.py` | Tasks individuais, XCom |
| **4** | `src/dags/maintenance.py` | Paralelismo, callbacks |
| **5** | `pyproject.toml` | testcontainers, markers |
| **5** | `tests/conftest.py` | Fixtures globais |
| **5** | `tests/e2e/test_full_pipeline.py` | Mover + rename |
| **5** | `Makefile` | Targets novos |
| **6** | `k8s/flink/fraud-detector.yaml` | Probes, graceful shutdown |
| **6** | `k8s/flink/transaction-processor.yaml` | Probes |
| **6** | `k8s/flink/realtime-aggregator.yaml` | Probes |
| **6** | `k8s/monitoring/alerting-rules.yaml` | Regras DLQ + ML |
| **7** | `src/flink_jobs/fraud_detector_function.py` | Metricas Prometheus |
| **7** | `src/flink_jobs/transaction_processor.py` | Metricas DLQ |
| **7** | `pyproject.toml` | prometheus-client, opentelemetry |
| **7** | `k8s/monitoring/service-monitors.yaml` | ServiceMonitor custom |
| **8** | `.github/workflows/ci.yaml` | Substituir por ci-complete |
| **8** | `.github/workflows/deploy.yaml` | Fallback manual |
| **8** | `infra/environments/dev/terragrunt.hcl` | ArgoCD dependency |
| **9** | `README.md` | Screenshots, Mermaid, badges |
| **9** | `ARCHITECTURE.md` | Mermaid, ML, DLQ, ADRs novos |
| **10** | `README.md` | Chaos results, ML, final polish |
| **10** | `docs/FRAUD_DETECTION.md` | ML section, Mermaid |
| **10** | `docs/RUNBOOK.md` | DLQ, ML, chaos procedures |
| **10** | `Makefile` | Target chaos |

**Total de arquivos MODIFICADOS: ~38**

---

## SCORING PROJECTION

### Score Atual: 4.5/10

| Categoria | Score Atual | Peso | Problemas |
|-----------|-------------|------|-----------|
| Flink Real (KeyedProcessFunction) | 1/10 | 25% | Dicts Python, sem state management real |
| ML Pipeline | 0/10 | 15% | Inexistente |
| Tests (Unit + Integration + Contract) | 4/10 | 15% | 85 tests mas todos in-memory, sem infra |
| Airflow DAGs | 3/10 | 10% | Triviais, sem TaskGroups/callbacks |
| CI/CD GitOps | 3/10 | 10% | CI basico, deploy manual |
| Observabilidade | 5/10 | 5% | Alertas existem mas sem metricas customizadas |
| Schema Evolution + DLQ | 0/10 | 5% | Inexistente |
| K8s Hardening | 3/10 | 5% | Funcional mas sem policies/probes |
| Documentacao | 6/10 | 5% | README bom mas sem screenshots reais |
| Chaos Engineering | 0/10 | 5% | Inexistente |
| **TOTAL PONDERADO** | **4.5/10** | 100% | |

### Score Projetado por Fase

| Apos Fase | Score | Delta | Categoria Impactada |
|-----------|-------|-------|---------------------|
| Fase 1 | 5.5 | +1.0 | Flink Real: 1 -> 5 (KeyedProcessFunction real mas sem deploy) |
| Fase 2 | 6.5 | +1.0 | ML Pipeline: 0 -> 7 (Isolation Forest + Feature Store) |
| Fase 3 | 7.0 | +0.5 | DLQ + Schema: 0 -> 8 |
| Fase 4 | 7.5 | +0.5 | Airflow DAGs: 3 -> 8 (TaskGroups, callbacks, SLA) |
| Fase 5 | 8.0 | +0.5 | Tests: 4 -> 8 (Integration + Contract + Testcontainers) |
| Fase 6 | 8.3 | +0.3 | K8s: 3 -> 8 (Policies, PDB, probes) |
| Fase 7 | 8.6 | +0.3 | Observabilidade: 5 -> 9 (metricas customizadas, tracing) |
| Fase 8 | 9.0 | +0.4 | CI/CD: 3 -> 9 (GitOps completo, ArgoCD, security) |
| Fase 9 | 9.5 | +0.5 | Flink: 5 -> 10, Docs: 6 -> 9 (deploy real + screenshots) |
| Fase 10 | **10.0** | +0.5 | Chaos: 0 -> 9, Docs: 9 -> 10 |

### Score Minimo Aceitavel (se faltar tempo)

**Parar apos Fase 5 = 8.0/10** — ja e suficiente para Staff. Fases 6-10 sao o "polish" que leva de Staff para Staff+ / Principal.

---

## SUCCESS METRICS para 10/10

| # | Metrica | Target | Como Medir |
|---|---------|--------|------------|
| 1 | Flink usa KeyedProcessFunction real | ValueState + checkpoint recovery | Inspecao de codigo + k8s manifest |
| 2 | ML pipeline funcional | Modelo treinado, scores [0,1], FR-006 | `scripts/train_model.py` + testes |
| 3 | DLQ implementada | Zero eventos silenciosamente descartados | Teste de integracao + topico DLQ |
| 4 | DAGs com TaskGroups | >= 3 TaskGroups por DAG principal | DagBag validation test |
| 5 | Testes de integracao reais | Testcontainers com Kafka + PostgreSQL | `pytest -m integration` |
| 6 | Contract tests | Schema compatibility validada | `pytest -m contract` |
| 7 | CI/CD automatico | Push -> Lint -> Test -> Deploy | GitHub Actions green |
| 8 | ArgoCD GitOps | Sync automatico de manifests K8s | ArgoCD UI screenshot |
| 9 | Deploy real | Pods Running no K3s 15.235.61.251 | `kubectl get pods` screenshot |
| 10 | Chaos Engineering | 4 cenarios testados, recovery documentado | `CHAOS_REPORT.md` |
| 11 | Metricas customizadas | 5+ metricas de negocio no Prometheus | Grafana dashboard screenshot |
| 12 | Cobertura de testes | >= 80% | `pytest --cov` report |
| 13 | Zero erros de qualidade | ruff + mypy --strict | CI pipeline |
| 14 | Documentacao premium | Mermaid diagrams + screenshots no README | GitHub rendering |

---

## VERIFICACAO FINAL (Checklist pos-implementacao)

```
REQUISITOS
[_] Todos os 10 problemas da auditoria corrigidos
[_] Score >= 9.5/10 na auto-avaliacao
[_] README impressiona em 30 segundos de leitura

CODIGO
[_] ruff check src/ tests/ scripts/ — 0 erros
[_] ruff format --check src/ tests/ scripts/ — 0 diffs
[_] mypy src/ scripts/ --strict — 0 erros
[_] pytest tests/unit/ — todos passam
[_] pytest tests/integration/ -m integration — todos passam
[_] pytest tests/contract/ -m contract — todos passam
[_] pytest --cov=src --cov-report=term-missing — >= 80%

INFRAESTRUTURA
[_] kubectl get pods -A | grep streamflow — todos Running
[_] kubectl get networkpolicy -A — policies aplicadas
[_] kubectl get pdb -A — PDBs configurados
[_] ArgoCD app synced e healthy

FLINK
[_] fraud-detector usa state.backend: rocksdb
[_] fraud-detector usa upgradeMode: savepoint
[_] Checkpoints completando (Flink dashboard)
[_] KeyedProcessFunction com ValueState funcional

ML
[_] Modelo treinado com metricas documentadas
[_] Scoring retorna [0, 1]
[_] FR-006 ML_ANOMALY aparece em alertas
[_] Feature Store materializado no Gold

AIRFLOW
[_] 5+ DAGs carregam sem erros
[_] TaskGroups visiveis no UI
[_] Callbacks configurados
[_] SLA definido

TESTES
[_] >= 120 testes (atualmente 85)
[_] Unit tests < 2s
[_] Integration tests com containers reais
[_] Contract tests validam schemas

CI/CD
[_] GitHub Actions CI completo passando
[_] Security scan (bandit + safety)
[_] Deploy automatico via ArgoCD ou Actions

OBSERVABILIDADE
[_] Metricas customizadas no Prometheus
[_] Dashboards de negocio no Grafana
[_] Alertas de DLQ e ML configurados

CHAOS
[_] Kafka failure recovery testado
[_] PostgreSQL failure recovery testado
[_] Flink checkpoint recovery testado
[_] Network partition recovery testado
[_] CHAOS_REPORT.md documentado

DOCUMENTACAO
[_] README com screenshots reais
[_] Mermaid diagrams renderizando
[_] ARCHITECTURE.md atualizado
[_] FRAUD_DETECTION.md com secao ML
[_] ML_PIPELINE.md completo
[_] RUNBOOK.md com procedimentos novos
[_] CHAOS_REPORT.md com resultados
```

---

## TIMELINE VISUALIZATION

```
  Fase 1     Fase 2     Fase 3    Fase 4    Fase 5
 Flink Real  ML Pipeline  DLQ     DAGs     Tests
|---------|---------|--------|--------|---------|
  HIGH       HIGH      MEDIUM   MEDIUM    HIGH
  ~8 files   ~10 files  ~7 files ~16 files ~12 files

                                              Score: 8.0/10
                                              (minimo aceitavel)

  Fase 6     Fase 7     Fase 8    Fase 9    Fase 10
 K8s Hard   Observ     CI/CD    Deploy    Chaos+Docs
|---------|---------|--------|--------|---------|
  MEDIUM    MEDIUM    MEDIUM   MEDIUM    MEDIUM
  ~8 files  ~6 files  ~10 files ~5 files  ~12 files

                                              Score: 10.0/10
                                              (objetivo final)
```

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 10 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 10 |
| Validations Completed | 7 |
| Problems Identified | 10 |
| Phases Planned | 10 |
| Files to Create | ~78 |
| Files to Modify | ~38 |
| Total File Operations | ~116 |
| Risk Items | 10 |
| Success Metrics | 14 |

---

## ADRs Novos (a documentar durante implementacao)

| # | ADR | Decisao |
|---|-----|---------|
| 008 | ML Algorithm | Isolation Forest (nao-supervisionado, leve, sem labels) |
| 009 | Feature Store Location | PostgreSQL Gold (zero infra extra) |
| 010 | State Serialization | msgpack (compacto, tipado, cross-language) |
| 011 | Dead Letter Queue | Topico Kafka dedicado + tabela PostgreSQL |
| 012 | Schema Evolution Strategy | Additive-only, forward-compatible, version header |
| 013 | GitOps Operator | ArgoCD (popular, UI, community) |
| 014 | Chaos Engineering Approach | Scripts leves (nao LitmusChaos/ChaosMesh) |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_STAFF_UPGRADE.md`

Ou, se preferir executar diretamente, comecar pela **Fase 1: KeyedProcessFunction Real** com:

```
/build "Fase 1 do BRAINSTORM_STAFF_UPGRADE.md — Reescrever fraud_detector.py como KeyedProcessFunction real"
```

---

> **"A diferenca entre Senior e Staff nao e o que voce sabe — e o que voce DEMONSTRA."**
> Este plano demonstra: arquitetura de sistemas distribuidos, ML aplicado, resiliencia, observabilidade, GitOps, e mentalidade de producao.
