---
type: regras_canonicas
project: EddY
phase: FASE H4
status: canonical
last_updated: 2026-05-06
aliases: [regras, rules, 00_regras]
tags: [canonical, rules, governance, axiom_sovereign_engine]
supersedes: "00_REGRAS_CANONICAS.md (FASE H3)"
---

# Regras Canônicas — Axiom Sovereign Engine / EddY PDOS
**Versão:** FASE H4 | **Data:** 2026-05-06
**Status:** CANÔNICO

---

## Regras Absolutas (inalteráveis)

| ID | Regra |
|----|-------|
| A1 | **Nada é deletado — jamais.** Todo arquivo vai para archive/ ou recebe status=deleted no banco. |
| A2 | **SQLite single-writer.** Nunca dois processos escrevem no mesmo .db simultaneamente. |
| A3 | **Sempre dry-run antes de executar.** Toda operação física requer revisão prévia. |
| A4 | **archive/ é histórico imutável.** Nunca reorganizar, nunca mover o que está em archive/. |
| A5 | **O banco SQLite é a única fonte de verdade operacional.** Metadados físicos são secundários. |
| A6 | **brain/ é camada semântica.** Contém apenas MDs canônicos e índices — sem JSONs de análise. |
| A7 | **G:\ é superfície mista (Google Drive mount, 285k files).** Duas zonas: MIRROR_STALE (Backup_EddY_23-04-2026) e ESTRUTURA_VIVA (EDDY_ECOSSISTEMA_FINAL — NeverLost, IP ESL). READ_ONLY em todas as zonas. G:\ não substitui R:\EddY como núcleo. |
| A8 | **Duplicado não é inútil.** Verificar evolução e conteúdo antes de qualquer decisão de descarte. |
| A9 | **Conteúdo externo entra via _INBOX_CONVERGENCE\.** Nunca diretamente no destino final. |
| A10 | **EddY_Observer\ é patrimônio histórico crítico.** Nenhum .db deletado sem SHA256 confirmatório. |

---

## Regras de Superfície (NOVA — S3.3)

| ID | Regra |
|----|-------|
| S1 | **C:\ é EVACUATION_ONLY.** Nenhum artefato permanente do Axiom Sovereign Engine vai para C:\. |
| S2 | **Única exceção em C:\:** arquivos efêmeros de sessão em AppData\Local\Temp — autodestrutivos. |
| S3 | **PCEDDY.mp4 e qualquer vídeo EddY pertencem a R:\EddY\media\.** C:\Desktop não é destino válido. |
| S4 | **Se o sistema tentar escrever em C:\, interromper e registrar a violação** em c_write_violation_map.json. |
| S5 | **Downloads/ é staging de entrada — nunca destino final.** Zero mistura direta com root truth. |
| S6 | **R:\EddY continua sendo a raiz física.** NÃO renomear fisicamente o root agora. |
| S7 | **Move > Copy.** Para evacuação e ingestão, mover preferível a duplicar. |

---

## Regras de Identidade (NOVA — S3.1)

| ID | Regra |
|----|-------|
| I1 | **"EddY" = identidade pessoal / origem / corpus histórico.** Não é nome de produto. |
| I2 | **"Axiom Sovereign Engine" = motor técnico do produto.** Usar este nome em novos documentos técnicos. |
| I3 | **"Cognitive Protocol" = camada semântica / ontologia.** O que interpreta e organiza o significado. |
| I4 | **"EDS" = Eddy Digital Solutions = holding/empresa.** Separar de EddY pessoal. |
| I5 | **"ESL" = Exclusivity ESL = marca criativa / IP.** Nunca misturar com o pipeline técnico. |
| I6 | **"NeverLost" = produto público derivado / auditor sensor.** Não é o sistema inteiro. |
| I7 | **Nomes legados (EddY como produto) são preservados apenas como histórico.** Não usar em documentos novos. |
| I8 | **R:\EddY é âncora física por compatibilidade.** O nome do diretório não define a identidade lógica. |

---

