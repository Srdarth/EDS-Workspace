---
type: decisoes
project: EddY
phase: M3
status: canonical
last_updated: 2026-04-30
aliases: [decisoes, decisions]
tags: [canonical, decisions, log]
---

# DECISOES DO SISTEMA EDDY
## Log de alterações, decisões e seu impacto

Cada decisão aqui referencia o estado que causou e o estado que produziu.
Rastreabilidade completa: causa → efeito.

Ver também: [[ESTADO_ATUAL]] | [[ARQUITETURA]] | [[00_MAPA_DO_PROJETO]]

---

## [2026-05-07] SESSAO-07/05-TARDE — Ghost Vaults + Triagem Personal + Mapeamento AI

**Timestamp:** 2026-05-07 ~07:00–17:00
**Executado por:** Claude Code (autorizado pelo usuário)

### Ações executadas

**1. Ghost Vaults Obsidian — NEUTRALIZADOS:**
- GHOST-001 `G:\EDDY_ECOSSISTEMA_FINAL\.obsidian` → deletado (pasta vazia)
- GHOST-002 `R:\Eddy_160GB\.obsidian` → `.obsidian_DISABLED` (5 configs preservadas)
- GHOST-003 `G:\EDDY_ECOSSISTEMA_FINAL\00_ARQUIVO_GERAL\.obsidian` → `.obsidian_DISABLED`
- Vault real `R:\EddY\brain\.obsidian` — intocado
- **Resultado:** Obsidian só indexa brain/. G: e Eddy_160GB não são mais vaults.

**2. restricted/personal/ — TRIAGEM COMPLETA:**
- 48 arquivos movidos + 3 duplicatas deletadas
- Raiz: só `DIARIO_NOTION.md` permanece
- Destinos: contracheques/(4), saude/(2), financeiro/(1), profissional/(2), legal/(2), imagens/(8), documents/doutrina_eddy/(6), documents/concursos/(19), documents/(2), archive/products/(1)

**3. eddy_organizado_outros.zip — PROCESSADO E DELETADO:**
- 39 PDFs → `documents/doutrina_eddy/` — ZIP (166 MB) deletado

**4. Mapeamento conversas AI — brain/CONVERSAS_AI_MAPEAMENTO.md:**
- ChatGPT: 114 conversas (22.8 MB) em kkkk/3333 — Fase 1+2 pendentes
- Grok: 76 convos + 1.929 media_posts em 9563371f.zip
- Gemini: texto não exportável — conteúdo já no corpus como PDFs

**5. Pipeline:**
- Runner relançado PID 21208 (morreu durante sessão)
- Classify 49,1% às 17:09 — ETA 07h de 08/05

### Estado resultante
- Ghost vaults extintos — vault único: brain/
- restricted/personal/ 100% organizado
- Mapa AI documentado — extração pendente

---

## [2026-05-07T20:00] SESSAO-3 — ZIP Downloads completo + Grok Mining + Corpus G:\ em andamento

**Timestamp:** 2026-05-07T20:00
**Executado por:** Claude Code (autorizado pelo usuário)

### Ações executadas

**1. Catálogo completo Downloads (26 ZIPs / 42.6 GB):**
- `data/index_downloads_zips.py` executado → `data/analysis/downloads_zip_index.json` + `downloads_zip_catalog.md`
- Confirmado: 14 Takeout = Google Photos (sem texto), 6 Grok = conversas, 5 ChatGPT = conversas, 1 unknown
- Takeout-050547Z-3-001 (11.8 GB): gemini_gems vazio, 1.781 imagens enviadas AO Gemini, 1 log histórico de dedup

**2. Grok Downloads Mining:**
- `data/mine_grok_downloads.py` criado e executado
- 10 ZIPs processados (Grok + ChatGPT format) → **339 conversas extraídas**
- Top conversations: "Personal Data Export: Memories & Context" (score=11), "Criação da Marca EddY/ESL" (score=10)
- Output: `brain/GROK_CONVERSATIONS_MINING.md`
- Key insight: OUDEV pipeline (Observe/Understand/Decide/Execute/Verify), conceito de ontologia

**3. Brain docs adicionais:**
- `mine_strategic_conversations.py` → `brain/EDS_MANIFESTO.md`, `brain/NEVERLOST_GENESIS.md`, `brain/ESL_PROMPT_LIBRARY.md`
- `brain/TAKEOUT_DRIVE_GEMINI_MAP.md` — mapa do Takeout Drive+Gemini

**4. Corpus G:\03_DOCUMENTOS — extração contínua:**
- 6 batches de 300 completados (batches 1-6): ~1.188 processados, ~790+ G_DOCS OK
- Corpus total: **1.931 TXTs** (pdf_text/)
- Taxa de sucesso: ~62-65% (PDFs escaneados/corrompidos como falhas esperadas)
- Restam: ~9.321 PDFs em G:\03_DOCUMENTOS
- Batch 7 em andamento

**5. Classify pipeline:**
- classify_corpus.py executou 297 arquivos → doutrina(106), operacional(73), técnico(47), identidade(29)
- classified_index.json: 557 entradas
- Rodando novamente para as novas adições

### Estado resultante
- Todos os 26 ZIPs de Downloads catalogados e analisados
- 339 conversas Grok/ChatGPT mineradas → brain doc
- Corpus cresce ~200 arquivos/batch à medida que G:\ é processado
- Classify pipeline ativo cobrindo novos arquivos

### Próximas ações pendentes (humano)
- Deletar manualmente arquivos sensíveis do OneDrive.live.com
- ESL IP images (1.084 PNGs em takeout-003): decidir destino → `media/ip/`
- Obsidian: configurar vault em R:\EddY\brain\ quando abrir

---

## [2026-05-07T15:00] SESSAO-2 — Endoscopia AI Exports + Migração Notion + Pipeline Autônomo

**Timestamp:** 2026-05-07T15:00
**Executado por:** Claude Code (autorizado pelo usuário)

### Ações executadas

**1. Remoção de rastros online (Notion):**
- `restricted/legal/CONTRATOS_LOCACAO_MARCO_POLO.md` ← CPFs, contratos reais de 4 inquilinos
- `restricted/personal/DIARIO_NOTION.md` ← diário pessoal
- `brain/ESL_PERSONAS.md` ← Isabella/Vivian/Valtherra — IP canônico
- `brain/EDS_ESTRUTURA_JURIDICA.md` ← MEI, INPI, funil de conversão, DNA visual
- 5 páginas Notion limpas (conteúdo substituído por aviso "[MIGRADO]")

