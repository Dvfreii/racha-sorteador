export async function postForm(url, form) {
  const response = await fetch(url, { method: 'POST', body: new FormData(form) });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response;
}

export async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}
