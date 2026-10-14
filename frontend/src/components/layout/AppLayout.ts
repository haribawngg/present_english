import { sidebarTemplate } from './Sidebar';
import { classificationTemplate } from '../../pages/ClassificationPage';
import { evaluationTemplate } from '../../pages/EvaluationPage';
import { ambientBackgroundTemplate } from './AmbientBackground';
export function layoutTemplate(): string {
    return `
${ambientBackgroundTemplate()}${sidebarTemplate()}<div class="shell"><header class="topbar"><div><span class="muted">Workspace</span><span class="separator">/</span><span id="breadcrumb">Phân loại tin nhắn</span></div><button id="connection" class="connection" title="Kiểm tra lại kết nối"><i></i><span>Đang kết nối…</span></button></header>
<main><div id="global-error" role="alert" class="error hidden"></div>
${classificationTemplate()}${evaluationTemplate()}<footer><span>SMS Lab <b>·</b> Text classification playground</span><span>Naive Bayes / Logistic Regression / Neural Network</span></footer></main></div>`;
}
