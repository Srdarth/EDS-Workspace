import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Route, Router as WouterRouter, Switch } from 'wouter';
import {
  ArrowDownRight,
  ArrowUpRight,
  CalendarDays,
  Check,
  ChevronDown,
  CircleAlert,
  CircleDashed,
  Copy,
  Download,
  FileArchive,
  FileAudio,
  FileCode2,
  FileImage,
  FileText,
  FileVideo,
  FolderOpen,
  FolderTree,
  HardDrive,
  Layers3,
  LoaderCircle,
  LockKeyhole,
  RefreshCcw,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  TableProperties,
  UploadCloud,
  X,
  Zap,
} from 'lucide-react';
import NotFound from '@/pages/not-found';

// ─── Types ────────────────────────────────────────────────────────────────────

type ScanState = 'empty' | 'analyzing' | 'result' | 'error';
type FileKind = 'imagem' | 'video' | 'audio' | 'documento' | 'arquivo' | 'código' | 'outro';
type PipelineStage = 'observe' | 'understand' | 'identify' | 'decide';

type FileRecord = {
  file: File;
  kind: FileKind;
  sig: string; // quick_signature (size + first-chunk hash)
  orgDest: string; // planned organization destination
};

type OrgPlanEntry = {
  dest: string;
  count: number;
  bytes: number;
  example: string;
};

type ExtStat = {
  ext: string;
  count: number;
  bytes: number;
};

type ScanResult = {
  files: FileRecord[];
  totalBytes: number;
  distribution: { kind: FileKind; count: number; bytes: number }[];
  oldest: number;
  newest: number;
  duplicateGroups: FileRecord[][];
  unknownTypeCount: number;
  orgPlan: OrgPlanEntry[];
  topExtensions: ExtStat[];
  uniqueExtCount: number;
  scanDate: string;
};

// ─── Constants ────────────────────────────────────────────────────────────────

const kindLabels: Record<FileKind, string> = {
  imagem: 'Imagens',
  video: 'Vídeos',
  audio: 'Áudios',
  documento: 'Documentos',
  arquivo: 'Compactados',
  código: 'Código',
  outro: 'Outros',
};

const kindColors: Record<FileKind, string> = {
  imagem: '#d88b43',
  video: '#336d6c',
  audio: '#926b86',
  documento: '#758b5c',
  arquivo: '#b6784c',
  código: '#536c82',
  outro: '#89918b',
};

const PIPELINE_STAGES: { id: PipelineStage; label: string; desc: string }[] = [
  { id: 'observe', label: 'Observe', desc: 'Catalogando nomes, tamanhos e datas' },
  { id: 'understand', label: 'Understand', desc: 'Inferindo categorias e assinaturas' },
  { id: 'identify', label: 'Identify', desc: 'Detectando duplicatas e padrões' },
  { id: 'decide', label: 'Decide', desc: 'Gerando plano de organização' },
];

// ─── EddY Rules Engine (browser port of decide.py DEFAULT_RULES) ──────────────

