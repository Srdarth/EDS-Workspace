---
type: mapeamento_conversas
project: EddY
status: canonical
last_updated: 2026-05-07
tags: [canonical, chatgpt, grok, gemini, corpus, conversas, IP]
---

# MAPEAMENTO DAS CONVERSAS AI — Origem do EddY/ESL/EDS

> "99% de tudo — das fotos das modelas até as lores e o sistema — nasceu nessas conversas."
> — Edson Souza Leite, 07/05/2026

---

## DIAGNÓSTICO GERAL

| Fonte | Arquivo | Conversas | Status Corpus |
|-------|---------|-----------|---------------|
| **ChatGPT** | `R:/Eddy_160GB/kkkk/3333/...conversations.json` | **114 conversas** (22.8 MB) | ❌ Não extraído para corpus |
| **ChatGPT shared** | `C:/Downloads/eddy.zip` | 4 conversas compartilhadas | ❌ Não extraído |
| **Grok** | `C:/Downloads/9563371f-83b4-42c8-b8cf-d77f7426cee9.zip` | 76 conversas + **1.929 media_posts** | ❌ Não extraído |
| **Gemini** | Google Takeout (14 ZIPs) | **Zero** — texto não exportável | ✅ Conteúdo já no corpus como PDFs |

---

## CHATGPT — 114 CONVERSAS (PRINCIPAL)

**Localização:** `R:/Eddy_160GB/kkkk/3333/74b064f5.../conversations.json`
**Tamanho:** 22.8 MB JSON
**Formato:** Padrão ChatGPT export — `mapping` com mensagens user/assistant

### Top Conversas por Relevância EddY/ESL (score = ocorrências de keywords)

| Score | Título | Conteúdo |
|-------|--------|---------|
| 1013 | Comandos DALL-E para Logotipos | Prompts Isabella, logos ESL |
| 871 | Revamp Company Name | Origem do nome EDS/ESL |
| 796 | Profile Analysis for Company | Estratégia ESL completa |
| 685 | Refinando Empresa Pessoal | Fundação EDS |
| 651 | Isabella: Modelo Carioca Misteriosa | Origem da Isabella |
| 442 | Modeling Isabella: Technical Elegance | Spec técnica Isabella |
| 442 | Currículo eficaz: dicas essenciais | — |
| 440 | AI Image Generation Codes | Prompts de geração |
| 314 | Tipos e Características de Animes | Valtherra/lore |
| 263 | Perfil Gráfico Digital | EDS branding |
| 260 | Modelo carioca Isabella | Isabella spec |
| 206 | Carioca Beauty Signature | ESL estética |
| 203 | Criar personagem EDDY | Origem do sistema |

**Total com relevância >0:** 100 de 114 conversas
**Total com relevância >50:** 45 conversas
**Alta relevância (>200):** 13 conversas — OURO para o corpus

---

## GROK — 76 CONVERSAS + 1.929 MEDIA POSTS

**Localização:** `C:/Downloads/9563371f-83b4-42c8-b8cf-d77f7426cee9.zip`
**Arquivo principal:** `ttl/30d/export_data/e5b2e300.../prod-grok-backend.json` (47 MB)
**Estrutura JSON:** `conversations` (76) + `media_posts` (1.929) + `tasks` + `projects`

**Media posts:** Conteúdo criado com Grok — prompts de imagem, descrições ESL, posts sociais, lore.
São potencialmente mais ricos que as conversas brutas para ESL.

**Outros ZIPs Grok disponíveis (em C:/Downloads):**
Veja `brain/GROK_CONVERSATIONS_MINING.md` — 339 conversas mineradas anteriormente.

---

## GEMINI — POR QUE NÃO HÁ TEXTO NOS TAKEOUTS

O Google Takeout NÃO exporta o texto das conversas do Gemini.
O que existe nos 14 ZIPs de Takeout:
- 1.781 imagens enviadas ao Gemini (PNG, JPG)
- HTML de atividade (log de pesquisas, não conteúdo)
- `gemini_gems_data.html` — vazio
- `gemini_scheduled_actions_data.html` — vazio

**Mas o Gemini está no corpus assim mesmo:**
Tudo que o Gemini criou com Edson foi salvo como PDFs e já está extraído:
- `Estudo Definitivo Agência Exclusivity ESL.pdf` → corpus ✅
- `Consolidação Padrão Exclusivity ESL.pdf` → corpus ✅
- `A Filosofia da Marca – O Padrão Edson Souza Leite.pdf` → corpus ✅
- `A Doutrina EddY – O Ecossistema Canônico.pdf` → corpus ✅
- `Bíblia do Sistema EddY.pdf` → corpus ✅
- `Sistema EddY Blueprint Operacional.pdf` → corpus ✅
- `Consolidação da Marca Eddy Digital Solutions.pdf` → corpus ✅
- `EDDY_GROK.pdf`, `EDDY_GPT1.pdf`, `EDDY_GPT2.pdf`, `EDDY_GROK2.pdf` → corpus ✅

O conteúdo do Gemini está no corpus na forma dos seus *outputs* (documentos gerados), não dos chats brutos.

---

## PLANO DE EXTRAÇÃO

### Fase 1 — Automática (corpus TXT)
Extrair todas as conversas para TXT → jogar em `data/_eddy_corpus/pdf_text/ai_convs/`
- 114 ChatGPT → `chatgpt_conv_001.txt` a `chatgpt_conv_114.txt`
- 76 Grok conversas → `grok_conv_001.txt` a `grok_conv_076.txt`
- 1.929 Grok media_posts → `grok_media_001.txt` a ...

**Script a criar:** `data/extract_ai_conversations.py`
**Após extração:** Novo round de classify picking up automaticamente

### Fase 2 — Estruturada (brain docs)
Análise profunda das top 13 ChatGPT por score → criar documentos brain/ com:
- Decisões de marca ESL/EDS tomadas naquelas conversas
- Spec completa Isabella (origem, evolução)
- Estratégia EDS (nome, posicionamento)
- Prompts canônicos de geração de imagem
- Lore Valtherra/Desrruptura extraído

**Status:** PENDENTE — aguarda aprovação de execução

---

## IMAGENS ESL NO TAKEOUT

**1.084 imagens ESL** encontradas em `Takeout/Google Fotos/ESL/` (takeout-050547Z-3-001.zip)
Destino: `media/ip/` — PENDENTE de decisão de extração

---

## KEYWORDS USADAS NO SCORING

`eddy, esl, eds, isabella, vivian, valtherra, neverlost, modelo, agencia, fanvue, onlyfans, corpus, pipeline, sistema, digital, marca, lore, personagem`
