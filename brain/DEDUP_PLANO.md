---
type: dedup_plan
generated: 2026-05-07
status: pendente_execucao
fonte: cross_drive_scan_20260507_1855.json
---

# Plano de Dedup + Backup — Documentos

Baseado no scan de 07/05/2026. Foco: documentos (PDF/DOCX/XLSX…).  
Áudios e vídeos: tratados separado, não estão neste plano.

---

## Hierarquia Canônica

```
R:\EddY          → PRIMARY (canônico, estruturado)
K:\              → BACKUP secundário (FENIX_DRIVE, 94 GB livre)
G:\              → BACKUP terciário (HD externo, 183 GB livre) — destino futuro
C:\Users\        → EVACUAÇÃO ONLY (não é destino permanente)
```

**Regra:** se o arquivo está em R: → K: e C: são cópias → candidatos a remoção.

---

## FASE 1 — C: Limpeza Imediata (baixo risco)

### 1.1 — 00IMPRIMIR ESSE AQUI.docx ×251
- **Localização:** `C:\Users\Usuário\OneDrive\`
- **Ação:** manter 1 cópia, deletar 250
- **Risco:** BAIXO — todas idênticas (sig "err", OneDrive sync)
- **Ganho:** ~250 inodes (arquivo pequeno, <1 MB cada)
- **Script:** buscar todas com `Get-ChildItem "C:\Users\Usuário\OneDrive" -Recurse -Filter "00IMPRIMIR ESSE AQUI.docx"`, deletar tudo menos 1

### 1.2 — R:+C: cross-duplicatas (63 grupos)
- **Ação:** deletar cópia em C: onde R: já tem o arquivo
- **Arquivos afetados:** principalmente em `C:\...\OneDrive\`, `C:\...\Downloads\`
- **Ganho:** ~0,20 GB
- **Verificação:** confirmar cada arquivo antes de deletar

---

## FASE 2 — K: Dedup Interno (maior ganho)

### Alvo
- 1.042 grupos duplicados **dentro de K:** → 1,83 GB recuperável
- Principais: `Pasta_D` vs `desktop/` vs `HD EddY/` — mesmos arquivos em 2-3 pastas

### Estratégia
Para cada grupo de dups dentro de K::
1. Identificar a cópia em pasta mais "organizada" (prioridade: `HD EddY/` > `desktop/` > outros)
2. Manter essa, deletar as demais
3. Logar cada deleção

### Pastas K: com mais dups internas estimadas:
- `Exclusivity-ESL` (HD EddY) vs `Exclusivity-ESL` (desktop) — 14 dups entre si
- `Historia` (HD EddY) vs `Historia` (desktop) — ~7 dups
- `Tattoo` (HD EddY) vs `Tattoo` (desktop) — 17 dups

### Script a criar: `data/dedup_k_internal.py`
- Ler JSON do scan
- Para cada sig com múltiplos paths em K::
  - Prioridade: manter path com `HD EddY` > `desktop` > outros
  - Deletar os outros
  - Log em `data/analysis/dedup_k_internal_log.json`

---

## FASE 3 — C: Evacuação de Conteúdo Único

Arquivos ÚNICOS em C: (não estão em R: nem K:) → mover para R:\EddY\

| Fonte C: | Destino R: | Tipo |
|----------|-----------|------|
| `OneDrive\Documentos\` (153 docs, 427 MB) | `R:\EddY\restricted\` (triagem) | Pessoal/trabalho |
| `Downloads\CAMPOS\` (39 docs, 118 MB) | `R:\EddY\restricted\trabalho\campos_suas` | Concurso CAMPOS |
| `Desktop\AEgea\` (32 docs, 18 MB) | `R:\EddY\restricted\trabalho\aegea` | AEgea |
| `Downloads\aec\` (74 docs, 31 MB) | `R:\EddY\restricted\trabalho\aec` | AEC |

**Ação:** NÃO deletar de C: até confirmar que chegou em R: com integridade.

---

## FASE 4 — K: Conteúdo Exclusivo para EddY

Conteúdo em K: que o EddY não tem e deveria ter:

### 4.1 — Exclusivity-ESL (6 únicos, 5,5 MB)
- **Origem:** `K:\_BACKUP_HD160\HD EddY\Exclusivity-ESL\`
- **Destino:** `R:\EddY\documents\doutrina_eddy\` (ou triagem manual)
- **Ação:** COPIAR (não mover — K: permanece backup)

### 4.2 — Historia / Lore (12 únicos, 44 MB)
- **Origem:** `K:\_BACKUP_HD160\HD EddY\Historia\`
- **Destino:** `R:\EddY\brain\04_LORE\` ou `archive\lore\`
- **Ação:** COPIAR

### 4.3 — Tattoo (17 docs, 34 MB)
- **Origem:** `K:\_BACKUP_HD160\HD EddY\Tattoo\`
- **Destino:** `R:\EddY\brain\03_ESL_ASSETS\01_IDENTIDADE_VISUAL\tattoo\`
- **Ação:** COPIAR (referências de tattoo da Isabella)

---

## FASE 5 — Backup R:\EddY → G:

Após dedup e evacuação:
- **Destino:** `G:\EDDY_ECOSSISTEMA_FINAL\backup_r_eddy_YYYYMMDD\`
- **Conteúdo:** `R:\EddY\` inteiro (exceto `data\_eddy_corpus\` — muito grande)
- **Ferramenta:** `robocopy R:\EddY G:\EDDY_ECOSSISTEMA_FINAL\backup_r_eddy_YYYYMMDD /MIR /LOG`
- **Tamanho estimado R:\EddY:** ~1 GB (sem corpus)
- **G: livre:** 183 GB ✅

---

## Resumo de Ganhos Esperados

| Fase | Ganho | Risco |
|------|-------|-------|
| F1.1 — 00IMPRIMIR ×251 | ~250 arquivos | Baixo |
| F1.2 — R:+C: dups | ~0,20 GB | Baixo |
| F2 — K: interno | **1,83 GB** | Médio |
| F3 — C: evacuação | 0 (move, não ganha) | Baixo |
| F4 — K: ESL/Lore | 0 (copia) | Zero |
| F5 — Backup G: | 0 (adiciona) | Zero |
| **TOTAL** | **~2,0 GB + limpeza** | — |

---

## Ordem de Execução — STATUS

| # | Fase | Status | Resultado |
|---|------|--------|-----------|
| 4 | K: ESL+Lore+Esoterica → R: | ✅ DONE 07/05 | 39 arquivos copiados |
| 1.2 | C: dups de R: deletados | ✅ DONE 07/05 | 131 arquivos deletados |
| 2 | K: dedup interno | ✅ DONE 07/05 | **1.107 deletados, 1.87 GB recuperados** |
| 3 | C: evacuação conteúdo único | ✅ DONE 07/05 | AEgea(71), CAMPOS(39), Downloads misc, Pictures, Documents movidos |
| 1.1 | 00IMPRIMIR OneDrive | ⏳ PENDENTE | Precisa de sync local OneDrive |
| — | C: lixo/caches | ✅ DONE 07/05 | revisado(8k arqs), 746 tmp, eddy.zip, 1.13GB browser cache |
| — | AI ZIPs C: → K: | ✅ DONE 07/05 | 4 ZIPs → K:\_AI_SOURCE (2.1 GB) |
| — | OneDrive cloud cleanup | ⏳ PENDENTE MANUAL | Login onedrive.live.com → deletar Documentos + sensíveis |
| 5 | Backup R:\EddY → G: | ⏳ PENDENTE | Próximo passo |
