import type { Model, Report } from '../types';
export function createAppState() {
    return {
        available: [] as Model[],
        selected: 'nb' as Model,
        report: null as Report | null,
        ready: false,
        busy: false,
        // Ignore responses when the user changes the message/model mid-request.
        revision: 0,
    };
}
