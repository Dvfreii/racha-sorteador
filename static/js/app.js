import { getJogadores } from './api/jogadores.js';
import { getPosicoes } from './api/posicoes.js';
import state from './state.js';
import { renderJogadorForm } from './components/jogador-form.js';
import { renderJogadorList } from './components/jogador-list.js';
import { renderSorteadorPanel, updateCounter } from './components/sorteador-panel.js';
import { renderResultadoPanel } from './components/resultado-panel.js';
import { renderHistoricoPanel } from './components/historico-panel.js';
import { renderWhatsAppPreview, showWhatsAppPreview } from './components/whatsapp-preview.js';
import { mountStarRatings } from './components/star-rating.js';
import { qs, qsa } from './utils/dom.js';

async function bootstrap() {
  try {
    state.jogadores = await getJogadores();
    state.posicoes = await getPosicoes();
  } catch (err) {
    console.error('Falha ao carregar dados:', err);
    return;
  }

  renderJogadorForm(qs('#section-form'));
  mountStarRatings();
  renderJogadorList(qs('#section-list'), state.jogadores);
  renderSorteadorPanel(qs('#section-sorteio'));
  renderResultadoPanel(qs('#section-resultado'), null);
  renderWhatsAppPreview(qs('#whatsapp-container'));
  renderHistoricoPanel(qs('#section-historico'));

  qs('#btn-importar')?.addEventListener('click', async () => {
    const lista = qs('#import-textarea').value;
    if (!lista.trim()) return;
    const r = await fetch('/api/importar-whatsapp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lista }),
    });
    const data = await r.json();
    qs('#import-result').innerHTML = `<div class="alert alert-success">Importados ${data.adicionados} jogadores/goleiros.</div>`;
    window.dispatchEvent(new CustomEvent('jogadores-changed'));
  });
}

window.addEventListener('jogadores-changed', async () => {
  state.jogadores = await getJogadores();
  renderJogadorList(qs('#section-list'), state.jogadores);
  renderSorteadorPanel(qs('#section-sorteio'));
  renderResultadoPanel(qs('#section-resultado'), null);
  updateCounter();
  renderHistoricoPanel(qs('#section-historico'));
});

window.addEventListener('sorteio-done', (e) => {
  renderResultadoPanel(qs('#section-resultado'), e.detail);
  document.getElementById('section-resultado')?.scrollIntoView({ behavior: 'smooth' });
});

window.addEventListener('open-whatsapp-preview', (e) => {
  showWhatsAppPreview(e.detail);
});

window.addEventListener('jogadores-changed', () => {
  const checks = qsa('.jogador-check');
  checks.forEach(cb => {
    cb.addEventListener('change', updateCounter);
  });
  updateCounter();
}, { once: false });

bootstrap();
