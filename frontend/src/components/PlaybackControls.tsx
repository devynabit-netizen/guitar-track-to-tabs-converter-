export function PlaybackControls({
  playing,
  speed,
  onSpeed,
  onLoop,
  onPlay,
  onStop,
  onExport,
}: {
  playing: boolean;
  speed: number;
  onSpeed: (v: number) => void;
  onLoop: (start: number, end: number) => void;
  onPlay: () => void;
  onStop: () => void;
  onExport: (f: 'midi' | 'gp5') => void;
}) {
  return (
    <div className="rounded-lg border border-slate-800 p-4 flex gap-2 flex-wrap items-center">
      <button className="rounded bg-cyan-600 px-3 py-2" onClick={playing ? onStop : onPlay}>
        {playing ? 'Stop' : 'Play'}
      </button>
      <label className="text-sm">Speed
        <input className="ml-2 w-16 rounded bg-slate-900 p-1" type="number" min={0.5} max={1.5} step={0.1} value={speed} onChange={(e) => onSpeed(Number(e.target.value))} />
      </label>
      <button className="rounded bg-slate-700 px-3 py-2" onClick={() => onLoop(0, 8)}>Loop 0-8s</button>
      <button className="rounded bg-slate-700 px-3 py-2" onClick={() => onExport('midi')}>
        Export MIDI
      </button>
      <button className="rounded bg-slate-700 px-3 py-2" onClick={() => onExport('gp5')}>
        Export GP5
      </button>
    </div>
  );
}
