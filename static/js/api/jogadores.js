import { API } from '../config.js';

export async function getJogadores(incluirInativos = false) {
  const url = incluirInativos
    ? `${API.JOGADORES}?incluir_inativos=true`
    : API.JOGADORES;
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

export async function createJogador(data) {
  const r = await fetch(API.JOGADORES, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!r.ok) {
    const e = await r.json();
    throw new Error(e.erro || 'Erro ao criar');
  }
  return r.json();
}

export async function updateJogador(id, data) {
  const r = await fetch(`${API.JOGADORES}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!r.ok) {
    const e = await r.json();
    throw new Error(e.erro || 'Erro ao atualizar');
  }
  return r.json();
}

export async function deleteJogador(id) {
  const r = await fetch(`${API.JOGADORES}/${id}`, { method: 'DELETE' });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}