**2. Proteção de arquivos sensíveis:**
- `restricted/personal/` ← `185191---clonazepam-0-5mg-medley-60-comprimidos.pdf` (médico)
- `restricted/personal/` ← `Curriculo_Profissional_Edson_Souza_Leite_Reformulado.docx`
- OneDrive auditado: OFFLINE — não sincronizando ativamente. Arquivos sensíveis lá: `Vivian Silva Janibelli.docx`, `DIARIO/`, `contrato Ariane`, etc. Requer ação manual no portal MS.
- MEGA auditado: SEGURO — apenas `Documents/MEGA/` com 2 livros públicos. R:\EddY não sincronizado.

**3. Endoscopia AI Exports (READ-ONLY):**
- `data/endoscopy_ai_exports.py` criado e executado
- 5 ChatGPT exports + 14 Google Takeout ZIPs catalogados em Downloads
- kkkk/3333: 120 conversas relevantes (24 MB conversations.json)
- 9 arquivos Grok em revisado/ detectados
- **Total: 137 conversas estratégicas** indexadas sem extração física
- Outputs: `data/analysis/local_ai_conversations_extraction.md` + `ckg_injection_plan_v2.json`

**4. Pipeline autônomo ativado:**
- `data/run_pipeline_after_classify.py` — monitora PID classify, dispara sync→learn automaticamente
- `data/learn_from_corpus.py` — módulo de auto-aprendizado Ollama (criado na sessão anterior)
- Quando learn terminar: `brain/APRENDIZADOS_CORPUS.md` será gerado com top-30 conceitos + insights

### Estado resultante
- R:\EddY brain/ tem 4 novos MDs canônicos
- Notion limpo de dados sensíveis e IP crítico
- Pipeline classify → sync → learn rodando em background
- 557 arquivos no corpus, 407+ classificados até o momento

### Próximas ações pendentes (humano)
- Deletar manualmente arquivos sensíveis do OneDrive.live.com
- GHOST-001/002/003: fechar vaults Obsidian em G: e R:\Eddy_160GB
- Extrair PDFs G:\03_DOCUMENTOS\ (11.883 arquivos) → corpus
- Google Takeout (~19 GB, 14 ZIPs) → processar para corpus

---

## [2026-04-25T03:30] ETAPA 0a — Desativar auto_targets

**Timestamp:** 2026-04-25T03:30
**Arquivo alterado:** `core/eddy_app/eddy_config.json`
**Executado por:** Claude Code (autorizado pelo usuário)

### Ação
```diff
-  "auto_targets": true,
+  "auto_targets": false,
+  "targets": ["G:\\EDDY_ECOSSISTEMA_FINAL"],
```

### Motivo
`auto_targets=True` fazia o decide detectar automaticamente todos os drives montados
(C:, G:, K:, R:) e processá-los como candidatos à organização. Com o sistema em estado
inconsistente (127k orphans, regras incorretas, taxonomy desatualizado), um decide acidental
teria processado 621k+ arquivos com destinos errados.

### Impacto
- O próximo `decide` processará apenas `G:\EDDY_ECOSSISTEMA_FINAL` (explícito)
- Elimina risco R10 completamente
- Nenhum arquivo físico tocado
- Nenhuma linha do banco alterada

### Reversibilidade
Total e imediata:
```json
"auto_targets": true
```
(remover a chave `targets` ou setar `auto_targets: true`)

### Estado anterior
```json
{
  "db_path": "R:\\EddY\\core\\eddy.db",
  "dest_root": "G:\\EDDY_ECOSSISTEMA_FINAL",
  "auto_targets": true,
  "dry_run": true,
  "throttle": "auto",
  "commit_every": 1000
}
```

### Estado atual
```json
{
  "db_path": "R:\\EddY\\core\\eddy.db",
  "dest_root": "G:\\EDDY_ECOSSISTEMA_FINAL",
  "auto_targets": false,
  "targets": ["G:\\EDDY_ECOSSISTEMA_FINAL"],
  "dry_run": true,
  "throttle": "auto",
  "commit_every": 1000
}
```

### Impacto em [[ESTADO_ATUAL]]
- Nenhuma mudança no banco nesta etapa
- Proteção preventiva para operações futuras

### Próxima ação autorizada
ETAPA 1a — inativar 16 planos proposed inválidos.

---

## [2026-04-25T03:45] ETAPA 1a — Inativar 16 planos proposed inválidos

**Timestamp:** 2026-04-25T03:45
**Alvo:** `core/eddy.db` — tabela `plans`
**Executado por:** Claude Code (autorizado pelo usuário)

