from flask import Flask, render_template, request, redirect, url_for, session
import numpy as np
from tensorflow.keras.models import load_model
from src.utils import preprocess_image
from src.database import init_db
from src.auth import auth
from flask_bcrypt import Bcrypt
import random

app = Flask(__name__)
app.secret_key = 'brain123'

init_db(app)

bcrypt = Bcrypt(app)
app.config['BCRYPT'] = bcrypt

from src.auth import auth
app.register_blueprint(auth, url_prefix='/auth')

model = load_model("model/brain_tumor_best.h5")

with open("model/classes.txt", "r") as f:
    classes = [line.strip() for line in f.readlines()]

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))


@app.route("/predict", methods=["GET", "POST"])
def index():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    prediction = None
    confidence = None
    error = None

    if "num1" not in session or "num2" not in session:
        session["num1"] = random.randint(1, 10)
        session["num2"] = random.randint(1, 10)

    num1 = session["num1"]
    num2 = session["num2"]

    if request.method == "POST":

        user_answer = request.form.get("captcha")

        try:
            if int(user_answer) != (num1 + num2):
                error = "❌ Incorrect CAPTCHA. Try again."

                session["num1"] = random.randint(1, 10)
                session["num2"] = random.randint(1, 10)

                return render_template(
                    "prediction.html",
                    num1=session["num1"],
                    num2=session["num2"],
                    error=error
                )
        except:
            error = "❌ Invalid input in CAPTCHA"
            return render_template(
                "prediction.html",
                num1=num1,
                num2=num2,
                error=error
            )

        file = request.files["file"]

        if file:
            image = preprocess_image(file)
            pred = model.predict(image)[0][0]

            if pred > 0.3:
                prediction = "Tumor"
                confidence = round(float(pred) * 100, 2)
            else:
                prediction = "No Tumor"
                confidence = round((1 - float(pred)) * 100, 2)

        session["num1"] = random.randint(1, 10)
        session["num2"] = random.randint(1, 10)

    return render_template(
        "prediction.html",
        prediction=prediction,
        confidence=confidence,
        error=error,
        num1=session["num1"],
        num2=session["num2"],
        model_name="MobileNetV2"
    )

if __name__ == "__main__":
    app.run(debug=True)