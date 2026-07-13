import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import os
import nltk

# Ensure punkt is downloaded here as well, sometimes multithreading needs it
nltk.download('punkt')

from preprocessing import preprocess_text

def train_and_evaluate(X_train, X_test, y_train, y_test, model_name, target_name, model):
    print(f"\n--- Training {model_name} for {target_name} ---")
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, average='weighted', zero_division=0)
    recall = recall_score(y_test, predictions, average='weighted', zero_division=0)
    f1 = f1_score(y_test, predictions, average='weighted', zero_division=0)
    
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    
    # Returning metrics for comparison later
    return model, {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }

def main():
    print("Loading dataset...")
    df = pd.read_csv('large_water_complaints_dataset.csv')
    
    print("Preprocessing text...")
    df['cleaned_text'] = df['complaint_text'].apply(preprocess_text)
    
    # Split data for Category Classification
    X_train_cat, X_test_cat, y_train_cat, y_test_cat = train_test_split(
        df['cleaned_text'], df['category'], test_size=0.2, random_state=42
    )
    
    # Split data for Priority Classification
    X_train_pri, X_test_pri, y_train_pri, y_test_pri = train_test_split(
        df['cleaned_text'], df['priority'], test_size=0.2, random_state=42
    )
    
    print("Vectorizing text using TF-IDF...")
    # Using unigrams, bigrams, and trigrams to capture complex Kannada phrases
    vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 3))
    
    # Fit and transform on training data
    X_train_cat_tfidf = vectorizer.fit_transform(X_train_cat)
    X_test_cat_tfidf = vectorizer.transform(X_test_cat)
    
    X_train_pri_tfidf = vectorizer.transform(X_train_pri)
    X_test_pri_tfidf = vectorizer.transform(X_test_pri)
    
    # Models
    nb_cat = MultinomialNB()
    lr_cat = LogisticRegression(max_iter=1000, class_weight='balanced')
    
    nb_pri = MultinomialNB()
    lr_pri = LogisticRegression(max_iter=1000, class_weight='balanced')
    
    # Train Category Models
    nb_cat_model, nb_cat_metrics = train_and_evaluate(X_train_cat_tfidf, X_test_cat_tfidf, y_train_cat, y_test_cat, "Naive Bayes", "Category", nb_cat)
    lr_cat_model, lr_cat_metrics = train_and_evaluate(X_train_cat_tfidf, X_test_cat_tfidf, y_train_cat, y_test_cat, "Logistic Regression", "Category", lr_cat)
    
    # Train Priority Models
    nb_pri_model, nb_pri_metrics = train_and_evaluate(X_train_pri_tfidf, X_test_pri_tfidf, y_train_pri, y_test_pri, "Naive Bayes", "Priority", nb_pri)
    lr_pri_model, lr_pri_metrics = train_and_evaluate(X_train_pri_tfidf, X_test_pri_tfidf, y_train_pri, y_test_pri, "Logistic Regression", "Priority", lr_pri)
    
    print("\n--- Saving Models and Vectorizer ---")
    os.makedirs('models', exist_ok=True)
    joblib.dump(vectorizer, 'models/tfidf_vectorizer.pkl')
    
    # Save the better performing models (in this typical case, we will just save LR as the primary model, 
    # but we can save both or use LR for the app while showing metrics for both). 
    # Let's save Logistic Regression as the default model for the web app since it often performs better on TF-IDF.
    joblib.dump(lr_cat_model, 'models/category_model.pkl')
    joblib.dump(lr_pri_model, 'models/priority_model.pkl')
    
    # Save metrics for the Streamlit dashboard to show comparison
    metrics = {
        'Category': {'Naive Bayes': nb_cat_metrics, 'Logistic Regression': lr_cat_metrics},
        'Priority': {'Naive Bayes': nb_pri_metrics, 'Logistic Regression': lr_pri_metrics}
    }
    joblib.dump(metrics, 'models/metrics.pkl')
    
    print("All models, vectorizer, and metrics saved successfully in the 'models/' directory.")

if __name__ == "__main__":
    main()
