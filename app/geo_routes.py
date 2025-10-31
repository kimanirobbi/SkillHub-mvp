from flask import Blueprint, request, jsonify, render_template
from sqlalchemy import text
from app import db

# Blueprint for geo-related routes
geo_bp = Blueprint("geo", __name__)

def _is_postgres() -> bool:
    try:
        return db.engine.url.drivername.startswith("postgresql")
    except Exception:
        return False

@geo_bp.route("/api/professionals/nearby")
def get_nearby():
    if not _is_postgres():
        return (
            jsonify({
                "error": "Geo search requires PostgreSQL + PostGIS.",
                "hint": "Set DATABASE_URL to a PostgreSQL URL with PostGIS enabled in your .env."
            }),
            501,
        )

    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))
    radius = float(request.args.get("radius", 5000))  # meters

    # Note: This query requires PostgreSQL with PostGIS extension enabled
    query = text(
        """
        SELECT id, full_name, profession, ST_AsText(location) as coords
        FROM professionals
        WHERE ST_DWithin(location, ST_MakePoint(:lon, :lat)::geography, :radius);
        """
    )

    results = db.session.execute(query, {"lat": lat, "lon": lon, "radius": radius}).mappings().all()
    return jsonify([dict(row) for row in results])

@geo_bp.route("/map")
def map_page():
    return render_template("map.html")

@geo_bp.route('/api/nearby-professionals')
def get_nearby_professionals():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    radius = request.args.get('radius', 10000, type=int)  # Default 10km radius
    
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
    return jsonify([dict(row) for row in results])