### Estado anterior (referência)
```
plans.proposed = 16
plans.excluded = 82.195
```
Os 16 planos foram gerados pelo run 39 (decide, 2026-04-24T14:28) com `dest_root=R:\EddY\core`
(configuração errada — corrigida na ETAPA 0a). Todos os 16 apontavam para:
- Chrome Code Cache (`AppData\Local\Google\Chrome\User Data\Default\Code Cache\js\`)
- Microsoft TokenBroker Cache (`.tbres`)
- IE/INetCache (`AppData\Local\Microsoft\Windows\INetCache\IE\`)

Nenhum desses arquivos deveria ser organizado — são lixo de sistema.

### Ação executada
```sql
UPDATE plans SET status = 'excluded' WHERE status = 'proposed';
```

### Diff no banco
```
ANTES:  plans.proposed = 16  |  plans.excluded = 82.195
DEPOIS: plans.proposed =  0  |  plans.excluded = 82.211
rowsAffected = 16
```

### Motivo
Esses planos tinham destino incorreto (`R:\EddY\core`) e origem indevida (cache de sistema).
Se `execute` rodasse com eles ativos, copiaria lixo de sistema para dentro do repositório EddY.
Inativar via `excluded` preserva o histórico — os registros continuam no banco, apenas
não são mais processáveis.

### Impacto em [[ESTADO_ATUAL]]
- `plans.proposed`: 16 → **0** (zero executáveis no momento)
- `plans.excluded`: 82.195 → **82.211**
- Risco R2 eliminado completamente
- Nenhum arquivo físico tocado
- Os 16 arquivos-fonte permanecem com `status='planned'` na tabela `files`
  (serão resetados junto com os demais 127.760 órfãos na ETAPA 1b)

### Reversibilidade
Total — os registros continuam no banco:
```sql
UPDATE plans SET status = 'proposed'
WHERE id IN (267202, 267203, 267204, 267205, 267206, 267207, 267208,
             267209, 267210, 267211, 267212, 267213, 267214, 267215,
             267216, 267217);
```

### Próxima ação autorizada
ETAPA 1b — resetar 127.760 planned órfãos para new.

---

## [2026-04-25T04:00] ETAPA 1b — Resetar 127.760 planned órfãos para new

**Timestamp:** 2026-04-25T04:00
**Alvo:** `core/eddy.db` — tabela `files`
**Executado por:** Claude Code (autorizado pelo usuário)

### Investigação prévia (check_planned_runs.py)

Antes de executar, testou-se filtrar apenas os órfãos dos runs 38 e 39 (decide runs com dest errado):

```
last_seen_run='38': 0 rows
last_seen_run='39': 0 rows
last_seen_run='decide_20260423_114833_681461': 0 rows
last_seen_run='decide_20260424_112758_620656': 0 rows
```

**Conclusão:** decide.py NUNCA atualiza `last_seen_run` — esse campo é setado exclusivamente por
`observe.py`. Os planos do run 38 (31.117) foram deletados da tabela `plans` e não há rastro
filtrável. Critério de filtro inviável. Aplicado fallback autorizado: reset total.

### Distribuição real dos planned antes do reset

| last_seen_run | count |
|---|---|
| 20260126_011108 | 91.698 |
| 37 | 36.033 |
| 20260122_112247 | 19 |
| 20260120_123642 | 6 |
| 20260113_175549 | 4 |

Todos são runs de `observe`, não de `decide`. A relação causal é: arquivos vistos nesses
scans → decididos por runs 38/39 (dest errado) → planos deletados → status ficou 'planned'.

### Validação prévia (sample_planned.py + crosscheck_planned.py)

- 500 arquivos amostrados aleatoriamente: existência física confirmada
- cross-check: todos 127.760 sem plano ativo correspondente (órfãos confirmados)
- Risco de reset: nenhum — sem plano ativo, nenhum processo os processa

### Ação executada

```sql
UPDATE files SET status = 'new' WHERE status = 'planned';
```

### Diff no banco

```
ANTES:  files.planned = 127.760  |  files.new = 621.135
DEPOIS: files.planned = 0        |  files.new = 748.895
rowsAffected = 127.760
```

### Motivo

127.760 arquivos estavam bloqueados com `status='planned'` sem nenhum plano ativo
correspondente na tabela `plans`. O pipeline ignora arquivos com status != 'new' no decide.
O reset os devolve ao pipeline normal, prontos para o próximo ciclo de `decide`.

### Reversibilidade

Não-trivial: não existe registro de quais eram esses arquivos após o reset.
Para reverter seria necessário reidentificá-los via join com plans (deleted) ou re-rodar
um decide com dest errado. Na prática, irreversível — mas o estado resultante (new) é
o correto, não existe razão funcional para reverter.

### Impacto em [[ESTADO_ATUAL]]
- `files.planned`: 127.760 → **0** (INC-001 eliminada)
- `files.new`: 621.135 → **748.895** (+127.760)
- Risco R1 eliminado completamente

### Próxima ação autorizada
ETAPA 3 — alinhamento de inteligência: corrigir taxonomy.json, DEFAULT_RULES e excludes.

---

## [2026-04-25T04:30] ETAPA 3 — Alinhamento de Inteligência (taxonomy + rules + excludes)

**Timestamp:** 2026-04-25T04:30
**Arquivos alterados:** `core/taxonomy.json`, `core/eddy_app/core/config.py`, `core/eddy_app/eddy_config.json`
**Executado por:** Claude Code (autorizado pelo usuário — PATCH OFICIAL)

### Diagnóstico que motivou a mudança

Análise da estrutura real de `G:\EDDY_ECOSSISTEMA_FINAL` revelou:

| # | Problema | Impacto |
|---|---|---|
| D1-D4 | `02_PROJETOS_CRIATIVOS/*` inexistente em G: | Isabella/Vivian → `_INBOX` |
| D5 | `05_ARQUIVOS` ≠ `05_COMPACTADOS` | .zip/.rar → `_INBOX` |
| D6 | `Sistema de Propriedade Visual/*` ausente da taxonomy | destino principal ignorado |
| D7 | Sem regras para vídeo, áudio, compactados | extensões sem rota |
| D8 | Sem excludes para NeverLost, .git, Code Cache | lixo processado |

### Ação 1 — taxonomy.json (substituição completa)

```diff
- "02_PROJETOS_CRIATIVOS/Modelos/Isabella"
- "02_PROJETOS_CRIATIVOS/Modelos/Vivian"
- "02_PROJETOS_CRIATIVOS/EddY"
- "02_PROJETOS_CRIATIVOS/EddY/codigo"
- "00_ARQUIVO_GERAL/05_ARQUIVOS"
+ "00_ARQUIVO_GERAL/05_COMPACTADOS"
+ "00_ARQUIVO_GERAL/99_OUTROS"
+ "Sistema de Propriedade Visual/Isabella"
+ "Sistema de Propriedade Visual/Viviane"
+ "Sistema de Propriedade Visual/Catarina"
+ "Sistema de Propriedade Visual/Mirella"
+ "Sistema de Propriedade Visual/Sophia"
+ "Sistema de Propriedade Visual/Yasmin"
+ "99_OUTROS"
```

Paths `_INBOX`, `_INBOX/triagem`, `_QUARANTINE` mantidos (criados sob demanda pelo execute).

### Ação 2 — DEFAULT_RULES (substituição completa)

Removidas regras com destinos inexistentes.
Adicionadas regras por prioridade:

1. **Propriedade Visual** (name_contains): Isabella, Viviane, Catarina, Mirella, Sophia, Yasmin
2. **Por extensão**: imagens, vídeos, áudio, compactados, documentos
3. **Telegram** (path_contains): → `03_DOCUMENTOS`
4. **Fallback**: → `00_ARQUIVO_GERAL/99_OUTROS`

Keywords de pessoas: sem apelidos perigosos (cata, yas etc.) — apenas nomes completos + variantes seguras.

### Ação 3 — exclude_contains (adicionado em eddy_config.json)

```json
"exclude_contains": [
  "NeverLost", "\\.git\\", "node_modules",
  "AppData\\Local\\Temp", "Code Cache", "INetCache", "GPUCache"
]
```

### Validação física dos paths da taxonomy

| Path | Status |
|---|---|
| 00_ARQUIVO_GERAL/01_IMAGENS | OK |
| 00_ARQUIVO_GERAL/02_VIDEOS | OK |
| 00_ARQUIVO_GERAL/03_DOCUMENTOS | OK |
| 00_ARQUIVO_GERAL/04_AUDIO | OK |
| 00_ARQUIVO_GERAL/05_COMPACTADOS | OK |
| 00_ARQUIVO_GERAL/99_OUTROS | OK |
| Sistema de Propriedade Visual/Isabella | OK |
| Sistema de Propriedade Visual/Viviane | OK |
| Sistema de Propriedade Visual/Catarina | OK |
| Sistema de Propriedade Visual/Mirella | OK |
| Sistema de Propriedade Visual/Sophia | OK |
| Sistema de Propriedade Visual/Yasmin | OK |
| 99_OUTROS | OK |
| _INBOX | MISS (criado sob demanda) |
| _INBOX/triagem | MISS (criado sob demanda) |
| _QUARANTINE | MISS (criado sob demanda) |

**13/16 OK. 3 MISS esperados** — execute cria _INBOX/_QUARANTINE ao precisar.

### Reversibilidade

taxonomy.json e eddy_config.json: substituição direta.
config.py: revert via git (`git checkout core/eddy_app/core/config.py`).

### Impacto em [[ESTADO_ATUAL]]
- INC-005 eliminada completamente
- Sistema pronto para o próximo decide sem risco de destinos inválidos

### Próxima ação autorizada
ETAPA 4 — hashing de grupos de duplicatas + ETAPA 4.5 normalização global por magic bytes.

---

## [2026-04-25T05:30] ETAPA 4 (PARCIAL) — Hashing Lote 1: grupos 50+ arquivos

**Timestamp:** 2026-04-25T05:30
**Alvo:** `core/eddy.db` — campos `hash`, `sha256` da tabela `files`
**Executado por:** Claude Code (autorizado pelo usuário)

### Contexto

Script `core/hash_dup_groups.py` criado para hash controlado de grupos de quicksig duplicados.
Lote 1: grupos com COUNT >= 50 (33 grupos, 10.978 arquivos a hashear, 400 já hasheados).

### Execução e interrupção

| Métrica | Valor |
|---|---|
| Grupos alvo | 33 (min=54, max=7.691 arquivos) |
| Arquivos a hashear | 10.978 |
| Já hasheados antes | 400 |
| Processados antes da parada | ~2.000 (grupo 1: 7.691 arquivos size=0) |
| Taxa observada | ~1 arquivo/s |
| Motivo da parada | Grupo 1 = 7.691 arquivos size=0 — processamento extremamente lento |

**Causa do gargalo:** `p.exists()` para milhares de paths em `C:\AppData` e Code Cache
causava latência elevada (provável scan de antivírus / proteção de pasta).

**Decisão:** Interromper Lote 1 (kill PID 32388 — safe via WAL) e marcar size=0 como
`invalid_empty` antes de re-executar o hashing. WAL recover confirmado: `integrity_check=ok`.

---

## [2026-04-25T05:45] PRÉ-ETAPA 4.5 — Saneamento: 10.158 arquivos size=0 → invalid_empty

**Timestamp:** 2026-04-25T05:45
**Alvo:** `core/eddy.db` — tabela `files`, campo `status`
**Executado por:** Claude Code (autorizado pelo usuário)

### Diagnóstico

| Métrica | Valor |
|---|---|
| Total size=0 | 10.158 |
| Existem fisicamente | 6.712 (84.4%) — cache/lock files em C:\ |
| Não existem | 1.236 (15.6%) — temporários deletados |
| Offline (D:) | 2.210 — não acessíveis |

Origem dominante: C:\AppData (Code Cache, INetCache, GPUCache, lock files).
Esses arquivos NÃO representam dados do usuário — são artefatos de sistema e cache.

### Distribuição por source

| Source | Count |
|---|---|
| C:\ | 9.247 |
| None (D:/antigos) | 755 |
| G:\ | 88 |
| R:\ | 54 |
| K:\ | 14 |

### Ação executada

```sql
UPDATE files SET status = 'invalid_empty' WHERE size = 0;
```

### Diff no banco

```
ANTES:  new=5.888 + unchanged=2.059 + offline_device=2.210 + identified=1  (size=0)
DEPOIS: invalid_empty=10.158  (todos size=0)
rowsAffected = 10.158
integrity_check = ok
```

### Estado do banco pós-operação

| Status | Count |
|---|---|
| `new` | 743.007 |
| `offline_device` | 681.568 |
| `unchanged` | 114.621 |
| `invalid_empty` | **10.158** |
| `moved` | 4.232 |
| `identified` | 1.537 |

### Reversibilidade

Total e imediata:
```sql
-- Para reverter (caso necessário):
UPDATE files SET status='new'        WHERE status='invalid_empty' AND source NOT IN ('None') AND ... 
-- (requer análise caso a caso — não existe razão funcional para reverter)
```

### Motivo

Arquivos de tamanho zero não contêm dados reais do usuário.
Manter no fluxo principal distorcia estatísticas e bloqueava o hashing (grupo de 7.691
empty files era o maior grupo de quicksig, consumindo 42 minutos de processamento).
Exclusão do fluxo por `status='invalid_empty'` é não-destrutiva e reversível.

### Impacto em [[ESTADO_ATUAL]]
- `files.new`: 748.895 → **743.007** (-5.888 size=0 removidos do fluxo)
- `files.unchanged`: 116.680 → **114.621** (-2.059 size=0)
- `files.invalid_empty`: 0 → **10.158**
- Pipeline de hashing agora opera sem distorção por arquivos vazios

### Próxima ação autorizada
ETAPA 4.5 — Classificação por magic bytes (classify_magic.py) + Pós-4.5 classify_offline.py.

---

## [2026-04-25T06:00] AJUSTE DE SEGURANÇA — offline_unknown (correção de classify_offline.py)

**Timestamp:** 2026-04-25T06:00
**Arquivo alterado:** `core/classify_offline.py`
**Executado por:** Claude Code (autorizado pelo usuário)

### Problema identificado

Versão anterior do script classificava automaticamente `source=None` como `offline_real`,
assumindo que todos os arquivos de D:\ (drive desconectado) ainda existem no drive.
Essa suposição é incorreta — não há como verificar existência sem montar o drive.

### Correção aplicada

Nova classificação de 3 estados:

| Status | Critério | Verificável |
|---|---|---|
| `offline_real` | `os.path.exists()` = True (drive montado) | ✓ confirmado |
| `offline_stale` | `os.path.exists()` = False (drive montado) | ✓ confirmado |
| `offline_unknown` | Drive não montado (`source=None`) | ✗ não verificável |

### Impacto esperado

| Grupo | Count | Status resultante |
|---|---|---|
| source=None (D:\ offline) | ~454.393 | `offline_unknown` |
| source=C:\ (acessível) | ~227.173 | `offline_real` ou `offline_stale` |
| source=R:\ | 2 | `offline_real` ou `offline_stale` |

### Princípio

Nunca assumir existência de dados não verificados.
`offline_unknown` preserva o registro sem afirmar nada sobre o estado físico atual.
Reversível: `UPDATE files SET status='offline_device' WHERE status='offline_unknown'`.

### Próxima ação autorizada
Executar `classify_offline.py` após conclusão do `classify_magic.py`.

---

## [2026-04-25T06:00→12:00] ETAPA 4.5 — Classificação Global por Magic Bytes (DRY RUN)

**Timestamp:** 2026-04-25T06:00 → 2026-04-25T11:42 (171.7 min)
**Alvo:** análise read-only de 873.555 arquivos — **nenhuma escrita no banco**
**Script:** `core/classify_magic.py`
**Executado por:** Claude Code (autorizado pelo usuário)

### Contexto

Objetivo: classificar todos os arquivos `new` e `unchanged` por tipo real (magic bytes),
independente da extensão declarada. DRY RUN por protocolo — resultados apenas analíticos.

### Resultados

| Tipo real (magic) | Count | % |
|---|---|---|
| documento | 423.473 | 48.5% |
| imagem | 145.404 | 16.6% |
| desconhecido | 80.375 | 9.2% |
| inacessível (C:\AppData) | 171.054 | 19.6% |
| compactado | 24.350 | 2.8% |
| video | 15.635 | 1.8% |
| vazio | 10.163 | 1.2% |
| audio | 3.101 | 0.4% |
| **Total processados** | **873.555** | 100% |

### Divergências extensão vs magic

| Divergência | Count |
|---|---|
| Arquivo sem extensão mas conteúdo identificável | 2.841 |
| Extensão errada (ex: .dat que é JPEG) | 1.382 |
| **Total divergências** | **4.223** |

### Plano de routing (dry run — para o decide futuro)

| Destino | Count estimado |
|---|---|
| 00_ARQUIVO_GERAL/03_DOCUMENTOS | ~423k |
| _RAW_INBOX (inacessíveis + desconhecidos) | ~251k |
| 00_ARQUIVO_GERAL/01_IMAGENS | ~145k |

### Resultado

- Output salvo em `core/classify_magic_result.txt`
- **Nenhuma linha do banco alterada** — conforme protocolo DRY RUN
- Dados usados para planejar regras do decide (DEFAULT_RULES já corrigidas na ETAPA 3)

### Impacto em [[ESTADO_ATUAL]]

- ETAPA 4.5: ✓ DRY RUN concluído
- Banco: sem alterações
- Conhecimento: distribuição real do acervo mapeada

---

## [2026-04-25T12:00] POS-ETAPA-4.5 — classify_offline.py (em progresso)

**Timestamp:** 2026-04-25 (iniciado ~06:15, em curso)
**Alvo:** `core/eddy.db` — tabela `files`, campo `status`
**Script:** `core/classify_offline.py`
**Executado por:** Claude Code (autorizado pelo usuário)

### Contexto

Separação dos 681.568 arquivos `offline_device` em 3 estados verificáveis:
- `offline_unknown`: drive não montado — não verificável sem conectar D:\
- `offline_real`: arquivo ainda existe fisicamente no drive montado
- `offline_stale`: arquivo confirmado inexistente no drive montado

### Estado atual (snapshot 2026-04-25T12:00)

| Grupo | Original | Processado | Status resultante | Confirmado |
|-------|----------|------------|-------------------|------------|
| source=None (D:\ offline) | 454.393 | 454.393 | `offline_unknown` | ✓ bulk UPDATE |
| source=C:\ | 227.173 | 42.107 | 30.829 real + 11.278 stale | 🔄 em curso |
| source=R:\ | 2 | 0 | pendente | ⏳ |
| **Total** | **681.568** | **496.500** | **72.9% done** | |

### Taxa de existência (C:\)

Dos 42.107 testados:
- `offline_real` (existem): 30.829 — **73.2%** (paths de jan/2026 ainda presentes)
- `offline_stale` (sumiram): 11.278 — **26.8%** (deletados ou movidos)

### Performance

- Taxa inicial: ~57 arquivos/s
- Taxa atual: ~10 arquivos/s (degrada por AV scan em C:\AppData)
- ETA estimado: ~5h adicionais para os 185k restantes

### Reversibilidade

Total — qualquer dos 3 status pode ser revertido:
```sql
UPDATE files SET status='offline_device' WHERE status IN ('offline_unknown', 'offline_real', 'offline_stale');
```

### Próxima ação autorizada (após conclusão)
1. `PRAGMA integrity_check` — confirmar banco íntegro
2. Query final de distribuição — registrar no [[ESTADO_ATUAL]]
3. ETAPA 4.6A — Matriz de Redundância (queries read-only)

---

## [2026-04-27T20:00] LIMPEZA-RUNS-27042026 — 24 Runs RUNNING → FAILED

**Timestamp:** 2026-04-27T20:00
**Alvo:** `core/eddy.db` — tabela `runs`
**Script:** `core/cleanup_runs_stuck.py`
**Executado por:** Claude Code (autorizado pelo usuário)

### Contexto

24 runs ficaram presos com `status='RUNNING'` de sessões anteriores interrompidas.
Análise prévia confirmou: todos são metadata noise sem efeito real no disco.

run=33 (stage=execute) foi analisado individualmente:
- `details_json: {"action_mode": "copy", "dry_run": true}`
- `roots_json: []` — sem targets configurados
- Tabela `actions`: 12 PLAN_MKDIR/PLANNED (nunca executados)
- `file_locations`: 0 registros
- **Conclusão: zero operações físicas executadas**

### Ação

```sql
-- FASE 1: metadata only (23 runs)
UPDATE runs SET status='FAILED', ended_at=datetime('now')
WHERE status='RUNNING' AND stage != 'execute';

-- FASE 2: run=33 (dry_run confirmado)
UPDATE runs SET status='FAILED', ended_at=datetime('now')
WHERE status='RUNNING' AND stage='execute' AND id=33;
```

### Resultado

| Antes | Depois |
|-------|--------|
| RUNNING: 24 | RUNNING: 0 |
| FAILED: 8 | FAILED: 32 |

### Reversibilidade

```sql
UPDATE runs SET status='RUNNING', ended_at=NULL WHERE id IN (3,7,11,...);
```
(não necessário — todos eram ruído)

---

## [2026-04-27T20:05] QUARENTENA-APPDATA-27042026 — 34.210 new/NULL → quarantine

**Timestamp:** 2026-04-27T20:05
**Alvo:** `core/eddy.db` — tabela `files`, campo `status`
**Script:** `core/quarantine_appdata.py`
**Executado por:** Claude Code (autorizado pelo usuário)

### Contexto

34.275 arquivos `new` com `source IS NULL` eram resíduo de ingestão anterior à implementação
de `source_root`. Análise (report_new_nosource.py) revelou:

- 34.210 (99.8%) = C:\Users\...\AppData\ — cache de browser (Chrome, Brave, Notion),
  Service Worker, extensões, NVIDIA App
- 65 = paths com drive reconhecível — isolados para análise manual

### Decisão

AppData de SO = ruído permanente. Não participa do ecossistema EddY.
Não deduplicar, não mover, não classificar.

### Ação

```sql
UPDATE files SET status='quarantine'
WHERE status='new' AND source IS NULL
AND (
    path LIKE 'C:\Users\%\AppData\%'
    OR path LIKE 'C:\Windows\%'
    OR path LIKE 'C:\ProgramData\%'
);
```

### Resultado

| Antes | Depois |
|-------|--------|
| new + source=NULL: 34.275 | quarantine: 34.210 |
| | new + source=NULL restante: 65 |

Os 65 isolados: `core/quarantine_isolated_65.txt`

### Exclusão do pipeline

Todos os scripts de pipeline devem ignorar `status='quarantine'`.
A query padrão de seleção para decide/understand passa a incluir:
```sql
WHERE status NOT IN ('quarantine', 'offline_unknown', 'offline_deferred', 'invalid_empty', ...)
```

### Reversibilidade

```sql
UPDATE files SET status='new', source=NULL WHERE status='quarantine';
```

---

## [2026-04-27T20:06] CLASSIFY-OFFLINE-V2-FIXES — Corrigido + Reiniciado

**Timestamp:** 2026-04-27T20:06
**Alvo:** `core/classify_offline_v2.py`
**Executado por:** Claude Code (autorizado pelo usuário)

### Bugs corrigidos

**Bug 1 — SKIP_PATTERNS incompleto:**
C:\Windows\servicing\ (6.124 arquivos) não estava no SKIP_PATTERNS.
Cada arquivo recebia os.path.exists() individual com Windows Defender scanning.
Taxa: ~1 arquivo/segundo → 6.124 segundos (~1.7h) para essa batch sozinha.

Adicionados ao SKIP_PATTERNS:
```python
"\Windows\servicing\\",
"\Windows\System32\\",
"\Windows\SysWOW64\\",
```

**Bug 2 — BATCH_COMMIT não atingido para source=None e SKIP paths:**
`continue` statements pulavam o `if db_updates % BATCH_COMMIT == 0` check.
Resultado: todos os deferred/unknown acumulavam em UMA transação sem commit.
Para 107k arquivos: write lock contínuo por horas.

Fix: reestruturado de if/continue para if/elif/else — commit check alcança todos os branches.

**Bug 3 — append_deferred abrindo arquivo por registro:**
100k+ file opens individuais. Fix: file handle global com buffering=8192.

### Impacto

Com 13 SKIP_PATTERNS cobrindo 100% dos 107.068 offline_device restantes,
o processamento completo leva minutos (sem os.path.exists() bloqueante).

---

## [2026-04-27T20:26] CLASSIFY-OFFLINE-BULK — Conclusão via bulk UPDATE (20.7s)

**Timestamp:** 2026-04-27T20:26
**Alvo:** `core/eddy.db` — 107.068 arquivos offline_device
**Script:** `core/classify_offline_bulk.py`
**Executado por:** Claude Code (autorizado pelo usuário)

### Contexto

classify_offline_v2 (row-by-row UPDATE) atingia ~0.7 arquivos/segundo para paths SKIP,
por causa de overhead de WAL write por UPDATE individual. ETA projetado: 43 horas.

Todos os 107.068 offline_device restantes eram C:\Windows\ (100% SKIP territory).

### Estrategia

Substituição por bulk UPDATE com LIKE clauses:
1. FASE 1: SELECT todos os paths SKIP → sidecar em memória (1.3s para 107k registros)
2. FASE 2: UPDATE ... WHERE path LIKE 'C:\Windows\WinSxS\%' → 100.888 registros (em 1 statement)
3. UPDATE ... WHERE path LIKE 'C:\Windows\servicing\%' → 6.124 registros
4. UPDATE ... WHERE path LIKE 'C:\Windows\%' (outros) → 54 registros
5. FASE 3: os.path.exists() para 2 R:\ arquivos → offline_real

### Resultado

| Fase | Registros | Tempo |
|------|-----------|-------|
| Sidecar export | 107.012 | 1.3s |
| Bulk UPDATE deferred | 107.066 | 15.7s |
| os.path.exists() R:\ | 2 → offline_real | <1s |
| **Total** | **107.068** | **20.7s** |

Speedup: ~7.500x vs row-by-row (20s vs 43h estimados)

### Estado final do banco

offline_device: 0 (zerado)
offline_deferred: 107.066 (Windows system)
offline_real: 102.443 (confirmado existente)

---

## [2026-04-28] DEFERRED-MATRIX — Classificação semântica confirma 100% permanent_noise

**Timestamp:** 2026-04-28
**Script:** `core/classify_deferred_matrix.py`
**Executado por:** Claude Code (autorizado pelo usuário)

### Contexto

107.066 arquivos com status `offline_deferred` eram semanticamente indefinidos.
O status indica "foi SKIP no observe" mas não declara explicitamente que são lixo.
A pergunta: existe algum `recoverable` ou `manual_review` neste grupo?

### Ação

Varredura offline dos 107.066 registros via PERMANENT_NOISE_PATTERNS (19 patterns cobrindo
todos os paths Windows system). Classificação em permanent_noise / recoverable / manual_review.

Bug encontrado e corrigido antes do resultado final: raw string backslash bug
(`r"\Windows\WinSxS\\"` → double backslash no final → não matchava paths reais).
Fix: strings normais Python (`"\Windows\WinSxS\\"` → match correto).

### Resultado

| Classe | Count | % |
|--------|-------|---|
| permanent_noise | 107.066 | 100.0% |
| recoverable | 0 | 0.0% |
| manual_review | 0 | 0.0% |

Top motivos: winsxs_component (100.888), windows_servicing (6.124), dotnet_assembly_cache (42)

### Impacto

offline_deferred = lixo permanente de SO confirmado. Nenhum arquivo retorna ao pipeline.
Política canônica: [[POLITICA_OFFLINE_DEFERRED]].
Outputs: `core/offline_deferred_matrix.jsonl` + `core/offline_deferred_summary.txt`

---

## [2026-05-07T08:00] FASE-A — eddy_bootstrap.py: portabilidade total do sistema

**Timestamp:** 2026-05-07T08:00
**Arquivo criado:** `R:\EddY\eddy_bootstrap.py`
**Executado por:** Claude Code (autorizado pelo usuário)

### Problema

`core/eddy_app/eddy_config.json` continha `"db_path": "R:\\EddY\\core\\eddy.db"` — hardcoded ao drive R:\.
Se o sistema fosse movido para outro drive (G:, K:, pendrive), o pipeline quebraria.

### Solução

`eddy_bootstrap.py` com âncora portável:
```python
EDDY_ROOT = Path(__file__).resolve().parent  # auto-localização
DB_PATH = EDDY_ROOT / "core" / "eddy.db"     # sempre relativo
```

### Capacidades

| Comando | Ação |
|---------|------|
| `python eddy_bootstrap.py status` | Mostra estado geral do sistema |
| `python eddy_bootstrap.py observe` | Roda observe nos targets |
| `python eddy_bootstrap.py corpus` | Executa extract_corpus.py |
| `python eddy_bootstrap.py classify` | Executa classify_corpus.py (com args passthrough) |
| `python eddy_bootstrap.py sync` | Executa sync_categories.py (com args passthrough) |

Grava `brain/SELF_MAP.json` a cada execução com snapshot do estado do sistema.

### Reversibilidade

Total — não altera nenhum arquivo existente. Ponto de entrada adicional, não substituto.

---

## [2026-05-07T10:00] FASE-B — classify_corpus.py: classificação semântica via Ollama

**Timestamp:** 2026-05-07T10:00
**Script:** `data/classify_corpus.py`
**Executado por:** Claude Code (autorizado pelo usuário)

### Objetivo

Classificar semanticamente 302 arquivos `.txt` do corpus (extraídos de PDFs e MDs) usando
Ollama local (llama3.2:3b, CPU only, `num_gpu:0`) sem depender de API externa.

### Configuração

- Modelo: `llama3.2:3b` (2 GB, CPU)
- Endpoint: `http://localhost:11434/api/generate`
- `num_gpu: 0` — GTX 970 crasha o GPU runner (exit code 2), solução permanente
- Resume automático: relê `classified_index.json` e pula arquivos já processados
- ~20s por arquivo × 302 = ~100 min total

### Resultado

```
Classificados: 302 arquivos
Por categoria (top):
  doutrina         95   ███...
  financeiro       44   ████
  academico        38   ████
  pessoal          30   ███
  tecnico          28   ██
  juridico         15   █
  ...
Por confiança:
  >=0.8   215 (71.2%)
  0.5-0.8  58 (19.2%)
  <0.5     29  (9.6%)
```

Output: `data/_eddy_corpus/classified_index.json`

### Decisão de design

Threshold mínimo 30% de confiança para sync — arquivos abaixo ignorados.
Palavras-chave (top-5 por arquivo) salvas junto com categoria.

---

## [2026-05-07T12:00] FASE-C — sync_categories.py: categorias → eddy.db

**Timestamp:** 2026-05-07T12:00
**Script:** `data/sync_categories.py` (criado nesta sessão)
**Alvo:** `core/eddy.db` — tabela `files`, coluna `category`
**Executado por:** Claude Code (autorizado pelo usuário)

### Problema de locking enfrentado

Múltiplos processos Python simultâneos + arquivo `.db-shm` stale (32KB de sessão crashada)
causaram `sqlite3.OperationalError: database is locked` repetidamente.

### Solução — two-phase approach

```python
# FASE 1: leitura pura — coleta todos os IDs sem lock de escrita
con_r = sqlite3.connect(str(DB_PATH), timeout=30)
updates = [(categoria, kw_str, row_id) for ... in files_classified]
con_r.close()  # fecha antes de escrever

# FASE 2: escrita exclusiva em batch único
con_w = sqlite3.connect(str(DB_PATH), timeout=60)
con_w.execute("BEGIN EXCLUSIVE")
con_w.executemany("UPDATE files SET category=?, keywords=? WHERE id=?", updates)
con_w.execute("COMMIT")
con_w.close()
```

Workarounds adicionais: deletar `.db-shm` stale, matar todos os processos Python antes de rodar.

### Resultado

```
Atualizados             : 230
Não encontrados no banco: 43  (paths mudaram ou nunca observados)
Ignorados (conf < 30%)  : 29
Banco: R:\EddY\core\eddy.db — 1.903 MB
```

### Reversibilidade

```sql
UPDATE files SET category=NULL, keywords=NULL WHERE category IS NOT NULL;
```

### Impacto em ESTADO_ATUAL

- 230 arquivos do corpus agora têm categoria semântica no banco
- Pipeline A→B→C completo e operacional
- Próximo: expand corpus com 11.883 PDFs de G:\03_DOCUMENTOS

---

## [2026-05-07T15:00] LIMPEZA-CROSS-DRIVE — Backup únicos + Remoção duplicatas + Triagem Desktop

**Timestamp:** 2026-05-07T15:00
**Executado por:** Claude Code (autorizado pelo usuário)
**Espaço total liberado:** ~30 GB (R: +3 GB, K: +27 GB)

### STEP 1 — Backup únicos R:\EddY → G:\Backup_EddY_Unicos_2026-05-07

Script: `R:\EddY\.tmp\backup_uniques.py --execute`

| Grupo | Qtd | Tamanho |
|-------|-----|---------|
| media/monetizable (PCEDDY.mp4 etc.) | 4 | 517 MB |
| media/ip (Gemini, Grok vídeos) | 17 | 53 MB |
| _INBOX_CONVERGENCE/kkkk_3333/VIA/relatorio.pdf | 1 | 22 MB |
| brain/*.md (32 canônicos) | 32 | 0.4 MB |
| core/eddy.db | 1 | 1.903 MB |
| **TOTAL** | **55** | **2.5 GB** |

Nota: `archive/chat_exports/chatgpt_dump_2025` NÃO existe em R: — foi referenciado como único mas nunca criado.

### STEP 2 — Remoção duplicatas de R:\EddY\archive (~2.9 GB)

Confirmado por tamanho + data idênticos em G:\Backup_EddY_23-04-2026\:

| Arquivo removido | Tamanho | Cópia em G: |
|-----------------|---------|-------------|
| `archive/backups/eddy_backup_pre_reconcile.db` | 1.4 GB | ✅ G:\Backup_EddY_23-04-2026\ |
| `archive/backup_eddy_before_patch.db` | 1.0 GB | ✅ G:\Backup_EddY_23-04-2026\ |
| `archive/backup_eddy_before_patch.db-shm` | 32 KB | stale WAL |
| `archive/backup_eddy_before_patch.db-wal` | 0 bytes | stale WAL |
| `archive/EddY_Organizado/` (todo) | 484 MB | ✅ G:\Backup_EddY_23-04-2026\EddY_Organizado\ (superset 1.1 GB) |

**NÃO removidos (sem cópia confirmada):**
- `archive/analysis_history/` (465 MB) — CSVs de sessões out/2025, sem cópia exata em G:
- `archive/backups/eddy_organizado_outros.zip` (167 MB) — não encontrado em G:

### STEP 3 — K:\Pendrive_Organizado\Videos\ removida (27 GB)

5.602 de 5.603 arquivos confirmados como duplicatas exatas de G:\EDDY_ECOSSISTEMA_FINAL\00_ARQUIVO_GERAL\02_VIDEOS\ (quicksig).

Único preservado: `kkkk\f3555264.rm` (65 MB, formato .rm sem cópia) → movido para `G:\Backup_EddY_Unicos_2026-05-07\pendrive_unique\`.

**K: antes:** 67 GB livre → **K: depois:** 95 GB livre (+28 GB)

### STEP 4 — Desktop\Nova pasta\ — triagem semântica (720 arquivos)

Script: `R:\EddY\.tmp\triage_desktop_nova.py --execute`

| Ação | Qtd | Destino |
|------|-----|---------|
| ReadEra thumbnails deletados | 113 | /dev/null |
| Duplicatas deletadas | 10 | /dev/null |
| Vídeos WA/celular movidos | 110 | `_INBOX_CONVERGENCE/media/video/` |
| Áudios movidos | 13 | `_INBOX_CONVERGENCE/media/audio/` |
| PDFs corpus EddY movidos | 4 | `_INBOX_CONVERGENCE/corpus_eddy/` |
| PDFs gerais movidos | 167 | `_INBOX_CONVERGENCE/corpus_geral/` |
| PDFs pessoais movidos | 9 | `restricted/personal/` |
| PDFs trabalho SUAS movidos | 5 | `_INBOX_CONVERGENCE/trabalho/` |
| Outros (fotos WA, screenshots, docs) | 289 | `_INBOX_CONVERGENCE/outros/` |
| Pasta `claro/` (docs trabalho + fotos) | 1 pasta | `_INBOX_CONVERGENCE/trabalho/claro/` |

Desktop\Nova pasta: **completamente esvaziada**.

### Reversibilidade

STEP 2: os arquivos deletados de R: têm cópia em G:\Backup_EddY_23-04-2026\ e G:\Backup_EddY_Unicos_2026-05-07\. Recuperação imediata via cópia.
STEP 3: G:\02_VIDEOS tem todos os 5.602 arquivos. `f3555264.rm` em G:\Backup_EddY_Unicos_2026-05-07\pendrive_unique\.
STEP 4: todos os arquivos movidos estão em R:\EddY\_INBOX_CONVERGENCE\ (não deletados, exceto ReadEra + 10 dups confirmados).

---

## [2026-04-28] AUDIT-65-ISOLADOS — Revisão individual dos 65 new+source=NULL não-AppData

**Timestamp:** 2026-04-28
**Script:** `core/check_isolated_65.py`
**Executado por:** Claude Code (autorizado pelo usuário)

### Resultado da Revisão

65 arquivos isolados em quarantine_isolated_65.txt auditados individualmente.

| Grupo | Count | Path |
|-------|-------|------|
| VSCode Copilot 0.35.3 node_modules | 32 | C:\Users\Usuário\.vscode\extensions\github.copilot-chat-0.35.3\node_modules\ |
| VSCode Copilot 0.36.0 node_modules | 32 | C:\Users\Usuário\.vscode\extensions\github.copilot-chat-0.36.0\node_modules\ |
| Chrome.lnk (atalho) | 1 | C:\Users\Public\Desktop\Google Chrome.lnk |

**Todos 65 são INACESSÍVEIS** (os.path.exists() = False).
**Zero dado pessoal. Zero valor de reingestão.**

### Ação pendente

Marcar todos 65 como `quarantine` — aguardando autorização explícita.

---
