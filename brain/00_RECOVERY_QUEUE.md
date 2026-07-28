---
type: recovery_queue
project: EddY
version: 4.6B-J
status: active
last_updated: 2026-04-29
tags: [recovery, queue, acoes, prioridade, pendente]
aliases: [RECOVERY, QUEUE, PENDENCIAS]
---

# EddY — Fila de Recovery (29/04/2026)
**Modo:** DRY-RUN — zero movimentação física sem aprovação explícita

---

## P1 — [CRÍTICO] Copiar kkkk/3333 → _INBOX_CONVERGENCE

**Urgência:** IMEDIATA
**Fonte:** `R:\Eddy_160GB\kkkk\3333\`
**Destino:** `R:\EddY\_INBOX_CONVERGENCE\kkkk_3333\`
**Referência:** `data/analysis/kkkk_3333_manifest.json`

**O que copiar:**
1. Todos os PDFs canônicos EddY/ESL (Bíblia, Dossiê Supremo, Estudo ESL, Blueprint, etc.)
2. Master_Asset_Catalog_Eddy_Digital_Solutions.xlsx
3. ChatGPT export (dir 74b064f5...)
4. Arquivos CREATIVE_IP

**Separar em subpasta isolada:**
- `_sensitive/` → cartao-cns.png, formulários médicos, certidões, docs legais pessoais

**Verificação:** SHA256 de cada canonical após cópia.

> [!danger] Este bloco tem arquivos ÚNICOS sem cópia confirmada em G:\ ou D:\
> Risco de perda permanente se o drive R:\Eddy_160GB\ falhar.

---

## P2 — [ALTO] SHA256 dos DBs históricos em EddY_Observer

**Script:** `core/db_sha256_audit.py`
**Target:** `R:\EddY_Observer\*.db` (13 bancos, 2.5GB total)
**Output:** `data/analysis/observer_sha256_audit.json`

Bancos críticos:
- `neverlost.db` (352MB, 927k arquivos)
- `eddy_backup_before_fix.db` (573MB)
- `eddy_backup_before_ingest_fix2.db` (554MB)
- `eddy_backup_before_sources_fix.db` (554MB)

> Pré-requisito para qualquer decisão sobre convergência dos DBs históricos.

---

## P3 — [ALTO] Indexar ChatGPT Export por conteúdo

**Script:** `core/chat_semantic_indexer.py`
**Target:** `R:\Eddy_160GB\kkkk\3333\74b064f5.../`
**Output:** `data/analysis/chatgpt_conversation_index.json`

> 109+ conversas não indexadas por conteúdo — apenas por título.
> Contexto histórico crítico do desenvolvimento do EddY.

---

## P4 — [MÉDIO] Extrair Master_Asset_Catalog.xlsx

**Método:** Abrir manualmente ou usar openpyxl
**Target:** `R:\Eddy_160GB\kkkk\3333\Master_Asset_Catalog_Eddy_Digital_Solutions.xlsx`
**Output:** `data/analysis/master_asset_catalog_extracted.json`

> Pode ser o inventário definitivo do sistema ESL — alta prioridade de leitura.

---

## P5 — [MÉDIO] Reconciliar EddY_OS_Brain com brain/

**Método:** Leitura manual + merge seletivo
**Target:** `R:\EddY\brain\EddY_OS_Brain\` (35 Notion MDs + 1 Sem título/)
**Output:** novos MDs em brain/ ou atualizações dos canônicos existentes

Conteúdo potencialmente único:
- Bíblia Canônica do Sistema EddY
- World Bible Valtherra
- NeverLost Produto
- Dossiê Completo das Modelos (Isabella/Vivian)
- Estrutura Jurídica MEI

---

## P6 — [MÉDIO] Inspecionar neverlost.db schema

**Comando:** `sqlite3 R:\EddY_Observer\neverlost.db ".schema"`
**Output:** `data/analysis/neverlost_schema.json`

---

## P7 — [BAIXO] Mover 12 JSONs de brain/ → data/analysis/

**Arquivos:**
`core_candidates_expanded.json`, `core_knowledge_candidates.json`, `core_knowledge_patterns.json`,
`core_manifest_r_unique.json`, `core_value_matrix.json`, `distributed_knowledge_map.json`,
`eddy_internal_inventory.json`, `fase_4_6b_d_report.json`, `full_inventory_r_eddy.json`,
`knowledge_fragments_map.json`, `structure_map_r_eddy.json`, `value_matrix_expanded.json`

> brain/ deve conter apenas MDs canônicos. Análise técnica fica em data/analysis/.

---

## P8 — [BAIXO] Deletar WAL ghosts após integrity_check

**Pré-condição:**
```
sqlite3 R:\EddY\core\eddy.db "PRAGMA integrity_check;"
```
Deve retornar: `ok`

**Então:** deletar `eddy_backup_pre_reconcile.db-shm` e `eddy_backup_pre_reconcile.db-wal` da raiz de R:\EddY.

---

## P9 — [BAIXO] Rebuild CKG

**Script:** `core/build_ckg.py`
**Pré-condição:** P1 + P5 + P7 concluídos (brain/ estabilizado)
**Output:** `brain/structured_knowledge/knowledge_base.json` (atualizado)

> 269 candidatos de ingestão aguardando. Não rebuildar antes de brain/ estabilizar.

---

*Atualizado: 2026-04-29 — FASE 4.6B-J | Ver também: [[00_ESTADO_CONSOLIDADO]] | [[ESTADO_ATUAL]]*
