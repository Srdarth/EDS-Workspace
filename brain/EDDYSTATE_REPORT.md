---
type: state_report
project: EddY
status: archived
phase: initial
generated: 2026-01-31
tags: [archived, state, historical]---

# EDDYSTATE REPORT
Generated: 2026-01-31T03:12:34

## Pipeline
observe -> identify -> understand -> decide -> execute

## Config (eddy_app)
- db_path: C:\Users\Usuário\AppData\Local\EddY\runtime\run_20260131_031152\eddy.db
- targets (2): ['C:\\Users', 'R:\\']
- exclude_contains (15): ['\\\\$RECYCLE.BIN\\\\', '\\\\System Volume Information\\\\', '\\\\Windows\\\\', '\\\\Windows\\\\System32\\\\', '\\\\Program Files\\\\', '\\\\Program Files (x86)\\\\', '\\\\ProgramData\\\\', '\\\\Recovery\\\\', '\\\\PerfLogs\\\\', '\\\\$WINDOWS.~BT\\\\', '\\\\AppData\\\\', '\\\\EddY\\\\EddY_Organizado\\\\', 'R:\\\\EddY', 'R:\\EddY', 'R:\\EddY\\EddY_Organizado']
- dest_root: R:\\EddY\\EddY_Organizado
- action_mode: copy
- hash_max_bytes: 26214400
- identify_max_bytes: 52428800
- text_preview_chars: 400
- name_confidence_min: 60
- precount: False
- mark_missing: False
- missing_scope: targets
- resume_scan: True
- dir_cache: True
- plan_duplicates: False

## Targets (roots)
- config targets: ['C:\\Users', 'R:\\']
- latest roots_json: ['C:\\', 'D:\\', 'K:\\', 'R:\\']

## DB Status
- db_path: C:\Users\Usuário\AppData\Local\EddY\runtime\run_20260131_031152\eddy.db
- os.access(db, W_OK): True
- os.access(dir, W_OK): True
- eddy.db-wal: exists size=0 mtime=2026-01-30T17:55:08
- eddy.db-shm: exists size=32768 mtime=2026-01-31T02:41:08
- query_only: 0
- journal_mode: wal
- locking_mode: normal
- runs: 2
- actions: 0
- plans: 0
- plans_proposed: 0
- files: 1240150
- roots_json missing/empty: 0

### runs schema
- run_id TEXT notnull=0 pk=1 default=None
- started_at TEXT notnull=1 pk=0 default=None
- finished_at TEXT notnull=0 pk=0 default=None
- roots_json TEXT notnull=0 pk=0 default=None
- id INTEGER notnull=0 pk=0 default=None
- run_key TEXT notnull=0 pk=0 default=None
- stage TEXT notnull=0 pk=0 default=None
- status TEXT notnull=0 pk=0 default=None
- details_json TEXT notnull=0 pk=0 default=None
- ended_at TEXT notnull=0 pk=0 default=None
- config_snapshot TEXT notnull=0 pk=0 default=None

### files.status counts
- NEW: 489201
- unchanged: 359344
- excluded: 264141
- new: 123629
- OK: 2629
- moved: 771
- identified: 363
- MOVED: 72

## Ultimo run por stage
- (n/a)

## config.yaml (excerpt)
### santuario
```
santuario: "D:/EDDY_ECOSSISTEMA_FINAL"
```
### db_path
```
db_path: "R:/Eddy_160GB/Nova pasta"
```
### report_dir
```
report_dir: "R:/Eddy_160GB/Nova pasta/reports"
```
### territorios
```
territorios:
  - nome: "NucleoPrimordial"
    path: "D:/EddY_BASE_FINAL"
    tipo: "photorec_recovery"
  - nome: "ArquivoCivil"
    path: "K:/"
    tipo: "intact_backup"
  - nome: "ColoniaRecursos"
    path: "R:/"
    tipo: "mixed_archive"
```
### arquitetura_canonica
```
arquitetura_canonica:
  - "01_ESTUDOS/PF"
  - "01_ESTUDOS/TJRJ"
  - "02_PROJETOS_CRIATIVOS/Modelos/Isabella/Imagens"
  - "02_PROJETOS_CRIATIVOS/Modelos/Vivian/Imagens"
  - "00_ARQUIVO_GERAL/01_IMAGENS"
  - "00_ARQUIVO_GERAL/03_DOCUMENTOS"
  - "99_OUTROS"
```
### diretrizes_de_assimilacao
```
diretrizes_de_assimilacao:
  - nome: "Classificacao por nome (basica)"
    tipo: "analise_de_nome"
    regras:
      - "se \"isabella\" ou \"isa\" em nome_do_arquivo -> /02_PROJETOS_CRIATIVOS/Modelos/Isabella"
      - "se \"vivian\" em nome_do_arquivo -> /02_PROJETOS_CRIATIVOS/Modelos/Vivian"
  - nome: "Classificacao por tipo (fallback)"
    tipo: "analise_de_extensao"
    regras:
      - "se extensao em [\".jpg\",\".png\"] -> mover_para /00_ARQUIVO_GERAL/01_IMAGENS"
      - "se extensao em [\".pdf\",\".epub\"] -> mover_para /00_ARQUIVO_GERAL/03_DOCUMENTOS"
```

## eddy_config.json (excerpt)
- db_path: R:\\EddY\\eddy.db
- targets: []
- exclude_contains: ['\\\\$RECYCLE.BIN\\\\', '\\\\System Volume Information\\\\', '\\\\Windows\\\\', '\\\\Windows\\\\System32\\\\', '\\\\Program Files\\\\', '\\\\Program Files (x86)\\\\', '\\\\ProgramData\\\\', '\\\\Recovery\\\\', '\\\\PerfLogs\\\\', '\\\\$WINDOWS.~BT\\\\', '\\\\AppData\\\\', '\\\\EddY\\\\EddY_Organizado\\\\', 'R:\\\\EddY']
- dest_root: R:\\EddY\\EddY_Organizado
- rules: []
- fallback_dest: _INBOX
- quarantine_dir: _QUARANTINE
- hash_max_bytes: 26214400
- precount: False
- mark_missing: False
- missing_scope: targets
- resume_scan: True
- dir_cache: True
- plan_duplicates: False
- action_mode: copy

## Proximos passos sugeridos
- Sem planos: rode `decide` para gerar planos a partir dos arquivos elegiveis.

