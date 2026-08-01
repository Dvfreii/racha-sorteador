import { qsa, qs, toggleAll, updateCounter, validateSelection } from '../utils/dom.js';

export function mountPlayerSelection() {
  const items = qsa('.jogador-check');
  const counter = qs('#contador');
  const update = () => updateCounter(items, counter);
  items.forEach((item) => item.addEventListener('change', update));
  qs('#select-all')?.addEventListener('click', () => { toggleAll(items); update(); });
  document.querySelectorAll('.delete-trigger').forEach((button) => {
    button.addEventListener('click', async () => {
      const response = await fetch(button.dataset.deleteUrl, { method: 'POST' });
      if (response.ok || response.redirected) button.closest('.player-card')?.remove();
      update();
    });
  });
  update();
  qs('#draw-form')?.addEventListener('submit', (event) => {
    if (!validateSelection(items)) event.preventDefault();
  });
  return { items, update };
}

export default mountPlayerSelection;
