import { qs } from '../utils/dom.js';
import { renderPosicaoPicker, getSelectedPosicoes } from './posicao-picker.js';
import { renderRestricaoPicker, getSelectedRestricoes } from './restricao-picker.js';
import { createJogador, updateJogador } from '../api/jogadores.js';
import state from '../state.js';

export function renderJogadorForm(container, jogador = null) {
  const isEdit = !!jogador;
  const nome = jogador?.nome || '';
  const nota = jogador?.nota || 3;
  const isGoleiro = jogador?.is_goleiro || false;

  container.innerHTML = `
    <form id="jogador-form" class="row g-2">
      <div class="col-12 col-md-4">
        <label>Nome</label>
        <input name="nome" class="form-control" value="${nome}" placeholder="Nome do jogador" required>
      </div>
      <div class="col-12 col-md-3">
        <label>Nota (1-5)</label>
        <input name="nota" type="number" class="form-control" value="${nota}" min="1" max="5" step="0.5" required>
      </div>
      <div class="col-12 col-md-3">
        <label>Goleiro</label>
        <div class="form-check mt-2">
          <input name="is_goleiro" type="checkbox" class="form-check-input" ${isGoleiro ? 'checked' : ''}>
          <span class="form-check-label">\uD83E\uDDE4 E goleiro?</span>
        </div>
      </div>
      <div class="col-12">
        <label>Posicoes</label>
        <div id="posicao-picker"></div>
      </div>
      <div class="col-12">
        <label>Restricoes (nao joga com)</label>
        <div id="restricao-picker"></div>
      </div>
      <div class="col-12 mt-2">
        <button type="submit" class="btn btn-primary">${isEdit ? 'Salvar alteracoes' : 'Adicionar jogador'}</button>
        ${isEdit ? '<button type="button" class="btn btn-light ms-2 cancel-edit">Cancelar</button>' : ''}
      </div>
    </form>`;

  const form = qs('#jogador-form');
  renderPosicaoPicker(qs('#posicao-picker'), state.posicoes, jogador?.posicoes || []);
  renderRestricaoPicker(qs('#restricao-picker'), state.jogadores.filter(j => j.id !== jogador?.id), jogador?.restricoes || []);

  qs('.cancel-edit')?.addEventListener('click', () => {
    renderJogadorForm(container);
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
      nome: form.nome.value.trim(),
      nota: parseFloat(form.nota.value),
      is_goleiro: form.is_goleiro.checked,
      posicoes: getSelectedPosicoes(form),
      restricoes: getSelectedRestricoes(form),
    };

    try {
      if (isEdit) {
        await updateJogador(jogador.id, data);
      } else {
        await createJogador(data);
      }
      window.dispatchEvent(new CustomEvent('jogadores-changed'));
      renderJogadorForm(container);
    } catch (err) {
      alert(err.message);
    }
  });
}
