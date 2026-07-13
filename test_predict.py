import sys
from utils import load_models, predict_complaint

vectorizer, category_model, priority_model = load_models()
texts = [
    "Water is leaking from the main pipe near Jayanagar.",
    "No water supply since morning.",
    "Drainage is blocked and overflowing.",
    "Jayanagar ಹತ್ತಿರ ಮುಖ್ಯ ಪೈಪ್‌ನಿಂದ ನೀರು ಸೋರುತ್ತಿದೆ.",
    "ಕುಡಿಯುವ ನೀರು ಕಲುಷಿತಗೊಂಡಿದೆ.",
    "ಒಳಚರಂಡಿ ಕಟ್ಟಿಕೊಂಡಿದೆ ಮತ್ತು ಉಕ್ಕಿ ಹರಿಯುತ್ತಿದೆ."
]
for t in texts:
    c, p = predict_complaint(t, vectorizer, category_model, priority_model)
    print(f"Text: {t}\nCategory: {c}, Priority: {p}\n")
