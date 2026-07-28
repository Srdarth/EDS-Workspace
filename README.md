# EDS-Workspace

**EDS — Estúdio Digital Soberano**  
Sistema pessoal de soberania digital, organização de arquivos e produção criativa.

> "Você não perde arquivos. Você só ainda não os organizou."

---

## O que é este workspace

Este repositório contém todo o ecossistema EDS — a infraestrutura de código, documentação canônica (brain), e os produtos que nascem dele.

### Hierarquia de identidade

```
MooVeeL (umbrella criativo)
└── EDS — Estúdio Digital Soberano (holding)
    ├── ESL Exclusivity (IP criativo)
    │   └── Personas: Isabella · Viviane · Catarina · Mirella · Sophia · Yasmin
    └── NeverLost (produto público)
        └── EddY — Axiom Sovereign Engine (motor de organização)
```

---

## Estrutura do workspace

```
EDS-Workspace/
│
├── apps/
│   ├── neverlost-observer/   # 🐍 Python — pipeline EddY offline (Windows/WSL2)
│   └── neverlost-scanner/    # 🌐 Web — NeverLost Scanner no browser
│
├── brain/                    # 📚 Vault de conhecimento (20 documentos canônicos)
│
├── infra/
│   └── docker/               # 🐳 PostgreSQL para análises pesadas (opcional)
│
├── docs/                     # 📐 Documentação técnica
│
├── scanner.py                # Módulo básico de scan (legacy/demo)
└── setup_desktop.sh          # Setup WSL2 para desenvolvimento local
```

---

## Início rápido

### NeverLost Observer (Python, Windows/WSL2)

```bash
# Clone
git clone https://github.com/Srdarth/EDS-Workspace.git
cd EDS-Workspace

# Setup (WSL2) — ou execute setup_desktop.sh
pip install -r apps/neverlost-observer/requirements.txt

# Observar seus arquivos
python apps/neverlost-observer/main.py observe --targets /mnt/c/Users /mnt/d/

# Entender (calcular hashes, detectar duplicatas)
python apps/neverlost-observer/main.py understand

# Relatório
python apps/neverlost-observer/main.py report

# Plano de organização (dry-run — nada é movido)
python apps/neverlost-observer/main.py decide --dest /mnt/r/EddY_Organizado
```

### NeverLost Scanner (Web — zero instalação)

Acesse: **https://neverlost.replit.app** *(ou rode localmente no Replit)*

Arraste e solte seus arquivos — a análise acontece 100% no seu browser, sem upload.

---

## EddY — Pipeline de 6 etapas

| # | Etapa | O que faz |
|---|-------|-----------|
| 1 | **Observe** | Varre diretórios, calcula quicksig (SHA-1 parcial), detecta new/moved/unchanged |
| 2 | **Understand** | Hash completo (MD5 + SHA256), detecta duplicatas reais |
| 3 | **Identify** | Extrai conteúdo (PDF/DOCX/EXIF), sugere nomes canônicos |
| 4 | **Decide** | Aplica regras de taxonomia, gera plano (dry_run=True por padrão) |
| 5 | **Execute** | Move/copia com verificação de hash, gera undo log |
| 6 | **Verify** | Verificação independente pós-execução |

**Invariante absoluta:** nenhum arquivo é deletado. O sistema só copia/move com verificação.

---

## Brain

O diretório [`brain/`](brain/) contém a documentação canônica do projeto — um espelho do vault Obsidian localizado em `R:\EddY\brain\` (máquina local).

Documentos principais:
- [`00_INDEX_MESTRE.md`](brain/00_INDEX_MESTRE.md) — índice canônico
- [`ARQUITETURA.md`](brain/ARQUITETURA.md) — arquitetura técnica
- [`00_REGRAS_CANONICAS.md`](brain/00_REGRAS_CANONICAS.md) — regras do sistema
- [`DECISOES.md`](brain/DECISOES.md) — log de decisões arquiteturais
- [`EDDYSTATE_REPORT.md`](brain/EDDYSTATE_REPORT.md) — estado atual do sistema

---

## Escala atual (Fase H4, maio 2026)

- **~1.596.493 arquivos** catalogados
- **~2 TB** de dados mapeados (R: / G: / K: / C: / D:)
- **10 fases concluídas** (K → S3)
- **113 scripts ativos** no ecossistema
- **539+ outputs analíticos** gerados

---

## Segurança & privacidade

- Nenhum dado pessoal é armazenado neste repositório
- O `.gitignore` exclui: `*.db`, `*.sqlite`, `relatorio_*.html`, `venv/`, `.env`
- O NeverLost Scanner web não faz upload de nenhum arquivo
- O Observer Python roda 100% offline

---

## Licença

Código: MIT  
Conteúdo do Brain: propriedade pessoal (ESL Exclusivity / MooVeeL)
