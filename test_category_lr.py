import joblib
vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
category_model = joblib.load('models/category_model.pkl')
print("Model classes:", category_model.classes_)
feature_names = vectorizer.get_feature_names_out()
for i, c in enumerate(category_model.classes_):
    coefs = category_model.coef_[i]
    top_indices = coefs.argsort()[-5:][::-1]
    top_features = [feature_names[j] for j in top_indices]
    print(f"Top features for {c}: {top_features}")
