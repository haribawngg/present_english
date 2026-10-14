import { element as $ } from '../../utils/dom';
import type { Model, Report } from '../../types';
export function renderMatrix(report: Report) {
    const m = $<HTMLSelectElement>('matrix-model').value as Model;
    const cm = report.models[m].confusion_matrix;
    $('matrix').innerHTML = `<div class="matrix-wrap"><div class="matrix-grid"><div></div><span>Dự đoán ham</span><span>Dự đoán spam</span><span>Thực tế ham</span><div class="correct"><strong>${cm[0][0]}</strong><small>True negative</small></div><div class="incorrect"><strong>${cm[0][1]}</strong><small>False positive</small></div><span>Thực tế spam</span><div class="incorrect"><strong>${cm[1][0]}</strong><small>False negative</small></div><div class="correct"><strong>${cm[1][1]}</strong><small>True positive</small></div></div><div class="matrix-info"><h3>Đọc kết quả</h3><p><b>${cm[0][1]} tin thường</b> bị nhận nhầm thành spam.</p><p><b>${cm[1][0]} tin spam</b> bị bỏ sót và nhận thành ham.</p><p class="footnote">Precision đo độ chính xác khi báo spam. Recall đo khả năng tìm được các tin spam thực sự.</p></div></div>`;
}