## Regras de Casa Única

| ID | Regra |
|----|-------|
| C1 | Cada ativo tem **UMA** casa canônica. Existência em múltiplos lugares requer resolução explícita. |
| C2 | **core/** = código ativo, bancos ativos, scripts ativos, configs. |
| C3 | **brain/** = documentos canônicos em Markdown e índices mestres — nada mais. |
| C4 | **data/analysis/** = outputs técnicos: mapas, relatórios, índices, JSONs de análise. |
| C5 | **data/_eddy_corpus/** = textos extraídos e corpus processado. |
| C6 | **archive/** = origem histórica e versões congeladas — imutável. |
| C7 | **restricted/** = documentos sensíveis pessoais (saúde, legal, identidade, profissional). |
| C8 | **media/** = vídeos e imagens de IP / monetizáveis. |
| C9 | **_INBOX_CONVERGENCE/** = staging temporário — nunca destino final permanente. |
| C10 | Mídia grande (>1 MB, imagem/vídeo) **não entra no Brain**. Brain recebe: índice + metadado + pointer. |

---

## Regras de Precedência de Fonte

| Ordem | Fonte | Papel |
|-------|-------|-------|
| 1 | R:\EddY (canonical home) | Verdade primária operacional |
| 2 | Banco SQLite (eddy.db) | Verdade de metadados e status |
| 3 | brain/ MDs canônicos | Verdade semântica e governança |
| 4 | data/analysis/ JSONs | Verdade técnica e analítica |
| 5 | _INBOX_CONVERGENCE/kkkk_3333/ | Origem crítica única (staging — aguarda HR01) |
| 6 | R:\EddY_Observer\*.db | Patrimônio histórico (legado) |
| 7 | G:\ (snapshot 23/04/2026) | Mirror forense (leitura apenas) |
| 8 | K:\ pendrive | Backup secundário legado |
| 9 | D:\ (offline) | Desconhecido — aguardando HR04 |

---

## Regras de Pipeline

| ID | Regra |
|----|-------|
| P1 | Pipeline: observe → identify → understand → decide → execute → verify. |
| P2 | Falha em arquivo individual nunca pode travar a execução total. |
| P3 | Se um diretório já foi consolidado, não reabrir o mesmo trabalho do zero. |
| P4 | Confiar em: conteúdo, hash, fingerprint, estrutura, contexto e precedência. |
| P5 | Ignorar: nome, extensão e pasta como verdade primária. |
| P6 | Outputs já gerados não são reescritos — são patchados e validados. |
| P7 | **Não expandir antes de fechar o estado interno.** Execute gap é o principal risco sistêmico. |

---

## Regras de Contexto de Identidade (NOVA — S3.2)

| ID | Regra |
|----|-------|
| N1 | Documentos de produto usam "Axiom Sovereign Engine", não "EddY". |
| N2 | Documentos de empresa usam "EDS (Eddy Digital Solutions)", não "EddY". |
| N3 | Documentos de marca usam "ESL (Exclusivity ESL)", não "EddY". |
| N4 | Documentos pessoais e de origem usam "EddY" ou "Edson Souza Leite". |
| N5 | O motor técnico e a pessoa nunca compartilham o mesmo rótulo em novos documentos. |

---

---

## Regras ESL (NOVA — H3)

| ID | Regra |
|----|-------|
| ESL-R01 | **Yasmin (16 anos) é modelo menor.** ZERO conteúdo sexual — compliance legal inegociável em qualquer formato. |
| ESL-R02 | **Anira é universo NSFW/Liber Tenebris.** Nunca associar com ESL, Isabella, Vivian ou qualquer persona ESL premium. |
| ESL-R03 | **DNA Fixo das modelos é imutável.** Tatuagens, cor de olhos e físico base são fixos — não variar sem decisão explícita do fundador. |

---

*Atualizado: 2026-05-06 — FASE H4 | Ver: [[00_ESTADO_CONSOLIDADO]] | [[MAPA]] | [[IDENTIDADE_CANONICO]]*
