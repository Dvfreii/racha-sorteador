import { estrelas, iconePosicao } from '../utils/format.js';
import { deleteJogador } from '../api/jogadores.js';
import state from '../state.js';

function esc(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

window.__state = state;

export function renderJogadorList(container, jogadores) {
  if (!jogadores.length) {
    container.innerHTML = '<p class="text-muted">Nenhum jogador cadastrado.</p>';
    return;
  }

  let html = '<div class="player-grid">';
  for (const j of jogadores) {
    html += `
      <div class="player-card" data-id="${j.id}">
        <label>
          <input class="form-check-input jogador-check" type="checkbox" name="jogadores" value="${j.id}">
          <span class="player-avatar">${esc(j.nome)[0]}</span>
          <span class="player-info">
            <strong>${esc(j.nome)}</strong>
            <span class="player-meta">
              <span class="player-stars">${estrelas(j.nota)}</span>
              ${j.is_goleiro ? '<span class="badge bg-info">\uD83E\uDDE4</span>' : ''}
              <span class="player-pos">${(j.posicoes || []).map(p => p.nome).join(', ') || '-'}</span>
            </span>
          </span>
        </label>
        <button class="edit-trigger" data-action="edit" data-id="${j.id}">\u270E</button>
        <button class="delete-trigger" data-action="delete" data-id="${j.id}">\u00D7</button>
      </div>`;
  }
  html += '</div>';
  container.innerHTML = html;

  container.querySelectorAll('.delete-trigger').forEach(btn => {
    btn.addEventListener('click', async () => {
      await deleteJogador(parseInt(btn.dataset.id));
      window.dispatchEvent(new CustomEvent('jogadores-changed'));
    });
  });

  container.querySelectorAll('.edit-trigger').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = parseInt(btn.dataset.id);
      const jogador = state.jogadores.find(j => j.id === id);
      if (jogador) {
        import('./jogador-form.js').then(m => {
          const formContainer = document.getElementById('section-form');
          if (formContainer) m.renderJogadorForm(formContainer, jogador);
        });
      }
    });
  });
}
