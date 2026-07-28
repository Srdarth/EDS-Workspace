---
type: cross_drive_scan_report
generated: 2026-05-07T18:55
status: completo
scan_file: data/analysis/cross_drive_scan_20260507_1855.json
---

# Cross-Drive Scan Report — 07/05/2026

Varredura completa: R: + K: + G: + C:\Users\Usuário  
Script: `data/cross_drive_scan.py` | Duração: 158s | READ-ONLY

---

## Totais Gerais

| Métrica | Valor |
|---------|-------|
| Arquivos relevantes | 28.967 |
| Grupos com duplicatas | 3.055 |
| Documentos (pdf/doc/xlsx…) | **10.895** |
| Textos (txt/md/json) | 4.798 |
| Imagens | 9.912 |
| Vídeos | 2.119 |
| Áudios | 1.243 |

---

## Documentos por Drive

| Drive | Arquivos | Tamanho | Papel |
|-------|----------|---------|-------|
| **K:** | 9.961 | 18,91 GB | Backup principal (FENIX_DRIVE) |
| **R:** | 587 | 0,52 GB | EddY PRIMARY — canônico |
| **C:** | 346 | 0,62 GB | Evacuação pendente |
| **G:** | 1 | 0,00 GB | HD externo (quase vazio de docs) |

---

## K: — Distribuição por Pasta

| Pasta | Docs | Tamanho | Nota |
|-------|------|---------|------|
| `K:\_BACKUP_HD160\HD EddY\Pasta_D` | 7.395 | 9,18 GB | Bulk — Estácio + outros |
| `K:\_BACKUP_HD160\HD EddY\ESTACIO` | 724 | 2,64 GB | Faculdade Estácio |
| `K:\_BACKUP_HD160\HD EddY\Só PDF` | 464 | 4,06 GB | Coleção geral PDFs |
| `K:\_BACKUP_HD160\HD EddY\Documentos` | 172 | 0,26 GB | Documentos pessoais |
| `K:\_BACKUP_SSD120\oioi\mprj` | 29 | 0,31 GB | MPRJ legal |
| `K:\_BACKUP_HD160\HD EddY\Nova pasta` | 57 | 0,03 GB | Miscelânea |
| `K:\_BACKUP_HD160\HD EddY\Exclusivity-ESL` | **20** | **17,4 MB** | **ALTA VALOR — ESL** |
| `K:\_BACKUP_HD160\HD EddY\Historia` | **20** | **53,2 MB** | **ALTA VALOR — Lore** |
| `K:\_BACKUP_HD160\desktop\Exclusivity-ESL` | 18 | 13,3 MB | Dup de pasta acima |
| `K:\_BACKUP_HD160\desktop\Historia` | 17 | 14,0 MB | Dup de pasta acima |
| `K:\_BACKUP_HD160\HD EddY\Tattoo` | 17 | 34,5 MB | Referências tattoo Isabella |
| `K:\_BACKUP_HD160\desktop\Tattoo` | 17 | 34,5 MB | Dup da pasta acima |

---

## R: — Distribuição por Pasta

| Pasta | Docs | Tamanho | Nota |
|-------|------|---------|------|
| `R:\EddY\restricted\trabalho\claro` | 83 | 49,2 MB | Docs Claro |
| `R:\EddY\restricted\personal\contracheques` | 60 | 8,0 MB | Contracheques pessoais |
| `R:\EddY\restricted\personal\financeiro` | 53 | 5,3 MB | Financeiro |
| `R:\EddY\restricted\personal\profissional` | 46 | 3,7 MB | Profissional |
| `R:\EddY\restricted\legal\VIA` | 33 | 81,9 MB | Legal VIA (=dup de Eddy_160GB) |
| `R:\Eddy_160GB\kkkk\3333\VIA` | 33 | 81,9 MB | Mesma pasta — 2 locais |
| `R:\EddY\restricted\personal\saude` | 10 | 6,0 MB | Saúde |

---

## C: — Distribuição por Pasta

| Pasta | Docs | Tamanho | Nota |
|-------|------|---------|------|
| `C:\Users\...\OneDrive\Documentos` | 149 | 427,6 MB | **Evacuação prioritária** |
| `C:\Users\...\Downloads\aec` | 74 | 8,8 MB | AEC (concurso?) |
| `C:\Users\...\Desktop\AEgea` | 53 | 55,5 MB | AEgea |
| `C:\Users\...\Downloads\CAMPOS` | 39 | 118,6 MB | CAMPOS SUAS |
| `C:\Users\...\Documents\MEGA` | 2 | 6,3 MB | MEGA sync |

---

## Análise de Duplicatas — Documentos

### Resumo

| Tipo | Grupos | Cópias extra | Espaço recuperável |
|------|--------|-------------|-------------------|
| K: internas | **1.042** | ~1.800 | **1,83 GB** |
| R:+C: cross | 63 | ~63 | ~0,20 GB |
| C: internas | 3 | ~172 | ~2,7 MB |
| R:+K: cross | 57 | 57 | (manter — K: é backup) |
| **TOTAL** | **1.246** | **~1.761** | **~2,16 GB** |

### Top Duplicatas Cross-Drive

| Cópias | Arquivo | Drives |
|--------|---------|--------|
| 251x | `00IMPRIMIR ESSE AQUI.docx` | C: only (OneDrive) |
| 10x | `430459 - Contra-cheque 2025-06-7 (1).pdf` | C: K: R: |
| 9x | `00064_00.CONTRA_CHEQUE.pdf` | C: K: R: |
| 8x | `Consolidação Padrão Exclusivity ESL (1).pdf` | K: R: |
| 8x | `rad03117.html (1).pdf` | G: K: R: |
| 7x | `Estudo Definitivo Agência Exclusivity ESL (2).pdf` | K: R: |
| 6x | `Compilação Detalhada Isabella Vivian.pdf` | K: R: |
| 6x | `bella_spec_canonica.pdf` | K: R: |
| 6x | `otimo.PDF` | K: R: |
| 5x | `Master_Asset_Catalog_Eddy_Digital_Solutions.xlsx` | K: R: |

### Alerta: 00IMPRIMIR ESSE AQUI.docx
- 251 cópias idênticas em `C:\Users\Usuário\OneDrive\`
- Sig: `err` (OneDrive não deixou ler — arquivo em sync cloud)
- Ação: manter 1, deletar 250

---

## Conteúdo Único em K: (não está em R:)

| Pasta K: | Arquivos únicos | Tamanho |
|----------|----------------|---------|
| Pasta_D | 7.395 | 9,18 GB |
| ESTÁCIO | 722 | 2,64 GB |
| Só PDF | 461 | 4,05 GB |
| Documentos | 164 | 0,25 GB |
| **Exclusivity-ESL** | **6** | **5,5 MB** (únicos, outros 14 são dups de desktop/) |
| **Historia** | **12** | **44,2 MB** |
| Tattoo | 17 | 34,5 MB |

**Total único em K::** 9.858 arquivos / 16,95 GB  
*(K: é o único lugar que tem todo esse conteúdo — não deletar sem backup confirmado)*

---

## Conteúdo Único em C: (não está em R: nem K:)

79 sigs únicos → ~305 arquivos → principal: OneDrive/Documentos (153 docs, 427 MB)

---

## Textos (TXT/MD/JSON/CSV)

| Drive | Arquivos |
|-------|----------|
| C: | 2.594 (maioria: .claude, VS Code, Downloads) |
| K: | 1.777 (backup Tor Browser, docs txt antigos) |
| R: | 399 (EddY corpus + config) |

---

## Próximos Passos → ver `DEDUP_PLANO.md`
