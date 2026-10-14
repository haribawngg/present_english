import type { Model } from '../types';
export const names: Record<Model, string> = { nb: 'Naive Bayes', count_lr: 'Count + Logistic', tfidf_lr: 'TF-IDF + Logistic', tfidf_dense: 'TF-IDF + Dense' };
export const descriptions: Record<Model, string> = { nb: 'Counter · Multinomial NB', count_lr: 'Tần suất từ · Logistic Regression', tfidf_lr: 'Trọng số TF-IDF · Logistic Regression', tfidf_dense: 'TF-IDF · Neural Network' };
