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

export type ProjectStatus = {
  project_id: number;
  status: string;
  progress: number;
  current_phase: number;
  total_phases: number;
  phase_name: string;
  error_message?: string | null;
  error_code?: string | null;
};
