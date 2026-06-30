from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_file
)

import sqlite3
import pandas as pd

from sentiment import predict_sentiment

app = Flask(__name__)
app.secret_key = "customer_review_secret_key"

DB_PATH = "database/sentiment.db"


# -----------------------------
# Database Connection
# -----------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# Save Prediction
# -----------------------------
def save_prediction(review, sentiment, confidence):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO history
        (review,sentiment,confidence)

        VALUES(?,?,?)
        """,
        (review, sentiment, confidence)
    )

    conn.commit()

    conn.close()


# -----------------------------
# Dashboard Statistics
# -----------------------------
def get_dashboard_data():

    conn = get_connection()

    total = conn.execute(
        "SELECT COUNT(*) FROM history"
    ).fetchone()[0]

    positive = conn.execute(
        "SELECT COUNT(*) FROM history WHERE sentiment='Positive'"
    ).fetchone()[0]

    negative = conn.execute(
        "SELECT COUNT(*) FROM history WHERE sentiment='Negative'"
    ).fetchone()[0]

    neutral = conn.execute(
        "SELECT COUNT(*) FROM history WHERE sentiment='Neutral'"
    ).fetchone()[0]

    conn.close()

    return total, positive, negative, neutral


# -----------------------------
# Login
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()

        user = conn.execute(
            """
            SELECT *
            FROM admin
            WHERE username=?
            AND password=?
            """,
            (username, password)
        ).fetchone()

        conn.close()

        if user:

            session["user"] = username

            return redirect(url_for("dashboard"))

        else:

            error = "Invalid Username or Password"

    return render_template(
        "login.html",
        error=error
    )


# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# -----------------------------
# Analyze
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def analyze():

    prediction = None
    confidence = None
    review = ""

    if request.method == "POST":

        review = request.form["review"]

        prediction, confidence = predict_sentiment(review)

        save_prediction(
            review,
            prediction,
            confidence
        )

    return render_template(
        "analyze.html",
        review=review,
        prediction=prediction,
        confidence=confidence
    )

# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    total, positive, negative, neutral = get_dashboard_data()

    return render_template(
        "dashboard.html",
        total=total,
        positive=positive,
        negative=negative,
        neutral=neutral
    )


# -----------------------------
# History
# -----------------------------
@app.route("/history")
def history():

    if "user" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search", "")

    conn = get_connection()

    if search:

        reviews = conn.execute(
            """
            SELECT *
            FROM history
            WHERE review LIKE ?
            OR sentiment LIKE ?
            ORDER BY id DESC
            """,
            (f"%{search}%", f"%{search}%")
        ).fetchall()

    else:

        reviews = conn.execute(
            """
            SELECT *
            FROM history
            ORDER BY id DESC
            """
        ).fetchall()

    conn.close()

    return render_template(
        "history.html",
        reviews=reviews,
        search=search
    )


# -----------------------------
# Delete Review
# -----------------------------
@app.route("/delete/<int:id>")
def delete(id):

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()

    conn.execute(
        "DELETE FROM history WHERE id=?",
        (id,)
    )

    conn.commit()

    conn.close()

    return redirect(url_for("history"))


# -----------------------------
# Export CSV
# -----------------------------
@app.route("/export")
def export():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM history",
        conn
    )

    conn.close()

    filename = "history.csv"

    df.to_csv(
        filename,
        index=False
    )

    return send_file(
        filename,
        as_attachment=True
    )


# -----------------------------
# Edit Review
# -----------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()

    if request.method == "POST":

        review = request.form["review"]

        prediction, confidence = predict_sentiment(review)

        conn.execute(
            """
            UPDATE history
            SET review=?,
                sentiment=?,
                confidence=?
            WHERE id=?
            """,
            (
                review,
                prediction,
                confidence,
                id
            )
        )

        conn.commit()

        conn.close()

        return redirect(url_for("history"))

    review = conn.execute(
        "SELECT * FROM history WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit.html",
        review=review
    )
# -----------------------------
# Home Redirect
# -----------------------------
@app.route("/home")
def home():

    return redirect(url_for("analyze"))


# -----------------------------
# Error Handlers
# -----------------------------
@app.errorhandler(404)
def page_not_found(error):

    return (
        "<h2 style='text-align:center;margin-top:50px;'>"
        "404 - Page Not Found"
        "</h2>",
        404
    )


@app.errorhandler(500)
def internal_server_error(error):

    return (
        "<h2 style='text-align:center;margin-top:50px;'>"
        "500 - Internal Server Error"
        "</h2>",
        500
    )


# -----------------------------
# Run Flask App
# -----------------------------
# -----------------------------
# Run Flask App
# -----------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

