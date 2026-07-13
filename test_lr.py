import joblib
import pandas as pd
vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
priority_model = joblib.load('models/priority_model.pkl')
print("Model classes:", priority_model.classes_)
feature_names = vectorizer.get_feature_names_out()
for i, c in enumerate(priority_model.classes_):
    coefs = priority_model.coef_[i]
    top_indices = coefs.argsort()[-5:][::-1]
    top_features = [feature_names[j] for j in top_indices]
    print(f"Top features for {c}: {top_features}")
