import json
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

with open("./data/training_data1.json","r") as f:
    data = json.load(f)

queries = [d["query"] for d in data]
labels = [d["intent"] for d in data]

vectorizer = TfidfVectorizer(ngram_range=(1,2))
X = vectorizer.fit_transform(queries)

X_train, X_test, y_train, y_test = train_test_split(
    X, labels, test_size=0.2, random_state=42
)

clf = LogisticRegression(max_iter=1000)
clf.fit(X_train, y_train)

predictions = clf.predict(X_test)

print("Accuracy:", accuracy_score(y_test, predictions))
print(classification_report(y_test, predictions))

joblib.dump(vectorizer,"intent_vectorizer.pkl")
joblib.dump(clf,"intent_classifier.pkl")
