"""
utils.py
--------
Model loading, prediction, and confidence scoring utilities.
"""

import joblib
import os
from preprocessing import preprocess_text


def load_models():
    """Load trained TF-IDF vectorizer and classification models."""
    try:
        vectorizer      = joblib.load('models/tfidf_vectorizer.pkl')
        category_model  = joblib.load('models/category_model.pkl')
        priority_model  = joblib.load('models/priority_model.pkl')
        return vectorizer, category_model, priority_model
    except FileNotFoundError:
        return None, None, None


def load_metrics():
    """Load saved evaluation metrics dict."""
    try:
        return joblib.load('models/metrics.pkl')
    except FileNotFoundError:
        return None


def predict_complaint(text, vectorizer, category_model, priority_model):
    """Basic prediction — returns (category, priority)."""
    cleaned  = preprocess_text(text)
    features = vectorizer.transform([cleaned])
    category = category_model.predict(features)[0]
    priority = priority_model.predict(features)[0]
    return category, priority


def predict_with_confidence(text, vectorizer, category_model, priority_model):
    """
    Extended prediction with confidence scores.

    Returns
    -------
    category        : str   — predicted category label
    priority        : str   — predicted priority label
    conf_category   : float — top-class probability for category (0–100)
    conf_priority   : float — top-class probability for priority  (0–100)
    cat_proba_dict  : dict  — {label: probability} for all categories
    pri_proba_dict  : dict  — {label: probability} for all priorities
    """
    cleaned  = preprocess_text(text)
    features = vectorizer.transform([cleaned])

    # ── Category ──────────────────────────────────────────────────────────────
    category       = category_model.predict(features)[0]
    cat_proba      = category_model.predict_proba(features)[0]
    cat_classes    = category_model.classes_
    conf_category  = float(max(cat_proba)) * 100
    cat_proba_dict = {cls: round(float(p) * 100, 1)
                      for cls, p in zip(cat_classes, cat_proba)}

    # ── Priority ──────────────────────────────────────────────────────────────
    priority       = priority_model.predict(features)[0]
    pri_proba      = priority_model.predict_proba(features)[0]
    pri_classes    = priority_model.classes_
    conf_priority  = float(max(pri_proba)) * 100
    pri_proba_dict = {cls: round(float(p) * 100, 1)
                      for cls, p in zip(pri_classes, pri_proba)}

    return category, priority, conf_category, conf_priority, cat_proba_dict, pri_proba_dict
