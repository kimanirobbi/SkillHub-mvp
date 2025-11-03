from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.main import bp

@bp.route('/')
def index():
    return render_template('index.html', title='Home')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route that requires authentication."""
    return render_template('dashboard_new.html', title='Dashboard')
