import { JSDOM } from 'jsdom';

const dom = new JSDOM('<!doctype html><html><body></body></html>');
global.window = dom.window;
global.document = dom.window.document;
global.bootstrap = { Modal: class { show() {} hide() {} } };

const { renderJogadorList } = await import('../static/js/components/jogador-list.js');

const jogadores = [
  { id: 1, nome: 'Ana', nota: 3, is_goleiro: false, posicoes: [], posicao_primaria_id: null },
  { id: 2, nome: 'Bruno', nota: 3, is_goleiro: false, posicoes: [], posicao_primaria_id: null },
  { id: 3, nome: 'Carla', nota: 3, is_goleiro: false, posicoes: [], posicao_primaria_id: null },
];

const container = document.createElement('div');
document.body.append(container);
const checkedIds = () =>
  [...container.querySelectorAll('.jogador-check:checked')].map((el) => el.value);
const click = (el) => {
  el.checked = !el.checked;
  el.dispatchEvent(new window.Event('change', { bubbles: true }));
};

let failed = 0;
const check = (name, actual, expected) => {
  const ok = JSON.stringify(actual) === JSON.stringify(expected);
  if (!ok) failed += 1;
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name} (esperado [${expected}], obtido [${actual}])`);
};

renderJogadorList(container, jogadores);
click(container.querySelector('.jogador-check[value="1"]'));
click(container.querySelector('.jogador-check[value="2"]'));

renderJogadorList(container, jogadores.filter((j) => j.id !== 1)); // filtro de busca
check('filtro mantem marcacao', checkedIds(), ['2']);

renderJogadorList(container, []); // filtro sem resultado
check('lista vazia fica vazia', checkedIds(), []);

renderJogadorList(container, jogadores); // limpar filtro
check('limpar filtro restaura marcacoes', checkedIds(), ['1', '2']);

click(container.querySelector('.jogador-check[value="2"]')); // desmarcar
check('desmarcar persiste apos re-render (editar)', checkedIds(), ['1']);

process.exit(failed ? 1 : 0);
