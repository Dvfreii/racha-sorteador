import { qs, qsa, flash, validateSelection } from '../utils/dom.js';
import { sortear } from '../api/sorteios.js';
import state from '../state.js';

export function renderSorteadorPanel(container) {
  const selectedCount = qsa('.jogador-check').filter(el => el.checked).length;

  container.innerHTML = `
    <div class="selection-tools mb-2">
      <button type="button" id="select-all" class="btn btn-sm btn-light">Selecionar todos</button>
      <span id="contador" class="count-badge">${selectedCount} selecionados</span>
    </div>
    <div class="draw-options row g-2 mt-2">
      <div class="col-6">
        <label>Quantidade de times</label>
        <select id="team-count" class="form-select">
          ${[2,3,4,5,6,7,8].map(n => `<option value="${n}" ${n === 3 ? 'selected' : ''}>${n} times</option>`).join('')}
        </select>
      </div>
      <div class="col-6">
        <label>Jogadores por time (opcional)</label>
        <input id="por-time" class="form-control" placeholder="Ex.: 8" value="8">
      </div>
    </div>
    <button id="btn-sortear" class="btn btn-draw w-100 mt-3">Sortear times equilibrados</button>
    <div id="sort-error" class="mt-2"></div>
  `;

  qs('#select-all')?.addEventListener('click', () => {
    const checks = qsa('.jogador-check');
    const selectAll = checks.some(el => !el.checked);
    checks.forEach(el => { el.checked = selectAll; });
    document.getElementById('contador').textContent = `${qsa('.jogador-check').filter(el => el.checked).length} selecionados`;
  });

  qs('#btn-sortear')?.addEventListener('click', async () => {
    const checks = qsa('.jogador-check');

    if (!validateSelection(checks)) return;

    const ids = checks
      .filter(el => el.checked)
      .map(el => parseInt(el.value));

    const quantidade = parseInt(qs('#team-count').value);
    const porTime = qs('#por-time').value.trim();
    const tamanhos = porTime ? [parseInt(porTime)] : null;

    qs('#btn-sortear').disabled = true;
    qs('#btn-sortear').textContent = 'Sorteando...';

    try {
      const result = await sortear(ids, quantidade, tamanhos);
      state.resultado = result;
      window.dispatchEvent(new CustomEvent('sorteio-done', { detail: result }));
    } catch (err) {
      flash(err.message, 'danger');
    } finally {
      qs('#btn-sortear').disabled = false;
      qs('#btn-sortear').textContent = 'Sortear times equilibrados';
    }
  });
}

export function updateCounter() {
  const counter = document.getElementById('contador');
  if (counter) {
    counter.textContent = `${qsa('.jogador-check').filter(el => el.checked).length} selecionados`;
  }
}
