import { useEffect, useMemo, useState } from 'react';
import { PlaybackControls } from './components/PlaybackControls';
import { TabEditor } from './components/TabEditor';
import { Toast, ToastMessage } from './components/Toast';
import { UploadPanel } from './components/UploadPanel';
import { exportFile, getStatus, getTab, uploadProject } from './lib/api';
import { usePlayback } from './hooks/usePlayback';
import { ProjectStatus, TabData } from './types/tab';

const PHASE_LABELS = ['uploaded', 'preprocessing', 'transcribing', 'tab_generation', 'finalizing'];

export default function App() {
  const [projectId, setProjectId] = useState<number | null>(null);
  const [status, setStatus] = useState<ProjectStatus | null>(null);
  const [tab, setTab] = useState<TabData | null>(null);
  const [tempo, setTempo] = useState(120);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const playback = usePlayback(tab?.notes ?? [], tempo);

  const addToast = (kind: ToastMessage['kind'], text: string) => {
    setToasts((prev) => [...prev, { id: Date.now() + prev.length, kind, text }]);
  };

  const retryStatusPoll = async () => {
    if (!projectId) return;
    try {
      const state = await getStatus(projectId);
      setStatus(state);
    } catch {
      addToast('error', 'Retry failed. Please try again.');
    }
  };

  useEffect(() => {
    if (!projectId || !status || !['queued', 'processing'].includes(status.status)) return;
    const poll = window.setInterval(async () => {
      try {
        const state = await getStatus(projectId);
        setStatus(state);
        if (state.status === 'complete') {
          const result = await getTab(projectId);
          setTab(result);
          setTempo(result.tempo_bpm);
          addToast('success', 'Transcription complete. Tab is ready.');
        }
      } catch {
        addToast('error', 'Could not refresh project status.');
      }
    }, 1500);
    return () => window.clearInterval(poll);
  }, [projectId, status]);

  const handleUpload = async (name: string, file: File) => {
    try {
      const created = await uploadProject(name, file);
      setProjectId(created.project_id);
      setTab(null);
      setStatus({
        project_id: created.project_id,
        status: created.status,
        progress: 0.2,
        current_phase: 1,
        total_phases: 5,
        phase_name: 'uploaded',
      });
      addToast('success', 'Upload complete. Processing started.');
    } catch {
      addToast('error', 'Upload failed. Please try another file.');
    }
  };

  const phaseChecklist = useMemo(() => {
    if (!status) return [];
    return PHASE_LABELS.map((phaseName, index) => ({
      phaseName,
      done: index + 1 <= status.current_phase,
      active: phaseName === status.phase_name,
    }));
  }, [status]);

  return (
    <main className="max-w-5xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">Guitar Stem → Tablature</h1>
      <UploadPanel onSubmit={handleUpload} />

      <section className="rounded-lg border border-slate-800 p-4 space-y-3">
        <p className="text-sm text-slate-300">
          Status: <span className="font-semibold">{status?.status ?? 'idle'}</span>
        </p>
        {status && (
          <>
            <p className="text-xs text-slate-400">
              Phase {status.current_phase}/{status.total_phases}: {status.phase_name}
            </p>
            <div className="h-2 rounded bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-emerald-500 transition-all"
                style={{ width: `${Math.round(status.progress * 100)}%` }}
              />
            </div>
            <ul className="grid grid-cols-1 md:grid-cols-5 gap-2 text-xs">
              {phaseChecklist.map((item) => (
                <li
                  key={item.phaseName}
                  className={`rounded border px-2 py-1 ${
                    item.active ? 'border-emerald-500 text-emerald-400' : 'border-slate-700 text-slate-400'
                  }`}
                >
                  {item.done ? '✓ ' : '○ '}
                  {item.phaseName}
                </li>
              ))}
            </ul>
            {status.status === 'failed' && (
              <button className="rounded bg-amber-600 px-3 py-1 text-xs" onClick={retryStatusPoll}>
                Retry status check
              </button>
            )}
            {status.error_message && <p className="text-xs text-red-400">{status.error_message}</p>}
          </>
        )}
      </section>

      {tab && (
        <>
          <PlaybackControls
            playing={playback.playing}
            onPlay={playback.play}
            onStop={playback.stop}
            onExport={async (fmt) => {
              if (!projectId) return;
              try {
                const result = await exportFile(projectId, fmt);
                addToast('success', `Exported ${fmt.toUpperCase()} to ${result.path}`);
              } catch {
                addToast('error', `Failed to export ${fmt.toUpperCase()}.`);
              }
            }}
          />
          <TabEditor tab={tab} cursor={playback.cursor} onTempoChange={setTempo} />
        </>
      )}

      <div className="fixed bottom-4 right-4 space-y-2 w-80">
        {toasts.map((toast) => (
          <Toast key={toast.id} message={toast} onClose={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />
        ))}
      </div>
    </main>
  );
}
