import { useState } from 'react';

export function UploadPanel({ onSubmit }: { onSubmit: (name: string, file: File, tuning: string) => Promise<void> }) {
  const [name, setName] = useState('New Project');
  const [tuning, setTuning] = useState('E2,A2,D3,G3,B3,E4');
  const [file, setFile] = useState<File | null>(null);

  return (
    <div className="rounded-lg border border-slate-800 p-4 space-y-3">
      <h2 className="font-semibold">Upload Guitar/Full Mix Audio</h2>
      <input className="w-full rounded bg-slate-900 p-2" value={name} onChange={(e) => setName(e.target.value)} />
      <input className="w-full rounded bg-slate-900 p-2" value={tuning} onChange={(e) => setTuning(e.target.value)} />
      <input
        className="w-full"
        type="file"
        accept="audio/wav,audio/mpeg,audio/flac,.wav,.mp3,.flac"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />
      <button
        className="rounded bg-emerald-600 px-4 py-2 disabled:opacity-50"
        disabled={!file}
        onClick={() => file && onSubmit(name, file, tuning)}
      >
        Start Transcription
      </button>
    </div>
  );
}
