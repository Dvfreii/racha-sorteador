export async function submitForm(form) {
  const response = await fetch(form.action, {
    method: form.method || 'POST',
    body: new FormData(form),
  });
  if (!response.ok) throw new Error(`Falha HTTP ${response.status}`);
  return response;
}

export function selectedPlayers() {
  return [...document.querySelectorAll('.jogador-check:checked')]
    .map((item) => Number(item.value));
}
