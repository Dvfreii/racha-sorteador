import { API } from '../config.js';

export async function sortear(jogadores, quantidadeTimes = 3, tamanhos = null) {
  const r = await fetch(API.SORTEIOS_SORTEAR, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jogadores, quantidade_times: quantidadeTimes, tamanhos }),
  });
  if (!r.ok) {
    const e = await r.json();
    throw new Error(e.erro || 'Erro ao sortear');
  }
  return r.json();
}

export async function salvarSorteio(times, goleiros) {
  const r = await fetch(API.SORTEIOS, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ times, goleiros }),
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

export async function getHistorico(limite = 10, offset = 0) {
  const r = await fetch(`${API.SORTEIOS}?limite=${limite}&offset=${offset}`);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

export async function deleteSorteio(id) {
  const r = await fetch(`${API.SORTEIOS}/${id}`, { method: 'DELETE' });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}
