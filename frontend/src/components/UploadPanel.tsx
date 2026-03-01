import { useState } from 'react';

export function UploadPanel({ onSubmit }: { onSubmit: (name: string, file: File) => Promise<void> }) {
  const [name, setName] = useState('New Project');
  const [file, setFile] = useState<File | null>(null);

  return (
    <div className="rounded-lg border border-slate-800 p-4 space-y-3">
      <h2 className="font-semibold">Upload Guitar Stem</h2>
      <input className="w-full rounded bg-slate-900 p-2" value={name} onChange={(e) => setName(e.target.value)} />
      <input
        className="w-full"
        type="file"
        accept="audio/wav,audio/mpeg"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />
      <button
        className="rounded bg-emerald-600 px-4 py-2 disabled:opacity-50"
        disabled={!file}
        onClick={() => file && onSubmit(name, file)}
      >
        Start Transcription
      </button>
    </div>
  );
}
