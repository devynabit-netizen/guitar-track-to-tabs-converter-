export function PlaybackControls({ playing, onPlay, onStop, onExport }: { playing: boolean; onPlay: () => void; onStop: () => void; onExport: (f: 'midi' | 'gp5') => void }) {
  return (
    <div className="rounded-lg border border-slate-800 p-4 flex gap-2 flex-wrap">
      <button className="rounded bg-cyan-600 px-3 py-2" onClick={playing ? onStop : onPlay}>
        {playing ? 'Stop' : 'Play'}
      </button>
      <button className="rounded bg-slate-700 px-3 py-2" onClick={() => onExport('midi')}>
        Export MIDI
      </button>
      <button className="rounded bg-slate-700 px-3 py-2" onClick={() => onExport('gp5')}>
        Export GP5
      </button>
    </div>
  );
}
