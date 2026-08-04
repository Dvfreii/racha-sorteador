import { qs } from '../utils/dom.js';
import { formatarWhatsApp } from '../api/whatsapp.js';

export function renderWhatsAppPreview(container) {
  container.innerHTML = `
    <div class="modal fade" id="whatsapp-modal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5>Copiar para WhatsApp</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <pre id="whatsapp-text" style="white-space: pre-wrap; font-family: monospace; font-size: 14px; background: #e8f5ee; border-radius: 8px; padding: 16px;"></pre>
          </div>
          <div class="modal-footer">
            <button id="btn-copy-text" class="btn btn-primary">Copiar texto</button>
          </div>
        </div>
      </div>
    </div>`;
}

export async function showWhatsAppPreview(resultado) {
  const modal = document.getElementById('whatsapp-modal');
  const pre = document.getElementById('whatsapp-text');

  try {
    const { texto } = await formatarWhatsApp(
      resultado.times,
      resultado.goleiros,
      resultado.medias,
    );
    pre.textContent = texto;

    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();

    document.getElementById('btn-copy-text').onclick = () => {
      navigator.clipboard.writeText(texto).then(() => {
        alert('Texto copiado! Cole no WhatsApp.');
        bsModal.hide();
      });
    };
  } catch (err) {
    pre.textContent = 'Erro ao gerar texto.';
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
  }
}
