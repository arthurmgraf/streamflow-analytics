# TASK 01 - Mapeamento do Processo Atual de Dados

## Titulo
Mapeamento Completo do Fluxo de Dados Atual da MR. HEALTH

## Objetivo
Documentar de forma detalhada o fluxo de dados atual da rede MR. HEALTH, desde a geracao dos dados nas ~50 unidades ate a consolidacao final pela equipe do Ricardo Martins na sede. Identificar todos os gargalos, pontos de falha, riscos operacionais e problemas decorrentes do processo manual vigente.

## Contexto
A MR. HEALTH e uma rede de restaurantes slow-food com aproximadamente 50 unidades distribuidas pelo sul do Brasil. Atualmente, o processo de dados funciona da seguinte forma:

- **Origem dos dados**: Cada unidade gera diariamente dois arquivos CSV:
  - `PEDIDO.CSV` - Dados dos pedidos realizados no dia
  - `ITEM_PEDIDO.CSV` - Itens detalhados de cada pedido
- **Frequencia**: Envio diario a meia-noite (dados do dia anterior, D-1)
- **Destino**: Os arquivos sao enviados para a sede/equipe central
- **Consolidacao**: A equipe do Ricardo Martins recebe os CSVs e realiza consolidacao manual em planilhas (provavelmente Excel/Google Sheets)
- **Dados complementares na sede**: Existem tabelas PostgreSQL no sistema da sede contendo dados de referencia:
  - `PRODUTO` - Catalogo de produtos
  - `UNIDADE` - Cadastro das unidades
  - `ESTADO` - Estados brasileiros
  - `PAIS` - Paises

### Problemas conhecidos e esperados
- Processo manual sujeito a erros humanos
- Escalabilidade limitada (50 unidades enviando CSV)
- Sem validacao automatica dos dados recebidos
- Risco de perda de arquivos ou envio duplicado
- Dificuldade de rastreabilidade e auditoria
- Tempo elevado para consolidacao manual
- Sem integracao automatica entre CSVs e dados do PostgreSQL

## Criterios de Aceitacao

1. **Diagrama de fluxo AS-IS** documentado com todas as etapas do processo atual
2. **Inventario de fontes de dados** listando:
   - Todas as fontes (CSVs das unidades + PostgreSQL da sede)
   - Esquema/estrutura de cada arquivo CSV (colunas, tipos, volume estimado)
   - Esquema das tabelas PostgreSQL relevantes
3. **Mapa de gargalos** com identificacao clara de:
   - Pontos de falha unicos (single points of failure)
   - Etapas manuais que causam atraso
   - Riscos de qualidade de dados
   - Limitacoes de escalabilidade
4. **Matriz de problemas** categorizada por:
   - Severidade (critico, alto, medio, baixo)
   - Tipo (operacional, qualidade, performance, seguranca)
   - Impacto no negocio
5. **Metricas do processo atual** (estimadas):
   - Tempo medio de consolidacao
   - Volume de dados diario/mensal
   - Taxa estimada de erros/retrabalho

## Subtasks

### 1.1 - Levantamento das Fontes de Dados CSV
- Documentar a estrutura esperada do `PEDIDO.CSV` (colunas, tipos de dados, delimitador, encoding)
- Documentar a estrutura esperada do `ITEM_PEDIDO.CSV`
- Estimar volume diario por unidade (numero de registros)
- Calcular volume total diario (~50 unidades x registros/unidade)
- Identificar mecanismo atual de envio (FTP, email, upload manual, etc.)

### 1.2 - Levantamento das Fontes PostgreSQL (Sede)
- Documentar schema da tabela `PRODUTO` (colunas, PK, FK, volume)
- Documentar schema da tabela `UNIDADE` (colunas, PK, FK, volume)
- Documentar schema da tabela `ESTADO` (colunas, PK, FK, volume)
- Documentar schema da tabela `PAIS` (colunas, PK, FK, volume)
- Mapear relacionamentos entre as tabelas de referencia
- Identificar frequencia de atualizacao dessas tabelas

### 1.3 - Mapeamento do Fluxo Atual (AS-IS)
- Desenhar diagrama de fluxo completo: unidade -> envio -> recepcao -> consolidacao -> consumo
- Documentar cada etapa com responsavel, ferramenta utilizada e tempo estimado
- Identificar handoffs entre equipes/sistemas
- Documentar o processo de consolidacao manual em planilhas

### 1.4 - Analise de Gargalos e Riscos
- Listar todos os pontos de falha identificados
- Classificar cada gargalo por severidade e impacto
- Documentar cenarios de falha (ex.: unidade nao envia arquivo, arquivo corrompido, dados duplicados)
- Avaliar impacto de crescimento (ex.: de 50 para 100 unidades)

### 1.5 - Consolidacao e Documentacao Final
- Compilar todas as informacoes em documento unico
- Criar diagrama visual do fluxo AS-IS (Mermaid ou similar)
- Redigir resumo executivo dos principais problemas
- Validar completude do mapeamento

## Dependencias
- Acesso ao case `case_MrHealth.md` para extrair todas as informacoes do cenario
- Nenhuma dependencia tecnica externa para esta task (analise documental)
- Esta task e **pre-requisito** para todas as demais (TASK_02 a TASK_05)

## Agentes Sugeridos (Claude Code)

| Agente | Papel | Justificativa |
|--------|-------|---------------|
| **Agente Analista de Negocios** | Leitura e interpretacao do case | Extrair requisitos de negocio, entender o contexto operacional da MR. HEALTH |
| **Agente de Documentacao** | Estruturacao do documento final | Organizar o mapeamento em formato claro, criar diagramas Mermaid |
| **Agente de Dados** | Analise tecnica das fontes | Avaliar estruturas CSV e PostgreSQL, estimar volumes, identificar problemas de qualidade |

## Notas Adicionais
- Priorizar a clareza do documento para que stakeholders nao-tecnicos consigam compreender
- Utilizar diagramas Mermaid para representacoes visuais (compativel com Markdown)
- Manter rastreabilidade: cada problema identificado deve ser referenciado nas tasks seguintes
- Este mapeamento sera a base para justificar as decisoes de arquitetura nas tasks 02, 03 e 04
