from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from .modules import User
from flask_login import login_user, logout_user, login_required, current_user
from .utils import role_required

# create a blueprint for routes
auth_bp = Blueprint("auth", __name__)

# -----------------------
# Home Route
# -----------------------
@auth_bp.route("/")
def home():
    return render_template("index.html")

# -----------------------
# Signup Route
# -----------------------
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("auth.login"))

        if not password:
            flash("Password is required.", "danger")
            return redirect(url_for("auth.signup"))

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = User(
            name=name,  
            email=email,
            phone=phone,
            password_hash=hashed_password,
            role='client'
        )
         
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")

# login + logout (unchanged, except blueprint reference)...

# -----------------------
# Login Route
# -----------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)  # Flask-Login manages session
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


# -----------------------
# Dashboard (Protected) - see role-based redirect at bottom
# -----------------------

# -----------------------
# Logout
# -----------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
    
@auth_bp.route("/client-dashboard")
@role_required("client")
def client_dashboard():
    return render_template("dashboard.html")

@auth_bp.route("/professional-dashboard")
@role_required("professional")
def professional_dashboard():
    return render_template("dashboard.html")

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "client":
        return redirect(url_for("auth.client_dashboard"))
    elif current_user.role == "professional":
        return redirect(url_for("auth.professional_dashboard"))
    else:
        return "Unknown role", 400
