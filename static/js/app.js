import { mountPlayerSelection } from './components/player-selection.js';
import { mountStarRatings } from './components/star-rating.js';

mountPlayerSelection();
mountStarRatings();

export default {
  name: 'Sorteador de Racha',
  version: '1.0.0',
  mode: 'web',
  backend: 'Flask',
  database: 'SQLite',
};

// Frontend modular: components, hooks, utils, api e services.
// O backend continua responsável pelo algoritmo e pela persistência.
