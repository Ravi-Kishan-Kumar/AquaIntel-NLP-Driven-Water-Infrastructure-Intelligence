import sys
from utils import load_models, predict_complaint
vectorizer, category_model, priority_model = load_models()
texts = ["hello world", "test", ""]
for t in texts:
    c, p = predict_complaint(t, vectorizer, category_model, priority_model)
    print(f"Text: '{t}' -> Category: {c}, Priority: {p}")
