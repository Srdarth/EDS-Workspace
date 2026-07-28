---
name: NeverLost MVP direction
description: Decisões duráveis sobre arquitetura, pipeline e produto do NeverLost / EddY OS
---

## Arquitetura EddY — pipeline de 6 etapas

O EddY real (Python) roda um pipeline sequencial:
1. **Observe** — varredura do filesystem, quick_signature (SHA-1 de tamanho + primeiros 2 MB), detecta new/moved/unchanged/missing
2. **Understand** — hash completo (MD5 + SHA256), infer_kind por extensão, detecção de duplicatas
3. **Identify** — extração de conteúdo (PyPDF2, python-docx, Pillow EXIF), sugestão de nome, fingerprint
4. **Decide** — engine de regras (name_contains, ext_in, kind_is, path_contains, fallback), gera plans no SQLite
5. **Execute** — copy/move com verificação de hash antes/depois, log de undo
6. **Verify** — verificação independente pós-execução

**Why:** entender o pipeline é necessário para refletir com precisão o comportamento nas interfaces web e nos slides.

## Taxonomia DEFAULT_RULES (config.py)

Ordem de prioridade das regras:
1. Sistema de Propriedade Visual (Isabella, Viviane, Catarina, Mirella, Sophia, Yasmin) — **prioridade máxima**
2. Imagens → `00_ARQUIVO_GERAL/01_IMAGENS`
3. Vídeos → `00_ARQUIVO_GERAL/02_VIDEOS`
4. Áudio → `00_ARQUIVO_GERAL/04_AUDIO`
5. Compactados → `00_ARQUIVO_GERAL/05_COMPACTADOS`
6. Documentos → `00_ARQUIVO_GERAL/03_DOCUMENTOS`
7. Fallback → `00_ARQUIVO_GERAL/99_OUTROS`

O scanner web porta exatamente essas regras em TypeScript via `EDDY_RULES` + `resolveOrg()`.

## NeverLost Observer — dados reais de scan

Scan real do usuário (C:\ + D:\ + R:\):
- 909.089 arquivos, 1,53 TB total
- D:\EDDY_ECOSSISTEMA_FINAL = 733 GB (workspace principal)
- Top ext por volume: .img (1 TB!), .zip, .m4a, .pdf, .iso, .mp4

**Why:** calibra expectativas sobre escala e ajuda a dimensionar melhorias futuras (ex: paginação de resultados com >100k arquivos).

## NeverLost Scanner Web — o que foi implementado

Porta completa do pipeline EddY no browser (App.tsx):
- **Quick signature** via Web Crypto API (SHA-1 de tamanho + primeiros 2 MB) — idêntico ao Python
- **Pipeline de 4 etapas** animado durante o scan (Observe, Understand, Identify, Decide)
- **Plano de organização** (etapa Decide) com engine de regras portada em TS
- **Top extensões** com barra visual
- **Export "Mapa do Caos" HTML** — idêntico ao relatório do NeverLost Observer EXE
- Detecção de duplicatas por assinatura, não só por nome+tamanho

**Why:** o scanner web deve ser demonstrável como versão browser-first do pipeline real, não um mock simplificado.

## Produto

- EDS = marca guarda-chuva (Eddy Digital Solutions)
- EddY = motor de organização digital (Python, SQLite, regras configuráveis)
- NeverLost = primeiro produto (Observer Edition = read-only, Pro = com Execute)
- ESL = Exclusivity / agência (marca separada dentro do ecossistema EDS)
- "Sistema de Propriedade Visual" = conjunto de personagens (Isabella, Viviane, etc.) com conteúdo categorizado pelo EddY
