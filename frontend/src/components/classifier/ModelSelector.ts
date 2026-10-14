import { element as $ } from '../../utils/dom';
import { names, descriptions } from '../../constants/models';
import type { Model } from '../../types';
export function renderModels(available: Model[], selected: Model, onSelect: (model: Model) => void) {
    $('model-count').textContent = `${available.length} mô hình`;
    $('model-options').innerHTML = available.map(m => `<button class="model-option ${m === selected ? 'selected' : ''}" data-model="${m}" aria-pressed="${m === selected}"><span class="radio"></span><span><b>${names[m]}</b><small>${descriptions[m]}</small></span>${m === 'nb' ? '<em>Baseline</em>' : ''}</button>`).join('');
    document.querySelectorAll<HTMLButtonElement>('[data-model]').forEach(btn => btn.onclick = () => { onSelect(btn.dataset.model as Model); });
}
