import { qs } from '../utils/dom.js';
import { getHistorico, deleteSorteio } from '../api/sorteios.js';

function esc(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

export async function renderHistoricoPanel(container) {
  container.innerHTML = '<p class="text-muted">Carregando...</p>';

  try {
    const historico = await getHistorico(20);

    if (!historico.length) {
      container.innerHTML = '<p class="empty-state">Nenhum sorteio salvo ainda.</p>';
      return;
    }

    let html = '<section class="panel history-panel">';
    html += '<div class="panel-heading"><h2>Historico</h2></div>';

    for (const s of historico) {
      const d = new Date(s.data);
      const data = d.toLocaleDateString('pt-BR') + ' ' + d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
      html += `<details class="history-item">`;
      html += `<summary>Sorteio #${s.id} \u00B7 ${data} <button class="btn-del-sorteio icon-button" data-id="${s.id}" title="Excluir">\u00D7</button></summary>`;
      html += '<div class="team-columns">';
      const nomes = Object.keys(s.times);
      for (let i = 0; i < nomes.length; i++) {
        const nome = nomes[i];
        const jogadores = s.times[nome];
        const g = (s.goleiros || {})[nome];
        html += `<div class="team-col">`;
        html += `<h3 class="team-col-title">Time ${i + 1}</h3>`;
        html += '<ul class="team-col-list">';
        for (const j of jogadores) {
          if (g && j.nome === g) continue;
          html += `<li>${esc(j.nome)}</li>`;
        }
        html += '</ul>';
        if (g) html += `<div class="goalie-note">Goleiro: <strong>${esc(g)}</strong></div>`;
        html += '</div>';
      }
      html += '</div></details>';
    }

    html += '</section>';
    container.innerHTML = html;

    container.querySelectorAll('.btn-del-sorteio').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        await deleteSorteio(parseInt(btn.dataset.id));
        renderHistoricoPanel(container);
      });
    });

  } catch (err) {
    container.innerHTML = '<p class="text-danger">Erro ao carregar historico.</p>';
  }
}
