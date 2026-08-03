import { API } from '../config.js';

export async function formatarWhatsApp(times, goleiros, medias) {
  const r = await fetch(API.WHATSAPP, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ times, goleiros, medias }),
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}
