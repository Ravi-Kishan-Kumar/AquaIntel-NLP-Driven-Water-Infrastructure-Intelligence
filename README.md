# 💧 AquaIntel — NLP Water Complaint Intelligence System

> **College Project | Course: Natural Language Processing**  
> An end-to-end NLP-powered system to classify, prioritize, and analyze water-related citizen complaints for smart city governance in Bangalore.

---

## 📌 Project Objectives

| # | Objective |
|---|-----------|
| 1 | Automatically **classify** water complaints into categories: Leakage, Contamination, Supply Issues, Drainage Overflow, Billing Problems |
| 2 | **Determine urgency levels** (High / Medium / Low) to support faster prioritization of critical issues |
| 3 | **Detect recurring complaint patterns** across locations and time periods to identify infrastructure hotspots |
| 4 | Generate **actionable insights** through interactive visualizations and location-based analytics |

---

## 🧠 NLP Pipeline

```
Raw Complaint Text (English / Kannada / Code-mixed)
        ↓
   Preprocessing
   • Lowercasing
   • Special character removal (keeps Kannada Unicode [\u0C80-\u0CFF])
   • Tokenization (NLTK word_tokenize)
   • Stopword removal (English + custom Kannada stopwords)
   • Lemmatization (WordNet)
        ↓
   Feature Extraction
   • TF-IDF Vectorizer (max_features=10000, ngram_range=(1,3))
        ↓
   Classification Models
   • Naive Bayes   (MultinomialNB)
   • Logistic Regression (class_weight='balanced', max_iter=1000)
        ↓
   Outputs: Category + Priority + Confidence Scores
```

---

## 🏗️ System Architecture

```
NLP Water Complaint Analyzer/
├── app.py                    # Entry point — session routing
├── preprocessing.py          # NLP preprocessing pipeline
├── train_model.py            # Model training + evaluation
├── utils.py                  # Model loading + prediction with confidence
├── recurring_detector.py     # Recurring issue detection engine
├── generate_data.py          # Synthetic dataset generator
│
├── auth/
│   ├── db.py                 # SQLite DB — users, complaints, Bangalore regions
│   └── auth_ui.py            # Login / Registration UI
│
├── pages/
│   ├── citizen_portal.py     # Citizen: submit + track complaints
│   └── authority_portal.py   # Authority: full analytics dashboard
│
├── models/
│   ├── tfidf_vectorizer.pkl  # Trained TF-IDF vectorizer
│   ├── category_model.pkl    # Logistic Regression (category)
│   ├── priority_model.pkl    # Logistic Regression (priority)
│   └── metrics.pkl           # NB vs LR evaluation metrics
│
├── large_water_complaints_dataset.csv   # Training dataset (~10k records)
├── requirements.txt
└── water_complaints.db       # SQLite DB (auto-created on first run)
```

---

## 🔑 Key Features

### 👤 Citizen Portal
- Submit water complaints in **English, Kannada, or code-mixed text**
- AI classifies complaint → shows **category + priority + confidence scores**
- Low-confidence warning if model is uncertain (<55%)
- Generates a unique **Ticket ID** (e.g. `WC-20260604-3FF6D5`)
- **My Complaints** — full history with status tracking and resolution notes

### 🏛️ Authority Portal (6 Dashboard Tabs)

| Tab | Description |
|-----|-------------|
| **Overview** | Live metrics: total, pending, in-progress, resolved, high-priority open |
| **Analytics** | Category charts, priority distribution, time trends, word cloud |
| **Hotspot Map** | Interactive Folium map with color-coded circles + heatmap layer |
| **Region Analysis** | Drill-down by Bangalore locality with category/priority breakdown |
| **Recurring Issues** | Detects locations with repeated complaints within configurable time windows |
| **Manage Complaints** | Update status, add resolution notes, filter + download reports |
| **Model Metrics** | NB vs Logistic Regression comparison (Accuracy, Precision, Recall, F1) |

### 🗺️ Hotspot Map Legend
| Circle Color | Risk Level | Meaning |
|---|---|---|
| 🔴 **Bold Red** | Critical | High complaint volume + High priority open cases |
| 🟠 **Orange** | Elevated | Moderate complaint load requiring attention |
| 🟡 **Yellow** | Monitor | Low complaint volume, watch for trends |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend / UI | Streamlit |
| NLP Preprocessing | NLTK (tokenization, lemmatization, stopwords) |
| Feature Extraction | scikit-learn TF-IDF Vectorizer |
| Classification | Logistic Regression + Naive Bayes (scikit-learn) |
| Database | SQLite (via Python `sqlite3`) |
| Authentication | bcrypt password hashing |
| Maps | Folium (circle markers + heatmap) |
| Charts | Matplotlib, Seaborn, Plotly |
| Word Cloud | wordcloud library |

---

## ⚙️ Setup & Run

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/nlp-water-complaint-analyzer.git
cd nlp-water-complaint-analyzer
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download NLTK data
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### 5. Train the models
```bash
python train_model.py
```

### 6. Run the app
```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 🔐 Login Credentials (Demo)

| Role | How to register |
|------|----------------|
| **Citizen** | Register with any email + password |
| **Authority** | Register with role = Authority + code: `WATER_AUTH_2024` |

---

## 📊 Model Performance

Both models trained on ~10,000 synthetic Bangalore water complaints (English + Kannada + code-mixed):

| Task | Model | Accuracy | F1-Score |
|------|-------|----------|----------|
| Category | Logistic Regression | ~0.96+ | ~0.96+ |
| Category | Naive Bayes | ~0.93+ | ~0.93+ |
| Priority | Logistic Regression | ~0.94+ | ~0.94+ |
| Priority | Naive Bayes | ~0.90+ | ~0.90+ |

> *Logistic Regression outperforms Naive Bayes because TF-IDF features are correlated — LR handles this better than NB's independence assumption.*

---

## 🗺️ Bangalore Regions Supported

60+ localities including: Koramangala, Whitefield, HSR Layout, Indiranagar, Jayanagar, Electronic City, Marathahalli, Hebbal, JP Nagar, BTM Layout, Malleswaram, and more.

---

## 📄 Dataset

The dataset (`large_water_complaints_dataset.csv`) contains ~10,000 synthetic water-related complaints:
- **Languages**: English, Native Kannada (ಕನ್ನಡ), Transliterated Kannada, Code-mixed
- **Categories**: Leakage, Contamination, Water Supply Issues, Drainage Overflow, Billing Problems
- **Priority Labels**: High, Medium, Low
- **Fields**: `complaint_text`, `category`, `priority`, `location`, `date`

---

## 👨‍💻 Author

**Ravi Kumar** — B.E. / B.Tech Student  
**Srikar Reddy** — B.E. / B.Tech Student
**Rayala Yuvaraj Vaishnav** — B.E. / B.Tech Student
Course: Natural Language Processing  

---

## 📜 License

This project is for academic purposes only.
