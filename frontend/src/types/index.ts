export type Model = 'nb' | 'count_lr' | 'tfidf_lr' | 'tfidf_dense';
export type Score = {
    accuracy: number;
    precision: number;
    recall: number;
    f1: number;
    confusion_matrix: number[][];
};
export type Report = {
    metadata: {
        train_rows: number;
        test_rows: number;
        original_rows: number;
        vocab_size: number;
        seed: number;
    };
    models: Record<string, Score>;
};
export type Prediction = {
    model: Model;
    label: 'ham' | 'spam';
    confidence: number;
    normalized: string;
    probabilities: {
        ham: number;
        spam: number;
    };
    warning: string | null;
    explanation?: {
        terms: {
            token: string;
            count: number;
            spam_log_odds_contribution: number;
        }[];
    };
};
