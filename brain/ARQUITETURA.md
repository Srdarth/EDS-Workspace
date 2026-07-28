---
type: arquitetura
project: EddY
status: reference
phase: FASE_0
generated: 2026-04-25
tags: [reference, architecture, pipeline, canonical]---

# ARQUITETURA DO SISTEMA EDDY
**Gerado em:** 2026-04-25T03:00 (FASE 0 — Auto-consciência)
**Versão analisada:** codebase em R:\EddY\core\

Ver também: [[ESTADO_ATUAL]] | [[DECISOES]] | [[00_MAPA_DO_PROJETO]] | [[REGRAS]]

---

## 1. VISÃO GERAL

EddY é um Personal Digital Operating System (PDOS) offline. Seu objetivo é catalogar,
entender e organizar arquivos pessoais distribuídos em múltiplos drives sem depender
de nenhum serviço externo. Toda a inteligência e persistência são locais.

**Paradigma central:** o banco SQLite (`core/eddy.db`) é a única fonte de verdade.
Nenhuma ação física acontece sem antes ser registrada no banco.

---

## 2. PIPELINE DE ESTÁGIOS

```
OBSERVE → IDENTIFY → UNDERSTAND → DECIDE → EXECUTE
```

Cada estágio é independente, reversível e registrado na tabela `runs`.

### OBSERVE (`eddy_app/core/observe.py`)
**Responsabilidade:** varrer diretórios físicos e registrar arquivos no banco.

**Entradas:** lista de targets, lista de excludes, db_path
**Saídas:** registros na tabela `files` com status `new`, `unchanged` ou `moved`

**Algoritmo:**
1. Para cada arquivo encontrado: calcula `quicksig` (SHA1 dos primeiros 2MB + tamanho)
2. Se path já existe no banco → update (unchanged ou new se quicksig mudou)
3. Se quicksig bate com outro path → detecta `moved`
4. Se path é novo → INSERT com status `new`
5. Resume automático via tabela `scan_state` (retoma do último arquivo processado)

**Campos-chave produzidos:**
- `quicksig`: SHA1(primeiros 2MB) — identidade rápida por conteúdo
- `content_id`: "{size}:{quicksig}" — chave de deduplicação rápida
- `source`: drive raiz (ex: "G:\\")
- `mtime_ns`: timestamp de modificação em nanosegundos [BUG CORRIGIDO: overflow em NTFS]

**Bug corrigido (2026-04-24):** arquivos com mtime NTFS corrompido causavam OverflowError
ao inserir no SQLite. Fix: clamp de mtime_ns para o range INTEGER do SQLite (±2^63).

---

### IDENTIFY (`eddy_app/core/identify.py`)
**Responsabilidade:** enriquecer metadados — ler conteúdo, extrair texto, inferir contexto.

**Capacidades (dependências opcionais):**
- `PyPDF2`: extração de texto de PDFs (até 10 páginas / 2MB)
- `python-docx`: extração de texto de DOCX
- `PIL/Pillow`: leitura de EXIF de imagens

**Campos produzidos:**
- `kind`: imagem | video | documento | codigo | arquivo | outros
- `title`, `keywords`, `text_preview`
- `canonical_name`, `name_confidence`
- `content_date`: data extraída do conteúdo

**Status resultante:** `new` → `identified`

---

### UNDERSTAND (`eddy_app/core/understand.py`)
**Responsabilidade:** hashing completo (MD5 + SHA256) para deduplicação real.

**Classificação por extensão:**
```python
IMG_EXT  = {.jpg, .jpeg, .png, .webp, .bmp, .gif, .heic, .tiff}
VID_EXT  = {.mp4, .mov, .mkv, .avi, .wmv, .webm, .m4v}
DOC_EXT  = {.pdf, .doc, .docx, .ppt, .txt, .md, ...}
CODE_EXT = {.py, .js, .ts, .html, .json, .yml, ...}
ARC_EXT  = {.zip, .rar, .7z, .tar, .gz}
```

**Status resultante:** → `understood`
**Atenção:** runs 36 e 37 estão presos como RUNNING no banco — foram interrompidos.

