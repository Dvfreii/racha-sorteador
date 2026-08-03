export function renderPosicaoPicker(container, posicoes, selecionadas = [], primariaId = null) {
  const posicoesSemGoleiro = posicoes.filter(p => p.nome.toLowerCase() !== 'goleiro');
  const idsSelecionados = new Set(selecionadas.map(p => p.id));
  let html = '<div class="posicao-picker">';
  for (const p of posicoesSemGoleiro) {
    const checked = idsSelecionados.has(p.id) ? 'checked' : '';
    html += `
      <label class="posicao-chip">
        <input type="checkbox" name="posicoes" value="${p.id}" ${checked}>
        <span>${p.nome}</span>
        <input type="radio" name="posicao_primaria_id" value="${p.id}" class="ms-1" ${primariaId === p.id ? 'checked' : ''} title="Posicao principal">
      </label>`;
  }
  html += '</div>';
  html += '<small class="text-muted d-block mt-1">Marque as posicoes e selecione a principal (⚫)</small>';
  container.innerHTML = html;
}

export function getSelectedPosicoes(form) {
  return [...form.querySelectorAll('input[name="posicoes"]:checked')]
    .map(el => parseInt(el.value));
}

export function getSelectedPosicaoPrimaria(form) {
  const radio = form.querySelector('input[name="posicao_primaria_id"]:checked');
  return radio ? parseInt(radio.value) : null;
}
