---
type: contexto_mestre
project: EddY
phase: M3
status: canonical
last_updated: 2026-04-30
aliases: [contexto_mestre, eddy_context]
tags: [canonical, context, master]
---

# 🧠 EDDY — CONTEXTO MESTRE DO SISTEMA

## DEFINIÇÃO

O Sistema EddY é um motor de reconstrução de verdade digital que transforma um acervo massivo de arquivos em:

1. Base física confiável
2. Estrutura de redundância validada
3. Conhecimento semântico estruturado (CKG)
4. Ativos digitais monetizáveis (ESL)

---

## CAMADAS DO SISTEMA

### 1. CAMADA FÍSICA (CORE)

* Banco SQLite (`files`)
* Estado real dos arquivos
* Classificação física (online/offline)

Regra:

> Nenhuma decisão sem verdade física validada

---

### 2. CAMADA ESTRUTURAL

* Matriz de redundância
* Clusterização por quicksig + hash
* Mapeamento entre drives

Regra:

> Nenhuma ação sem entender duplicação global

---

### 3. CAMADA DE INTELIGÊNCIA

* Planejador (decide ações)
* NÃO executa nada
* Gera:

  * KEEP
  * MOVE
  * DUPLICATE
  * IGNORE

Regra:

> Decidir antes de agir

---

### 4. CAMADA SEMÂNTICA (CKG / BRAIN)

* Obsidian
* Markdown estruturado
* Wikilinks

Regra:

> Só entra conteúdo validado e relevante

---

### 5. CAMADA DE VALOR (ESL / EDS)

* Marca Exclusivity ESL
* Modelos (Isabella, Vivian)
* Conteúdo monetizável

Regra:

> Nunca misturar com dados brutos ou pipeline técnico

---

## PRINCÍPIOS ABSOLUTOS

* CONSISTÊNCIA > VELOCIDADE
* SQLite é single-writer
* Nenhuma operação destrutiva sem validação
* Brain não é backup, é conhecimento
* Nem todo arquivo vira conhecimento

---

## ESTADO ATUAL (2026-04-25)

* Saneamento em estágio avançado — ETAPAs 0a, 1a, 1b, 3, Pré-4.5 concluídas
* ETAPA 4.5 (classify_magic.py): DRY RUN concluído — 873.555 arquivos mapeados
* Pós-4.5 (classify_offline.py): 72.9% — separando offline_device em 3 estados
* Brain expandido: [[CORPUS_HISTORICO]] | [[MATRIZ_REDUNDANCIA]] | [[03_ESL_ASSETS/00_INDEX]]
* Pipeline: taxonomy + DEFAULT_RULES corrigidos. Decide: aguardando hashing
* Ver estado completo: [[ESTADO_ATUAL]] | [[DECISOES]]

---

## PROXIMA ACAO

1. Aguardar classify_offline.py (em curso — ~5h restantes)
2. Validar banco: `PRAGMA integrity_check` + distribuicao final
3. Gerar matriz de redundancia — ETAPA 4.6A (queries read-only)
4. Retomar hashing Lote 2 — grupos quicksig excluindo invalid_empty
5. Rodar decide dry_run em G:\ only

---

## ALERTA CRÍTICO

Qualquer tentativa de:

* organizar arquivos
* expandir conhecimento
* deletar dados

ANTES da matriz de redundância

→ pode corromper o sistema

---

## FRASE DEFINITIVA

"EddY não organiza arquivos.
EddY descobre a verdade antes de permitir qualquer ação."
