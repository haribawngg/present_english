export async function api<T>(path: string, body?: unknown): Promise<T> {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 60000);
    try {
        const response = await fetch(`/api/${path}`, { signal: controller.signal, ...(body ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) } : {}) });
        const data = await response.json();
        if (!response.ok)
            throw new Error(data.detail || 'API không thể xử lý yêu cầu.');
        return data as T;
    }
    catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError')
            throw new Error('Yêu cầu quá thời gian. Hãy thử lại.');
        throw error;
    }
    finally {
        window.clearTimeout(timeout);
    }
}
