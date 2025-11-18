from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.main import bp
from app.forms import JobForm, UpdateProfileForm
from app import db
import os
import secrets
from PIL import Image

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/uploads/profiles', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@bp.route('/')
def index():
    return render_template('index.html', title='Home')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route that requires authentication."""
    return render_template('dashboard.html', title='Dashboard')

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.profile_picture = picture_file
            db.session.commit()
            flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.profile'))
    image_file = url_for('static', filename='uploads/profiles/' + current_user.profile_picture)
    return render_template('profile.html', title='Profile', image_file=image_file, form=form)

@bp.route('/post_job', methods=['GET', 'POST'])
@login_required
def post_job():
    """Route for posting a job."""
    form = JobForm()
    if form.validate_on_submit():
        # Here you would typically save the job to the database
        flash('Your job has been posted!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('post_job.html', title='Post a Job', form=form)

@bp.route('/ai_recommendations')
@login_required
def ai_recommendations():
    """Placeholder route for AI recommendations."""
    return render_template('ai_recommendations.html', title='AI Recommendations')

@bp.route('/payment')
@login_required
def payment():
    """Placeholder route for payments."""
    return render_template('payment.html', title='Payment')