const EDDY_RULES: { type: string; keywords?: string[]; exts?: string[]; dest: string }[] = [
  // Propriedade Visual — personagens
  { type: 'name_contains', keywords: ['isabella', 'isbl', 'isa_'], dest: 'Sistema de Propriedade Visual/Isabella' },
  { type: 'name_contains', keywords: ['viviane', 'vivian'], dest: 'Sistema de Propriedade Visual/Viviane' },
  { type: 'name_contains', keywords: ['catarina'], dest: 'Sistema de Propriedade Visual/Catarina' },
  { type: 'name_contains', keywords: ['mirella'], dest: 'Sistema de Propriedade Visual/Mirella' },
  { type: 'name_contains', keywords: ['sophia'], dest: 'Sistema de Propriedade Visual/Sophia' },
  { type: 'name_contains', keywords: ['yasmin'], dest: 'Sistema de Propriedade Visual/Yasmin' },
  // Extensões
  { type: 'ext_in', exts: ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.heic', '.tiff', '.psd', '.ai', '.svg'], dest: '00_ARQUIVO_GERAL/01_IMAGENS' },
  { type: 'ext_in', exts: ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.m4v', '.webm'], dest: '00_ARQUIVO_GERAL/02_VIDEOS' },
  { type: 'ext_in', exts: ['.mp3', '.flac', '.wav', '.aac', '.ogg', '.m4a', '.wma', '.aiff'], dest: '00_ARQUIVO_GERAL/04_AUDIO' },
  { type: 'ext_in', exts: ['.zip', '.rar', '.7z', '.gz', '.tar', '.bz2'], dest: '00_ARQUIVO_GERAL/05_COMPACTADOS' },
  { type: 'ext_in', exts: ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.epub', '.odt', '.csv'], dest: '00_ARQUIVO_GERAL/03_DOCUMENTOS' },
  { type: 'ext_in', exts: ['.js', '.ts', '.tsx', '.jsx', '.py', '.css', '.html', '.json', '.yml', '.yaml', '.sh', '.md', '.sql', '.bat', '.ps1'], dest: '00_ARQUIVO_GERAL/06_CODIGO' },
  // Fallback
  { type: 'fallback', dest: '00_ARQUIVO_GERAL/99_OUTROS' },
];

function resolveOrg(file: File): string {
  const name = file.name.toLowerCase();
  const ext = '.' + (file.name.split('.').pop() ?? '').toLowerCase();
  for (const rule of EDDY_RULES) {
    if (rule.type === 'name_contains' && rule.keywords) {
      if (rule.keywords.some((k) => name.includes(k))) return rule.dest;
    }
    if (rule.type === 'ext_in' && rule.exts) {
      if (rule.exts.includes(ext)) return rule.dest;
    }
    if (rule.type === 'fallback') return rule.dest;
  }
  return '00_ARQUIVO_GERAL/99_OUTROS';
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function getFileKind(file: File): FileKind {
  const extension = file.name.split('.').pop()?.toLowerCase() ?? '';
  if (file.type.startsWith('image/') || ['psd', 'ai', 'sketch', 'fig', 'svg'].includes(extension)) return 'imagem';
  if (file.type.startsWith('video/') || ['mov', 'mp4', 'avi', 'mkv', 'webm', 'm4v', 'wmv'].includes(extension)) return 'video';
  if (file.type.startsWith('audio/') || ['mp3', 'wav', 'aiff', 'flac', 'm4a', 'aac', 'wma', 'ogg'].includes(extension)) return 'audio';
  if (file.type.startsWith('text/') || file.type.includes('pdf') || ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'csv', 'epub'].includes(extension)) return 'documento';
  if (['zip', 'rar', '7z', 'tar', 'gz', 'bz2'].includes(extension)) return 'arquivo';
  if (['js', 'ts', 'tsx', 'jsx', 'css', 'html', 'json', 'py', 'sql', 'md', 'sh', 'bat', 'yaml', 'yml'].includes(extension)) return 'código';
  return 'outro';
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const unitIndex = Math.floor(Math.log(bytes) / Math.log(1024));
  const value = bytes / Math.pow(1024, unitIndex);
  return `${new Intl.NumberFormat('pt-BR', { maximumFractionDigits: value < 10 ? 1 : 0 }).format(value)} ${units[unitIndex]}`;
}

function formatDate(timestamp: number): string {
  if (!timestamp) return 'Data não informada';
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium' }).format(new Date(timestamp));
}

function getFileIcon(kind: FileKind, size = 18) {
  const props = { size, strokeWidth: 1.8 };
  if (kind === 'imagem') return <FileImage {...props} />;
  if (kind === 'video') return <FileVideo {...props} />;
  if (kind === 'audio') return <FileAudio {...props} />;
  if (kind === 'arquivo') return <FileArchive {...props} />;
  if (kind === 'código') return <FileCode2 {...props} />;
  return <FileText {...props} />;
}

/** Quick signature: SHA-1 of (size + first 2 MB) — mirrors Python's quick_signature() */
async function quickSignature(file: File): Promise<string> {
  const PARTIAL = 2 * 1024 * 1024;
  const slice = file.slice(0, PARTIAL);
  const buffer = await slice.arrayBuffer();
  const sizeBytes = new TextEncoder().encode(String(file.size));
  const combined = new Uint8Array(sizeBytes.byteLength + buffer.byteLength);
  combined.set(sizeBytes);
  combined.set(new Uint8Array(buffer), sizeBytes.byteLength);
  const hashBuffer = await crypto.subtle.digest('SHA-1', combined);
  return Array.from(new Uint8Array(hashBuffer))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

// ─── Async scan pipeline ──────────────────────────────────────────────────────

async function runPipeline(
  files: File[],
  onStage: (stage: PipelineStage, progress: number) => void,
): Promise<ScanResult> {
  // Stage 1 — Observe: catalogue names, sizes, dates
  onStage('observe', 5);
  await new Promise((r) => setTimeout(r, 180));

  const extMap = new Map<string, { count: number; bytes: number }>();
  for (const file of files) {
    const ext = '.' + (file.name.split('.').pop()?.toLowerCase() ?? '');
    const cur = extMap.get(ext) ?? { count: 0, bytes: 0 };
    extMap.set(ext, { count: cur.count + 1, bytes: cur.bytes + file.size });
  }

  onStage('observe', 20);
  await new Promise((r) => setTimeout(r, 80));

  // Stage 2 — Understand: infer kinds + compute quick signatures
  onStage('understand', 22);

  const BATCH = 40;
  const records: Omit<FileRecord, 'orgDest'>[] = [];
  for (let i = 0; i < files.length; i += BATCH) {
    const batch = files.slice(i, i + BATCH);
    const sigs = await Promise.all(batch.map(quickSignature));
    batch.forEach((file, bi) =>
      records.push({ file, kind: getFileKind(file), sig: sigs[bi] }),
    );
    onStage('understand', 22 + Math.round(((i + BATCH) / files.length) * 38));
    if (i % (BATCH * 3) === 0) await new Promise((r) => setTimeout(r, 0));
  }

  onStage('understand', 60);
  await new Promise((r) => setTimeout(r, 80));

  // Stage 3 — Identify: detect duplicates
  onStage('identify', 62);

  const sigGroups = new Map<string, typeof records>();
  for (const rec of records) {
    const group = sigGroups.get(rec.sig) ?? [];
    group.push(rec);
    sigGroups.set(rec.sig, group);
  }
  const duplicateGroups: FileRecord[][] = [];
  // will be finalised once orgDest is attached
  const dupSigs = new Set<string>();
  for (const [sig, group] of sigGroups) {
    if (group.length > 1) dupSigs.add(sig);
  }

  onStage('identify', 80);
  await new Promise((r) => setTimeout(r, 80));

  // Stage 4 — Decide: apply EddY rules and generate org plan
  onStage('decide', 82);

  const finalRecords: FileRecord[] = records.map((rec) => ({
    ...rec,
    orgDest: resolveOrg(rec.file),
  }));

  for (const [sig] of sigGroups) {
    if (dupSigs.has(sig)) {
      duplicateGroups.push(finalRecords.filter((r) => r.sig === sig));
    }
  }

  // Build org plan
  const orgMap = new Map<string, OrgPlanEntry>();
  for (const rec of finalRecords) {
    const entry = orgMap.get(rec.orgDest) ?? { dest: rec.orgDest, count: 0, bytes: 0, example: rec.file.name };
    entry.count++;
    entry.bytes += rec.file.size;
    orgMap.set(rec.orgDest, entry);
  }
  const orgPlan = [...orgMap.values()].sort((a, b) => b.count - a.count);

  // Distribution
  const distMap = new Map<FileKind, { count: number; bytes: number }>();
  for (const rec of finalRecords) {
    const cur = distMap.get(rec.kind) ?? { count: 0, bytes: 0 };
    distMap.set(rec.kind, { count: cur.count + 1, bytes: cur.bytes + rec.file.size });
  }
  const distribution = [...distMap.entries()]
    .map(([kind, vals]) => ({ kind, ...vals }))
    .sort((a, b) => b.bytes - a.bytes);

  // Top extensions
  const topExtensions = [...extMap.entries()]
    .map(([ext, vals]) => ({ ext, ...vals }))
    .sort((a, b) => b.bytes - a.bytes)
    .slice(0, 15);

  const dates = files.map((f) => f.lastModified).filter(Boolean);

  onStage('decide', 100);
  await new Promise((r) => setTimeout(r, 60));

  return {
    files: finalRecords,
    totalBytes: files.reduce((t, f) => t + f.size, 0),
    distribution,
    oldest: dates.length ? Math.min(...dates) : 0,
    newest: dates.length ? Math.max(...dates) : 0,
    duplicateGroups,
    unknownTypeCount: finalRecords.filter((r) => r.kind === 'outro').length,
    orgPlan,
    topExtensions,
    uniqueExtCount: extMap.size,
    scanDate: new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date()),
  };
}

// ─── Export: Mapa do Caos HTML ─────────────────────────────────────────────────

function generateMapaDoCalos(result: ScanResult): string {
  const duplicateCount = result.duplicateGroups.reduce((t, g) => t + g.length, 0);
  const catRows = result.distribution
    .map(
      (d) =>
        `<tr><td>${kindLabels[d.kind]}</td><td>${new Intl.NumberFormat('pt-BR').format(d.count)}</td><td>${formatBytes(d.bytes)}</td></tr>`,
    )
    .join('\n');
  const extRows = result.topExtensions
    .map(
      (e) =>
        `<tr><td>${e.ext || '(sem extensão)'}</td><td>${new Intl.NumberFormat('pt-BR').format(e.count)}</td><td>${formatBytes(e.bytes)}</td></tr>`,
    )
    .join('\n');
  const planRows = result.orgPlan
    .map(
      (p) =>
        `<tr><td><code>${p.dest}</code></td><td>${new Intl.NumberFormat('pt-BR').format(p.count)}</td><td>${formatBytes(p.bytes)}</td><td>${p.example}</td></tr>`,
    )
    .join('\n');

  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mapa do Caos Digital — NeverLost · EddY OS</title>
<style>
  body { background:#0b0b0b; color:#e8e2d9; font-family:'Segoe UI',Arial,sans-serif; margin:0; padding:24px; }
  h1 { color:#d88b43; font-size:1.9rem; margin-bottom:4px; }
  h2 { color:#4ab5b4; font-size:1.1rem; margin:28px 0 10px; border-bottom:1px solid #1e3a3a; padding-bottom:6px; }
  .meta { color:#7a9090; font-size:.82rem; margin-bottom:28px; font-family:monospace; }
  .kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin-bottom:28px; }
  .kpi { background:#0e2222; border:1px solid #1e3a3a; border-radius:10px; padding:16px 18px; }
  .kpi-label { color:#7a9090; font-size:.72rem; text-transform:uppercase; letter-spacing:.12em; font-family:monospace; }
  .kpi-value { color:#00c9a7; font-size:1.65rem; font-weight:700; margin-top:4px; }
  table { width:100%; border-collapse:collapse; margin-bottom:8px; font-size:.88rem; }
  th,td { border:1px solid #1e3a3a; padding:8px 10px; text-align:left; }
  th { background:#0e2222; color:#4ab5b4; font-family:monospace; font-size:.76rem; letter-spacing:.08em; text-transform:uppercase; }
  tr:hover td { background:#0f2828; }
  code { background:#0e2222; padding:2px 5px; border-radius:4px; font-size:.82em; color:#d88b43; }
  .footer { margin-top:48px; border-top:1px solid #1e3a3a; padding-top:14px; color:#3a5454; font-size:.78rem; font-family:monospace; }
  .tag { display:inline-block; background:#0e2222; border:1px solid #1e3a3a; color:#4ab5b4; border-radius:20px; padding:2px 10px; font-size:.72rem; font-family:monospace; margin-right:6px; }
</style>
</head>
<body>
<h1>Mapa do Caos Digital</h1>
<p class="meta">
  <span class="tag">NeverLost Scanner · EddY OS</span>
  <span class="tag">Gerado em ${result.scanDate}</span>
  <span class="tag">100% local · sem upload</span>
</p>

<div class="kpi-grid">
  <div class="kpi"><div class="kpi-label">Total de Arquivos</div><div class="kpi-value">${new Intl.NumberFormat('pt-BR').format(result.files.length)}</div></div>
  <div class="kpi"><div class="kpi-label">Tamanho Total</div><div class="kpi-value">${formatBytes(result.totalBytes)}</div></div>
  <div class="kpi"><div class="kpi-label">Duplicatas</div><div class="kpi-value">${duplicateCount > 0 ? new Intl.NumberFormat('pt-BR').format(duplicateCount) : '—'}</div></div>
  <div class="kpi"><div class="kpi-label">Extensões Únicas</div><div class="kpi-value">${result.uniqueExtCount}</div></div>
  <div class="kpi"><div class="kpi-label">Período</div><div class="kpi-value">${result.oldest ? new Date(result.oldest).getFullYear() + '–' + new Date(result.newest).getFullYear() : '—'}</div></div>
</div>

<h2>Distribuição por Categoria</h2>
<table>
  <thead><tr><th>Categoria</th><th>Arquivos</th><th>Tamanho</th></tr></thead>
  <tbody>${catRows}</tbody>
</table>

<h2>Top Extensões por Volume</h2>
<table>
  <thead><tr><th>Extensão</th><th>Arquivos</th><th>Tamanho</th></tr></thead>
  <tbody>${extRows}</tbody>
</table>

<h2>Plano de Organização EddY (Decide)</h2>
<table>
  <thead><tr><th>Destino (EddY_Organizado)</th><th>Arquivos</th><th>Tamanho</th><th>Exemplo</th></tr></thead>
  <tbody>${planRows}</tbody>
</table>

<div class="footer">
  Relatório gerado pelo NeverLost Scanner · EddY OS — Digital Sovereignty System · EDS<br>
  Modo Observer: somente leitura · nenhum arquivo foi movido ou alterado
</div>
</body>
</html>`;
}

function downloadHtml(html: string, filename: string) {
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ─── UI Components ────────────────────────────────────────────────────────────

function StatCard({
  label,
  value,
  detail,
  icon,
}: {
  label: string;
  value: string;
  detail: string;
  icon: React.ReactNode;
}) {
  return (
    <div
      className="hover-lift rounded-2xl border bg-card px-5 py-5"
      data-testid={`stat-${label.toLowerCase().replaceAll(' ', '-')}`}
    >
      <div className="mb-5 flex items-center justify-between text-muted-foreground">
        <span className="font-mono-ui text-[10px] uppercase tracking-[0.17em]">{label}</span>
        <span className="text-primary/70">{icon}</span>
      </div>
      <strong className="font-display block text-[2.1rem] font-semibold leading-none tracking-[-0.04em] text-foreground">
        {value}
      </strong>
      <p className="mt-2 text-xs text-muted-foreground">{detail}</p>
    </div>
  );
}

function UploadPanel({ onFiles }: { onFiles: (files: File[]) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files ?? []);
    if (files.length) onFiles(files);
    event.target.value = '';
  };

  const acceptDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    const files = Array.from(event.dataTransfer.files ?? []);
    if (files.length) onFiles(files);
  };

  return (
    <div
      className={`relative overflow-hidden rounded-[1.4rem] border-2 border-dashed p-7 transition-colors duration-300 sm:p-10 ${isDragging ? 'border-accent bg-accent/10' : 'border-primary/25 bg-card/75'}`}
      onDragEnter={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragOver={(e) => e.preventDefault()}
      onDragLeave={(e) => { if (e.currentTarget === e.target) setIsDragging(false); }}
      onDrop={acceptDrop}
      data-testid="upload-dropzone"
    >
      <div className="absolute -right-10 -top-10 h-36 w-36 rounded-full border border-accent/20" />
      <div className="absolute -right-5 -top-5 h-26 w-26 rounded-full border border-accent/20" />
      <div className="relative mx-auto max-w-md text-center">
        <div className="mx-auto mb-5 grid h-16 w-16 place-items-center rounded-full bg-primary text-primary-foreground shadow-[0_0_0_9px_rgba(38,91,91,0.08)]">
          <UploadCloud size={26} strokeWidth={1.6} />
        </div>
        <p className="font-display text-2xl font-semibold tracking-[-0.03em]">Comece pelo que já está aí.</p>
        <p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-muted-foreground">
          Arraste arquivos para este espaço ou abra uma pasta local. O NeverLost lê apenas metadados e assinaturas, direto no seu navegador.
        </p>
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="mt-7 inline-flex min-h-12 items-center gap-2 rounded-full bg-accent px-6 text-sm font-bold text-foreground shadow-[0_8px_22px_rgba(216,139,67,0.22)] transition-transform hover:-translate-y-0.5 active:translate-y-0"
          data-testid="button-select-files"
        >
          <FolderOpen size={17} />
          Selecionar arquivos
        </button>
        <input
          ref={inputRef}
          onChange={handleInput}
          className="sr-only"
          type="file"
          multiple
          aria-label="Selecionar arquivos para analisar"
          data-testid="input-file-upload"
        />
        <p className="mt-4 font-mono-ui text-[10px] uppercase tracking-[0.14em] text-muted-foreground">
          Múltiplos arquivos · sem envio para a nuvem
        </p>
      </div>
    </div>
  );
}

function PipelineStageBar({
  activeStage,
  progress,
  count,
}: {
  activeStage: PipelineStage;
  progress: number;
  count: number;
}) {
  const activeIdx = PIPELINE_STAGES.findIndex((s) => s.id === activeStage);
  const activeInfo = PIPELINE_STAGES[activeIdx];
  return (
    <div className="rounded-[1.4rem] border bg-card p-7 sm:p-10" data-testid="state-analyzing">
      <div className="mx-auto max-w-lg">
        {/* Scanner icon */}
        <div className="relative mx-auto mb-8 grid h-20 w-20 place-items-center">
          <div className="scanner-ring absolute inset-0 rounded-full border border-accent/60" />
          <div className="absolute inset-3 rounded-full border border-primary/20" />
          <ScanSearch size={28} className="relative text-primary" strokeWidth={1.5} />
        </div>

        {/* Pipeline stages */}
        <div className="mb-8 grid grid-cols-4 gap-1.5">
          {PIPELINE_STAGES.map((stage, idx) => {
            const done = idx < activeIdx;
            const active = idx === activeIdx;
            return (
              <div key={stage.id} className="flex flex-col items-center gap-2">
                <div
                  className={`flex h-8 w-8 items-center justify-center rounded-full border text-[11px] font-bold transition-all duration-500 font-mono-ui ${
                    done
                      ? 'border-accent bg-accent text-foreground'
                      : active
                      ? 'border-primary bg-primary text-primary-foreground shadow-[0_0_0_4px_rgba(38,91,91,0.12)]'
                      : 'border-border bg-secondary text-muted-foreground'
                  }`}
                >
                  {done ? <Check size={13} strokeWidth={2.5} /> : idx + 1}
                </div>
                <span
                  className={`text-center font-mono-ui text-[9px] uppercase tracking-[0.08em] ${
                    active ? 'text-primary font-bold' : done ? 'text-accent' : 'text-muted-foreground'
                  }`}
                >
                  {stage.label}
                </span>
              </div>
            );
          })}
        </div>

        {/* Active stage info */}
        <div className="text-center">
          <p className="font-mono-ui text-[10px] uppercase tracking-[0.18em] text-accent">
            {activeInfo?.label}
          </p>
          <h2 className="font-display mt-2 text-2xl font-semibold tracking-[-0.04em]">
            {activeInfo?.desc}
          </h2>
          <p className="mt-1.5 text-sm text-muted-foreground">
            {count} {count === 1 ? 'arquivo' : 'arquivos'} · processamento local
          </p>
        </div>

        {/* Progress bar */}
        <div className="mt-7">
          <div className="mb-1.5 flex justify-between font-mono-ui text-[10px] uppercase tracking-[0.1em] text-muted-foreground">
            <span>Progresso</span>
            <span>{progress}%</span>
          </div>
          <div
            className="h-2 overflow-hidden rounded-full bg-secondary"
            role="progressbar"
            aria-valuenow={progress}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <div
              className="h-full rounded-full bg-accent transition-[width] duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function Distribution({ result }: { result: ScanResult }) {
  const maxBytes = result.distribution[0]?.bytes ?? 1;
  return (
    <section className="rounded-2xl border bg-card p-6 sm:p-7" data-testid="section-distribution">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono-ui text-[10px] uppercase tracking-[0.16em] text-muted-foreground">01 / composição</p>
          <h3 className="font-display mt-2 text-2xl font-semibold tracking-[-0.035em]">Onde o espaço está.</h3>
        </div>
        <Layers3 className="mt-1 text-primary/50" size={22} strokeWidth={1.5} />
      </div>
      <div className="mt-7 space-y-4">
        {result.distribution.map((item) => (
          <div key={item.kind} data-testid={`distribution-${item.kind}`}>
            <div className="mb-1.5 flex items-center justify-between gap-3 text-sm">
              <span className="flex items-center gap-2 font-medium">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: kindColors[item.kind] }} />
                {kindLabels[item.kind]}
              </span>
              <span className="font-mono-ui text-[10px] text-muted-foreground">
                {item.count} · {formatBytes(item.bytes)}
              </span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-secondary">
              <div
                className="h-full rounded-full transition-[width] duration-700"
                style={{
                  width: `${Math.max(5, (item.bytes / maxBytes) * 100)}%`,
                  backgroundColor: kindColors[item.kind],
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function TopExtensions({ result }: { result: ScanResult }) {
  const [showAll, setShowAll] = useState(false);
  const visible = showAll ? result.topExtensions : result.topExtensions.slice(0, 8);
  const maxBytes = result.topExtensions[0]?.bytes ?? 1;

  return (
    <section className="rounded-2xl border bg-card p-6 sm:p-7" data-testid="section-top-extensions">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono-ui text-[10px] uppercase tracking-[0.16em] text-muted-foreground">02 / extensões</p>
          <h3 className="font-display mt-2 text-2xl font-semibold tracking-[-0.035em]">Top extensões por volume.</h3>
        </div>
        <TableProperties className="mt-1 text-primary/50" size={20} strokeWidth={1.5} />
      </div>
      <div className="mt-6 space-y-3">
        {visible.map((ext) => (
          <div key={ext.ext} className="flex items-center gap-3">
            <span className="w-20 shrink-0 rounded-md bg-secondary px-2 py-1 text-center font-mono-ui text-[10px] uppercase tracking-[0.08em] text-muted-foreground">
              {ext.ext || 'sem ext'}
            </span>
            <div className="flex-1">
              <div className="h-1.5 overflow-hidden rounded-full bg-secondary">
                <div
                  className="h-full rounded-full bg-primary/60 transition-[width] duration-700"
                  style={{ width: `${Math.max(4, (ext.bytes / maxBytes) * 100)}%` }}
                />
              </div>
            </div>
            <span className="w-16 shrink-0 text-right font-mono-ui text-[10px] text-muted-foreground">
              {new Intl.NumberFormat('pt-BR').format(ext.count)}
            </span>
            <span className="w-16 shrink-0 text-right font-mono-ui text-[10px] text-muted-foreground">
              {formatBytes(ext.bytes)}
            </span>
          </div>
        ))}
      </div>
      {result.topExtensions.length > 8 && (
        <button
          type="button"
          onClick={() => setShowAll((v) => !v)}
          className="mt-4 flex items-center gap-1.5 text-xs font-bold text-primary hover:underline"
        >
          {showAll ? 'Ver menos' : `Ver ${result.topExtensions.length - 8} mais`}
          <ChevronDown size={13} className={`transition-transform ${showAll ? 'rotate-180' : ''}`} />
        </button>
      )}
      <p className="mt-3 font-mono-ui text-[9px] uppercase tracking-[0.1em] text-muted-foreground">
        {result.uniqueExtCount} extensões únicas encontradas
      </p>
    </section>
  );
}

function OrganizationPlan({ result }: { result: ScanResult }) {
  const [showAll, setShowAll] = useState(false);
  const visible = showAll ? result.orgPlan : result.orgPlan.slice(0, 7);

  // Separate Sistema de Propriedade Visual from ARQUIVO_GERAL
  const hasSPV = result.orgPlan.some((p) => p.dest.startsWith('Sistema de Propriedade Visual'));

  return (
    <section className="rounded-2xl border bg-card" data-testid="section-org-plan">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b px-6 py-6 sm:px-7">
        <div>
          <p className="font-mono-ui text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
            Etapa Decide / EddY
          </p>
          <h3 className="font-display mt-2 text-2xl font-semibold tracking-[-0.035em]">
            Plano de organização.
          </h3>
          <p className="mt-1.5 max-w-md text-sm text-muted-foreground">
            Onde o EddY colocaria cada arquivo em{' '}
            <code className="rounded bg-secondary px-1 py-0.5 font-mono-ui text-[10px]">EddY_Organizado/</code>{' '}
            se executado. Modo dry-run — nenhum arquivo foi movido.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <FolderTree size={18} className="text-primary/50" strokeWidth={1.5} />
          <span className="rounded-full bg-secondary px-3 py-1.5 font-mono-ui text-[10px] uppercase tracking-[0.1em] text-muted-foreground">
            {result.orgPlan.length} destinos
          </span>
        </div>
      </div>

      {hasSPV && (
        <div className="border-b bg-accent/5 px-6 py-3 sm:px-7">
          <p className="font-mono-ui text-[10px] uppercase tracking-[0.12em] text-accent">
            ⚡ Sistema de Propriedade Visual detectado
          </p>
          <p className="mt-0.5 text-xs text-muted-foreground">
            Arquivos com nomes de personagens EddY serão roteados com prioridade máxima.
          </p>
        </div>
      )}

      <div className="divide-y">
        {visible.map((entry) => {
          const isSpv = entry.dest.startsWith('Sistema de Propriedade Visual');
          const parts = entry.dest.split('/');
          const folder = parts[0];
          const subfolder = parts.slice(1).join('/');
          return (
            <div
              key={entry.dest}
              className="flex items-center gap-4 px-6 py-4 sm:px-7"
              data-testid={`org-row-${entry.dest}`}
            >
              <div
                className={`grid h-9 w-9 shrink-0 place-items-center rounded-xl text-primary/70 ${isSpv ? 'bg-accent/15' : 'bg-secondary'}`}
              >
                <FolderOpen size={17} strokeWidth={1.7} className={isSpv ? 'text-accent' : ''} />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium" title={entry.dest}>
                  <span className="text-muted-foreground">{folder}/</span>
                  {subfolder && <span className="font-semibold">{subfolder}</span>}
                </p>
                <p className="mt-0.5 truncate font-mono-ui text-[10px] uppercase tracking-[0.07em] text-muted-foreground">
                  Ex: {entry.example}
                </p>
              </div>
              <div className="shrink-0 text-right">
                <p className="font-mono-ui text-xs font-bold text-foreground">
                  {new Intl.NumberFormat('pt-BR').format(entry.count)}{' '}
                  <span className="font-normal text-muted-foreground">arq.</span>
                </p>
                <p className="font-mono-ui text-[10px] text-muted-foreground">{formatBytes(entry.bytes)}</p>
              </div>
            </div>
          );
        })}
      </div>

      {result.orgPlan.length > 7 && (
        <button
          type="button"
          onClick={() => setShowAll((v) => !v)}
          className="flex w-full items-center justify-center gap-2 border-t px-6 py-4 text-xs font-bold text-primary transition-colors hover:bg-secondary/60"
        >
          {showAll ? 'Mostrar menos' : `Ver ${result.orgPlan.length - 7} destinos restantes`}
          <ChevronDown size={15} className={`transition-transform ${showAll ? 'rotate-180' : ''}`} />
        </button>
      )}
    </section>
  );
}

function Recommendations({ result }: { result: ScanResult }) {
  const recommendations = useMemo(() => {
    const items: {
      title: string;
      description: string;
      tone: 'accent' | 'teal' | 'neutral';
      icon: React.ReactNode;
    }[] = [];

    const duplicateCount = result.duplicateGroups.reduce((t, g) => t + g.length, 0);
    const dupBytes = result.duplicateGroups
      .flat()
      .slice(1)
      .reduce((t, r) => t + r.file.size, 0);

    if (result.duplicateGroups.length) {
      items.push({
        title: `${result.duplicateGroups.length} grupo${result.duplicateGroups.length > 1 ? 's' : ''} de duplicatas por assinatura`,
        description: `${duplicateCount} arquivos detectados por quick-signature (tamanho + primeiros 2 MB). Potencial de ${formatBytes(dupBytes)} recuperáveis.`,
        tone: 'accent',
        icon: <Copy size={18} />,
      });
    }

    const spvCount = result.orgPlan.filter((p) => p.dest.startsWith('Sistema de Propriedade Visual')).reduce((t, p) => t + p.count, 0);
    if (spvCount > 0) {
      items.push({
        title: `${spvCount} arquivo${spvCount > 1 ? 's' : ''} no Sistema de Propriedade Visual`,
        description: 'Conteúdo de personagens EddY detectado. EddY os organizaria com prioridade máxima.',
        tone: 'teal',
        icon: <Zap size={18} />,
      });
    }

    const largest = result.files.slice().sort((a, b) => b.file.size - a.file.size)[0];
    if (largest && largest.file.size > 100 * 1024 * 1024) {
      items.push({
        title: `${largest.file.name} concentra peso`,
        description: `${Math.round((largest.file.size / result.totalBytes) * 100)}% do volume analisado em um único arquivo.`,
        tone: 'teal',
        icon: <ArrowUpRight size={18} />,
      });
    }

    if (result.unknownTypeCount) {
      items.push({
        title: `${result.unknownTypeCount} arquivo${result.unknownTypeCount > 1 ? 's' : ''} sem categoria clara`,
        description: 'Vão para 00_ARQUIVO_GERAL/99_OUTROS. Vale nomear ou verificar a extensão antes de organizar.',
        tone: 'neutral',
        icon: <CircleAlert size={18} />,
      });
    }

    if (!items.length) {
      items.push({
        title: 'Acervo com boa legibilidade',
        description: 'Nenhum sinal de duplicidade ou formato indefinido nesta leitura.',
        tone: 'teal',
        icon: <Check size={18} />,
      });
    }
    return items;
  }, [result]);

  return (
    <section className="rounded-2xl border bg-primary p-6 text-primary-foreground sm:p-7" data-testid="section-recommendations">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono-ui text-[10px] uppercase tracking-[0.16em] text-primary-foreground/60">
            próximo movimento
          </p>
          <h3 className="font-display mt-2 text-2xl font-semibold tracking-[-0.035em]">O que merece atenção.</h3>
        </div>
        <Sparkles className="text-accent" size={22} strokeWidth={1.5} />
      </div>
      <div className="mt-6 divide-y divide-primary-foreground/15">
        {recommendations.map((item) => (
          <div className="flex gap-4 py-4 first:pt-0 last:pb-0" key={item.title}>
            <div
              className={`mt-0.5 grid h-9 w-9 shrink-0 place-items-center rounded-full ${
                item.tone === 'accent'
                  ? 'bg-accent text-foreground'
                  : 'bg-primary-foreground/10 text-primary-foreground'
              }`}
            >
              {item.icon}
            </div>
            <div>
              <p className="text-sm font-bold">{item.title}</p>
              <p className="mt-1 text-xs leading-5 text-primary-foreground/65">{item.description}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function FileTable({ result }: { result: ScanResult }) {
  const [showAll, setShowAll] = useState(false);
  const visibleFiles = showAll ? result.files : result.files.slice(0, 8);
  return (
    <section className="rounded-2xl border bg-card" data-testid="section-file-list">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b px-6 py-6 sm:px-7">
        <div>
          <p className="font-mono-ui text-[10px] uppercase tracking-[0.16em] text-muted-foreground">inventário</p>
          <h3 className="font-display mt-2 text-2xl font-semibold tracking-[-0.035em]">Cada arquivo, no lugar.</h3>
        </div>
        <span className="rounded-full bg-secondary px-3 py-1.5 font-mono-ui text-[10px] uppercase tracking-[0.1em] text-muted-foreground">
          {result.files.length} itens
        </span>
      </div>
      <div className="divide-y">
        {visibleFiles.map((record, index) => (
          <div
            className="flex items-center gap-3 px-6 py-4 sm:px-7"
            key={`${record.file.name}-${record.file.size}-${index}`}
            data-testid={`file-row-${index}`}
          >
            <div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-secondary text-primary/70">
              {getFileIcon(record.kind, 17)}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium" title={record.file.name}>
                {record.file.name}
              </p>
              <p className="mt-0.5 truncate font-mono-ui text-[10px] uppercase tracking-[0.08em] text-muted-foreground">
                {kindLabels[record.kind]} · {formatDate(record.file.lastModified)}
              </p>
            </div>
            <div className="shrink-0 text-right">
              <span className="font-mono-ui text-[10px] text-muted-foreground">{formatBytes(record.file.size)}</span>
              <p className="mt-0.5 max-w-[130px] truncate font-mono-ui text-[9px] text-muted-foreground/60" title={record.orgDest}>
                → {record.orgDest.split('/').pop()}
              </p>
            </div>
          </div>
        ))}
      </div>
      {result.files.length > 8 && (
        <button
          type="button"
          onClick={() => setShowAll((v) => !v)}
          className="flex w-full items-center justify-center gap-2 border-t px-6 py-4 text-xs font-bold text-primary transition-colors hover:bg-secondary/60"
          data-testid="button-toggle-file-list"
        >
          {showAll ? 'Mostrar menos' : `Ver os ${result.files.length - 8} restantes`}
          <ChevronDown size={15} className={`transition-transform ${showAll ? 'rotate-180' : ''}`} />
        </button>
      )}
    </section>
  );
}

function ExportBar({ result }: { result: ScanResult }) {
  const [copied, setCopied] = useState(false);

  const handleExport = () => {
    const html = generateMapaDoCalos(result);
    const ts = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    downloadHtml(html, `mapa_do_caos_${ts}.html`);
  };

  const handleCopySig = async () => {
    const lines = [
      `NeverLost · EddY OS — ${result.scanDate}`,
      `Total: ${new Intl.NumberFormat('pt-BR').format(result.files.length)} arqs · ${formatBytes(result.totalBytes)}`,
      `Duplicatas: ${result.duplicateGroups.reduce((t, g) => t + g.length, 0)} · Ext únicas: ${result.uniqueExtCount}`,
    ].join('\n');
    await navigator.clipboard.writeText(lines);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border bg-card px-5 py-4 sm:px-7">
      <div className="flex items-center gap-3">
        <div className="grid h-9 w-9 place-items-center rounded-xl bg-primary text-primary-foreground">
          <Download size={17} strokeWidth={1.8} />
        </div>
        <div>
          <p className="text-sm font-bold">Exportar Mapa do Caos</p>
          <p className="text-xs text-muted-foreground">Relatório HTML idêntico ao NeverLost Observer</p>
        </div>
      </div>
      <div className="flex gap-2">
        <button
          type="button"
          onClick={handleCopySig}
          className="inline-flex min-h-9 items-center gap-1.5 rounded-full border border-primary/20 px-3.5 text-xs font-bold text-primary transition-colors hover:bg-secondary"
        >
          {copied ? <Check size={13} /> : <Copy size={13} />}
          {copied ? 'Copiado' : 'Copiar resumo'}
        </button>
        <button
          type="button"
          onClick={handleExport}
          className="inline-flex min-h-9 items-center gap-1.5 rounded-full bg-primary px-4 text-xs font-bold text-primary-foreground transition-transform hover:-translate-y-0.5"
        >
          <Download size={13} />
          Baixar HTML
        </button>
      </div>
    </div>
  );
}

function Results({ result, onReset }: { result: ScanResult; onReset: () => void }) {
  const duplicateCount = result.duplicateGroups.reduce((t, g) => t + g.length, 0);
  return (
    <div className="mt-12 space-y-5 sm:mt-16" id="diagnostico" data-testid="state-result">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <div className="mb-3 flex items-center gap-2 text-accent">
            <span className="grid h-6 w-6 place-items-center rounded-full bg-accent text-foreground">
              <Check size={14} strokeWidth={2.5} />
            </span>
            <span className="font-mono-ui text-[10px] font-bold uppercase tracking-[0.16em]">
              Pipeline EddY concluído · {result.scanDate}
            </span>
          </div>
          <h2 className="font-display text-4xl font-semibold tracking-[-0.05em] sm:text-5xl">
            O contorno do seu acervo.
          </h2>
          <p className="mt-3 max-w-xl text-sm leading-6 text-muted-foreground">
            Observe → Understand → Identify → Decide. Nenhum arquivo foi enviado, aberto ou movido.
          </p>
        </div>
        <button
          type="button"
          onClick={onReset}
          className="inline-flex min-h-10 items-center justify-center gap-2 self-start rounded-full border border-primary/20 px-4 text-xs font-bold text-primary transition-colors hover:bg-card sm:self-auto"
          data-testid="button-new-analysis"
        >
          <RefreshCcw size={14} />
          Nova análise
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-3 pt-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Itens"
          value={new Intl.NumberFormat('pt-BR').format(result.files.length)}
          detail="arquivos mapeados localmente"
          icon={<Layers3 size={18} />}
        />
        <StatCard
          label="Volume"
          value={formatBytes(result.totalBytes)}
          detail="espaço representado"
          icon={<HardDrive size={18} />}
        />
        <StatCard
          label="Duplicatas"
          value={duplicateCount ? `${duplicateCount}` : 'Nenhuma'}
          detail={duplicateCount ? `em ${result.duplicateGroups.length} grupos (quick-sig)` : 'detectadas por assinatura'}
          icon={<Copy size={18} />}
        />
        <StatCard
          label="Janela"
          value={result.oldest ? `${new Date(result.oldest).getFullYear()}` : '—'}
          detail={result.oldest ? `até ${new Date(result.newest).getFullYear()} · ${result.uniqueExtCount} ext.` : 'datas indisponíveis'}
          icon={<CalendarDays size={18} />}
        />
      </div>

      {/* Distribution + Top Extensions */}
      <div className="grid gap-5 pt-2 lg:grid-cols-2">
        <Distribution result={result} />
        <TopExtensions result={result} />
      </div>

      {/* Organization Plan */}
      <OrganizationPlan result={result} />

      {/* Recommendations + Export */}
      <div className="grid gap-5 lg:grid-cols-[1.1fr_.9fr]">
        <Recommendations result={result} />
        <div className="space-y-5">
          <ExportBar result={result} />
          {/* Pipeline stages summary */}
          <div className="rounded-2xl border bg-card px-6 py-5 sm:px-7">
            <p className="font-mono-ui text-[10px] uppercase tracking-[0.16em] text-muted-foreground mb-4">
              Pipeline EddY
            </p>
            <div className="space-y-3">
              {PIPELINE_STAGES.map((stage) => (
                <div key={stage.id} className="flex items-center gap-3">
                  <span className="grid h-6 w-6 place-items-center rounded-full bg-accent text-foreground">
                    <Check size={11} strokeWidth={2.5} />
                  </span>
                  <div>
                    <p className="font-mono-ui text-[10px] font-bold uppercase tracking-[0.08em] text-accent">
                      {stage.label}
                    </p>
                    <p className="text-xs text-muted-foreground">{stage.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Inventory */}
      <FileTable result={result} />
    </div>
  );
}

function EmptyExperience({ onFiles }: { onFiles: (files: File[]) => void }) {
  return (
    <div className="mt-12 sm:mt-16" id="scanner">
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <p className="font-mono-ui text-[10px] uppercase tracking-[0.18em] text-accent">Etapa Observe / 01</p>
          <h2 className="font-display mt-2 text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">
            Veja o que você tem.
          </h2>
        </div>
        <div className="hidden items-center gap-2 text-muted-foreground sm:flex">
          <CircleDashed size={16} />
          <span className="font-mono-ui text-[10px] uppercase tracking-[0.12em]">Pronto para começar</span>
        </div>
      </div>
      <UploadPanel onFiles={onFiles} />
    </div>
  );
}

function ErrorPanel({ onRetry, message }: { onRetry: () => void; message: string }) {
  return (
    <div
      className="mt-12 rounded-[1.4rem] border border-destructive/30 bg-destructive/5 p-8 text-center sm:mt-16"
      data-testid="state-error"
    >
      <div className="mx-auto grid h-14 w-14 place-items-center rounded-full bg-destructive/10 text-destructive">
        <CircleAlert size={25} />
      </div>
      <h2 className="font-display mt-5 text-3xl font-semibold tracking-[-0.04em]">A leitura não terminou.</h2>
      <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-muted-foreground">{message}</p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-6 inline-flex min-h-11 items-center gap-2 rounded-full bg-primary px-5 text-sm font-bold text-primary-foreground"
        data-testid="button-retry-scan"
      >
        <RefreshCcw size={16} />
        Tentar novamente
      </button>
    </div>
  );
}

// ─── Page ────────────────────────────────────────────────────────────────────

function Home() {
  const [scanState, setScanState] = useState<ScanState>('empty');
  const [result, setResult] = useState<ScanResult | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [progress, setProgress] = useState(0);
  const [activeStage, setActiveStage] = useState<PipelineStage>('observe');
  const [error, setError] = useState('');
  const abortRef = useRef<boolean>(false);

  const analyzeFiles = useCallback((files: File[]) => {
    if (!files.length) return;
    abortRef.current = false;
    setSelectedFiles(files);
    setResult(null);
    setError('');
    setProgress(0);
    setActiveStage('observe');
    setScanState('analyzing');

    runPipeline(files, (stage, prog) => {
      if (!abortRef.current) {
        setActiveStage(stage);
        setProgress(prog);
      }
    })
      .then((res) => {
        if (!abortRef.current) {
          setResult(res);
          setScanState('result');
        }
      })
      .catch((err) => {
        if (!abortRef.current) {
          setError(
            err?.message ||
              'Não foi possível interpretar os metadados. Tente selecionar outra pasta ou conjunto de arquivos.',
          );
          setScanState('error');
        }
      });
  }, []);

  const reset = useCallback(() => {
    abortRef.current = true;
    setSelectedFiles([]);
    setResult(null);
    setProgress(0);
    setError('');
    setScanState('empty');
    window.setTimeout(
      () => document.getElementById('scanner')?.scrollIntoView({ behavior: 'smooth', block: 'center' }),
      20,
    );
  }, []);

  return (
    <main className="page-shell grain min-h-[100dvh] overflow-hidden">
      <header className="mx-auto flex w-full max-w-[1240px] items-center justify-between px-5 py-5 sm:px-8 lg:px-10">
        <a href="#top" className="flex items-center gap-3" data-testid="link-brand">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-primary text-primary-foreground shadow-[0_5px_0_rgba(216,139,67,0.8)]">
            <ScanSearch size={19} strokeWidth={1.8} />
          </span>
          <span className="font-display text-xl font-semibold tracking-[-0.04em]">
            NeverLost{' '}
            <span className="font-sans text-[9px] font-bold uppercase tracking-[0.15em] text-muted-foreground">
              Scanner
            </span>
          </span>
        </a>
        <div className="hidden items-center gap-6 text-xs font-medium text-muted-foreground sm:flex">
          <a href="#como-funciona" className="transition-colors hover:text-foreground" data-testid="link-how-it-works">
            Como funciona
          </a>
          <span className="flex items-center gap-2 font-mono-ui text-[10px] uppercase tracking-[0.1em]">
            <LockKeyhole size={13} /> 100% local
          </span>
        </div>
        <a
          href="#scanner"
          className="inline-flex min-h-9 items-center gap-1.5 rounded-full border border-primary/20 px-3.5 text-xs font-bold text-primary transition-colors hover:bg-card sm:hidden"
          data-testid="link-start-mobile"
        >
          Começar <ArrowDownRight size={14} />
        </a>
      </header>

      <div className="mx-auto max-w-[1240px] px-5 pb-20 sm:px-8 lg:px-10">
        {/* Hero */}
        <section
          className="paper-grid relative mt-4 overflow-hidden rounded-[1.8rem] border border-primary/10 px-6 py-14 sm:mt-8 sm:px-12 sm:py-20 lg:px-20 lg:py-24"
          id="top"
        >
          <div className="pointer-events-none absolute -right-20 -top-28 h-80 w-80 rounded-full border border-accent/20 sm:h-[30rem] sm:w-[30rem]" />
          <div className="pointer-events-none absolute -right-6 -top-14 h-52 w-52 rounded-full border border-accent/15 sm:h-80 sm:w-80" />
          <div className="relative max-w-3xl">
            <div className="rise-in flex items-center gap-3 text-primary">
              <span className="h-px w-9 bg-accent" />
              <span className="font-mono-ui text-[10px] font-bold uppercase tracking-[0.2em]">EDS apresenta</span>
            </div>
            <h1 className="font-display rise-in rise-in-delay-1 mt-6 max-w-3xl text-[3.55rem] font-semibold leading-[.96] tracking-[-0.065em] text-foreground sm:text-7xl lg:text-[6.4rem]">
              O valor escondido{' '}
              <em className="font-normal text-primary">não sumiu.</em>
            </h1>
            <p className="rise-in rise-in-delay-2 mt-7 max-w-xl text-base leading-7 text-muted-foreground sm:text-lg">
              O NeverLost Scanner roda o pipeline EddY no seu navegador: Observe, Understand, Identify, Decide. Mapa do Caos completo, 100% local.
            </p>
            <div className="rise-in rise-in-delay-3 mt-8 flex flex-wrap items-center gap-x-5 gap-y-3">
              <a
                href="#scanner"
                className="inline-flex min-h-12 items-center gap-2 rounded-full bg-primary px-6 text-sm font-bold text-primary-foreground shadow-[0_10px_24px_rgba(31,77,82,0.18)] transition-transform hover:-translate-y-0.5"
                data-testid="link-start-scan"
              >
                Abrir o scanner
                <ArrowDownRight size={17} />
              </a>
              <span className="font-mono-ui text-[10px] uppercase tracking-[0.12em] text-muted-foreground">
                Sem login · sem upload
              </span>
            </div>
          </div>
          <div className="relative mt-14 flex items-end justify-between border-t border-primary/10 pt-5 sm:mt-20">
            <p className="max-w-[210px] text-xs leading-5 text-muted-foreground">
              Uma ferramenta EDS para quem sabe que arquivo parado também é patrimônio.
            </p>
            <div className="hidden text-right sm:block">
              <p className="font-mono-ui text-[10px] uppercase tracking-[0.14em] text-muted-foreground">
                Pipeline EddY / v1
              </p>
              <p className="mt-1 font-display text-lg text-primary">Da dispersão à clareza.</p>
            </div>
          </div>
        </section>

        {/* Scanner states */}
        {scanState === 'empty' && <EmptyExperience onFiles={analyzeFiles} />}
        {scanState === 'analyzing' && (
          <div className="mt-12 sm:mt-16" id="scanner">
            <PipelineStageBar activeStage={activeStage} progress={progress} count={selectedFiles.length} />
          </div>
        )}
        {scanState === 'error' && (
          <ErrorPanel
            message={error}
            onRetry={() => analyzeFiles(selectedFiles)}
          />
        )}
        {scanState === 'result' && result && <Results result={result} onReset={reset} />}

        {/* How it works */}
        <section className="mt-24 border-t border-primary/15 pt-12 sm:mt-32 sm:pt-16" id="como-funciona">
          <div className="grid gap-10 lg:grid-cols-[.75fr_1.25fr] lg:gap-24">
            <div>
              <p className="font-mono-ui text-[10px] uppercase tracking-[0.18em] text-accent">Pipeline EddY</p>
              <h2 className="font-display mt-3 max-w-sm text-4xl font-semibold leading-[1.02] tracking-[-0.05em] sm:text-5xl">
                Antes de produzir, enxergue.
              </h2>
            </div>
            <div className="grid gap-8 sm:grid-cols-4">
              {PIPELINE_STAGES.map((stage, idx) => (
                <div key={stage.id} className="border-t border-primary/20 pt-4">
                  <span className="font-mono-ui text-xs text-accent">0{idx + 1}</span>
                  <h3 className="mt-5 text-sm font-bold">{stage.label}</h3>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">{stage.desc}.</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <footer className="mt-20 flex flex-col justify-between gap-3 border-t border-primary/15 py-7 text-xs text-muted-foreground sm:mt-28 sm:flex-row sm:items-center">
          <p className="font-display text-base text-foreground">
            EDS <span className="font-sans text-xs text-muted-foreground">· patrimônio em movimento</span>
          </p>
          <p className="flex items-center gap-2 font-mono-ui text-[10px] uppercase tracking-[0.1em]">
            <ShieldCheck size={14} className="text-primary" /> seus arquivos permanecem no seu dispositivo
          </p>
        </footer>
      </div>
    </main>
  );
}

// ─── Router ──────────────────────────────────────────────────────────────────

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}>
      <Router />
    </WouterRouter>
  );
}

export default App;
