import { icon } from '../utils/icons';
import { composerTemplate } from '../components/classifier/MessageComposer';
import { resultTemplate } from '../components/classifier/PredictionResult';
import { pipelineTemplate } from '../components/classifier/Pipeline';
export function classificationTemplate(): string {
    return `<section id="classify-view"><div class="page-heading"><div><div class="eyebrow">SMS CLASSIFIER</div><h1>Tin nhắn này có phải spam?</h1><p>Nhập một tin nhắn và khám phá cách mô hình đưa ra quyết định.</p></div><span class="outline-tag">${icon('spark')} Live inference</span></div>
<div class="stats" id="stats"><div class="stat"><span>MÔ HÌNH SẴN SÀNG</span><strong>—</strong></div><div class="stat"><span>TẬP HUẤN LUYỆN</span><strong>—</strong></div><div class="stat"><span>TẬP KIỂM TRA</span><strong>—</strong></div><div class="stat"><span>ACCURACY · NAIVE BAYES</span><strong>—</strong></div></div>
<div class="work-grid">${composerTemplate()}${resultTemplate()}</div>
${pipelineTemplate()}</section>
`;
}
