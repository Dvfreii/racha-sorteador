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

let allJogadores = [];

async function bootstrap() {
  try {
    allJogadores = await getJogadores();
    state.jogadores = allJogadores;
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

  setupAsideNav();
  setupSearchFilter();
}

function setupAsideNav() {
  const links = qsa('.app-sidebar nav a');
  const sections = links.map(a => {
    const href = a.getAttribute('href');
    return href ? document.querySelector(href) : null;
  });

  links.forEach((a, i) => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      const target = sections[i];
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
        setActive(links, i);
      }
    });
  });

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      let activeIdx = 0;
      const scrollPos = window.scrollY + 100;
      for (let i = sections.length - 1; i >= 0; i--) {
        if (sections[i] && sections[i].offsetTop <= scrollPos) {
          activeIdx = i;
          break;
        }
      }
      setActive(links, activeIdx);
      ticking = false;
    });
  });
}

function setActive(links, idx) {
  links.forEach((a, i) => a.classList.toggle('active', i === idx));
}

function setupSearchFilter() {
  const input = document.getElementById('filter-nome');
  if (!input) return;
  input.addEventListener('input', () => {
    const term = input.value.toLowerCase().trim();
    state.jogadores = term
      ? allJogadores.filter(j => j.nome.toLowerCase().includes(term))
      : allJogadores;
    renderJogadorList(qs('#section-list'), state.jogadores);
    renderSorteadorPanel(qs('#section-sorteio'));
  });
}

window.addEventListener('jogadores-changed', async () => {
  allJogadores = await getJogadores();
  state.jogadores = allJogadores;
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

bootstrap();
