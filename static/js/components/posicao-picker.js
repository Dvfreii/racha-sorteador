import { qs } from '../utils/dom.js';

export function renderPosicaoPicker(container, posicoes, selecionadas = []) {
  const idsSelecionados = new Set(selecionadas.map(p => p.id));
  let html = '<div class="posicao-picker d-flex flex-wrap gap-2">';
  for (const p of posicoes) {
    const checked = idsSelecionados.has(p.id) ? 'checked' : '';
    html += `
      <label class="posicao-chip">
        <input type="checkbox" name="posicoes" value="${p.id}" ${checked}>
        <span>${p.nome}</span>
      </label>`;
  }
  html += '</div>';
  container.innerHTML = html;
}

export function getSelectedPosicoes(form) {
  return [...form.querySelectorAll('input[name="posicoes"]:checked')]
    .map(el => parseInt(el.value));
}
