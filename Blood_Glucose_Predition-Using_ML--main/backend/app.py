
from pathlib import Path
from datetime import date
import os
import logging
import sqlite3
import secrets
import re
import math
from functools import wraps

import joblib
import pandas as pd
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    jsonify,
    session,
    send_from_directory,
)
from werkzeug.security import generate_password_hash, check_password_hash


# ============================================================
# PATHS AND CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
PROJECT_DIR = BASE_DIR / "Dr.Diabetic"
TEMPLATE_DIR = PROJECT_DIR / "html_pages"
IMAGE_DIR = PROJECT_DIR / "img"
DATA_DIR = PROJECT_DIR / "data"
DATABASE_DIR = BASE_DIR / "db"

MODEL_PATH = BACKEND_DIR / "gradient_boosting_regressor_model.pkl"
FOOD_DATA_PATH = DATABASE_DIR / "pred_food.csv"
USER_DB_PATH = DATABASE_DIR / "users.sqlite3"

DATABASE_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(
    __name__,
    template_folder=str(TEMPLATE_DIR),
    static_folder=None,
)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")

if not app.secret_key:
    app.secret_key = secrets.token_hex(32)
    logging.warning(
        "FLASK_SECRET_KEY is not configured. Sessions may not persist "
        "across server restarts. Configure a persistent secret for normal use."
    )

