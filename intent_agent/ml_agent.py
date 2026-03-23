# NAVIGATIONAL
# INFORMATIONAL
# TECHNICAL
# COMPARISON
# RESEARCH


import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
vectorizer=joblib.load(os.path.join(BASE_DIR, "intent_vectorizer.pkl"))
clf=joblib.load(os.path.join(BASE_DIR, "intent_classifier.pkl"))

def detect_intent(query):
    q=vectorizer.transform([query])
    return clf.predict(q)[0]
