---
type: precedencia_fontes
project: EddY
version: 4.6B-J
status: active
last_updated: 2026-04-29
tags: [precedencia, fontes, verdade, canonical, mirror, regras]
aliases: [PRECEDENCIA, FONTES, SOURCE_PRECEDENCE]
---

# EddY — Precedência de Fontes (29/04/2026)

> **Regra geral:** R:\\EddY sempre ganha. Conteúdo sempre prevalece sobre nome/localização.

---

## Hierarquia de Verdade

```
1. R:\EddY\          ← CANONICAL HOME (verdade operacional)
   ├── brain/        ← Camada semântica humana
   ├── core/         ← Sistema ativo + eddy.db
   ├── data/         ← Análise técnica
   └── archive/      ← Histórico imutável

2. R:\Eddy_160GB\kkkk\3333\  ← FONTE ÚNICA CRÍTICA
   └── 27+ PDFs EddY/ESL + ChatGPT export (sem cópia confirmada em G:\)

3. R:\EddY_Observer\  ← ARQUIVO HISTÓRICO CRÍTICO
   └── 13 DBs históricos (pré-requisito: SHA256 antes de qualquer ação)

4. G:\               ← MIRROR FORENSE (snapshot 23/04/2026)
   └── 99.2% overlap com R:\EddY — NÃO promover a canonical sem confirmação

5. K:\               ← PENDRIVE BACKUP
   └── verificar contra R:\EddY antes de qualquer promoção

6. C:\               ← SO + Dados Usuário
   └── não pertence ao corpus EddY (quarantine/permanent_noise)

7. D:\               ← OFFLINE HISTÓRICO
   └── 454k arquivos desconhecidos — tratar como unknown até reconectar
```

---

## Por Tipo de Verdade

| Tipo | Fonte Primária | Fonte Secundária | Fallback |
|------|---------------|-----------------|---------|
| **Identidade** | `brain/IDENTIDADE_CANONICO.md` | `brain/IDENTIDADE.md`, `EddY_OS_Brain/` | `pdf_text/` extrações |
| **Estratégia** | `brain/ESL_ESTRATEGIA_CANONICO.md` | `brain/MONETIZACAO_CANONICO.md` | `pdf_text/ESL.txt` |
| **Persona/IP** | `brain/03_ESL_ASSETS/` | `brain/IDENTIDADE_CANONICO.md` | `kkkk/3333/*.pdf` |
| **Técnico** | `core/eddy.db` | `core/eddy_app/`, `core/*.py` | `EddY_Observer/` |
| **Histórico** | `archive/` | `Eddy_160GB/`, `EddY_Observer/` | `G:\EDDY_ECOSSISTEMA_FINAL\` |
| **Forense** | `G:\Backup_EddY_23-04-2026\` | `G:\EDDY_ECOSSISTEMA_FINAL\` | — |
| **Ruído** | `.git/`, `.claude/`, `__pycache__/` | `*.shm`, `*.wal` | — |

---

## Regras de Decisão

### Quando há conflito de versão (mesmo arquivo, tamanhos diferentes):
```
R:\EddY version WINS (canonical_home)
G:\    version é REFERENCE (mirror forense)
Ação: verificar R:\EddY, registrar divergência, NÃO sobrescrever
```

### Quando um arquivo está APENAS em G:\ (não em R:\EddY):
```
G:\-only → archive_candidate
Ação: avaliar se deve ir para _INBOX_CONVERGENCE
NÃO assumir que é canônico só por estar em G:\
```

### Quando um arquivo está APENAS em R:\ mas fora de R:\EddY:
```
R:\Eddy_160GB\ ou R:\EddY_Observer\ → external_unique
Ação: copiar para _INBOX_CONVERGENCE primeiro, classificar depois
NUNCA assumir que backup = cópia ativa
```

### Quando um arquivo não está em nenhuma fonte conhecida:
```
unknown → review manual
NÃO integrar automaticamente ao CKG
NÃO deletar sem SHA256 confirmatório
```

---

## Zona de Entrada: _INBOX_CONVERGENCE

```
R:\EddY\_INBOX_CONVERGENCE\
  ├── kkkk_3333\          ← P1 crítico (pendente cópia)
  │   └── _sensitive\     ← docs pessoais isolados
  ├── observer_legacy\    ← DBs históricos após SHA256
  ├── k_pendrive\         ← arquivos únicos do K:\
  └── esl_docs\           ← docs ESL de K:\_BACKUP_HD160
```

**Regra:** Todo conteúdo externo passa pela inbox antes de qualquer decisão.
**Nunca** mover diretamente de fonte externa para brain/ ou core/.

---

## O Que NÃO Fazer

1. **NÃO** promover G:\\ como canonical_home
2. **NÃO** tratar backup como segunda origem canônica
3. **NÃO** deletar de kkkk/3333 antes de cópia confirmada
4. **NÃO** integrar EddY_OS_Brain ao CKG automaticamente
5. **NÃO** executar decide em G:\\ antes de SHA256 dos Observer DBs
6. **NÃO** confiar em nome de arquivo — confiar em conteúdo e hash

---

*Atualizado: 2026-04-29 — FASE 4.6B-J | Fonte: data/analysis/source_precedence_matrix.json*
*Ver também: [[00_RECOVERY_QUEUE]] | [[REGRAS]] | [[GOVERNANCA_CORPUS_MASTER]]*
