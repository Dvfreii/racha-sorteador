export function estrelas(nota) {
  const inteiro = Math.floor(nota);
  const resto = nota - inteiro;
  const stars = '\u2605'.repeat(inteiro);
  return resto === 0.5 ? stars + '\u00BD' : stars;
}

export function iconePosicao(jogador) {
  if (jogador.is_goleiro) return '\uD83E\uDDE4';
  const nomes = (jogador.posicoes || []).map(p => p.nome.toLowerCase());
  if (nomes.some(n => n.includes('zagueiro') || n.includes('fixo'))) return '\uD83D\uDEE1\uFE0F';
  return '\u26BD';
}
