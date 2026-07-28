# EddY Brain — Vault de Conhecimento

Documentação canônica do ecossistema EDS / EddY / NeverLost.
Este diretório espelha o vault Obsidian localizado em `R:\EddY\brain\` (Windows).

---

## Estrutura

| Arquivo | Conteúdo |
|---------|---------|
| `00_INDEX_MESTRE.md` | Índice canônico de todos os documentos |
| `00_CONTEXTO_MESTRE.md` | Contexto consolidado do projeto |
| `00_ESTADO_CONSOLIDADO.md` | Estado atual do sistema (última sync) |
| `00_MAPA_DE_EXECUCAO.md` | Fila e mapa de execução de tarefas |
| `00_MAPA_DO_PROJETO.md` | Mapa completo do projeto EDS |
| `00_REGRAS_CANONICAS.md` | Regras canônicas do sistema EddY |
| `00_RECOVERY_QUEUE.md` | Fila de recuperação de tarefas pendentes |
| `00_PRECEDENCIA_DE_FONTES.md` | Hierarquia de prioridade de fontes |
| `ARQUITETURA.md` | Arquitetura técnica do sistema |
| `CONHECIMENTO.md` | Corpus de conhecimento acumulado |
| `CORPUS_HISTORICO.md` | Histórico completo de sessões e decisões |
| `DECISOES.md` | Log de decisões arquiteturais |
| `CHAT_SEMANTIC_INSIGHTS.md` | Insights semânticos de sessões de AI |
| `CONVERSAS_AI_MAPEAMENTO.md` | Mapeamento de conversas com AI |
| `APRENDIZADOS_CORPUS.md` | Aprendizados e padrões identificados |
| `EDDYSTATE_REPORT.md` | Relatório de estado do EddY |
| `CROSS_DRIVE_SCAN_REPORT.md` | Relatório de scan multi-drive |
| `DEDUP_PLANO.md` | Plano de deduplicação |
| `brain_canonical_index_v7.md` | Índice canônico v7 do brain |
| `eddy_brain_consolidado_profissional.md` | Versão consolidada profissional |

---

## Sincronização

O vault Obsidian em `R:\EddY\brain\` é a fonte de verdade para edições locais.
Este diretório é um espelho versionado no GitHub para backup e colaboração.

Para sincronizar (Windows PowerShell):
```powershell
cd R:\EddY\brain
xcopy /s /y *.md C:\path\to\EDS-Workspace\brain\
cd C:\path\to\EDS-Workspace
git add brain/
git commit -m "brain: sync vault $(Get-Date -Format 'yyyy-MM-dd')"
git push
```

---

## Hierarquia de identidade

```
MooVeeL (umbrella)
└── EDS — Estúdio Digital Soberano (holding)
    ├── ESL Exclusivity (IP criativo)
    │   └── Personas: Isabella, Viviane, Catarina, Mirella, Sophia, Yasmin
    └── NeverLost (produto público)
        └── EddY — Axiom Sovereign Engine (motor)
```