---

### DECIDE (`eddy_app/core/decide.py`)
**Responsabilidade:** gerar planos de organização na tabela `plans`.

**Entradas:** arquivos com status `new`, `moved`, `unchanged`, `understood`, `identified`
**Saídas:** registros em `plans` com `status='proposed'`, arquivos com `status='planned'`

**Sistema de regras (`rules` em config.py):**
```
Tipo name_contains: se nome contém keyword → dest especificado
Tipo ext_in:        se extensão está na lista → dest especificado
Tipo kind_is:       se kind bate → dest especificado
Fallback:           dest_root / kind / filename
```

**Validação por whitelist (taxonomy.json):**
O destino calculado é verificado contra `taxonomy.json`. Se não estiver na whitelist,
cai no `_INBOX`.

**PROBLEMA CRÍTICO ATUAL:**
- Runs 38 e 39 rodaram com `dest_root=R:\EddY\core` (ERRADO — bug já corrigido no config)
- DEFAULT_RULES apontam para `02_PROJETOS_CRIATIVOS` que NÃO existe em G:\EDDY_ECOSSISTEMA_FINAL
- taxonomy.json inclui `02_PROJETOS_CRIATIVOS/Modelos/Isabella` e `/Vivian` — paths inexistentes

**Filtros automáticos do decide:**
- Extensões de sistema: .dll, .exe, .sys, .cat, .pak, .bin, .msi, .ocx, .mui, .manifest etc
- Path fragments: found.000, recup_dir, $recycle.bin, windowsapps

---

### EXECUTE (`eddy_app/core/execute.py`)
**Responsabilidade:** executar os planos propostos (copy ou move com verificação de hash).

**Modos:**
- `dry_run=True` (PADRÃO): registra intenções, não toca o disco
- `dry_run=False`: executa fisicamente com verificação MD5+SHA256 antes e depois

**Segurança do execute (modo real):**
1. Calcula MD5+SHA256 do arquivo fonte
2. Faz copy/move
3. Recalcula MD5+SHA256 do arquivo destino
4. Se hashes não batem → RuntimeError (arquivo não é removido)
5. Registro em `file_locations` e `content_index` para rastreabilidade
6. Geração de `undo_{run_key}.txt` com todos os destinos (reversibilidade)

**Deduplicação no execute:**
- Verifica `content_index` (SHA256) antes de copiar
- Se conteúdo idêntico já existe no destino → `skipped_duplicate`

---

## 3. SCHEMA DO BANCO (core/eddy.db)

### Tabela `files` (central)
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER PK | Autoincrement |
| path | TEXT UNIQUE | Caminho absoluto atual |
| organized_path | TEXT | Caminho pós-organização |
| size | INTEGER | Tamanho em bytes |
| mtime_ns | INTEGER | Modificação em nanosegundos [clampado] |
| ext / extension | TEXT | Extensão do arquivo |
| filename | TEXT | Nome do arquivo |
| quicksig | TEXT | SHA1(2MB) para deduplicação rápida |
| content_id | TEXT | "{size}:{quicksig}" |
| status | TEXT | new/unchanged/moved/identified/understood/planned/excluded/offline_device |
| kind | TEXT | imagem/video/documento/codigo/arquivo/outros |
| hash | TEXT | MD5 completo |
| sha256 | TEXT | SHA256 completo |
| duplicate_of | TEXT | Path do original (se duplicata) |
| source | TEXT | Drive raiz (ex: "G:\\") |
| first_seen / last_seen | TEXT | Timestamps ISO |
| canonical_name | TEXT | Nome sugerido pelo identify |
| title / keywords / text_preview | TEXT | Metadados de conteúdo |
| content_date | TEXT | Data extraída do conteúdo |

### Tabela `plans`
| Coluna | Descrição |
|--------|-----------|
| src_path | Origem |
| dest_path | Destino calculado |
| action | copy / move / quarantine |
| status | proposed / excluded / done_copy / done_move / failed / missing_src / skipped_* |
| run_id | Run que gerou o plano |

