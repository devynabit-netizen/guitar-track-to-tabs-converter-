import axios from 'axios';
import { TabData } from '../types/tab';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

export async function uploadProject(name: string, audio: File) {
  const data = new FormData();
  data.append('name', name);
  data.append('audio', audio);
  const res = await api.post('/projects', data);
  return res.data as { project_id: number; status: string };
}

export async function getStatus(projectId: number) {
  const res = await api.get(`/projects/${projectId}/status`);
  return res.data as { project_id: number; status: string; progress: number };
}

export async function getTab(projectId: number) {
  const res = await api.get(`/projects/${projectId}/tab`);
  return res.data as TabData;
}

export async function exportFile(projectId: number, format: 'midi' | 'gp5') {
  const res = await api.post(`/projects/${projectId}/export/${format}`);
  return res.data as { path: string };
}
