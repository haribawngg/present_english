import { element } from '../../utils/dom';
export function bindNavigation() {
    document.querySelectorAll<HTMLButtonElement>('[data-view]').forEach(button => {
        button.onclick = () => {
            const evaluation = button.dataset.view === 'evaluation';
            element('classify-view').classList.toggle('hidden', evaluation);
            element('evaluation-view').classList.toggle('hidden', !evaluation);
            document.querySelectorAll('[data-view]').forEach(item => {
                item.classList.toggle('active', item === button);
            });
            element('breadcrumb').textContent = evaluation ? 'Đánh giá mô hình' : 'Phân loại tin nhắn';
        };
    });
}
