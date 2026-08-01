import { mountPlayerSelection } from './components/player-selection.js';

mountPlayerSelection();

export default {
  name: 'Sorteador de Racha',
  version: '1.0.0',
  mode: 'web',
  backend: 'Flask',
  database: 'SQLite',
};

// Frontend modular: components, hooks, utils, api e services.
// O backend continua responsável pelo algoritmo e pela persistência.
