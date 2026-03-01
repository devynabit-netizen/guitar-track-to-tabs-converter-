export type NoteEvent = {
  pitch_midi: number;
  start_time: number;
  duration: number;
  confidence: number;
  string: number;
  fret: number;
};

export type TabData = {
  project_id: number;
  tempo_bpm: number;
  tuning: string[];
  notes: NoteEvent[];
  tab_ascii: string;
};
