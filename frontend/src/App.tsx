import { useEffect, useState } from 'react';
import { PlaybackControls } from './components/PlaybackControls';
import { TabEditor } from './components/TabEditor';
import { UploadPanel } from './components/UploadPanel';
import { getStatus, getTab, uploadProject, exportFile } from './lib/api';
import { usePlayback } from './hooks/usePlayback';
import { TabData } from './types/tab';

export default function App() {
  const [projectId, setProjectId] = useState<number | null>(null);
  const [status, setStatus] = useState('idle');
  const [tab, setTab] = useState<TabData | null>(null);
  const [tempo, setTempo] = useState(120);
  const playback = usePlayback(tab?.notes ?? [], tempo);

  useEffect(() => {
    if (!projectId || status !== 'processing') return;
    const poll = window.setInterval(async () => {
      const state = await getStatus(projectId);
      if (state.status === 'complete') {
        const result = await getTab(projectId);
        setTab(result);
        setTempo(result.tempo_bpm);
        setStatus('complete');
      }
    }, 1500);
    return () => window.clearInterval(poll);
  }, [projectId, status]);

  const handleUpload = async (name: string, file: File) => {
    const created = await uploadProject(name, file);
    setProjectId(created.project_id);
    setStatus('processing');
  };

  return (
    <main className="max-w-5xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">Guitar Stem → Tablature</h1>
      <UploadPanel onSubmit={handleUpload} />
      <p className="text-sm text-slate-400">Status: {status}</p>
      {tab && (
        <>
          <PlaybackControls
            playing={playback.playing}
            onPlay={playback.play}
            onStop={playback.stop}
            onExport={async (fmt) => {
              if (!projectId) return;
              const result = await exportFile(projectId, fmt);
              alert(`Exported ${fmt.toUpperCase()} to ${result.path}`);
            }}
          />
          <TabEditor tab={tab} cursor={playback.cursor} onTempoChange={setTempo} />
        </>
      )}
    </main>
  );
}
