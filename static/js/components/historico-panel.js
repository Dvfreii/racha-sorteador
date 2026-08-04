import { qs } from '../utils/dom.js';
import { estrelas } from '../utils/format.js';
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
      html += '<div class="history-teams">';
      for (const [nome, jogadores] of Object.entries(s.times)) {
        html += `<div><strong>${nome}</strong> (Media ${s.medias[nome]})<small>`;
        html += jogadores.map(j => `${esc(j.nome)} ${estrelas(j.nota)}`).join(', ');
        html += '</small></div>';
      }
      html += '</div>';
      html += '<div class="history-goalies">';
      const goleiros = Object.entries(s.goleiros || {});
      if (goleiros.length) {
        html += '<strong>Goleiros</strong><div class="history-goalies-list">';
        html += goleiros.map(([time, nome]) => `\uD83E\uDD45 ${time}: ${nome}`).join(', ');
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
