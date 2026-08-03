export function renderRestricaoPicker(container, jogadores, selecionadas = []) {
  const idsSelecionados = new Set(selecionadas.map(r => r.id));
  let html = '<select class="form-select" name="restricoes" multiple size="5">';
  for (const j of jogadores) {
    const selected = idsSelecionados.has(j.id) ? 'selected' : '';
    html += `<option value="${j.id}" ${selected}>${j.nome} ${j.is_goleiro ? '\uD83E\uDDE4' : ''}</option>`;
  }
  html += '</select>';
  html += '<small class="text-muted">Ctrl+click para selecionar multiplos</small>';
  container.innerHTML = html;
}

export function getSelectedRestricoes(form) {
  return [...form.querySelectorAll('select[name="restricoes"] option:checked')]
    .map(el => parseInt(el.value));
}
