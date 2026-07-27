import { useEffect, useMemo, useRef, useState } from 'react';
import { Route, Router as WouterRouter, Switch } from 'wouter';
import {
  ArrowDownRight,
  ArrowUpRight,
  CalendarDays,
  Check,
  ChevronDown,
  CircleAlert,
  CircleDashed,
  FileArchive,
  FileAudio,
  FileCode2,
  FileImage,
  FileText,
  FileVideo,
  FolderOpen,
  HardDrive,
  Layers3,
  LoaderCircle,
  LockKeyhole,
  RefreshCcw,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  X,
  Zap,
} from 'lucide-react';
import NotFound from '@/pages/not-found';

type ScanState = 'empty' | 'analyzing' | 'result' | 'error';
type FileKind = 'imagem' | 'video' | 'audio' | 'documento' | 'arquivo' | 'código' | 'outro';

type FileRecord = {
  file: File;
  kind: FileKind;
};

type ScanResult = {
  files: FileRecord[];
  totalBytes: number;
  distribution: { kind: FileKind; count: number; bytes: number }[];
  oldest: number;
  newest: number;
  duplicateGroups: FileRecord[][];
  unknownTypeCount: number;
};

const kindLabels: Record<FileKind, string> = {
  imagem: 'Imagens',
  video: 'Vídeos',
  audio: 'Áudios',
  documento: 'Documentos',
  arquivo: 'Arquivos compactados',
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

function getFileKind(file: File): FileKind {
  const extension = file.name.split('.').pop()?.toLowerCase() ?? '';
  if (file.type.startsWith('image/') || ['psd', 'ai', 'sketch', 'fig'].includes(extension)) return 'imagem';
  if (file.type.startsWith('video/') || ['mov', 'mp4', 'avi', 'mkv', 'webm'].includes(extension)) return 'video';
  if (file.type.startsWith('audio/') || ['mp3', 'wav', 'aiff', 'flac', 'm4a'].includes(extension)) return 'audio';
  if (file.type.startsWith('text/') || file.type.includes('pdf') || ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'csv'].includes(extension)) return 'documento';
  if (['zip', 'rar', '7z', 'tar', 'gz'].includes(extension)) return 'arquivo';
  if (['js', 'ts', 'tsx', 'jsx', 'css', 'html', 'json', 'py', 'sql', 'md'].includes(extension)) return 'código';
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

function buildResult(files: File[]): ScanResult {
  const records = files.map((file) => ({ file, kind: getFileKind(file) }));
  const grouped = records.reduce<Record<string, FileRecord[]>>((accumulator, record) => {
    const key = `${record.file.name.toLowerCase()}::${record.file.size}`;
    accumulator[key] = [...(accumulator[key] ?? []), record];
    return accumulator;
  }, {});
  const distribution = Object.entries(
    records.reduce<Record<FileKind, { count: number; bytes: number }>>((accumulator, record) => {
      accumulator[record.kind] = {
        count: (accumulator[record.kind]?.count ?? 0) + 1,
        bytes: (accumulator[record.kind]?.bytes ?? 0) + record.file.size,
      };
      return accumulator;
    }, {} as Record<FileKind, { count: number; bytes: number }>),
  )
    .map(([kind, values]) => ({ kind: kind as FileKind, ...values }))
    .sort((a, b) => b.bytes - a.bytes);

  const dates = files.map((file) => file.lastModified).filter(Boolean);
  return {
    files: records,
    totalBytes: files.reduce((total, file) => total + file.size, 0),
    distribution,
    oldest: dates.length ? Math.min(...dates) : 0,
    newest: dates.length ? Math.max(...dates) : 0,
    duplicateGroups: Object.values(grouped).filter((group) => group.length > 1),
    unknownTypeCount: records.filter((record) => record.kind === 'outro').length,
  };
}

function StatCard({ label, value, detail, icon }: { label: string; value: string; detail: string; icon: React.ReactNode }) {
  return (
    <div className="hover-lift rounded-2xl border bg-card px-5 py-5" data-testid={`stat-${label.toLowerCase().replaceAll(' ', '-')}`}>
      <div className="mb-5 flex items-center justify-between text-muted-foreground">
        <span className="font-mono-ui text-[10px] uppercase tracking-[0.17em]">{label}</span>
        <span className="text-primary/70">{icon}</span>
      </div>
      <strong className="font-display block text-[2.1rem] font-semibold leading-none tracking-[-0.04em] text-foreground">{value}</strong>
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
      onDragEnter={(event) => { event.preventDefault(); setIsDragging(true); }}
      onDragOver={(event) => event.preventDefault()}
      onDragLeave={(event) => { if (event.currentTarget === event.target) setIsDragging(false); }}
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
          Arraste arquivos para este espaço ou abra uma pasta local. O NeverLost lê apenas metadados, direto no seu navegador.
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
        <input ref={inputRef} onChange={handleInput} className="sr-only" type="file" multiple aria-label="Selecionar arquivos para analisar" data-testid="input-file-upload" />
        <p className="mt-4 font-mono-ui text-[10px] uppercase tracking-[0.14em] text-muted-foreground">Múltiplos arquivos · sem envio para a nuvem</p>
      </div>
    </div>
  );
}

function AnalyzingPanel({ count, progress }: { count: number; progress: number }) {
  return (
    <div className="rounded-[1.4rem] border bg-card p-7 sm:p-10" data-testid="state-analyzing">
      <div className="mx-auto max-w-lg text-center">
        <div className="relative mx-auto mb-7 grid h-24 w-24 place-items-center">
          <div className="scanner-ring absolute inset-0 rounded-full border border-accent/60" />
          <div className="absolute inset-3 rounded-full border border-primary/20" />
          <ScanSearch size={30} className="relative text-primary" strokeWidth={1.5} />
        </div>
        <p className="font-mono-ui text-[10px] uppercase tracking-[0.18em] text-accent">Leitura local em andamento</p>
        <h2 className="font-display mt-3 text-3xl font-semibold tracking-[-0.04em]">Encontrando sinais no seu acervo.</h2>
        <p className="mt-3 text-sm text-muted-foreground">Mapeando nomes, tamanhos, formatos e datas — sem abrir o conteúdo.</p>
        <div className="mt-8">
          <div className="mb-2 flex justify-between font-mono-ui text-[10px] uppercase tracking-[0.1em] text-muted-foreground">
            <span>{count} {count === 1 ? 'arquivo selecionado' : 'arquivos selecionados'}</span>
            <span>{progress}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-secondary" role="progressbar" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100} aria-label="Progresso da análise">
            <div className="h-full rounded-full bg-accent transition-[width] duration-300" style={{ width: `${progress}%` }} />
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
              <span className="font-mono-ui text-[10px] text-muted-foreground">{item.count} · {formatBytes(item.bytes)}</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-secondary">
              <div className="h-full rounded-full transition-[width] duration-700" style={{ width: `${Math.max(5, (item.bytes / maxBytes) * 100)}%`, backgroundColor: kindColors[item.kind] }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function Recommendations({ result }: { result: ScanResult }) {
  const recommendations = useMemo(() => {
    const items: { title: string; description: string; tone: 'accent' | 'teal' | 'neutral'; icon: React.ReactNode }[] = [];
    if (result.duplicateGroups.length) {
      items.push({
        title: `${result.duplicateGroups.length} grupo${result.duplicateGroups.length > 1 ? 's' : ''} para revisar`,
        description: 'Arquivos com o mesmo nome e tamanho podem liberar espaço ou reduzir ruído.',
        tone: 'accent',
        icon: <RefreshCcw size={18} />,
      });
    }
    const largest = result.files.slice().sort((a, b) => b.file.size - a.file.size)[0];
    if (largest && largest.file.size > 100 * 1024 * 1024) {
      items.push({
        title: `${largest.file.name} concentra peso`,
        description: `Este arquivo representa ${Math.round((largest.file.size / result.totalBytes) * 100)}% do volume analisado.`,
        tone: 'teal',
        icon: <ArrowUpRight size={18} />,
      });
    }
    if (result.unknownTypeCount) {
      items.push({
        title: `${result.unknownTypeCount} arquivo${result.unknownTypeCount > 1 ? 's' : ''} sem categoria clara`,
        description: 'Vale nomear ou agrupar estes itens antes de decidir o próximo movimento.',
        tone: 'neutral',
        icon: <CircleAlert size={18} />,
      });
    }
    if (!items.length) {
      items.push({
        title: 'Acervo com boa legibilidade',
        description: 'Nenhum sinal de duplicidade ou formato indefinido apareceu nesta primeira leitura.',
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
          <p className="font-mono-ui text-[10px] uppercase tracking-[0.16em] text-primary-foreground/60">03 / próximo movimento</p>
          <h3 className="font-display mt-2 text-2xl font-semibold tracking-[-0.035em]">O que merece atenção.</h3>
        </div>
        <Sparkles className="text-accent" size={22} strokeWidth={1.5} />
      </div>
      <div className="mt-6 divide-y divide-primary-foreground/15">
        {recommendations.map((item) => (
          <div className="flex gap-4 py-4 first:pt-0 last:pb-0" key={item.title}>
            <div className={`mt-0.5 grid h-9 w-9 shrink-0 place-items-center rounded-full ${item.tone === 'accent' ? 'bg-accent text-foreground' : 'bg-primary-foreground/10 text-primary-foreground'}`}>
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
          <p className="font-mono-ui text-[10px] uppercase tracking-[0.16em] text-muted-foreground">04 / inventário</p>
          <h3 className="font-display mt-2 text-2xl font-semibold tracking-[-0.035em]">Cada arquivo, no lugar.</h3>
        </div>
        <span className="rounded-full bg-secondary px-3 py-1.5 font-mono-ui text-[10px] uppercase tracking-[0.1em] text-muted-foreground">{result.files.length} itens</span>
      </div>
      <div className="divide-y">
        {visibleFiles.map((record, index) => (
          <div className="flex items-center gap-3 px-6 py-4 sm:px-7" key={`${record.file.name}-${record.file.size}-${index}`} data-testid={`file-row-${index}`}>
            <div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-secondary text-primary/70">{getFileIcon(record.kind, 17)}</div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium" title={record.file.name}>{record.file.name}</p>
              <p className="mt-0.5 truncate font-mono-ui text-[10px] uppercase tracking-[0.08em] text-muted-foreground">{kindLabels[record.kind]} · {formatDate(record.file.lastModified)}</p>
            </div>
            <span className="shrink-0 font-mono-ui text-[10px] text-muted-foreground">{formatBytes(record.file.size)}</span>
          </div>
        ))}
      </div>
      {result.files.length > 8 && (
        <button
          type="button"
          onClick={() => setShowAll((value) => !value)}
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

function Results({ result, onReset }: { result: ScanResult; onReset: () => void }) {
  const duplicateCount = result.duplicateGroups.reduce((total, group) => total + group.length, 0);
  return (
    <div className="mt-12 space-y-5 sm:mt-16" id="diagnostico" data-testid="state-result">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <div className="mb-3 flex items-center gap-2 text-accent">
            <span className="grid h-6 w-6 place-items-center rounded-full bg-accent text-foreground"><Check size={14} strokeWidth={2.5} /></span>
            <span className="font-mono-ui text-[10px] font-bold uppercase tracking-[0.16em]">Leitura concluída no dispositivo</span>
          </div>
          <h2 className="font-display text-4xl font-semibold tracking-[-0.05em] sm:text-5xl">O contorno do seu acervo.</h2>
          <p className="mt-3 max-w-xl text-sm leading-6 text-muted-foreground">Uma primeira leitura para transformar dispersão em decisão. Nada foi enviado, aberto ou armazenado.</p>
        </div>
        <button type="button" onClick={onReset} className="inline-flex min-h-10 items-center justify-center gap-2 self-start rounded-full border border-primary/20 px-4 text-xs font-bold text-primary transition-colors hover:bg-card sm:self-auto" data-testid="button-new-analysis">
          <RefreshCcw size={14} />
          Nova análise
        </button>
      </div>
      <div className="grid gap-3 pt-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Itens" value={new Intl.NumberFormat('pt-BR').format(result.files.length)} detail="arquivos lidos localmente" icon={<Layers3 size={18} />} />
        <StatCard label="Volume" value={formatBytes(result.totalBytes)} detail="espaço representado" icon={<HardDrive size={18} />} />
        <StatCard label="Duplicatas" value={duplicateCount ? `${duplicateCount}` : 'Nenhuma'} detail={duplicateCount ? 'itens em grupos possíveis' : 'sinais encontrados'} icon={<RefreshCcw size={18} />} />
        <StatCard label="Janela" value={result.oldest ? `${new Date(result.oldest).getFullYear()}` : '—'} detail={result.oldest ? `até ${new Date(result.newest).getFullYear()}` : 'datas indisponíveis'} icon={<CalendarDays size={18} />} />
      </div>
      <div className="grid gap-5 pt-2 lg:grid-cols-[1.02fr_.98fr]">
        <Distribution result={result} />
        <Recommendations result={result} />
      </div>
      <FileTable result={result} />
    </div>
  );
}

function EmptyExperience({ onFiles }: { onFiles: (files: File[]) => void }) {
  return (
    <div className="mt-12 sm:mt-16" id="scanner">
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <p className="font-mono-ui text-[10px] uppercase tracking-[0.18em] text-accent">Primeiro passo / 01</p>
          <h2 className="font-display mt-2 text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">Veja o que você tem.</h2>
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
    <div className="mt-12 rounded-[1.4rem] border border-destructive/30 bg-destructive/5 p-8 text-center sm:mt-16" data-testid="state-error">
      <div className="mx-auto grid h-14 w-14 place-items-center rounded-full bg-destructive/10 text-destructive"><CircleAlert size={25} /></div>
      <h2 className="font-display mt-5 text-3xl font-semibold tracking-[-0.04em]">A leitura não terminou.</h2>
      <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-muted-foreground">{message}</p>
      <button type="button" onClick={onRetry} className="mt-6 inline-flex min-h-11 items-center gap-2 rounded-full bg-primary px-5 text-sm font-bold text-primary-foreground" data-testid="button-retry-scan">
        <RefreshCcw size={16} />
        Tentar novamente
      </button>
    </div>
  );
}

function Home() {
  const [scanState, setScanState] = useState<ScanState>('empty');
  const [result, setResult] = useState<ScanResult | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const scanTimer = useRef<number | null>(null);

  useEffect(() => () => {
    if (scanTimer.current) window.clearInterval(scanTimer.current);
  }, []);

  const analyzeFiles = (files: File[]) => {
    if (!files.length) return;
    if (scanTimer.current) window.clearInterval(scanTimer.current);
    setSelectedFiles(files);
    setResult(null);
    setError('');
    setProgress(6);
    setScanState('analyzing');
    let nextProgress = 6;
    scanTimer.current = window.setInterval(() => {
      nextProgress = Math.min(100, nextProgress + Math.max(7, Math.ceil(88 / Math.max(files.length, 1))));
      setProgress(nextProgress);
      if (nextProgress >= 100) {
        if (scanTimer.current) window.clearInterval(scanTimer.current);
        try {
          setResult(buildResult(files));
          setScanState('result');
        } catch {
          setError('Não foi possível interpretar os metadados destes arquivos. Tente selecionar outra pasta ou conjunto de arquivos.');
          setScanState('error');
        }
      }
    }, 90);
  };

  const reset = () => {
    if (scanTimer.current) window.clearInterval(scanTimer.current);
    setSelectedFiles([]);
    setResult(null);
    setProgress(0);
    setError('');
    setScanState('empty');
    window.setTimeout(() => document.getElementById('scanner')?.scrollIntoView({ behavior: 'smooth', block: 'center' }), 20);
  };

  return (
    <main className="page-shell grain min-h-[100dvh] overflow-hidden">
      <header className="mx-auto flex w-full max-w-[1240px] items-center justify-between px-5 py-5 sm:px-8 lg:px-10">
        <a href="#top" className="flex items-center gap-3" data-testid="link-brand">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-primary text-primary-foreground shadow-[0_5px_0_rgba(216,139,67,0.8)]"><ScanSearch size={19} strokeWidth={1.8} /></span>
          <span className="font-display text-xl font-semibold tracking-[-0.04em]">NeverLost <span className="font-sans text-[9px] font-bold uppercase tracking-[0.15em] text-muted-foreground">Scanner</span></span>
        </a>
        <div className="hidden items-center gap-6 text-xs font-medium text-muted-foreground sm:flex">
          <a href="#como-funciona" className="transition-colors hover:text-foreground" data-testid="link-how-it-works">Como funciona</a>
          <span className="flex items-center gap-2 font-mono-ui text-[10px] uppercase tracking-[0.1em]"><LockKeyhole size={13} /> 100% local</span>
        </div>
        <a href="#scanner" className="inline-flex min-h-9 items-center gap-1.5 rounded-full border border-primary/20 px-3.5 text-xs font-bold text-primary transition-colors hover:bg-card sm:hidden" data-testid="link-start-mobile">Começar <ArrowDownRight size={14} /></a>
      </header>

      <div className="mx-auto max-w-[1240px] px-5 pb-20 sm:px-8 lg:px-10">
        <section className="paper-grid relative mt-4 overflow-hidden rounded-[1.8rem] border border-primary/10 px-6 py-14 sm:mt-8 sm:px-12 sm:py-20 lg:px-20 lg:py-24" id="top">
          <div className="pointer-events-none absolute -right-20 -top-28 h-80 w-80 rounded-full border border-accent/20 sm:h-[30rem] sm:w-[30rem]" />
          <div className="pointer-events-none absolute -right-6 -top-14 h-52 w-52 rounded-full border border-accent/15 sm:h-80 sm:w-80" />
          <div className="relative max-w-3xl">
            <div className="rise-in flex items-center gap-3 text-primary">
              <span className="h-px w-9 bg-accent" />
              <span className="font-mono-ui text-[10px] font-bold uppercase tracking-[0.2em]">EDS apresenta</span>
            </div>
            <h1 className="font-display rise-in rise-in-delay-1 mt-6 max-w-3xl text-[3.55rem] font-semibold leading-[.96] tracking-[-0.065em] text-foreground sm:text-7xl lg:text-[6.4rem]">
              O valor escondido <em className="font-normal text-primary">não sumiu.</em>
            </h1>
            <p className="rise-in rise-in-delay-2 mt-7 max-w-xl text-base leading-7 text-muted-foreground sm:text-lg">
              O NeverLost Scanner dá um primeiro contorno ao que está espalhado. Selecione seus arquivos, entenda o acervo e encontre o próximo movimento.
            </p>
            <div className="rise-in rise-in-delay-3 mt-8 flex flex-wrap items-center gap-x-5 gap-y-3">
              <a href="#scanner" className="inline-flex min-h-12 items-center gap-2 rounded-full bg-primary px-6 text-sm font-bold text-primary-foreground shadow-[0_10px_24px_rgba(31,77,82,0.18)] transition-transform hover:-translate-y-0.5" data-testid="link-start-scan">
                Abrir o scanner
                <ArrowDownRight size={17} />
              </a>
              <span className="font-mono-ui text-[10px] uppercase tracking-[0.12em] text-muted-foreground">Sem login · sem upload</span>
            </div>
          </div>
          <div className="relative mt-14 flex items-end justify-between border-t border-primary/10 pt-5 sm:mt-20">
            <p className="max-w-[210px] text-xs leading-5 text-muted-foreground">Uma ferramenta EDS para quem sabe que arquivo parado também é patrimônio.</p>
            <div className="hidden text-right sm:block">
              <p className="font-mono-ui text-[10px] uppercase tracking-[0.14em] text-muted-foreground">Leitura 01</p>
              <p className="mt-1 font-display text-lg text-primary">Da dispersão à clareza.</p>
            </div>
          </div>
        </section>

        {scanState === 'empty' && <EmptyExperience onFiles={analyzeFiles} />}
        {scanState === 'analyzing' && <AnalyzingPanel count={selectedFiles.length} progress={progress} />}
        {scanState === 'error' && <ErrorPanel message={error} onRetry={() => analyzeFiles(selectedFiles)} />}
        {scanState === 'result' && result && <Results result={result} onReset={reset} />}

        <section className="mt-24 border-t border-primary/15 pt-12 sm:mt-32 sm:pt-16" id="como-funciona">
          <div className="grid gap-10 lg:grid-cols-[.75fr_1.25fr] lg:gap-24">
            <div>
              <p className="font-mono-ui text-[10px] uppercase tracking-[0.18em] text-accent">O jeito NeverLost</p>
              <h2 className="font-display mt-3 max-w-sm text-4xl font-semibold leading-[1.02] tracking-[-0.05em] sm:text-5xl">Antes de produzir, enxergue.</h2>
            </div>
            <div className="grid gap-8 sm:grid-cols-3">
              <div className="border-t border-primary/20 pt-4">
                <span className="font-mono-ui text-xs text-accent">01</span>
                <h3 className="mt-5 text-sm font-bold">Mapeia</h3>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">Quantidade, peso, tipo e datas. A forma do seu acervo aparece sem esforço.</p>
              </div>
              <div className="border-t border-primary/20 pt-4">
                <span className="font-mono-ui text-xs text-accent">02</span>
                <h3 className="mt-5 text-sm font-bold">Sinaliza</h3>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">Possíveis duplicatas e pontos de atenção para você não gastar energia no escuro.</p>
              </div>
              <div className="border-t border-primary/20 pt-4">
                <span className="font-mono-ui text-xs text-accent">03</span>
                <h3 className="mt-5 text-sm font-bold">Orienta</h3>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">Recomendações objetivas para transformar arquivo em um próximo movimento produtivo.</p>
              </div>
            </div>
          </div>
        </section>

        <footer className="mt-20 flex flex-col justify-between gap-3 border-t border-primary/15 py-7 text-xs text-muted-foreground sm:mt-28 sm:flex-row sm:items-center">
          <p className="font-display text-base text-foreground">EDS <span className="font-sans text-xs text-muted-foreground">· patrimônio em movimento</span></p>
          <p className="flex items-center gap-2 font-mono-ui text-[10px] uppercase tracking-[0.1em]"><ShieldCheck size={14} className="text-primary" /> seus arquivos permanecem no seu dispositivo</p>
        </footer>
      </div>
    </main>
  );
}

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
