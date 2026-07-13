import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Initialize lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
try:
    stop_words = set(stopwords.words('english'))
except LookupError:
    stop_words = set()

# Custom stopwords for Kannada transliterated and native text commonly found in dataset
custom_stopwords = {
    'illa', 'agthide', 'agide', 'barthide', 'nalli', 'hatra', 'inda', 'nam', 'manege', 'namma', 'bere',
    'ide', 'banthu', 'gottilla', 'matte', 'swalpa', 'tumba',
    'ಇಲ್ಲ', 'ಆಗ್ತಿದೆ', 'ಆಗಿದೆ', 'ಬರ್ತಿದೆ', 'ನಲ್ಲಿ', 'ಹತ್ರ', 'ಇಂದ', 'ನಮ್ಮ', 'ಮನೆಗೆ'
}
stop_words.update(custom_stopwords)

def preprocess_text(text):
    """
    Complete NLP preprocessing pipeline.
    1. Lowercasing
    2. Removing special characters and numbers
    3. Tokenization
    4. Stopword removal
    5. Lemmatization
    """
    if not isinstance(text, str):
        return ""
        
    # 1. Lowercasing
    text = text.lower()
    
    # 2. Removing special characters and numbers (keeping English alphabets, Kannada Unicode, and spaces)
    text = re.sub(r'[^a-zA-Z\u0C80-\u0CFF\s]', '', text)
    
    # 3. Tokenization
    try:
        tokens = word_tokenize(text)
    except LookupError:
        tokens = text.split()
    
    # 4. Stopword removal & 5. Lemmatization
    cleaned_tokens = []
    for word in tokens:
        if word in stop_words:
            continue
        try:
            cleaned_tokens.append(lemmatizer.lemmatize(word))
        except LookupError:
            cleaned_tokens.append(word)
    
    # Rejoin tokens into a single string
    return " ".join(cleaned_tokens)
