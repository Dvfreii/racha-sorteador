import { API } from '../config.js';

export async function getPosicoes() {
  const r = await fetch(API.POSICOES);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}
