# StreamFlow Analytics: Plano de Upgrade para Nivel Staff

## Por que esse upgrade e necessario?

Apos uma revisao honesta do codigo, o projeto recebeu nota **4.5/10 para nivel Staff**. Dois problemas criticos foram identificados:

1. **O `fraud_detector.py` NAO e um job Flink de verdade** — usa dicts Python simples para estado, quando deveria usar `KeyedProcessFunction` com `ValueState`/`ListState` (estado fault-tolerant com checkpointing)
2. **Nao tem nenhum componente de ML** — deteccao de fraude real usa algoritmos como Isolation Forest ou XGBoost, nao apenas regras simples

Alem disso: DAGs do Airflow muito basicas, testes E2E falsos, sem Dead Letter Queue.

**Objetivo:** Elevar o projeto para qualidade genuina de Staff Data Engineer, preservando toda a logica de negocios ja testada.

---

## Ordem de Execucao (5 Prioridades)

```
P1: Reescrever fraud_detector.py como PyFlink KeyedProcessFunction real
P2: Adicionar camada ML com Isolation Forest
P3: Dead Letter Queue + Evolucao de Schema
P4: DAGs Airflow de nivel producao
P5: Testes de integracao reais + reestruturacao de testes
```

P1 tem que ser primeiro (P2 depende dele). P3 e P4 sao independentes. P5 e escrito junto com cada fase.

---

## P1: KeyedProcessFunction Real no PyFlink

**O que esta errado hoje:**
O `FraudEngine` guarda estado em dicts Python (`self._amount_stats: dict[str, RunningStats]`). Se o job reiniciar, **todo o estado e perdido**. Em Flink de verdade, usamos `ValueState` que e salvo em checkpoints e sobrevive a falhas.

**Estrategia:** Manter a logica de negocios do `FraudEngine` (renomear para `FraudRuleEvaluator`), e envolver ela numa `KeyedProcessFunction` do Flink.

### Arquivos a modificar:

- **`src/flink_jobs/fraud_detector.py`** — Reescrita principal:
  - Renomear `FraudEngine` para `FraudRuleEvaluator` (Python puro, sem imports do Flink)
  - Refatorar os metodos das regras para receber objetos de estado como parametros em vez de ler dos dicts `self._*`
  - Criar `FraudDetectorFunction(KeyedProcessFunction)` com:
    - `open()`: inicializa `ValueState[bytes]` para amount_stats, hour_stats, last_location; `ListState[bytes]` para velocity_window
    - `process_element()`: desserializa estado, chama `FraudRuleEvaluator.evaluate()`, persiste estado atualizado, emite side output para alertas
    - `OutputTag("fraud-alerts")` para stream separada de alertas de fraude
  - Criar funcao `build_fraud_detection_pipeline()` (KafkaSource -> key_by -> FraudDetectorFunction -> sinks)
  - Manter alias `FraudEngine = FraudRuleEvaluator` para compatibilidade (todos os testes existentes continuam passando)

- **`src/flink_jobs/common/state.py`** — Adicionar `to_bytes()`/`from_bytes()` ao `RunningStats` e `GeoLocation` para serializacao do estado Flink

- **`k8s/flink/fraud-detector.yaml`** — Mudar `state.backend: rocksdb` (producao), adicionar `execution.checkpointing.mode: EXACTLY_ONCE`, mudar `upgradeMode: savepoint`

### Codigo reutilizado:
- Todos os 5 metodos de regras (high_value, velocity, geographic, time_anomaly, blacklist)
- `RunningStats`, `GeoLocation`, `FraudRuleResult`, `haversine_km` do `state.py`
- Padrao de pipeline do `transaction_processor.py` (KafkaSource, WatermarkStrategy, JdbcSink)

### Sem dependencias novas (apache-flink ja esta no pyproject.toml)

---

## P2: Deteccao de Anomalias com ML (Isolation Forest)

