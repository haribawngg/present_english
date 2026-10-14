import type { Model, Prediction, Report } from './types';
import { names } from './constants/models';
import { api } from './services/api';
import { createAppState } from './state/appState';
import { element } from './utils/dom';
import { downloadJson } from './utils/download';
import { layoutTemplate } from './components/layout/AppLayout';
import { bindNavigation } from './components/layout/Navigation';
import { setConnection, showError } from './components/layout/Feedback';
import { bindComposer, readMessage, setSubmitState } from './components/classifier/MessageComposer';
import { renderModels } from './components/classifier/ModelSelector';
import { renderResult, resetResult } from './components/classifier/PredictionResult';
import { renderStats } from './components/dashboard/StatsCards';
import { renderMetricsTable } from './components/evaluation/MetricsTable';
import { renderMatrix } from './components/evaluation/ConfusionMatrix';
/** Owns async orchestration; components receive data and report user actions. */
export function startApp(root: HTMLElement) {
    root.innerHTML = layoutTemplate();
    const state = createAppState();
    function updateSubmit() {
        setSubmitState(state.ready, state.busy);
    }
    function invalidate() {
        state.revision++;
        resetResult();
        updateSubmit();
    }
    function updateModels() {
        renderModels(state.available, state.selected, model => {
            state.selected = model;
            updateModels();
            invalidate();
        });
    }
    async function connect() {
        showError();
        setConnection('loading');
        state.ready = false;
        updateSubmit();
        try {
            const [models, report] = await Promise.all([
                api<{
                    models: Model[];
                }>('models'),
                api<Report>('metrics'),
            ]);
            state.available = models.models.filter(model => model in names);
            if (!state.available.length)
                throw new Error('Không có mô hình khả dụng.');
            if (!state.available.includes(state.selected))
                state.selected = state.available[0];
            state.report = report;
            state.ready = true;
            updateModels();
            renderStats(report, state.available);
            renderMetricsTable(report, state.available);
            element('matrix-model').innerHTML = state.available
                .map(model => `<option value="${model}">${names[model]}</option>`).join('');
            renderMatrix(report);
            element<HTMLButtonElement>('download').disabled = false;
            setConnection('ready');
        }
        catch (error) {
            showError(`Không kết nối được backend. Kiểm tra server rồi nhấn trạng thái kết nối để thử lại. ${error instanceof Error ? error.message : ''}`);
            setConnection('error');
        }
        updateSubmit();
    }
    async function predict() {
        if (state.busy || !state.ready || !readMessage().trim())
            return;
        const revision = state.revision;
        state.busy = true;
        showError();
        updateSubmit();
        const started = performance.now();
        try {
            const data = await api<{
                predictions: Prediction[];
            }>('predict', {
                messages: [readMessage()], model: state.selected, explain: true,
            });
            if (state.revision === revision)
                renderResult(data.predictions[0], performance.now() - started);
        }
        catch (error) {
            showError(error instanceof Error ? error.message : 'Không thể phân loại.');
        }
        finally {
            state.busy = false;
            updateSubmit();
        }
    }
    bindNavigation();
    bindComposer(invalidate, () => void predict());
    element('connection').onclick = () => void connect();
    element('matrix-model').onchange = () => {
        if (state.report)
            renderMatrix(state.report);
    };
    element('download').onclick = () => {
        if (state.report)
            downloadJson(state.report, 'sms-lab-metrics.json');
    };
    void connect();
}
