---
tipo: historico
criado_em: 2026-04-25
---

# CORPUS HISTÓRICO — EddY OS
## Linha do tempo e memória de longo prazo

Ver também: [[ESTADO_ATUAL]] | [[DECISOES]] | [[ARQUITETURA]] | [[00_MAPA_DO_PROJETO]]

> Registro permanente de marcos, descobertas e decisões de alto impacto.
> Ao contrário de [[DECISOES]] (técnico/operacional), este documento registra **o porquê histórico**:
> intenções, aprendizados e mudanças de paradigma.

---

## Linha do Tempo

### 2026-01-XX — Primeiros runs (era pre-estrutura)
- Primeiros observe no C:\ com estrutura diferente — paths agora inacessíveis
- Runs com IDs como `20260120_123642`, `20260122_112247`, `20260126_011108`
- ~127.760 arquivos ficaram com status `planned` sem plano correspondente (órfãos)
- Runs 36, 37 (understand) interrompidos — 165.504 `duplicate_of` parcialmente marcados

### 2026-04-18 a 2026-04-23 — EddY Pipeline (era estruturação)
- Runs 38, 39 (decide) rodaram com `dest_root=R:\EddY\core` (ERRADO — config incorreta)
- Planos gerados foram excluídos → logs em `brain/EddY_OS_Brain/ExportBlock*/EddY/...`
- Pipeline Log 2026-04-18 disponível na memória Notion exportada

### 2026-04-24T18:24 — Início Auditoria Global (era atual)
- Auditoria completa: R: → K: → C: → G: com run_audit.py
- Duração: ~7h40min (18:24 → 02:04)
- Descoberta: G:\ com 20 JPGs com mtime_ns corrompido (NTFS overflow) — fix aplicado em observe.py

### 2026-04-25T02:04 — Snapshot pós-auditoria
- 1.555.123 arquivos catalogados
- Descoberta: 44% duplicatas (174k grupos quicksig, 513k arquivos)
- Descoberta: 127.760 planned órfãos (INC-001)
- Descoberta: taxonomy.json apontava para paths inexistentes em G:\ (INC-005)
- Estado: ver [[ESTADO_ATUAL]]

### 2026-04-25T03:00 — FASE 0 Auto-consciência
- ARQUITETURA.md, ESTADO_ATUAL.md, DECISOES.md criados/reescritos
- Primeiro documento de auto-análise completo do sistema
- Separação definitiva: brain/ = Obsidian vault ativo | EddY_OS_Brain/ = legado Notion (ignorado)

### 2026-04-25T03:30 → 06:00 — Saneamento (ETAPAs 0a, 1a, 1b, 3, Pré-4.5)
- auto_targets desativado (risco eliminado)
- 16 planos errados → excluded
- 127.760 planned → new (INC-001 eliminada)
- taxonomy.json e DEFAULT_RULES corrigidos (INC-005 eliminada)
- 10.158 arquivos size=0 → invalid_empty

### 2026-04-25T06:00 → 12:00 — ETAPA 4.5 (classificação global por magic bytes)
- classify_magic.py: 873.555 arquivos em 171.7 min (DRY RUN — sem escrita no banco)
- Resultado: 423k documentos | 145k imagens | 80k desconhecidos | 24k compactados | 15k vídeos
- 19.6% inacessíveis (principalmente C:\AppData)
- 4.223 divergências entre magic type e extensão declarada
- DRY RUN: resultados em `core/classify_magic_result.txt` — nenhuma escrita no banco

### 2026-04-25 (em curso) — Pós-ETAPA 4.5 (classify_offline)
- classify_offline.py separando 681.568 `offline_device` em 3 categorias
- 454.393 source=None (D:\ offline) → `offline_unknown` (bulk, instantâneo)
- 227.175 source=C:\ → testados um a um via os.path.exists()
- Em andamento — ver [[ESTADO_ATUAL]] para progresso atual

---

## Decisões de Paradigma (não técnicas)

### "O banco é a única fonte de verdade"
Nenhuma ação física acontece sem registro no banco. Aprendizado de runs 38/39 (decide com config errada — se tivéssemos executado fisicamente, seria difícil reverter).

### "Nunca deletar — só skip_duplicate"
Mesmo arquivos confirmados como duplicados (SHA256) não são deletados. A decisão de deleção é exclusivamente humana.

### "D:\ offline é patrimônio, não lixo"
275k arquivos no D:\ desconectado são dados pessoais — não podem ser assumidos como inacessíveis permanentemente. Status `offline_unknown` preserva a informação sem afirmar destino.

### "dry_run=True é o padrão absoluto"
Nunca execute real sem autorização explícita. O custo de uma reversão é sempre maior que o custo de uma verificação.

---

## Conhecimento Acumulado (padrões observados)

### Sobre o acervo
- R:\Eddy_160GB\ contém principalmente exports do Telegram (513k+ .txt) + conteúdo criativo
- G:\ é o santuário — estrutura mais limpa e intencional
- C:\ tem camadas de runs antigos (jan/2026) sobrepostas com sistema atual
- D:\ é o drive que "sumiu" — 275k arquivos não acessíveis

### Sobre o pipeline
- quicksig falha em arquivos vazios (SHA1 de zero bytes → sempre igual)
- mtime_ns pode overflow em NTFS — já corrigido em observe.py com clamp 2^63
- Antivírus (Windows Defender) escaneia C:\AppData ao fazer os.path.exists() — degrada performance de 57/s para 10/s

### Sobre os dados
- 44% de duplicatas é principalmente R: vs G: (acervo criativo espelhado durante backup)
- 127k planned órfãos foram gerados quando runs 38/39 (decide) foram deletados sem resetar status
- 10.158 size=0 eram dominados por Code Cache do Chrome (C:\AppData)

---

*Atualizar com cada nova descoberta significativa.*
*Este documento é memória de longo prazo — não descreve estado momentâneo, descreve padrões.*
