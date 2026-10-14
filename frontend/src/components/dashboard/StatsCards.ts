import { element as $ } from '../../utils/dom';
import { pct } from '../../utils/format';
import type { Model, Report } from '../../types';
export function renderStats(report: Report, available: Model[]) {
    const meta = report.metadata;
    $('stats').innerHTML = [['MÔ HÌNH SẴN SÀNG', String(available.length), 'Đã huấn luyện'], ['TẬP HUẤN LUYỆN', meta.train_rows.toLocaleString('vi-VN'), 'Tin nhắn sau làm sạch'], ['TẬP KIỂM TRA', meta.test_rows.toLocaleString('vi-VN'), `Split cố định · seed ${meta.seed}`], ['ACCURACY · NAIVE BAYES', pct(report.models.nb.accuracy), 'Đánh giá trên tập test']].map(([label, value, note]) => `<div class="stat"><span>${label}</span><strong>${value}</strong><small>${note}</small></div>`).join('');
}
