import { element } from '../../utils/dom';
export function showError(message = '') {
    element('global-error').textContent = message;
    element('global-error').classList.toggle('hidden', !message);
}
export function setConnection(status: 'loading' | 'ready' | 'error') {
    const button = element('connection');
    button.classList.toggle('online', status === 'ready');
    button.querySelector('span')!.textContent = {
        loading: 'Đang kết nối…', ready: 'Flask API đã kết nối', error: 'Kết nối lại',
    }[status];
}
