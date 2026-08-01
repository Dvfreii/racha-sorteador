function paint(display, value) {
  display.querySelectorAll('.star-unit').forEach((unit) => {
    const star = Number(unit.dataset.star);
    unit.classList.toggle('is-full', value >= star);
    unit.classList.toggle('is-half', value >= star - 0.5 && value < star);
  });
}

export function mountStarRatings() {
  document.querySelectorAll('.rate').forEach((fieldset) => {
    if (fieldset.dataset.mounted) return;
    fieldset.dataset.mounted = 'true';

    const radios = [...fieldset.querySelectorAll('input[type="radio"]')];
    const display = document.createElement('span');
    display.className = 'star-display';
    display.setAttribute('role', 'radiogroup');
    display.setAttribute('aria-label', 'Nota de 0,5 a 5 estrelas');

    for (let star = 1; star <= 5; star += 1) {
      const unit = document.createElement('span');
      unit.className = 'star-unit';
      unit.dataset.star = String(star);
      unit.innerHTML = '<span class="star-glyph">★</span>';

      const half = document.createElement('button');
      half.type = 'button';
      half.className = 'star-hit star-hit-half';
      half.dataset.value = String(star - 0.5);
      half.setAttribute('aria-label', `${star - 0.5} estrela`);

      const full = document.createElement('button');
      full.type = 'button';
      full.className = 'star-hit star-hit-full';
      full.dataset.value = String(star);
      full.setAttribute('aria-label', `${star} estrela${star > 1 ? 's' : ''}`);

      [half, full].forEach((button) => {
        button.addEventListener('mouseenter', () => paint(display, Number(button.dataset.value)));
        button.addEventListener('click', () => {
          const value = Number(button.dataset.value);
          const radio = radios.find((item) => Number(item.value) === value);
          if (radio) radio.checked = true;
          paint(display, value);
        });
      });

      unit.append(half, full);
      display.append(unit);
    }

    display.addEventListener('mouseleave', () => {
      const selected = radios.find((radio) => radio.checked);
      paint(display, selected ? Number(selected.value) : 0);
    });

    fieldset.append(display);
    const selected = radios.find((radio) => radio.checked);
    paint(display, selected ? Number(selected.value) : 0);
  });
}

export default mountStarRatings;