app.config.update(
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# USER DATABASE
# ============================================================

def get_user_db():
    connection = sqlite3.connect(str(USER_DB_PATH), timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_user_db():
    connection = get_user_db()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                date_of_birth TEXT,
                location TEXT,
                diabetes_type TEXT,
                duration REAL,
                hba1c REAL,
                c_peptide REAL,
                doctor_consent INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        existing_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(users)")
        }

        migrations = {
            "date_of_birth": "TEXT",
            "location": "TEXT",
            "diabetes_type": "TEXT",
            "duration": "REAL",
            "hba1c": "REAL",
            "c_peptide": "REAL",
            "doctor_consent": "INTEGER NOT NULL DEFAULT 0",
        }

        for column, definition in migrations.items():
            if column not in existing_columns:
                # Column names and definitions come only from this fixed dictionary.
                connection.execute(
                    f"ALTER TABLE users ADD COLUMN {column} {definition}"
                )

        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        logger.exception("Could not initialize the user database.")
        raise

    finally:
        connection.close()


initialize_user_db()


# ============================================================
# CSRF AND AUTHENTICATION HELPERS
# ============================================================

def create_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_urlsafe(32)

    return session["_csrf_token"]


def valid_csrf_token():
    submitted_token = request.form.get("csrf_token", "")
    expected_token = session.get("_csrf_token", "")

    return bool(
        submitted_token
        and expected_token
        and secrets.compare_digest(submitted_token, expected_token)
    )


def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view_function(*args, **kwargs)

    return wrapped_view


def render_auth_error(page, message, status=400):
    context = {
        "error": message,
        "csrf_token": create_csrf_token(),
    }

    if page == "registration.html":
        context["registration_success"] = False

    return render_page(page, **context), status


# ============================================================
# LOAD MACHINE LEARNING MODEL
# ============================================================

model = None
model_bundle = None
model_input_columns = []

if MODEL_PATH.is_file():
    try:
        model_bundle = joblib.load(MODEL_PATH)

        if isinstance(model_bundle, dict) and "model" in model_bundle:
            model = model_bundle["model"]
            model_input_columns = list(
                model_bundle.get("input_columns") or []
            )
        else:
            model = model_bundle

        if not model_input_columns:
            model_input_columns = list(
                getattr(model, "feature_names_in_", [])
            )

        logger.info("ML model loaded from %s", MODEL_PATH)
        logger.info("Expected model columns: %s", model_input_columns)

        if not model_input_columns:
            logger.warning(
                "Model input columns could not be determined. "
                "Prediction will remain unavailable until the expected "
                "feature columns are configured."
            )

    except Exception:
        model = None
        model_input_columns = []
        logger.exception("Could not load the ML model.")
else:
    logger.error("Model file not found: %s", MODEL_PATH)


# ============================================================
# LOAD FOOD DATASET
# ============================================================

food_df = pd.DataFrame()

if FOOD_DATA_PATH.is_file():
    try:
        food_df = pd.read_csv(FOOD_DATA_PATH)
        food_df.columns = food_df.columns.astype(str).str.strip()
        logger.info("Food dataset loaded: %s", food_df.shape)

    except Exception:
        logger.exception("Could not load the food dataset.")
else:
    logger.warning("Food CSV not found: %s", FOOD_DATA_PATH)


# ============================================================
# PAGE HELPERS
# ============================================================

ALLOWED_PAGES = {
    "about.html",
    "account.html",
    "articles.html",
    "consultation.html",
    "diet.html",
    "homepage.html",
    "login.html",
    "prediction.html",
    "registration.html",
    "search.html",
    "videos.html",
}


def render_page(page, **context):
    if page not in ALLOWED_PAGES:
        abort(404)

    if not (TEMPLATE_DIR / page).is_file():
        logger.error("Template file missing: %s", TEMPLATE_DIR / page)
        abort(404)

    return render_template(page, **context)


# ============================================================
# FOOD DATA HELPERS
# ============================================================

def find_food_column(possible_names):
    if food_df.empty:
        return None

    normalized_columns = {
        str(column).strip().casefold(): column
        for column in food_df.columns
    }

    for name in possible_names:
        found = normalized_columns.get(name.strip().casefold())
        if found is not None:
            return found

    return None


def get_food_record(food_name):
    name_column = find_food_column(
        ["Food Name", "Food", "Name", "Food Item"]
    )

    if name_column is None or food_df.empty:
        return None

    matches = food_df[
        food_df[name_column]
        .astype(str)
        .str.strip()
        .str.casefold()
        == food_name.strip().casefold()
    ]

    if matches.empty:
        return None

    return matches.iloc[0].to_dict()


def find_record_value(record, possible_names):
    if not record:
        return None

    normalized_record = {
        str(key).strip().casefold(): value
        for key, value in record.items()
    }

    for name in possible_names:
        value = normalized_record.get(name.strip().casefold())

        if value is None:
            continue

        try:
            if pd.isna(value):
                continue
        except (TypeError, ValueError):
            pass

        return value

    return None


# ============================================================
# BUILD INPUT FOR THE ML MODEL
# ============================================================

def build_prediction_input(form, food_record):
    if model is None:
        raise ValueError("The ML model is not available.")

    if not model_input_columns:
        raise ValueError(
            "Model input columns are unavailable. "
            "Check the saved model and its expected features."
        )

    try:
        age = float(form.get("age", ""))
        weight = float(form.get("weight", ""))
        skin_thickness = float(form.get("skin_thickness", ""))

    except (TypeError, ValueError):
        raise ValueError(
            "Enter valid age, weight and skin thickness values."
        )

    if not all(math.isfinite(v) for v in (age, weight, skin_thickness)):
        raise ValueError("Input values must be finite numbers.")

    diabetes_type = form.get("diabetes_type", "").strip()

    if diabetes_type not in {"Type 1", "Type 2"}:
        raise ValueError("Select a valid diabetes type.")

    if not 1 <= age <= 120:
        raise ValueError("Age must be between 1 and 120.")

    if not 1 <= weight <= 500:
        raise ValueError("Weight must be between 1 and 500 kg.")

    if not 0 <= skin_thickness <= 100:
        raise ValueError("Skin thickness must be between 0 and 100.")

    food_features = {
        "Glycemic Index": ["Glycemic Index", "GI"],
        "Carbohydrates": ["Carbohydrates", "Carbohydrate", "Carbs"],
        "Protein": ["Protein"],
        "Fiber": ["Fiber", "Fibre", "Fiber Content", "Fibre Content"],
    }

    input_values = {
        "Type of Diabetes": diabetes_type,
        "Age": age,
        "Weight": weight,
        "Skin Thickness": skin_thickness,
    }

    for model_column, alternatives in food_features.items():
        value = find_record_value(food_record, alternatives)

        if value is None:
            raise ValueError(
                f"Food dataset does not provide '{model_column}' "
                "for the selected food."
            )

        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            raise ValueError(
                f"Invalid '{model_column}' value in food data."
            )

        if not math.isfinite(numeric_value):
            raise ValueError(
                f"Invalid '{model_column}' value in food data."
            )

        input_values[model_column] = numeric_value

    row = {}

    for column in model_input_columns:
        if column not in input_values:
            raise ValueError(
                f"Model expects feature '{column}', but no matching "
                "input value is configured. Check the model's feature list."
            )

        row[column] = input_values[column]

    return pd.DataFrame([row], columns=model_input_columns)


# ============================================================
# REGISTRATION
# ============================================================

@app.route("/registration", methods=["GET", "POST"])
@app.route("/registration.html", methods=["GET", "POST"])
def registration():
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("account"))

        return render_page(
            "registration.html",
            csrf_token=create_csrf_token(),
            error=None,
            registration_success=False,
        )

    if not valid_csrf_token():
        return render_auth_error(
            "registration.html",
            "Session expired. Refresh the page and try again.",
            400,
        )

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    date_of_birth = request.form.get("date_of_birth", "").strip()
    location = request.form.get("location", "").strip()
    diabetes_type = request.form.get("diabetes_type", "").strip()

    duration_text = request.form.get("duration", "").strip()
    hba1c_text = request.form.get("hba1c", "").strip()
    c_peptide_text = request.form.get("c_peptide", "").strip()

    doctor_consent = (
        1 if request.form.get("doctor_consent") == "yes" else 0
    )

    def show_error(message, status=400):
        return render_auth_error("registration.html", message, status)

    if not 3 <= len(username) <= 40:
        return show_error("Username must contain 3–40 characters.")

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return show_error("Enter a valid email address.")

    if len(email) > 254:
        return show_error("Email address is too long.")

    if len(password) < 8 or len(password.encode("utf-8")) > 1024:
        return show_error("Password must be at least 8 characters long.")

    if not date_of_birth or not location:
        return show_error("Date of birth and location are required.")

    allowed_diabetes_types = {"Type 1", "Type 2", "Gestational", "Other"}

    if diabetes_type not in allowed_diabetes_types:
        return show_error("Select a valid diabetes type.")

    try:
        dob = date.fromisoformat(date_of_birth)

        if dob > date.today():
            return show_error("Date of birth cannot be in the future.")

        if not duration_text:
            return show_error("Enter the duration of diabetes.")

        duration = float(duration_text)
        hba1c = float(hba1c_text) if hba1c_text else None
        c_peptide = float(c_peptide_text) if c_peptide_text else None

        numeric_values = [duration]
        if hba1c is not None:
            numeric_values.append(hba1c)
        if c_peptide is not None:
            numeric_values.append(c_peptide)

        if not all(math.isfinite(value) for value in numeric_values):
            raise ValueError

        if not 0 <= duration <= 120:
            raise ValueError

        if hba1c is not None and not 0 <= hba1c <= 20:
            raise ValueError

        if c_peptide is not None and not 0 <= c_peptide <= 100:
            raise ValueError

    except (ValueError, OverflowError):
        return show_error(
            "Check date of birth, diabetes duration, HbA1c "
            "and C-peptide values."
        )

    password_hash = generate_password_hash(password)
    connection = get_user_db()

    try:
        cursor = connection.execute(
            """
            INSERT INTO users (
                username, email, password_hash, date_of_birth,
                location, diabetes_type, duration, hba1c,
                c_peptide, doctor_consent
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username, email, password_hash, date_of_birth,
                location, diabetes_type, duration, hba1c,
                c_peptide, doctor_consent,
            ),
        )

        user_id = cursor.lastrowid
        connection.commit()

    except sqlite3.IntegrityError:
        connection.rollback()
        return show_error(
            "That username or email is already registered.", 409
        )

    except sqlite3.Error:
        connection.rollback()
        logger.exception("Registration database error.")
        return show_error(
            "Database error. Check the server terminal.", 500
        )

    finally:
        connection.close()

    session.clear()
    session["user_id"] = user_id
    session["username"] = username
    create_csrf_token()

    return redirect(url_for("account"))


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("account"))

        return render_page(
            "login.html",
            csrf_token=create_csrf_token(),
            error=None,
        )

    if not valid_csrf_token():
        return (
            render_page(
                "login.html",
                error="Session expired. Refresh the page and try again.",
                csrf_token=create_csrf_token(),
            ),
            400,
        )

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    connection = get_user_db()

    try:
        user = connection.execute(
            """
            SELECT id, username, password_hash
            FROM users
            WHERE username = ? COLLATE NOCASE
            """,
            (username,),
        ).fetchone()

    except sqlite3.Error:
        logger.exception("Login database error.")
        return (
            render_page(
                "login.html",
                error="Unable to access the user database.",
                csrf_token=create_csrf_token(),
            ),
            500,
        )

    finally:
        connection.close()

    if user is None or not check_password_hash(
        user["password_hash"], password
    ):
        return (
            render_page(
                "login.html",
                error="Invalid username or password.",
                csrf_token=create_csrf_token(),
            ),
            401,
        )

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    create_csrf_token()

    return redirect(url_for("account"))


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout", methods=["POST"])
def logout():
    if not valid_csrf_token():
        abort(400)

    session.clear()
    return redirect(url_for("login"))


# ============================================================
# WEBSITE PAGES
# ============================================================

@app.route("/")
def index():
    landing_file = PROJECT_DIR / "index.html"

    if landing_file.is_file():
        return send_from_directory(str(PROJECT_DIR), "index.html")

    return redirect(url_for("homepage"))


@app.route("/homepage")
@app.route("/homepage.html")
def homepage():
    return render_page("homepage.html")


@app.route("/about")
@app.route("/about.html")
def about():
    return render_page("about.html")


@app.route("/account")
@app.route("/account.html")
@login_required
def account():
    connection = get_user_db()

    try:
        user = connection.execute(
            """
            SELECT username, email, date_of_birth, location,
                   diabetes_type, duration, hba1c, c_peptide,
                   doctor_consent, created_at
            FROM users
            WHERE id = ?
            """,
            (session["user_id"],),
        ).fetchone()

    except sqlite3.Error:
        logger.exception("Could not load account details.")
        abort(500)

    finally:
        connection.close()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    return render_page(
        "account.html",
        user=user,
        username=user["username"],
        csrf_token=create_csrf_token(),
    )


@app.route("/articles")
@app.route("/articles.html")
def articles():
    return render_page("articles.html")


@app.route("/consultation")
@app.route("/consultation.html")
def consultation():
    return render_page("consultation.html")


@app.route("/diet")
@app.route("/diet.html")
def diet():
    return render_page("diet.html")


@app.route("/search")
@app.route("/search.html")
def search():
    return render_page("search.html")


@app.route("/videos")
@app.route("/videos.html")
def videos():
    return render_page("videos.html")


@app.route("/prediction")
@app.route("/prediction.html")
def prediction():
    return render_page("prediction.html")


@app.route("/html_pages/<page>")
def legacy_html_page(page):
    return render_page(page)


# ============================================================
# IMAGE FILES
# ============================================================

@app.route("/img/<path:filename>")
def images(filename):
    requested_path = (IMAGE_DIR / filename).resolve()

    try:
        requested_path.relative_to(IMAGE_DIR.resolve())
    except ValueError:
        abort(404)

    if not requested_path.is_file():
        abort(404)

    return send_from_directory(str(IMAGE_DIR), filename)


# ============================================================
# JAVASCRIPT DATA FILES
# ============================================================

@app.route("/data/<path:filename>")
def data_files(filename):
    requested_path = (DATA_DIR / filename).resolve()

    try:
        requested_path.relative_to(DATA_DIR.resolve())
    except ValueError:
        abort(404)

    if not requested_path.is_file() or requested_path.suffix.lower() != ".js":
        abort(404)

    response = send_from_directory(str(DATA_DIR), filename)
    response.headers["Content-Type"] = "application/javascript; charset=utf-8"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


# ============================================================
# FOOD SEARCH API
# ============================================================

@app.route("/api/foods")
def api_foods():
    if food_df.empty:
        return jsonify({"foods": []})

    name_column = find_food_column(
        ["Food Name", "Food", "Name", "Food Item"]
    )

    if name_column is None:
        return jsonify({"foods": []})

    query = request.args.get("q", "").strip().casefold()

    names = (
        food_df[name_column]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .tolist()
    )

    if query:
        names = [name for name in names if query in name.casefold()]

    return jsonify({"foods": names[:50]})


# ============================================================
# MACHINE LEARNING PREDICTION
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():
    if model is None or not model_input_columns:
        return (
            render_page(
                "prediction.html",
                error=(
                    "The ML model or its feature configuration is unavailable. "
                    "Check the model file and server terminal."
                ),
            ),
            503,
        )

    food_name = request.form.get("food_item", "").strip()

    if not food_name:
        return (
            render_page(
                "prediction.html",
                error="Please select a food item.",
            ),
            400,
        )

    food_record = get_food_record(food_name)

    if food_record is None:
        return (
            render_page(
                "prediction.html",
                error="That food item was not found in the food dataset.",
            ),
            400,
        )

    try:
        input_df = build_prediction_input(request.form, food_record)
        prediction_value = float(model.predict(input_df)[0])

        if not math.isfinite(prediction_value):
            raise ValueError("The model returned an invalid prediction.")

        return render_page(
            "prediction.html",
            prediction_text=(
                "Model estimate: " f"{prediction_value:.2f}"
            ),
            prediction_value=round(prediction_value, 2),
            selected_food=food_name,
            food_details=food_record,
        )

    except (ValueError, TypeError) as exc:
        return (
            render_page(
                "prediction.html",
                error=str(exc),
                selected_food=food_name,
            ),
            400,
        )

    except Exception:
        logger.exception("Prediction failed.")
        return (
            render_page(
                "prediction.html",
                error="Prediction failed. Check the server terminal.",
            ),
            500,
        )


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(error):
    return (
        "<h1>404 - Page Not Found</h1>"
        "<p>The requested page or asset could not be found.</p>"
        '<p><a href="/">Return to the home page</a></p>',
        404,
    )


@app.errorhandler(413)
def request_too_large(error):
    return "Request data is too large.", 413


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"

    app.run(
        host="127.0.0.1",
        port=port,
        debug=debug_mode,
    )
