import { TabData } from '../types/tab';

export function TabEditor({ tab, cursor, onTempoChange }: { tab: TabData; cursor: number; onTempoChange: (v: number) => void }) {
  return (
    <div className="rounded-lg border border-slate-800 p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold">Generated Tab</h2>
        <label className="text-sm">
          Tempo
          <input
            type="number"
            className="ml-2 w-20 rounded bg-slate-900 p-1"
            defaultValue={tab.tempo_bpm}
            onChange={(e) => onTempoChange(Number(e.target.value))}
          />
        </label>
      </div>
      <pre className="overflow-auto rounded bg-slate-900 p-4 text-sm leading-6">{tab.tab_ascii}</pre>
      <div className="h-2 rounded bg-slate-800">
        <div className="h-2 rounded bg-cyan-500" style={{ width: `${Math.min(100, cursor * 10)}%` }} />
      </div>
      <p className="text-xs text-slate-400">Click/drag note editing can be extended with SVG hit-testing in the TabCanvas component.</p>
    </div>
  );
}
