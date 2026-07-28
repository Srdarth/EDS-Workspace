# NeverLost Observer — EddY Python Pipeline

**Axiom Sovereign Engine v4.0** — Personal Digital Operating System (PDOS)

Scanner forense de soberania digital pessoal. 100% offline, sem upload, sem cloud.

---

## Pipeline

```
Observe → Understand → Identify → Decide → Execute → Verify
```

| Etapa | Módulo | O que faz |
|-------|--------|-----------|
| **Observe** | `core/observe.py` | Varre diretórios, detecta new/moved/unchanged via `quicksig` |
| **Understand** | `core/understand.py` | Hash completo MD5+SHA256, detecta duplicatas reais |
| **Identify** | `core/identify.py` | Extrai texto de PDF/DOCX, EXIF de imagens, sugere nomes |
| **Decide** | `core/decide.py` | Aplica regras de taxonomia, gera plano (`dry_run=True` padrão) |
| **Execute** | `core/execute.py` | Executa plano com verificação de hash antes/depois |
| **Verify** | `core/verify.py` | Verificação independente pós-execução |

---

## Início rápido

```bash
pip install -r requirements.txt

# Observar dois diretórios
python main.py observe --targets /mnt/c/Users/Seu /mnt/d/Arquivos

# Calcular hashes e detectar duplicatas
python main.py understand

# Gerar relatório
python main.py report

# Gerar plano de organização (dry-run)
python main.py decide --dest /destino/EddY_Organizado
```

---

## Configuração

Crie `eddy_config.json` na raiz ou use `targets.json` para múltiplos targets:

```json
{
  "db_path": "/caminho/para/eddy.db",
  "targets": ["/mnt/c/Users", "/mnt/d/"],
  "dest_root": "/mnt/r/EddY_Organizado",
  "dry_run": true,
  "action_mode": "copy",
  "hash_max_bytes": 26214400,
  "resume_scan": true
}
```

---

## Invariantes (nunca violar)

1. `dry_run=True` é o padrão absoluto
2. Nenhum arquivo é deletado — execute usa `copy` por padrão
3. O banco SQLite é a única fonte de verdade
4. Todo execute real gera `undo_{run_key}.txt`
5. Resume sempre — observe retoma do último arquivo

---

## Dependências opcionais

| Biblioteca | Para que |
|------------|---------|
| `PyPDF2` | Extração de texto de PDFs |
| `python-docx` | Extração de texto de DOCX |
| `Pillow` | Leitura de EXIF de imagens |

Sem essas bibliotecas, o sistema funciona 100% offline com only stdlib.
