import { qs } from '../utils/dom.js';
import { renderPosicaoPicker, getSelectedPosicoes, getSelectedPosicaoPrimaria } from './posicao-picker.js';
import { renderRestricaoPicker, getSelectedRestricoes } from './restricao-picker.js';
import { createJogador, updateJogador } from '../api/jogadores.js';
import { mountStarRatings } from './star-rating.js';
import state from '../state.js';

export function renderJogadorForm(container, jogador = null) {
  const isEdit = !!jogador;
  const nome = jogador?.nome || '';
  const nota = jogador?.nota || 3;

  const checked5 = nota === 5 ? 'checked' : '';
  const checked45 = nota === 4.5 ? 'checked' : '';
  const checked4 = nota === 4 ? 'checked' : '';
  const checked35 = nota === 3.5 ? 'checked' : '';
  const checked3 = (!jogador && nota === 3) || nota === 3 ? 'checked' : '';
  const checked25 = nota === 2.5 ? 'checked' : '';
  const checked2 = nota === 2 ? 'checked' : '';
  const checked15 = nota === 1.5 ? 'checked' : '';
  const checked1 = nota === 1 ? 'checked' : '';
  const checked05 = nota === 0.5 ? 'checked' : '';

  container.innerHTML = `
    <form id="jogador-form" class="row g-2">
      <div class="col-12 col-md-4">
        <label>Nome</label>
        <input name="nome" class="form-control" value="${nome}" placeholder="Ex.: Joao Silva" required>
      </div>
      <div class="col-12 col-md-4">
        <label>Nota</label>
        <fieldset class="rate" aria-label="Nota do jogador">
          <input type="radio" id="jn10" name="nota" value="5" ${checked5}><label for="jn10" title="5 estrelas"></label>
          <input type="radio" id="jn9" name="nota" value="4.5" ${checked45}><label class="half" for="jn9" title="4,5 estrelas"></label>
          <input type="radio" id="jn8" name="nota" value="4" ${checked4}><label for="jn8" title="4 estrelas"></label>
          <input type="radio" id="jn7" name="nota" value="3.5" ${checked35}><label class="half" for="jn7" title="3,5 estrelas"></label>
          <input type="radio" id="jn6" name="nota" value="3" ${jogador ? checked3 : 'checked'}><label for="jn6" title="3 estrelas"></label>
          <input type="radio" id="jn5" name="nota" value="2.5" ${checked25}><label class="half" for="jn5" title="2,5 estrelas"></label>
          <input type="radio" id="jn4" name="nota" value="2" ${checked2}><label for="jn4" title="2 estrelas"></label>
          <input type="radio" id="jn3" name="nota" value="1.5" ${checked15}><label class="half" for="jn3" title="1,5 estrela"></label>
          <input type="radio" id="jn2" name="nota" value="1" ${checked1}><label for="jn2" title="1 estrela"></label>
          <input type="radio" id="jn1" name="nota" value="0.5" ${checked05}><label class="half" for="jn1" title="0,5 estrela"></label>
        </fieldset>
      </div>
      <div class="col-6 col-md-4">
        <label>Posicao</label>
        <div id="posicao-picker"></div>
      </div>
      <div class="col-12">
        <div class="form-check">
          <input name="is_goleiro" type="checkbox" class="form-check-input" id="chk-goleiro" ${jogador?.is_goleiro ? 'checked' : ''}>
          <label class="form-check-label" for="chk-goleiro">🧤 E goleiro?</label>
        </div>
      </div>
      <div class="col-12">
        <label>Restricoes (nao joga com)</label>
        <div id="restricao-picker"></div>
      </div>
      <div class="col-12 mt-2">
        <button type="submit" class="btn btn-primary">${isEdit ? 'Salvar alteracoes' : '+ Adicionar jogador'}</button>
        ${isEdit ? '<button type="button" class="btn btn-light ms-2 cancel-edit">Cancelar</button>' : ''}
      </div>
    </form>`;

  const form = qs('#jogador-form');
  mountStarRatings();

  const posicoesSemGoleiro = state.posicoes.filter(p => p.nome.toLowerCase() !== 'goleiro');
  renderPosicaoPicker(qs('#posicao-picker'), posicoesSemGoleiro, jogador?.posicoes || [], jogador?.posicao_primaria_id);
  renderRestricaoPicker(qs('#restricao-picker'), state.jogadores.filter(j => j.id !== jogador?.id), jogador?.restricoes || []);

  qs('.cancel-edit')?.addEventListener('click', () => {
    renderJogadorForm(container);
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const notaRadio = form.querySelector('input[name="nota"]:checked');
    const data = {
      nome: form.nome.value.trim(),
      nota: parseFloat(notaRadio?.value || '3'),
      is_goleiro: form.is_goleiro.checked,
      posicoes: getSelectedPosicoes(form),
      posicao_primaria_id: getSelectedPosicaoPrimaria(form),
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
