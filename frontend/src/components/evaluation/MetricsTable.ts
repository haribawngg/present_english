import { element as $ } from '../../utils/dom';
import { names, descriptions } from '../../constants/models';
import { pct } from '../../utils/format';
import type { Model, Report } from '../../types';
export function renderMetricsTable(report: Report, available: Model[]) {
    $('metrics-table').innerHTML = `<table><thead><tr><th>Mô hình</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1 score</th></tr></thead><tbody>${available.map(m => `<tr><td><b>${names[m]}</b><small>${descriptions[m]}</small></td>${(['accuracy', 'precision', 'recall', 'f1'] as const).map(k => `<td>${pct(report.models[m][k])}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}
