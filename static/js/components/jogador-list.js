import { estrelas, iconePosicao } from '../utils/format.js';
import { deleteJogador, updateJogador } from '../api/jogadores.js';
import { mountStarRatings } from './star-rating.js';
import { updateCounter } from './sorteador-panel.js';
import state from '../state.js';

function esc(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

window.__state = state;

// ponytail: Set e a fonte de verdade da selecao entre re-renders (busca/edicao); ids de jogadores apagados ficam no Set sem efeito
const selecao = new Set();

document.addEventListener('change', (e) => {
  if (!e.target.classList?.contains('jogador-check')) return;
  if (e.target.checked) selecao.add(e.target.value);
  else selecao.delete(e.target.value);
  updateCounter();
});

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
              <span class="player-pos">${(j.posicoes || []).map(p => p.id === j.posicao_primaria_id ? `★${p.nome}` : p.nome).join(', ') || '-'}</span>
            </span>
          </span>
        </label>
        <button class="edit-trigger" data-action="edit" data-id="${j.id}">\u270E</button>
        <button class="delete-trigger" data-action="delete" data-id="${j.id}">\u00D7</button>
      </div>`;
  }
  html += '</div>';
  container.innerHTML = html;

  container.querySelectorAll('.jogador-check').forEach((cb) => {
    cb.checked = selecao.has(cb.value);
  });

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
      if (jogador) openEditModal(jogador);
    });
  });
}

function openEditModal(jogador) {
  const modal = document.getElementById('edit-modal');
  const nota = jogador.nota;

  const stars = [5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1, 0.5];
  let starHtml = '<fieldset class="rate mb-2">';
  for (const s of stars) {
    const checked = nota === s ? 'checked' : '';
    const sid = 'em' + s.toString().replace('.', '_');
    starHtml += `<input type="radio" id="${sid}" name="edit-nota" value="${s}" ${checked}><label for="${sid}" title="${s} estrelas"></label>`;
  }
  starHtml += '</fieldset>';

  const posicoesSemGoleiro = state.posicoes.filter(p => p.nome.toLowerCase() !== 'goleiro');
  const idsSelecionados = new Set((jogador.posicoes || []).map(p => p.id));
  let posHtml = '<div class="posicao-picker">';
  for (const p of posicoesSemGoleiro) {
    const checked = idsSelecionados.has(p.id) ? 'checked' : '';
    const isPrimary = jogador.posicao_primaria_id === p.id ? 'checked' : '';
    posHtml += `
      <label class="posicao-chip">
        <input type="checkbox" name="edit-posicoes" value="${p.id}" ${checked}>
        <span>${p.nome}</span>
        <input type="radio" name="edit-posicao-primaria" value="${p.id}" class="ms-1" ${isPrimary} title="Posicao principal">
      </label>`;
  }
  posHtml += '</div>';

  let restrHtml = '<select id="edit-restricoes" class="form-select" multiple size="5">';
  for (const j of state.jogadores) {
    if (j.id === jogador.id) continue;
    const hasRestr = (jogador.restricoes || []).some(r => r.id === j.id);
    restrHtml += `<option value="${j.id}" ${hasRestr ? 'selected' : ''}>${j.nome} ${j.is_goleiro ? '\uD83E\uDDE4' : ''}</option>`;
  }
  restrHtml += '</select>';

  modal.querySelector('.modal-body').innerHTML = `
    <label>Nome completo</label>
    <input id="edit-nome" class="form-control mb-2" value="${esc(jogador.nome)}" required>
    <label>Nota do jogador</label>
    ${starHtml}
    <label>Posicao</label>
    ${posHtml}
    <small class="text-muted d-block mt-1">Marque as posicoes e selecione a principal (⚫)</small>
    <div class="form-check mt-2">
      <input id="edit-goleiro" type="checkbox" class="form-check-input" ${jogador.is_goleiro ? 'checked' : ''}>
      <label class="form-check-label" for="edit-goleiro">🧤 E goleiro?</label>
    </div>
    <label class="mt-2">Restricoes (nao joga com)</label>
    ${restrHtml}
    <small class="text-muted">Ctrl+click para selecionar multiplos</small>
  `;

  modal.dataset.jogadorId = jogador.id;
  mountStarRatings();

  const bsModal = new bootstrap.Modal(modal);
  bsModal.show();
}

const btnSalvar = document.getElementById('btn-salvar-edit');
if (btnSalvar) {
  btnSalvar.addEventListener('click', async () => {
    const modal = document.getElementById('edit-modal');
    const id = parseInt(modal.dataset.jogadorId);
    const notaRadio = modal.querySelector('input[name="edit-nota"]:checked');
    const posicoes = [...modal.querySelectorAll('input[name="edit-posicoes"]:checked')]
      .map(el => parseInt(el.value));
    const primariaRadio = modal.querySelector('input[name="edit-posicao-primaria"]:checked');
    const posicao_primaria_id = primariaRadio ? parseInt(primariaRadio.value) : null;

    const restrSel = modal.querySelectorAll('#edit-restricoes option:checked');
    const restricoes = [...restrSel].map(o => parseInt(o.value));

    const data = {
      nome: modal.querySelector('#edit-nome').value.trim(),
      nota: parseFloat(notaRadio?.value || '3'),
      is_goleiro: modal.querySelector('#edit-goleiro').checked,
      posicoes,
      posicao_primaria_id,
      restricoes,
    };

    try {
      await updateJogador(id, data);
      bootstrap.Modal.getInstance(modal).hide();
      window.dispatchEvent(new CustomEvent('jogadores-changed'));
    } catch (err) {
      alert(err.message);
    }
  });
}
