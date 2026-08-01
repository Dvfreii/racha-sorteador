import { qsa, qs, updateCounter, validateSelection } from '../utils/dom.js';

export function usePlayerSelection() {
  const items = qsa('.jogador-check');
  const counter = qs('#contador');
  const update = () => updateCounter(items, counter);
  items.forEach((item) => item.addEventListener('change', update));
  update();
  return { items, update, valid: () => validateSelection(items) };
}

export default usePlayerSelection;