**O que esta faltando hoje:**
Fraude real e detectada com algoritmos matematicos de ML. O Isolation Forest e perfeito para isso: e um algoritmo de anomaly detection nao-supervisionado que isola pontos anomalos construindo arvores aleatorias.

**Estrategia:** Treinar modelo offline com dados gerados, carregar no Flink via `open()`, combinar score ML com score das regras.

### Arquivos novos:
- **`src/flink_jobs/ml/__init__.py`** — Pacote novo
- **`src/flink_jobs/ml/feature_engineering.py`** — Extrai vetor de 6 features do estado:
  - `amount_zscore` (quanto o valor desvia da media do cliente)
  - `velocity_count` (quantas transacoes na janela)
  - `time_deviation` (hora incomum para o cliente)
  - `geo_speed_kmh` (velocidade impossivel entre localizacoes)
  - `is_blacklisted` (0 ou 1)
  - `amount_ratio` (valor / media do cliente)
  - Python puro (sem dependencia do Flink, testavel isoladamente)
- **`src/flink_jobs/ml/model_scorer.py`** — Classe `AnomalyScorer`: carrega modelo joblib, normaliza `decision_function` do Isolation Forest para range [0,1]
- **`scripts/train_model.py`** — Script de treino offline usando geradores existentes (`TransactionGenerator`, `FraudInjector`)
  - Gera 10k transacoes mistas, extrai features, treina `IsolationForest(n_estimators=100, contamination=0.02)`
  - Salva em `models/fraud_model.joblib`

### Arquivos a modificar:
- **`src/flink_jobs/fraud_detector.py`** — No `open()`: carregar modelo ML. No `process_element()`: `score_final = alpha * score_ml + (1-alpha) * score_regras`
- **`src/models/fraud_alert.py`** — Adicionar `ML_ANOMALY = "FR-006"` ao `FraudRuleId`
- **`config/fraud_rules.yaml`** — Adicionar config FR-006 + `ml.alpha: 0.3`
- **`pyproject.toml`** — Adicionar `ml = ["scikit-learn>=1.4.0", "joblib>=1.3.0", "numpy>=1.26.0"]`

---

## P3: Dead Letter Queue + Evolucao de Schema

**O que esta faltando hoje:**
Eventos malformados sao simplesmente descartados com um `logger.warning`. Em producao, precisamos de uma DLQ para nao perder dados e poder investigar problemas.

### Arquivos novos:
- **`src/flink_jobs/common/dlq.py`** — Funcao `build_dlq_record()`: encapsula evento original com metadados de erro (tipo, mensagem, topico origem, timestamp)
- **`src/dags/dlq_monitor.py`** — DAG Airflow que verifica contagem de eventos DLQ a cada 5 min
- **`k8s/kafka/kafka-topics.yaml`** — Adicionar topico `streamflow.dlq` (1 particao, retencao 30 dias)

### Arquivos a modificar:
- **`src/flink_jobs/transaction_processor.py`** — Trocar o `_parse_and_validate` que retorna None por side output `OutputTag("dead-letter-queue")` para eventos malformados
- **`src/flink_jobs/common/serialization.py`** — Adicionar `CURRENT_SCHEMA_VERSION` e parsing forward-compatible (versao desconhecida = log warning, tenta parsear)

### Sem dependencias novas

---

## P4: DAGs Airflow de Nivel Producao

**O que esta errado hoje:**
- `bronze_to_silver.py`: apenas 2 tasks lineares
- `silver_to_gold.py`: 2 tasks + sensor
- `data_quality.py`: 1 unica task
- `maintenance.py`: 3 tasks lineares
- Nenhuma tem: TaskGroups, callbacks, SLA, tarefas dinamicas, alertas

