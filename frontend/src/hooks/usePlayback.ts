import { useEffect, useRef, useState } from 'react';
import { NoteEvent } from '../types/tab';

export function usePlayback(notes: NoteEvent[], tempoBpm: number) {
  const [playing, setPlaying] = useState(false);
  const [cursor, setCursor] = useState(0);
  const contextRef = useRef<AudioContext | null>(null);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    contextRef.current = new AudioContext({ latencyHint: 'interactive' });
    return () => {
      contextRef.current?.close();
    };
  }, []);

  useEffect(() => {
    if (!playing) {
      if (timerRef.current) {
        window.clearInterval(timerRef.current);
      }
      return;
    }

    const started = performance.now();
    timerRef.current = window.setInterval(() => {
      const elapsed = (performance.now() - started) / 1000;
      setCursor(elapsed);
    }, 16);

    return () => {
      if (timerRef.current) {
        window.clearInterval(timerRef.current);
      }
    };
  }, [playing]);

  const schedulePlayback = () => {
    const ctx = contextRef.current;
    if (!ctx) return;
    const now = ctx.currentTime + 0.05;

    notes.forEach((note) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.value = 440 * Math.pow(2, (note.pitch_midi - 69) / 12);
      gain.gain.value = 0.05;
      osc.connect(gain).connect(ctx.destination);
      osc.start(now + note.start_time * (120 / tempoBpm));
      osc.stop(now + (note.start_time + note.duration) * (120 / tempoBpm));
    });
  };

  return {
    cursor,
    playing,
    setPlaying,
    play: () => {
      setCursor(0);
      schedulePlayback();
      setPlaying(true);
    },
    stop: () => setPlaying(false),
  };
}
