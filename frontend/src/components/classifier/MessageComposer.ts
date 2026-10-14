import { element } from '../../utils/dom';
export function readMessage(): string {
    return element<HTMLTextAreaElement>('message').value;
}
export function setSubmitState(ready: boolean, busy: boolean) {
    const button = element<HTMLButtonElement>('predict');
    button.disabled = !ready || busy || !readMessage().trim();
    button.innerHTML = busy
        ? 'Đang phân tích <span class="spinner"></span>'
        : 'Phân loại tin nhắn <span>→</span>';
}
export function bindComposer(onChange: () => void, onSubmit: () => void) {
    const message = element<HTMLTextAreaElement>('message');
    message.oninput = () => {
        element('character-count').textContent = `${message.value.length.toLocaleString('vi-VN')} / 5.000`;
        onChange();
    };
    element('clear').onclick = () => {
        message.value = '';
        message.dispatchEvent(new Event('input'));
        message.focus();
    };
    document.querySelectorAll<HTMLButtonElement>('[data-sample]').forEach(button => {
        button.onclick = () => {
            message.value = button.dataset.sample === 'spam'
                ? 'Congratulations! You have won a FREE cash prize. Call 09012345678 now to claim your reward!'
                : 'Hey, are we still meeting for dinner tonight? I will see you at 7.';
            message.dispatchEvent(new Event('input'));
        };
    });
    element('predict').onclick = onSubmit;
}
export function composerTemplate(): string {
    return `<section class="card compose"><div class="card-heading"><h2><span class="step">01</span> Soạn tin nhắn</h2><button id="clear" class="text-button">Xóa nội dung</button></div><label class="field-label" for="message">Nội dung cần phân loại</label><div class="textarea-wrap"><textarea id="message" maxlength="5000" placeholder="Nhập SMS tiếng Anh tại đây…&#10;&#10;Ví dụ: Congratulations! You won a free prize. Call now!"></textarea><span id="character-count">0 / 5.000</span></div>
<div class="sample-row"><span>Thử nhanh</span><button data-sample="spam">✦ Tin quảng cáo</button><button data-sample="ham">☏ Tin thông thường</button></div>
<div class="model-heading"><label class="field-label">Chọn mô hình</label><span id="model-count" class="muted">Đang tải…</span></div><div id="model-options" class="model-options"></div>
<button id="predict" class="primary" disabled>Phân loại tin nhắn <span>→</span></button><p class="input-note">Dataset tiếng Anh · Không lưu nội dung tin nhắn trên máy chủ</p></section>
`;
}
