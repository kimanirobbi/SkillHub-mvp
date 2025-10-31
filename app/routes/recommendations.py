from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import db, Job, Professional
from app.ai.matcher import ProfessionalMatcher

bp = Blueprint('recommendations', __name__)

@bp.route('/api/jobs/<int:job_id>/recommendations', methods=['GET'])
@login_required
def get_recommendations(job_id):
    """
    Get professional recommendations for a specific job.
    
    Query Parameters:
        - max_distance: Maximum distance in kilometers (default: 50)
        - min_rating: Minimum professional rating (default: 0)
        - limit: Maximum number of results (default: 10)
        
    Returns:
        JSON response with recommended professionals and match details
    """
    # Get query parameters with defaults
    max_distance = request.args.get('max_distance', default=50, type=float)
    min_rating = request.args.get('min_rating', default=0, type=float)
    limit = request.args.get('limit', default=10, type=int)
    
    # Get the job with location data
    job = Job.query.get_or_404(job_id)
    
    if not job.location_lat or not job.location_lng:
        return jsonify({
            'error': 'Job location is not specified',
            'code': 400
        }), 400
    
    # Base query for professionals
    query = Professional.query.filter(
        Professional.is_available == True,
        Professional.rating >= min_rating
    )
    
    # Apply distance filter if coordinates are provided
    if job.location_lat and job.location_lng:
        # This is a simplified distance filter - for production, consider using PostGIS or similar
        # for more efficient spatial queries
        pass  # We'll filter in memory after getting the results
    
    professionals = query.all()
    
    if not professionals:
        return jsonify({
            'message': 'No professionals found matching the criteria',
            'recommendations': []
        })
    
    try:
        # Initialize the matcher with custom parameters
        matcher = ProfessionalMatcher(
            similarity_weight=0.7,
            distance_weight=0.3,
            max_distance_km=max_distance
        )
        
        # Get matches
        matches = matcher.match(
            job=job,
            professionals=professionals,
            top_n=limit,
            min_score=0.3  # Minimum matching score threshold
        )
        
        # Format the response
        recommendations = []
        for match in matches:
            pro = match['professional']
            recommendations.append({
                'id': pro.id,
                'name': pro.full_name,
                'profession': pro.profession,
                'photo': pro.profile_picture,
                'rating': pro.rating,
                'total_reviews': pro.total_reviews,
                'hourly_rate': pro.hourly_rate,
                'years_experience': pro.years_experience,
                'skills': pro.get_skills_list() if hasattr(pro, 'get_skills_list') else [],
                'distance_km': match.get('distance_km'),
                'match_score': match['score'],
                'similarity_score': match.get('similarity', 0),
                'distance_score': match.get('distance_score', 0)
            })
        
        return jsonify({
            'job_id': job.id,
            'job_title': job.title,
            'total_recommendations': len(recommendations),
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate recommendations',
            'details': str(e),
            'code': 500
        }), 500
