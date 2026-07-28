# Arquitetura EDS-Workspace

## Visão geral

```
EDS-Workspace/
├── apps/
│   ├── neverlost-observer/    # Python — pipeline EddY (offline, Windows/WSL2)
│   │   ├── eddy_app/
│   │   │   └── core/          # 10 módulos: observe, understand, identify, decide, execute, verify, merge, db, config, utils
│   │   ├── main.py            # CLI: observe / understand / identify / decide / report
│   │   └── requirements.txt
│   │
│   └── neverlost-scanner/     # React/Vite — NeverLost Scanner Web
│       └── src/               # App.tsx implementa pipeline EddY completo no browser
│           # (Web Crypto SHA-1, regras DEFAULT_RULES portadas de config.py)
│
├── brain/                     # Vault de conhecimento (espelho do Obsidian)
│   └── *.md                   # 20 documentos canônicos
│
├── infra/
│   └── docker/
│       ├── docker-compose.yml # PostgreSQL + pgAdmin (análises pesadas)
│       └── init.sql           # Schema analítico (espelho do SQLite)
│
├── docs/                      # Documentação técnica
│   └── architecture.md        # Este arquivo
│
├── scanner.py                 # Scanner simples (legacy / demo rápido)
└── setup_desktop.sh           # Setup WSL2 para desenvolvimento local
```

---

## Pipeline EddY (Axiom Sovereign Engine)

```
╔══════════════════════════════════════════════════════════╗
║  EddY — Cognitive Protocol v4                            ║
║                                                          ║
║  [Observe] → [Understand] → [Identify] → [Decide]        ║
║       ↓                                       ↓          ║
║  [Verify]  ←  ←  ←  [Execute]  ←  ←  ←  ←  ←            ║
╚══════════════════════════════════════════════════════════╝
```

### Observe
- Varre diretórios via `os.walk`
- Calcula `quicksig` = SHA-1 de (size + primeiros 2 MB)
- Detecta new / moved / unchanged sem abrir o arquivo
- Resume via `scan_state` — retoma do último arquivo em caso de interrupção

### Understand
- Hash completo: MD5 + SHA256 para arquivos sem hash
- Detecta duplicatas reais: mesmo SHA256 + mesmo tamanho
- Respeita `hash_max_bytes` para arquivos grandes

### Identify
- Extrai texto e metadados de: PDF, DOCX, imagens (EXIF), texto plano
- Sugere nome canônico com score de confiança (0–100)
- Respeita `timebox` para não bloquear o pipeline

### Decide
- Aplica regras do `DEFAULT_RULES` (portado de `config.py`)
- Sistema de Propriedade Visual — personas têm prioridade sobre destino padrão
- Saída: tabela `plans` no SQLite com `src_path → dest_path`
- `dry_run=True` por padrão — nada é movido sem confirmação explícita

### Execute
- Copia ou move arquivos verificando hash antes e depois
- Gera `undo_{run_key}.txt` para rollback
- Aborta se hash de destino não bater

### Verify
- Verificação independente pós-execute
- Compara hash de origem com hash de destino para cada arquivo do plano

---

## Banco de dados

**SQLite** (`eddy.db`) — fonte de verdade canônica
- Portátil, offline, sem instalação
- WAL mode para concorrência
- Schema em `apps/neverlost-observer/eddy_app/core/db.py`

**PostgreSQL** (`infra/docker/docker-compose.yml`) — espelho analítico opcional
- Para consultas pesadas e dashboards
- Nunca usado como source of truth

---

## NeverLost Scanner Web

Implementação do pipeline EddY no browser via:
- **Web Crypto API** (SHA-1 para quicksig)
- **TypeScript** (rules engine portado de `config.py`)
- **Drag & drop** de múltiplos arquivos
- **Export HTML** — gera `mapa_do_caos_YYYYMMDD.html` idêntico ao Observer real

Localização: `artifacts/neverlost-scanner/` (Replit monorepo)

---

## Escala real (Fase H4, maio 2026)

| Drive | Arquivos | Tamanho |
|-------|----------|---------|
| R: | ~900k | ~500 GB |
| G: | ~300k | — |
| K: | ~200k | — |
| C: + D: | ~196k | ~1 TB |
| **Total** | **~1.596.493** | **~2 TB** |

Workspace principal: `D:\EDDY_ECOSSISTEMA_FINAL` (733 GB)
