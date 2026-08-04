import { qs } from '../utils/dom.js';
import { estrelas, iconePosicao } from '../utils/format.js';
import { salvarSorteio } from '../api/sorteios.js';
import state from '../state.js';

function esc(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

export function renderResultadoPanel(container, resultado) {
  if (!resultado) { container.innerHTML = ''; return; }

  const { times, goleiros, medias } = resultado;

  let html = '<section class="results mt-4">';
  html += '<div class="panel-heading"><div><span class="section-kicker">RESULTADO</span><h2>Times sorteados</h2></div></div>';
  html += '<div class="row g-3">';

  for (const [nome, jogadores] of Object.entries(times)) {
    const media = medias[nome];
    const goleiro = goleiros[nome];
    html += `<div class="col-12 col-md-4"><div class="team">`;
    html += `<div class="team-title"><h3>${nome}</h3><span>${media} \u2605</span></div><ol>`;
    for (const j of jogadores) {
      if (j.is_goleiro) continue;
      html += `<li><span>${iconePosicao(j)} ${esc(j.nome)}</span><small>${estrelas(j.nota)}</small></li>`;
    }
    html += `</ol>`;
    html += `<div class="goalie-note">\uD83E\uDD45 Goleiro: <strong>${goleiro ? esc(goleiro.nome) : 'Improvisado'}</strong></div>`;
    html += `</div></div>`;
  }

  html += '</div>';
  html += '<div class="d-flex gap-2 mt-3">';
  html += '<button id="btn-salvar" class="btn btn-outline-primary">Salvar no historico</button>';
  html += '<button id="btn-copiar" class="btn btn-primary">\uD83D\uDCCB Copiar para WhatsApp</button>';
  html += '</div>';
  html += '</section>';

  container.innerHTML = html;

  qs('#btn-salvar')?.addEventListener('click', async () => {
    const timesIds = {};
    for (const [nome, jogadores] of Object.entries(times)) {
      timesIds[nome] = jogadores.map(j => j.id);
    }
    const goleirosIds = {};
    for (const [nome, g] of Object.entries(goleiros)) {
      goleirosIds[nome] = g ? g.id : null;
    }
    try {
      await salvarSorteio(timesIds, goleirosIds);
      window.dispatchEvent(new CustomEvent('jogadores-changed'));
      alert('Sorteio salvo!');
    } catch (err) {
      alert(err.message);
    }
  });

  qs('#btn-copiar')?.addEventListener('click', () => {
    window.dispatchEvent(new CustomEvent('open-whatsapp-preview', { detail: resultado }));
  });
}
