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


def find_similar_complaints(new_text, candidate_complaints, vectorizer, threshold=0.55):
    """
    TF-IDF Cosine Similarity check against active complaints in the same location.

    Parameters
    ----------
    new_text            : str   — raw text of the new complaint
    candidate_complaints: list  — list of dicts with keys 'complaint_text', 'ticket_id',
                                  'submitted_at', 'category', 'location'
    vectorizer          : fitted TfidfVectorizer
    threshold           : float — minimum cosine similarity to flag as similar (default 0.55)

    Returns
    -------
    list of dicts sorted by similarity desc:
        [{'ticket_id', 'similarity', 'complaint_text', 'submitted_at', 'category'}, ...]
    """
    from sklearn.metrics.pairwise import cosine_similarity

    if not candidate_complaints or vectorizer is None:
        return []

    new_cleaned = preprocess_text(new_text)
    texts       = [preprocess_text(c['complaint_text']) for c in candidate_complaints]

    try:
        all_vecs   = vectorizer.transform([new_cleaned] + texts)
        new_vec    = all_vecs[0:1]
        cand_vecs  = all_vecs[1:]
        sims       = cosine_similarity(new_vec, cand_vecs).flatten()
    except Exception:
        return []

    results = []
    for i, sim in enumerate(sims):
        if sim >= threshold:
            c = candidate_complaints[i]
            results.append({
                'ticket_id':      c.get('ticket_id', '—'),
                'similarity':     round(float(sim) * 100, 1),
                'complaint_text': c.get('complaint_text', ''),
                'submitted_at':   c.get('submitted_at', ''),
                'category':       c.get('category', ''),
                'location':       c.get('location', ''),
            })

    results.sort(key=lambda x: -x['similarity'])
    return results
