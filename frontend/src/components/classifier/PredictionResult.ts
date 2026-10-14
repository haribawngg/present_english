import { element as $ } from '../../utils/dom';
import { names } from '../../constants/models';
import { pct, escape } from '../../utils/format';
import type { Prediction } from '../../types';
export function resetResult() {
    $('result-state').textContent = 'Chưa phân loại';
    $('result').innerHTML = `<div class="empty-state"><div class="empty-art"><span>▤</span><b>?</b></div><h3>Sẵn sàng cho lần phân tích mới</h3><p>Nhấn phân loại để xem kết quả với nội dung<br>và mô hình đang chọn.</p></div>`;
}
export function resultTemplate(): string {
    return `<section class="card result-card"><div class="card-heading"><h2><span class="step">02</span> Kết quả phân tích</h2><span id="result-state" class="soft-tag">Chờ tin nhắn</span></div><div id="result" aria-live="polite"><div class="empty-state"><div class="empty-art"><span>▤</span><b>?</b></div><h3>Mỗi tin nhắn đều có tín hiệu</h3><p>Chọn một mô hình và nhấn phân loại.<br>Kết quả sẽ xuất hiện tại đây.</p><div class="empty-labels"><span>HAM · Tin thường</span><span>SPAM · Tin rác</span></div></div></div></section>`;
}
export function renderResult(p: Prediction, elapsed: number) {
    const spam = p.label === 'spam';
    $('result-state').textContent = `${elapsed.toFixed(0)} ms`;
    $('result').innerHTML = `<div class="verdict ${spam ? 'spam' : 'ham'}"><span class="verdict-icon">${spam ? '!' : '✓'}</span><div><span class="tiny">${names[p.model].toUpperCase()}</span><h3>${spam ? 'Có dấu hiệu spam' : 'Tin nhắn thông thường'}</h3><p>${spam ? 'Mô hình phân loại đây là tin nhắn rác.' : 'Mô hình phân loại đây là tin nhắn ham.'}</p></div><b>${p.label.toUpperCase()}</b></div>
  <div class="probability-heading"><h3>Xác suất dự đoán</h3><span class="muted">${pct(p.confidence)} · ${p.label}</span></div>
  <div class="probability"><div><span><i class="dot ham-dot"></i> Ham</span><b>${pct(p.probabilities.ham)}</b></div><div class="track"><span class="ham-bar" style="width:${p.probabilities.ham * 100}%"></span></div></div>
  <div class="probability"><div><span><i class="dot spam-dot"></i> Spam</span><b>${pct(p.probabilities.spam)}</b></div><div class="track"><span class="spam-bar" style="width:${p.probabilities.spam * 100}%"></span></div></div>
  <p class="footnote">Xác suất do mô hình ước lượng, chưa được hiệu chỉnh.</p>${p.warning ? '<div class="warning">Không có token trong vocabulary. Kết quả chỉ dựa trên baseline của mô hình.</div>' : ''}
  <div class="normalized"><h3>Văn bản sau chuẩn hóa</h3><div class="tokens">${p.normalized ? p.normalized.split(' ').map(t => `<span>${escape(t)}</span>`).join('') : '<span>Không có token</span>'}</div></div>
  ${p.explanation ? `<details open><summary>Từ nào ảnh hưởng đến dự đoán?</summary><p class="footnote">Đóng góp log-odds: dương nghiêng về spam, âm nghiêng về ham.</p><div class="terms">${p.explanation.terms.slice(0, 8).map(t => `<div><code>${escape(t.token)}</code><span class="${t.spam_log_odds_contribution >= 0 ? 'red' : 'green'}">${t.spam_log_odds_contribution >= 0 ? '+' : ''}${t.spam_log_odds_contribution.toFixed(2)}</span></div>`).join('') || '<p class="muted">Không có từ đã biết.</p>'}</div></details>` : '<div class="model-tip">Chọn Naive Bayes để xem đóng góp của từng từ vào dự đoán.</div>'}`;
}