### Arquivos novos:
- **`src/dags/common/__init__.py`** + **`src/dags/common/callbacks.py`** — Callbacks compartilhados: `on_failure_callback`, `on_success_callback`, `on_sla_miss_callback`
- **7 arquivos SQL** extraidos do `sql/transforms/silver_to_gold.sql` (sem mudanca de logica, apenas separacao):
  - `sql/transforms/gold/upsert_dim_customer.sql`
  - `sql/transforms/gold/upsert_dim_store.sql`
  - `sql/transforms/gold/upsert_dim_product.sql`
  - `sql/transforms/gold/load_fact_transactions.sql`
  - `sql/transforms/gold/load_fact_fraud_alerts.sql`
  - `sql/transforms/gold/refresh_hourly_sales.sql`
  - `sql/transforms/gold/refresh_daily_fraud.sql`
- **4 arquivos SQL** extraidos do `sql/quality/quality_checks.sql`:
  - `sql/quality/check_null_rate.sql`
  - `sql/quality/check_duplicates.sql`
  - `sql/quality/check_freshness.sql`
  - `sql/quality/check_amounts.sql`

### Arquivos a modificar:
- **`src/dags/bronze_to_silver.py`** — Adicionar TaskGroups (validacao, transformacao, pos-validacao), callbacks, SLA, checks pre/pos
- **`src/dags/silver_to_gold.py`** — Separar em TaskGroups (dimensoes, fatos, agregados), uma task por dimensao/fato, notificacao de sucesso
- **`src/dags/data_quality.py`** — Separar em tasks individuais por arquivo SQL + PythonOperator de alerta
- **`src/dags/maintenance.py`** — Pruning paralelo via TaskGroup, callbacks, task de notificacao

---

## P5: Testes de Integracao Reais + Reestruturacao

**O que esta errado hoje:**
O `test_full_pipeline.py` esta marcado como "e2e" mas so testa o `FraudEngine` em memoria — nao testa nenhuma infraestrutura real.

### Novos arquivos de teste:
- **`tests/unit/test_fraud_detector_function.py`** — MockValueState, MockListState, MockRuntimeContext; testa open(), process_element(), acumulacao de estado, emissao de side output
- **`tests/unit/test_feature_engineering.py`** — Testa formato do vetor de features, edge cases (sem historico, std_dev zero)
- **`tests/unit/test_model_scorer.py`** — Treina IsolationForest pequeno no teste, verifica range do score [0,1]
- **`tests/unit/test_dlq.py`** — Testa estrutura do build_dlq_record, truncamento de eventos grandes
- **`tests/unit/test_dag_structure.py`** — Validacao DagBag (import sem erros), contagem de tasks, dependencias corretas
- **`tests/integration/test_ml_pipeline.py`** — Feature extraction -> scoring end-to-end
- **`tests/integration/test_fraud_engine_flow.py`** — Renomeado de `tests/e2e/test_full_pipeline.py` (marcador mudado para `integration`)

### Arquivos a modificar:
- **`pyproject.toml`** — Adicionar marcador `integration`
- **`tests/conftest.py`** — Adicionar fixtures de ML e mocks de estado Flink

---

## Resumo de Arquivos

| Categoria | Novos | Modificados | Total |
|-----------|-------|-------------|-------|
| Codigo fonte (src/) | 5 | 7 | 12 |
| SQL | 11 | 0 | 11 |
| Testes | 7 | 2 | 9 |
| Config/K8s | 1 | 3 | 4 |
| Scripts | 1 | 0 | 1 |
| **Total** | **25** | **12** | **37** |

---

## Verificacao

Apos cada fase, rodar:
```bash
ruff check src/ tests/ scripts/
mypy src/ scripts/ --strict
pytest tests/ -v --tb=short
pytest tests/ --cov=src --cov-report=term-missing  # deve manter >80%
```

Validacao final:
1. Todas as 5 regras de fraude continuam passando nos testes existentes (compatibilidade via alias FraudEngine)
2. Testes novos da KeyedProcessFunction passam com estado mockado
3. Modelo ML treina com sucesso, scores retornam range [0,1]
4. Estrutura DLQ valida como JSON
5. Todas as 4+ DAGs carregam sem erros no DagBag
6. ruff: 0 erros | mypy --strict: 0 erros | pytest: todos passam | cobertura: >80%
