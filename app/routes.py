import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import db, limiter
from app.modules import AISuggestion as AISuggestionModel
from flask_login import login_user, logout_user, login_required, current_user
from .utils import role_required
from datetime import datetime
from .forms import JobForm  

# Configuration for file uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_picture(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{datetime.utcnow().timestamp()}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        return f"profiles/{filename}"
    return None

# Create blueprints
auth_bp = Blueprint("auth", __name__)
prof_bp = Blueprint("professional", __name__, url_prefix="/professional")

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
        email = request.form.get("email")
        password = request.form.get("password")
        full_name = request.form.get("full_name")
        bio = request.form.get("bio", "")
        profession = request.form.get("profession")
        
        # Handle file upload
        photo = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename != '':
                photo = save_profile_picture(file)

        # Validate inputs
        if not all([email, password, full_name, profession]):
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("auth.signup"))
            
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("auth.login"))
            
        # Validate password length
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return redirect(url_for("auth.signup"))

        try:
            # Create new user
            username = email.split('@')[0]
            user = User(
                username=username,
                email=email,
                first_name=full_name,  # Store full name in first_name
                bio=bio,
                photo=photo,
                is_professional=bool(profession),
                role='professional' if profession else 'client',
                is_active=True
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            # Create professional profile
            if profession:
                professional = Professional(
                    user_id=user.id,
                    profession=profession,
                    rating=0.0,
                    experience_years=0
                )
                db.session.add(professional)
            
            db.session.commit()
            login_user(user)
            flash("Registration successful! Welcome to SkillHub.", "success")
            return redirect(url_for("auth.dashboard"))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during registration: {str(e)}")
            flash("An error occurred during registration. Please try again.", "danger")
            return redirect(url_for("auth.signup"))

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

        if user and user.check_password(password):
            login_user(user)  # Flask-Login manages session
            flash(f"Welcome back, {user.get_full_name()}!", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for("auth.dashboard"))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


# =======================
# Professional Profile Routes
# =======================

@prof_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('professional')
def profile():
    professional = Professional.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        # Handle profile update
        professional.full_name = request.form.get('full_name', professional.full_name)
        professional.profession = request.form.get('profession', professional.profession)
        professional.bio = request.form.get('bio', professional.bio)
        professional.phone = request.form.get('phone', professional.phone)
        professional.address = request.form.get('address', professional.address)
        professional.city = request.form.get('city', professional.city)
        professional.country = request.form.get('country', professional.country)
        professional.years_experience = int(request.form.get('years_experience', 0))
        professional.hourly_rate = float(request.form.get('hourly_rate', 0))
        professional.skills = request.form.get('skills', '')
        professional.is_available = 'is_available' in request.form
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                picture_path = save_profile_picture(file)
                if picture_path:
                    professional.profile_picture = picture_path
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('professional.profile'))
    
    skills_list = professional.skills.split(',') if professional.skills else []
    return render_template('professional/profile.html', 
                         professional=professional,
                         skills_list=skills_list)

@prof_bp.route('/become_professional', methods=['GET', 'POST'])
@login_required
def become_professional():
    if current_user.role == 'professional':
        return redirect(url_for('professional.profile'))
        
    if request.method == 'POST':
        # Create professional profile
        professional = Professional(
            user_id=current_user.id,
            full_name=request.form.get('full_name', current_user.name),
            profession=request.form.get('profession', ''),
            phone=request.form.get('phone', ''),
            bio=request.form.get('bio', '')
        )
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                picture_path = save_profile_picture(file)
                if picture_path:
                    professional.profile_picture = picture_path
        
        db.session.add(professional)
        
        # Update user role
        current_user.role = 'professional'
        db.session.commit()
        
        flash('You are now a professional! Complete your profile to get started.', 'success')
        return redirect(url_for('professional.profile'))
        
    return render_template('professional/become_professional.html')

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

@auth_bp.route("/payment", methods=["GET", "POST"])
def payment():
    if request.method == "POST":
        amount = request.form.get("amount")
        phone = request.form.get("phone")
        if 'mpesa_api' not in globals():
            flash("Payment service unavailable.", "danger")
            return render_template("payment.html"), 503
        response = mpesa_api.stk_push(phone, amount)
        return render_template("payment.html", response=response)
    return render_template("payment.html")

@auth_bp.route("/payment-success")
def payment_success():
    return render_template("payment-success.html")

@auth_bp.route("/payment-failure")
def payment_failure():
    return render_template("payment-failure.html")

@auth_bp.route("/api/recommended", methods=["GET"])
def recommend():
    user_skills = request.args.get("skills").split(",")
    if 'ai_recommender' not in globals():
        return jsonify({"error": "Recommendation service unavailable"}), 503
    recommendations = ai_recommender.recommend(user_skills)
    return jsonify(recommendations)

@auth_bp.route("/api/ai-suggestions/high-scoring/count")
@login_required
def get_high_scoring_suggestions_count():
    """
    Get the count of high-scoring AI suggestions (score > 0.7)
    """
    try:
        count = AISuggestionModel.query.filter(AISuggestionModel.score > 0.7).count()
        return jsonify({
            'status': 'success',
            'count': count,
            'threshold': 0.7
        })
    except Exception as e:
        current_app.logger.error(f"Error getting high scoring suggestions count: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to get high scoring suggestions count',
            'error': str(e)
        }), 500

