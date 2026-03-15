import joblib

vectorizer=joblib.load("intent_vectorizer.pkl")
clf=joblib.load("intent_classifier.pkl")

def detect_intent(query):
    q=vectorizer.transform([query])
    return clf.predict(q)[0]



