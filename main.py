import joblib
import re
import nltk
import os
import warnings
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Suppress warnings
warnings.filterwarnings("ignore")

# Setup NLTK
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

def clean_text(text):
    """Preprocessing exactly as done in training"""
    ps = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    text = text.lower()
    text = re.sub('[^a-z]', ' ', text)
    words = text.split()
    words = [ps.stem(word) for word in words if word not in stop_words]
    return " ".join(words)

# Configuration
PROJ_DIR = r"d:\food project"
MODEL_FILE = "advanced_sentiment_model.pkl"
VECT_FILE = "advanced_tfidf_vectorizer.pkl"

def load_resources():
    """Load model and vectorizer from the project directory"""
    try:
        # Try local first, then project dir
        m_path = MODEL_FILE if os.path.exists(MODEL_FILE) else os.path.join(PROJ_DIR, MODEL_FILE)
        v_path = VECT_FILE if os.path.exists(VECT_FILE) else os.path.join(PROJ_DIR, VECT_FILE)
        
        model = joblib.load(m_path)
        vectorizer = joblib.load(v_path)
        return model, vectorizer
    except Exception as e:
        print(f"Error loading models: {e}")
        return None, None

def predict_review(review, model, vectorizer):
    """Perform prediction on a single string"""
    if not model or not vectorizer:
        return "Model not loaded"
    
    clean = clean_text(review)
    # Important: vectorizer.transform expects a list/iterable
    vector = vectorizer.transform([clean]).toarray()
    pred = model.predict(vector)[0]
    
    return "Positive" if pred == 1 else "Negative"

if __name__ == "__main__":
    print("--- Food Review Sentiment Analysis Core ---")
    model, vectorizer = load_resources()
    
    if model and vectorizer:
        print("Model and Vectorizer loaded successfully!")
        print("(Type 'exit' to quit)")
        while True:
            try:
                text = input("\nEnter a review: ").strip()
                if text.lower() == 'exit':
                    break
                if not text:
                    continue
                
                result = predict_review(text, model, vectorizer)
                print(f"Prediction: {result}")
            except KeyboardInterrupt:
                break
    else:
        print("Please ensure the .pkl files are in 'd:\food project\'")
