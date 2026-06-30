import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Load dataset
data = pd.read_csv("dataset.csv")

X = data["review"]
y = data["sentiment"]

# Convert text into vectors
vectorizer = TfidfVectorizer()

X_vector = vectorizer.fit_transform(X)

# Train model
model = MultinomialNB()

model.fit(X_vector, y)

# Save files
joblib.dump(model, "model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("✅ Model Trained Successfully!")