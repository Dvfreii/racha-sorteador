export const qs = (selector, root = document) => root.querySelector(selector);
export const qsa = (selector, root = document) => [...root.querySelectorAll(selector)];

export function updateCounter(items, counter) {
  if (counter) counter.textContent = `${items.filter((item) => item.checked).length} selecionados`;
}

export function flash(message, type = 'danger') {
  const area = qs('#flash-area');
  if (area) area.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
}

export function toggleAll(items) {
  const shouldSelect = items.some((item) => !item.checked);
  items.forEach((item) => { item.checked = shouldSelect; });
}

export function validateSelection(items) {
  const total = items.filter((item) => item.checked).length;
  if (total < 2) {
    flash(`Selecione pelo menos 2 jogadores. Atualmente: ${total}.`);
    return false;
  }
  return true;
}