### Tabela `runs`
Histórico de todos os estágios executados (observe, identify, understand, decide, execute).
Status: RUNNING / COMPLETED / FAILED

### Tabelas auxiliares
- `scan_state`: resume de observe por target (last_path processado)
- `dir_state`: cache de diretórios por mtime (otimização)
- `source_profiles`: metadados por drive raiz
- `file_locations`: histórico de onde cada arquivo já esteve
- `content_index`: índice de conteúdo canônico por SHA256
- `actions`: log detalhado de cada ação do execute
- `errors`: erros capturados por stage/run

---

## 4. MÓDULOS DE SUPORTE

### `core/eddy_app/core/config.py`
- `load_config()`: mescla DEFAULT_CONFIG + targets.json + eddy_config.json
- `detect_targets()`: auto-detecta drives montados (política: users_only para C:)
- `save_config()`: persiste em eddy_app/eddy_config.json

### `core/eddy_app/core/db.py`
- `connect()`: abre conexão com WAL mode, probes de escrita, ensure_schema
- `ensure_schema()`: cria/migra todas as tabelas e índices
- `start_run()` / `finish_run()`: ciclo de vida de runs
- `insert_action()` / `update_action()`: log de ações do execute

### `core/eddy_app/core/utils.py`
- `should_exclude()`: filtra paths por tokens/fragmentos (case-insensitive, Windows-safe)
- `normalize_path()`: normalização lowercase para comparações no banco
- `safe_filename()`: sanitiza nomes para o sistema de arquivos
- `mark_excluded()`: UPDATE em massa no banco para paths excluídos

---

## 5. SCRIPTS DE ORQUESTRAÇÃO

| Script | Função |
|--------|--------|
| `core/run_audit.py` | Roda observe em R: → K: → C: → G: com resume |
| `core/monitor_audit.py` | Monitor em tempo real (status.json) |
| `core/run_pipeline.py` | Pipeline completo observe→decide→execute |
| `core/run_eddy_app.py` | Launcher da GUI Tkinter |
| `core/eddy.py` | Entry point CLI alternativo |
| `core/monitor.py` | Monitor genérico de runs |

### Scripts de diagnóstico/manutenção (core/)
| Script | Função |
|--------|--------|
| `analyze_pipeline.py` | Análise do estado do pipeline |
| `cleanup_db.py` | Limpeza de registros inválidos |
| `clean_plans.py` / `clean_proposed_plans.py` | Limpeza de planos |
| `check_plans_count.py` / `check_tables.py` | Verificação de integridade |
| `fix_run_id.py` | Correção de run_ids inconsistentes |
| `create_view.py` / `check_view.py` | Views de diagnóstico |
| `export_eddy_corpus.py` | Exporta corpus para análise |
| `scan_knowledge.py` / `search_knowledge.py` | Índice de conhecimento semântico |

### Scripts do Paciente 0 (concluído)
| Script | Função |
|--------|--------|
| `decide_paciente0.py` | Classificação semântica de R:\EddY\ |
| `verify_paciente0.py` | Verificação dos resultados |
| `create_paciente0_db.py` / `rebuild_paciente0_db.py` | Gestão do banco isolado |
| `run_claude_paciente0.py` | Integração com Claude API (classificação semântica) |
| `finalize_catalogar.py` / `list_catalogar.py` | Execução dos 21 arquivos CATALOGAR |

---

## 6. ARQUITETURA DE CONFIGURAÇÃO

```
load_config() mescla em ordem:
  1. DEFAULT_CONFIG (config.py) — valores padrão com ROOT_DIR relativo
  2. targets.json (ROOT_DIR/)   — targets e excludes explícitos
  3. eddy_app/eddy_config.json  — overrides do usuário
```

**PROBLEMA CRÍTICO (identificado 06/05/2026):**
`eddy_config.json` sobrescreve `db_path` com caminho absoluto hardcoded:
```json
"db_path": "R:\\EddY\\core\\eddy.db"  ← QUEBRA EM OUTRO DRIVE/MÁQUINA
```
`config.py` já usa `ROOT_DIR = Path(__file__).resolve().parents[2]` corretamente,
mas o JSON anula isso. **FASE A resolve este problema.**

