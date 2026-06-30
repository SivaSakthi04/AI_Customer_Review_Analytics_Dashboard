import joblib

# Load trained model and vectorizer
model = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")


def predict_sentiment(review):

    review_vector = vectorizer.transform([review])

    prediction = model.predict(review_vector)[0]

    confidence = round(
        max(model.predict_proba(review_vector)[0]) * 100, 2
    )

    return prediction, confidence


# Test
if __name__ == "__main__":

    review = input("Enter Review : ")

    sentiment, confidence = predict_sentiment(review)

    print("\nPrediction :", sentiment)
    print("Confidence :", confidence, "%")