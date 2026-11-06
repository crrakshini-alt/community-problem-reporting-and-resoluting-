import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-demo-secret")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "civicconnect.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

# Demo credentials for the hackathon prototype. Change before any real deployment.
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "civic123")


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL,
                image TEXT,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TEXT NOT NULL
            )
        """)
        db.commit()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/report", methods=["POST"])
def report():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    category = request.form.get("category", "").strip()
    location = request.form.get("location", "").strip()
    description = request.form.get("description", "").strip()
    photo = request.files.get("photo")

    if not all([name, email, category, location, description]):
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("home"))

    image_name = None
    if photo and photo.filename:
        if not allowed_file(photo.filename):
            flash("Please upload a JPG, PNG, GIF or WEBP image.", "error")
            return redirect(url_for("home"))

        safe_name = secure_filename(photo.filename)
        # Prefix filename to avoid overwriting another user's upload.
        image_name = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{safe_name}"
        photo.save(os.path.join(app.config["UPLOAD_FOLDER"], image_name))

    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO complaints
            (name, email, category, location, description, image, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'Pending', ?)
        """, (name, email, category, location, description, image_name,
              datetime.now().strftime("%d-%m-%Y %I:%M %p")))
        complaint_id = cursor.lastrowid
        db.commit()

    return render_template("success.html", complaint_id=complaint_id)


@app.route("/track", methods=["GET", "POST"])
def track():
    complaint = None
    searched = False
    if request.method == "POST":
        searched = True
        complaint_id = request.form.get("complaint_id", "").strip()
        if complaint_id.isdigit():
            with get_db() as db:
                complaint = db.execute(
                    "SELECT id, category, location, status, created_at FROM complaints WHERE id = ?",
                    (int(complaint_id),)
                ).fetchone()
    return render_template("track.html", complaint=complaint, searched=searched)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("dashboard"))
        flash("Incorrect username or password.", "error")
    return render_template("admin_login.html")


@app.route("/admin")
@admin_required
def dashboard():
    with get_db() as db:
        complaints = db.execute(
            "SELECT * FROM complaints ORDER BY id DESC"
        ).fetchall()
    return render_template("dashboard.html", complaints=complaints)


@app.route("/admin/update/<int:complaint_id>", methods=["POST"])
@admin_required
def update_status(complaint_id):
    status = request.form.get("status", "")
    allowed_statuses = {"Pending", "In Progress", "Resolved"}
    if status not in allowed_statuses:
        abort(400)

    with get_db() as db:
        db.execute("UPDATE complaints SET status = ? WHERE id = ?",
                   (status, complaint_id))
        db.commit()
    flash(f"Complaint #{complaint_id} status updated.", "success")
    return redirect(url_for("dashboard"))


@app.route("/admin/logout")
@admin_required
def admin_logout():
    session.clear()
    return redirect(url_for("home"))


@app.errorhandler(413)
def too_large(_error):
    flash("Image is too large. Maximum upload size is 5 MB.", "error")
    return redirect(url_for("home"))


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    init_db()
    app.run(debug=True)