@auth_bp.route("/api/jobs/<int:job_id>/recommendations")
@login_required
@limiter.limit("10 per minute")  # Rate limit: 10 requests per minute per IP
def recommend_professionals(job_id):
    """
    Get professional recommendations for a specific job.
    Clears previous suggestions and generates new ones based on the job requirements.
    """
    try:
        # Get the job and professionals
        job = Job.query.get_or_404(job_id)
        professionals = Professional.query.filter_by(is_available=True).all()
        
        # Initialize the matcher
        matcher = ProfessionalMatcher(
            similarity_weight=0.7,
            distance_weight=0.3,
            max_distance_km=50
        )
        
        # Get matches
        matches = matcher.match(job, professionals, top_n=10)
        
        # Clear previous suggestions for this job
        AISuggestion.query.filter_by(job_id=job.id).delete()
        
        # Save new suggestions
        for match in matches:
            suggestion = AISuggestion(
                job_id=job.id,
                professional_id=match['professional'].id,
                score=match['score'],
                distance_km=match.get('distance_km'),
                similarity_score=match.get('similarity'),
                distance_score=match.get('distance_score'),
                is_contacted=False
            )
            db.session.add(suggestion)
        
        db.session.commit()
        
        # Format response
        response = {
            'job_id': job.id,
            'job_title': job.title,
            'total_recommendations': len(matches),
            'recommendations': [{
                'id': m['professional'].id,
                'name': m['professional'].full_name,
                'profession': m['professional'].profession,
                'photo': m['professional'].profile_picture or 'default_profile.png',
                'rating': m['professional'].rating,
                'total_reviews': m['professional'].total_reviews,
                'hourly_rate': m['professional'].hourly_rate,
                'years_experience': m['professional'].years_experience,
                'skills': m['professional'].get_skills_list() if hasattr(m['professional'], 'get_skills_list') else [],
                'score': m['score'],
                'distance_km': m.get('distance_km'),
                'similarity_score': m.get('similarity'),
                'distance_score': m.get('distance_score')
            } for m in matches]
        }
        
        return jsonify(response)
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in recommend_professionals: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to generate recommendations',
            'message': str(e)
        }), 500

@auth_bp.route("/api/nearby-professionals")
@auth_bp.route('/api/seed-professionals')
def seed_professionals():
    # Clear existing professionals
    Professional.query.delete()
    
    # Add test professionals
    professionals = [
        {'full_name': 'John Doe', 'profession': 'Plumber', 'latitude': -1.2921, 'longitude': 36.8219, 'user_id': 1},
        {'full_name': 'Jane Smith', 'profession': 'Electrician', 'latitude': -1.2925, 'longitude': 36.8225, 'user_id': 1},
        {'full_name': 'Mike Johnson', 'profession': 'Carpenter', 'latitude': -1.2930, 'longitude': 36.8230, 'user_id': 1},
        {'full_name': 'Sarah Williams', 'profession': 'Designer', 'latitude': -1.2915, 'longitude': 36.8210, 'user_id': 1},
        {'full_name': 'David Brown', 'profession': 'Developer', 'latitude': -1.2920, 'longitude': 36.8220, 'user_id': 1},
    ]
    
    for p in professionals:
        professional = Professional(**p)
        db.session.add(professional)
    
    db.session.commit()
    return jsonify({'message': 'Test professionals added successfully'})

@auth_bp.route('/api/professionals')
def get_professionals():
    professionals = Professional.query.all()
    return jsonify([
        {
            'id': p.id,
            'name': p.full_name,
            'profession': p.profession,
            'lat': p.latitude,
            'lon': p.longitude
        } for p in professionals
    ])

def get_nearby_professionals():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    radius = request.args.get("radius", 10000, type=int)  # Default 10km radius
    
    if not lat or not lon:
        return jsonify({"error": "Latitude and longitude are required"}), 400
    
    query = """
    SELECT id, full_name, profession, rating,
    ST_AsText(location) AS coords,
    ST_Distance(location, ST_MakePoint(:lon, :lat)::geography) AS distance
    FROM professionals
    WHERE ST_DWithin(location, ST_MakePoint(:lon, :lat)::geography, :radius)
    ORDER BY distance ASC;
    """
    
    results = db.session.execute(query, {"lat": lat, "lon": lon, "radius": radius}).mappings().all()
    return jsonify([{
        "id": r["id"],
        "full_name": r["full_name"],
        "profession": r["profession"],
        "rating": r["rating"],
        "coords": r["coords"],
        "distance": round(float(r["distance"]) / 1000, 2)  # Convert to km
    } for r in results])


@auth_bp.route('/post_job', methods=['POST'])
@login_required
def post_job():
    form = JobForm()
    if form.validate_on_submit():
        job = Job(
            title=form.title.data,
            description=form.description.data,
            profession=form.profession.data,
            location=form.location.data,
            latitude=request.form.get('latitude'),
            longitude=request.form.get('longitude'),
            client_id=current_user.id,
            status='open'
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('auth.dashboard'))
    
    # If form validation fails, show errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Error in {field}: {error}', 'danger')
    return redirect(url_for('auth.dashboard'))