**Configuração pós-FASE A (objetivo):**
```json
{
  "dest_root": "G:\\EDDY_ECOSSISTEMA_FINAL",
  "auto_targets": true,
  "dry_run": true,
  "action_mode": "copy",
  "plan_duplicates": false,
  "resume_scan": true
}
```
`db_path` removido do JSON → usa `ROOT_DIR / "eddy.db"` automaticamente (relativo).

**FASE A — Mudanças planejadas (06/05/2026):**
1. Remover `db_path` absoluto de `eddy_config.json`
2. Criar `eddy_bootstrap.py` na raiz de `R:\EddY\` — entry point portável
3. Bootstrap detecta seu próprio diretório, encontra drives, escreve `brain/SELF_MAP.json`
4. Todo caminho no sistema passa a ser relativo ao bootstrap

**Taxonomy (whitelist de destinos válidos) — `core/taxonomy.json`:**
```
00_ARQUIVO_GERAL/01_IMAGENS          ← existe em G:
00_ARQUIVO_GERAL/02_VIDEOS           ← existe em G:
00_ARQUIVO_GERAL/03_DOCUMENTOS       ← existe em G:
00_ARQUIVO_GERAL/04_AUDIO            ← existe em G:
00_ARQUIVO_GERAL/05_ARQUIVOS         ← existe em G:
02_PROJETOS_CRIATIVOS/Modelos/Isabella  ← NÃO existe em G: [RISCO]
02_PROJETOS_CRIATIVOS/Modelos/Vivian    ← NÃO existe em G: [RISCO]
02_PROJETOS_CRIATIVOS/EddY              ← NÃO existe em G: [RISCO]
_INBOX / _INBOX/triagem              ← fallback
_QUARANTINE                          ← quarentena
```

**AÇÃO NECESSÁRIA:** Corrigir taxonomy.json e DEFAULT_RULES para a estrutura real do G:.

---

## 7. FLUXO DE DEDUPLICAÇÃO

```
Nível 1 (OBSERVE):    quicksig = SHA1(primeiros 2MB) + size
                       → detecta moved, marca duplicate_of (parcial)

Nível 2 (UNDERSTAND): hash = MD5 completo
                       sha256 = SHA256 completo
                       → deduplicação confiável

Nível 3 (EXECUTE):    content_index (SHA256 → canonical_path)
                       → skipped_duplicate se cópia já existe no destino
```

**Estado atual:** 99%+ dos arquivos estão no Nível 1 apenas.
Apenas 10.630 de 1.555.123 arquivos têm hash completo (Nível 2).

---

## 8. INVARIANTES DO SISTEMA (nunca violar)

1. `dry_run=True` é o padrão — nunca setar False sem decisão explícita
2. Nenhum arquivo é deletado — execute usa copy por padrão, move só se explícito + hash confirmado
3. O banco é a fonte de verdade — não confiar em estado do filesystem sem consultar o banco
4. Reversibilidade — todo execute real gera `undo_{run_key}.txt`
5. Resume sempre — observe usa scan_state para retomar sem reprocessar
6. Paciente 0 isolado — eddy_paciente0.db não é modificado pelo pipeline global

---

## 9. DEPENDÊNCIAS EXTERNAS

| Dependência | Uso | Obrigatória? |
|-------------|-----|--------------|
| sqlite3 | Banco principal | Sim (stdlib) |
| pathlib | Manipulação de paths | Sim (stdlib) |
| hashlib | SHA1/MD5/SHA256 | Sim (stdlib) |
| PyPDF2 | Extração de texto PDF | Não |
| python-docx | Extração de texto DOCX | Não |
| Pillow | Leitura de EXIF | Não |
| tkinter | GUI | Não (stdlib, opcional) |

Sistema funciona 100% offline. Nenhuma dependência de rede.

---

*Documento gerado automaticamente pela FASE 0 do protocolo de auto-consciência EddY.*
*Próxima atualização: após mudanças estruturais no pipeline ou schema.*

