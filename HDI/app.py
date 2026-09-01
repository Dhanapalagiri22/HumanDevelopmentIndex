from flask import Flask, render_template, request, redirect, url_for, session, flash
import joblib
import numpy as np

app = Flask(__name__)
app.secret_key = "your_secret_key"

model = joblib.load("data/model.joblib")  

users = {"admin": "password123"}

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("logged_in"):
        return redirect(url_for("home"))

    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if username in users:
            error = "Username already exists"
        elif password != confirm_password:
            error = "Passwords do not match"
        else:
            users[username] = password
            flash("Account created successfully! You can login now.", "success")
            return redirect(url_for("login"))

    return render_template("register.html", error=error)

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("home"))

    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users and users[username] == password:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password"
            flash(error, "danger")

    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/home")
def home():
    if not session.get("logged_in"):
        flash("Please login first.", "warning")
        return redirect(url_for("login"))
    return render_template("home.html", username=session["username"])

@app.route("/predict", methods=["GET", "POST"])
def index():
    if not session.get("logged_in"):
        flash("Please login first.", "warning")
        return redirect(url_for("login"))
    
    prediction = None
    if request.method == "POST":
        try:
            life = float(request.form["life"])
            mean_school = float(request.form["mean_school"])
            expected_school = float(request.form["expected_school"])
            gni = float(request.form["gni"])
            
            features = np.array([[life, mean_school, expected_school, gni]])
            prediction = model.predict(features)[0]
            prediction = round(prediction, 3)
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
        
    return render_template("index.html", prediction=prediction)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if not session.get("logged_in"):
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    message_sent = False
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        message_sent = True
        flash("Thank you! Your message has been sent.", "success")

    return render_template("contact.html", username=session["username"], message_sent=message_sent)

@app.route("/about")
def about():
    if not session.get("logged_in"):
        flash("Please login first.", "warning")
        return redirect(url_for("login"))
    return render_template("about.html", username=session["username"])

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/")
def root():
    return redirect(url_for("welcome"))

if __name__ == "__main__":
    app.run(debug=True)
